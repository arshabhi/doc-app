# app/utils/qdrant.py

from typing import List, Optional, Dict, Any
import uuid
import numpy as np
from app.core.config import settings

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels


# ==============================================================
# ASYNC Qdrant Client Singleton
# ==============================================================

# Create ONE async client — async-safe and recommended by Qdrant team
async_qdrant = AsyncQdrantClient(url=settings.QDRANT_URL)


# ==============================================================
# Collection Management (ASYNC)
# ==============================================================

async def create_collection(
    collection_name: Optional[str] = None,
    vector_size: int = 1536,
    distance_metric: str = "COSINE",
):
    """
    Creates a Qdrant collection if it does not already exist.
    """
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    collections = await async_qdrant.get_collections()
    existing = {c.name for c in collections.collections}

    if collection_name in existing:
        print(f"⚠️ Collection '{collection_name}' already exists (skipping)")
        return

    await async_qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance=qmodels.Distance[distance_metric],
        ),
    )

    print(f"🧠 Created Qdrant collection '{collection_name}'")


async def delete_collection(collection_name: Optional[str] = None):
    """
    Deletes a Qdrant collection (use with caution!).
    """
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    try:
        await async_qdrant.delete_collection(collection_name)
        print(f"🗑️ Deleted Qdrant collection '{collection_name}'")
    except Exception as e:
        print(f"⚠️ Could not delete collection '{collection_name}': {e}")


# ==============================================================
# ASYNC UPSERT
# ==============================================================

async def upsert_vectors(
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    collection_name: Optional[str] = None,
) -> None:
    """
    Pushes vectors and their payloads to Qdrant.
    Each payload must correspond to a vector.
    """
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    if len(vectors) != len(payloads):
        raise ValueError("Vectors and payload lists must have same length")

    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload=payloads[i],
        )
        for i in range(len(vectors))
    ]

    await async_qdrant.upsert(
        collection_name=collection_name,
        points=points,
    )

    print(f"✨ Async upsert: {len(points)} vectors → '{collection_name}'")


# ==============================================================
# ASYNC Search / Query
# ==============================================================

async def search_vectors(
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

    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    filter_condition = None
    if filters:
        filter_condition = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key=k,
                    match=qmodels.MatchValue(value=v),
                )
                for k, v in filters.items()
            ]
        )

    # Expand limit for MMR
    effective_limit = prefetch_k or (limit * 4 if mmr else limit)

    results = await async_qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=effective_limit,
        with_vectors=mmr,
        search_params=qmodels.SearchParams(hnsw_ef=128, exact=False),
    )

    # MMR (optional)
    if mmr:
        # Keep only results that have vectors available
        results_with_vecs = [r for r in results if getattr(r, "vector", None) is not None]
        if len(results_with_vecs) > 1:
            results = _apply_mmr(
                query_vector, results_with_vecs, lambda_val=mmr_lambda, top_k=limit
            )
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

    # Build candidate matrix (n_candidates, dim)
    vecs = [r.vector for r in results if getattr(r, "vector", None) is not None]
    if not vecs:
        return results[:top_k]

    V = np.array(vecs, dtype=float)

    # Normalize candidate vectors
    V_norm = np.linalg.norm(V, axis=1, keepdims=True)
    V_norm[V_norm == 0.0] = 1.0
    V_unit = V / V_norm

    # Normalize query
    q = np.array(query_vector, dtype=float)
    q_norm = np.linalg.norm(q)
    q_norm = 1.0 if q_norm == 0 else q_norm
    q_unit = q / q_norm

    # Similarity of each candidate to the query
    sim_to_query = V_unit @ q_unit  # shape: (n_candidates,)

    selected = []
    candidate_indices = list(range(len(results)))

    while len(selected) < min(top_k, len(candidate_indices)):
        if not selected:
            # First pick: highest sim to query
            first = int(np.argmax(sim_to_query))
            selected.append(first)
            candidate_indices.remove(first)
            continue

        # Compute max similarity to already selected set (diversity term)
        S = np.array(selected, dtype=int)
        # similarities (remaining x selected)
        rem = np.array(candidate_indices, dtype=int)
        # cosine sims among candidates (since normalized, dot = cosine)
        sims_to_selected = V_unit[rem] @ V_unit[S].T  # shape: (n_remaining, len(selected))
        max_sim_to_selected = sims_to_selected.max(axis=1)  # shape: (n_remaining,)

        # MMR score
        mmr_scores = lambda_val * sim_to_query[rem] - (1 - lambda_val) * max_sim_to_selected
        best = int(np.argmax(mmr_scores))
        chosen = int(rem[best])

        selected.append(chosen)
        candidate_indices.remove(chosen)

    return [results[i] for i in selected]
