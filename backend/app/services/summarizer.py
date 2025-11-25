from langgraph.graph import StateGraph, END
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import time
import os
import asyncio
import json
from dotenv import load_dotenv

from qdrant_client.http import models as qmodels
from app.utils.qdrant import async_qdrant, search_vectors
from app.core.config import settings

from pydantic import BaseModel
from typing import List


# ============================================================
# Models
# ============================================================

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
    user_id: str
    document_id: str
    raw_text: str | None
    has_toc: bool
    toc_sections: list | None
    retrieved_chunks: list | None
    unified_summary: str | None


# ============================================================
# ASYNC – Efficient Qdrant Scroll (fetch first N chunks)
# ============================================================

async def fetch_first_chunks_from_qdrant(user_id, document_id, limit_chunks=5):
    """
    Fetches the first few chunks based on chunk_index for TOC detection.
    """

    filter_condition = qmodels.Filter(
        must=[
            qmodels.FieldCondition(key="owner_id", match=qmodels.MatchValue(value=str(user_id))),
            qmodels.FieldCondition(key="document_id", match=qmodels.MatchValue(value=str(document_id))),
        ]
    )

    all_points = []
    next_page = None

    # Async scroll loop
    while True:
        resp = await async_qdrant.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=filter_condition,
            limit=200,
            with_payload=True,
            with_vectors=False,
            offset=next_page,
        )

        points, next_page = resp

        if points:
            all_points.extend(points)

        if next_page is None:
            break

    valid = [
        p.payload
        for p in all_points
        if p.payload and "chunk_index" in p.payload and "text" in p.payload
    ]

    ordered = sorted(valid, key=lambda x: x["chunk_index"])
    selected = ordered[:limit_chunks]

    return "\n\n".join([item["text"] for item in selected])


# ============================================================
# Agents (All Async)
# ============================================================

async def orchestrator_agent(state: SummaryState):
    structured_llm = llm.with_structured_output(OrchestratorOutput)

    prompt = f"""
You are an expert document analyzer.

Reply ONLY in JSON.

Analyze this document sample and determine if it contains a Table of Contents:

Document sample:
{state["raw_text"][:5000]}
"""

    result: OrchestratorOutput = await structured_llm.ainvoke(prompt)

    state["has_toc"] = result.has_toc
    state["toc_sections"] = result.toc_sections

    return state


async def toc_agent(state: SummaryState):
    structured_llm = llm.with_structured_output(TocSelection)

    prompt = f"""
Select the most important TOC sections to summarize.

TOC:
{state["toc_sections"]}
"""

    result: TocSelection = await structured_llm.ainvoke(prompt)
    state["retrieved_chunks"] = result.sections
    return state


async def qdrant_retrieval_agent(state: SummaryState):
    """
    Semantic retrieval for non-TOC documents.
    """

    embedding_model = HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)

    query_vector = await asyncio.to_thread(
        embedding_model.embed_query,
        "main ideas of entire document",
    )

    results = await search_vectors(
        query_vector=query_vector,
        filters={
            "owner_id": str(state["user_id"]),
            "document_id": str(state["document_id"]),
        },
        limit=5,
        mmr=True,
    )

    state["retrieved_chunks"] = [r["payload"].get("text", "") for r in results]
    return state


async def summarizer_agent(state: SummaryState):
    context_text = "\n\n".join(state["retrieved_chunks"])

    prompt = f"""
Summarize the following content into a unified structured summary:

{context_text}
"""

    result = await llm.ainvoke(prompt)
    state["unified_summary"] = result.content
    return state


async def extract_key_points(summary_text: str) -> list[str]:
    structured_llm = llm.with_structured_output(KeyPointsOutput)

    prompt = f"""
Extract 3-6 key bullet points from this summary:

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
# Final Summary Function
# ============================================================

async def generate_summary(req, user_id, doc, custom=False):
    start = time.time()

    # Fetch early content for TOC detection
    raw_text = await fetch_first_chunks_from_qdrant(user_id, doc.id, limit_chunks=5)

    initial_state = SummaryState(
        user_id=user_id,
        document_id=doc.id,
        raw_text=raw_text,
        has_toc=False,
        toc_sections=[],
        retrieved_chunks=[],
        unified_summary=None,
    )

    result = await graph.ainvoke(initial_state)

    summary_text = result.get("unified_summary", "")
    chunks = result.get("retrieved_chunks", [])

    key_points = await extract_key_points(summary_text)

    processing_time = round(time.time() - start, 2)

    return {
        "content": summary_text,
        "keyPoints": key_points,
        "wordCount": len(summary_text.split()),
        "confidence": round(min(0.99, 0.75 + len(chunks) * 0.03), 2),
        "meta_data": {
            "model": "gemini-2.5-flash",
            "processingTime": processing_time,
        },
    }
