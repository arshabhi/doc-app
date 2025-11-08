# app/utils/qdrant.py
from typing import List, Optional, Dict, Any
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings

# ==============================================================
# Qdrant Client Initialization
# ==============================================================
def get_qdrant_client() -> QdrantClient:
    """
    Returns a Qdrant client connected to the configured endpoint.
    """
    return QdrantClient(url=settings.QDRANT_URL)


# ==============================================================
# Collection Management
# ==============================================================

def create_collection(
    collection_name: Optional[str] = None,
    vector_size: int = 1536,
    distance_metric: str = "COSINE"
) -> None:
    """
    Creates a Qdrant collection if it does not already exist.
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance[distance_metric],
            ),
        )
        print(f"🧠 Created Qdrant collection '{collection_name}'")
    else:
        print(f"✅ Qdrant collection '{collection_name}' already exists")


def delete_collection(collection_name: Optional[str] = None) -> None:
    """
    Deletes a Qdrant collection (use with caution!).
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    try:
        client.delete_collection(collection_name)
        print(f"🗑️ Deleted Qdrant collection '{collection_name}'")
    except Exception as e:
        print(f"⚠️ Error deleting collection '{collection_name}': {e}")


# ==============================================================
# Data Upsert / Push
# ==============================================================

def upsert_vectors(
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    collection_name: Optional[str] = None
) -> None:
    """
    Pushes vectors and their payloads to Qdrant.
    Each payload must correspond to a vector.
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    if len(vectors) != len(payloads):
        raise ValueError("Number of vectors and payloads must match.")

    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload=payloads[i],
        )
        for i in range(len(vectors))
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"✅ Upserted {len(points)} vectors to '{collection_name}'")


# ==============================================================
# Fetch / Search (with optional filters and MMR)
# ==============================================================

def search_vectors(
    query_vector: List[float],
    collection_name: Optional[str] = None,
    limit: int = 5,
    mmr: bool = True,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k similar vectors using cosine similarity.
    Optionally uses MMR (Maximal Marginal Relevance) for diversity
    and Qdrant filtering for scoped search.
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Construct optional filter
    filter_condition = None
    if filters:
        must_conditions = [
            qmodels.FieldCondition(
                key=k,
                match=qmodels.MatchValue(value=v),
            )
            for k, v in filters.items()
        ]
        filter_condition = qmodels.Filter(must=must_conditions)

    # Perform search
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=limit,
        search_params=qmodels.SearchParams(hnsw_ef=128, exact=False),
        score_threshold=None,
        with_vectors=False,
    )
    # print("results", results)

    # MMR (optional) #TODO
    # if mmr and len(results) > 1:
    #     results = _apply_mmr(query_vector, results, lambda_val=0.5, top_k=limit)

    return [
        {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


# ==============================================================
# Helper: Maximal Marginal Relevance (MMR)
# ==============================================================

def _apply_mmr(query_vector, results, lambda_val=0.5, top_k=5):
    """
    Implements Maximal Marginal Relevance for re-ranking.
    """
    import numpy as np

    query = np.array(query_vector)
    vectors = np.array([r.vector for r in results if hasattr(r, "vector")])
    if len(vectors) == 0:
        return results

    # Compute similarity to query
    sim_to_query = np.dot(vectors, query) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(query))

    selected = []
    while len(selected) < min(top_k, len(results)):
        if not selected:
            idx = np.argmax(sim_to_query)
            selected.append(idx)
            continue

        remaining = [i for i in range(len(results)) if i not in selected]
        diversity = np.max(np.dot(vectors[remaining], vectors[selected].T), axis=1)
        scores = lambda_val * sim_to_query[remaining] - (1 - lambda_val) * diversity
        idx = remaining[np.argmax(scores)]
        selected.append(idx)

    return [results[i] for i in selected]
