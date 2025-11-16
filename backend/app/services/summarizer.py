from langgraph.graph import StateGraph, END
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import time
import os
import asyncio
import json
from dotenv import load_dotenv

from qdrant_client.http import models as qmodels
from app.utils.qdrant import get_qdrant_client
from app.core.config import settings


from pydantic import BaseModel
from typing import List, Optional

class OrchestratorOutput(BaseModel):
    has_toc: bool
    toc_sections: List[str]

class TocSelection(BaseModel):
    sections: List[str]

class KeyPointsOutput(BaseModel):
    key_points: List[str]

# ============================================================
# ENV + LLM
# ============================================================

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found in environment variables.")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2,
)

# ============================================================
# LangGraph State
# ============================================================

class SummaryState(dict):
    """
    Workflow state passed between LangGraph nodes.
    """
    user_id: str
    document_id: str
    raw_text: str | None
    has_toc: bool
    toc_sections: list | None
    retrieved_chunks: list | None
    unified_summary: str | None


# ============================================================
# Efficient Qdrant Scroll — Fetch First N Chunks (by chunk_index)
# ============================================================

async def fetch_first_chunks_from_qdrant(user_id, document_id, limit_chunks=3):
    """
    Retrieves the first N chunks (ordered by chunk_index) using Qdrant Scroll.
    Fully compatible with Qdrant Python client which returns (points, next_page).
    """

    client = get_qdrant_client()

    filter_condition = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="owner_id", match=qmodels.MatchValue(value=str(user_id))
            ),
            qmodels.FieldCondition(
                key="document_id", match=qmodels.MatchValue(value=str(document_id))
            )
        ]
    )

    all_points = []
    next_page = None

    # Scroll loop
    while True:
        points, next_page = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=filter_condition,
            limit=200,
            with_payload=True,
            with_vectors=False,   # we only need metadata + text
            offset=next_page,
        )

        if points:
            all_points.extend(points)

        if next_page is None:
            break

    # Extract valid payloads
    valid = [
        p.payload for p in all_points
        if "chunk_index" in p.payload and "text" in p.payload
    ]

    # Sort by chunk_index ascending
    ordered = sorted(valid, key=lambda x: x["chunk_index"])

    # Take the first N chunks
    selected = ordered[:limit_chunks]

    return "\n\n".join([item["text"] for item in selected])


# ============================================================
# Agents
# ============================================================

async def orchestrator_agent(state: SummaryState):
    """
    Determines whether document contains a TOC / Index.
    """
    structured_llm = llm.with_structured_output(OrchestratorOutput)
    prompt = f"""
You are an expert document analyzer.

STRICT RULES:
- Your ENTIRE reply must be ONLY valid JSON.
- No markdown, no explanation, no commentary.
- Format: {{"has_toc": true/false, "toc_sections": [ ... ]}}

Analyze this document sample and determine if it contains a Table of Contents:

Document sample:
{state["raw_text"][:5000]}
"""

    result = await structured_llm.ainvoke(prompt)
    # data = json.loads(result.content)

    state["has_toc"] = result.has_toc
    state["toc_sections"] = result.toc_sections

    return state


async def toc_agent(state: SummaryState):
    """
    Selects important TOC sections.
    """
    structured_llm = llm.with_structured_output(TocSelection)
    prompt = f"""
Your job is to select the most important sections from this TOC
for producing a global document summary.

TOC:
{state["toc_sections"]}

Return a JSON list of the most relevant section titles.
"""

    result = await structured_llm.ainvoke(prompt)
    # selected = json.loads(result.content)

    state["retrieved_chunks"] = result.sections
    return state


async def qdrant_retrieval_agent(state: SummaryState):
    """
    Semantic retrieval of chunks when no TOC is detected.
    """

    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    query_vector = await asyncio.to_thread(
        embedding_model.embed_query,
        "main ideas of entire document"
    )

    from app.utils.qdrant import search_vectors

    results = search_vectors(
        query_vector=query_vector,
        filters={
            "owner_id": str(state["user_id"]),
            "document_id": str(state["document_id"])
        },
        limit=5,
        mmr=True,
    )

    chunks = [res["payload"].get("text", "") for res in results if res.get("payload")]
    state["retrieved_chunks"] = chunks
    return state


async def summarizer_agent(state: SummaryState):
    """
    Summarizes all retrieved content into unified summary.
    """
    context_text = "\n\n".join(state["retrieved_chunks"])

    prompt = f"""
You are a professional summarizer.
Summarize the following document content into a unified, coherent summary.

Content:
{context_text}

Provide a structured summary with:
- Main themes
- Key arguments
- Important details
- Final conclusions
"""

    result = await llm.ainvoke(prompt)
    state["unified_summary"] = result.content
    return state


async def extract_key_points(summary_text: str) -> list[str]:
    
    structured_llm = llm.with_structured_output(KeyPointsOutput)

    prompt = f"""
Extract 3-6 key bullet points from the summary below.

Summary:
{summary_text}
"""

    result: KeyPointsOutput = await structured_llm.ainvoke(prompt)
    return result.key_points

# ============================================================
# LangGraph Workflow
# ============================================================

workflow = StateGraph(SummaryState)

workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("toc_agent", toc_agent)
workflow.add_node("qdrant_agent", qdrant_retrieval_agent)
workflow.add_node("summarizer", summarizer_agent)

workflow.set_entry_point("orchestrator")

def select_path(state: SummaryState):
    return "toc_agent" if state["has_toc"] else "qdrant_agent"

workflow.add_conditional_edges(
    "orchestrator",
    select_path,
    {
        "toc_agent": "toc_agent",
        "qdrant_agent": "qdrant_agent",
    },
)

workflow.add_edge("toc_agent", "summarizer")
workflow.add_edge("qdrant_agent", "summarizer")
workflow.add_edge("summarizer", END)

graph = workflow.compile()


# ============================================================
# Final User-Facing Summary Function
# ============================================================

async def generate_summary(req, user_id, doc, custom=False):
    """
    Generates a structured summary using LangGraph workflow.
    """

    start_time = time.time()

    # Fetch early content for TOC detection
    raw_text = await fetch_first_chunks_from_qdrant(user_id, doc.id, limit_chunks=5)

    # Build initial workflow state
    initial_state = SummaryState(
        user_id=user_id,
        document_id=doc.id,
        raw_text=raw_text,
        has_toc=False,
        toc_sections=[],
        retrieved_chunks=[],
        unified_summary=None,
    )

    # Execute workflow
    result = await graph.ainvoke(initial_state)

    summary_text = result.get("unified_summary", "")
    chunks = result.get("retrieved_chunks", [])


    # Extract chunk indices
    source_chunks = []
    for c in chunks:
        if isinstance(c, dict) and "chunk_index" in c:
            source_chunks.append(c["chunk_index"])

    key_points = await extract_key_points(summary_text)

    # Final metadata
    word_count = len(summary_text.split())
    confidence = round(min(0.99, 0.75 + (len(chunks) * 0.03)), 2)
    processing_time = round(time.time() - start_time, 2)

    return {
        "content": summary_text,
        "keyPoints": key_points,
        "wordCount": word_count,
        "confidence": confidence,
        "meta_data": {
            "model": "gemini-2.5-flash",
            "processingTime": processing_time,
            "sourceChunks": source_chunks,
        },
    }
