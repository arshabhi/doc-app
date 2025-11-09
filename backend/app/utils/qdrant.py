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
    mmr_lambda: float = 0.5,
    prefetch_k: Optional[int] = None,
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

    # If MMR, fetch more and include vectors
    effective_limit = prefetch_k if prefetch_k is not None else (limit * 4 if mmr else limit)


    # Perform search
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=effective_limit,
        search_params=qmodels.SearchParams(hnsw_ef=128, exact=False),
        score_threshold=None,
        with_vectors=mmr,
    )

    # MMR (optional)
    if mmr:
        # Keep only results that have vectors available
        results_with_vecs = [r for r in results if getattr(r, "vector", None) is not None]
        if len(results_with_vecs) > 1:
            results = _apply_mmr(query_vector, results_with_vecs, lambda_val=mmr_lambda, top_k=limit)
        else:
            # Not enough to re-rank, just trim to requested limit
            results = results[:limit]
    else:
        results = results[:limit]

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
def _apply_mmr(query_vector: List[float], results, lambda_val: float = 0.5, top_k: int = 5):
    """
    Maximal Marginal Relevance for result diversification.

    Assumes each `result` has `.vector` (list[float]) and `.payload`.
    Uses cosine similarity on L2-normalized vectors.
    """
    import numpy as np

    # Build candidate matrix (n_candidates, dim)
    vecs = [r.vector for r in results if getattr(r, "vector", None) is not None]
    if not vecs:
        return results[:top_k]

    V = np.array(vecs, dtype=float)

    # Normalize candidate vectors (avoid divide-by-zero)
    V_norm = np.linalg.norm(V, axis=1, keepdims=True)
    V_norm[V_norm == 0.0] = 1.0
    V_unit = V / V_norm

    # Normalize query
    q = np.array(query_vector, dtype=float)
    q_norm = np.linalg.norm(q)
    if q_norm == 0.0:
        q_norm = 1.0
    q_unit = q / q_norm

    # Similarity of each candidate to the query
    sim_to_query = V_unit @ q_unit  # shape: (n_candidates,)

    selected = []
    candidate_indices = list(range(len(results)))

    while len(selected) < min(top_k, len(candidate_indices)):
        if not selected:
            # First pick: highest sim to query
            first_idx = int(np.argmax(sim_to_query))
            selected.append(first_idx)
            candidate_indices.remove(first_idx)
            continue

        # Compute max similarity to already selected set (diversity term)
        S = np.array(selected, dtype=int)
        # similarities (remaining x selected)
        rem = np.array(candidate_indices, dtype=int)
        # cosine sims among candidates (since normalized, dot = cosine)
        sims_to_selected = V_unit[rem] @ V_unit[S].T  # shape: (n_remaining, len(selected))
        max_sim_to_selected = sims_to_selected.max(axis=1)  # shape: (n_remaining,)

        # MMR score
        mmr_scores = lambda_val * sim_to_query[rem] - (1.0 - lambda_val) * max_sim_to_selected
        best_local = int(np.argmax(mmr_scores))
        chosen = int(rem[best_local])

        selected.append(chosen)
        candidate_indices.remove(chosen)

    return [results[i] for i in selected]
