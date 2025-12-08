# back/routers/graph.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from big_graph import compute_neighbors, push_ego_graph_to_neo4j

router = APIRouter(prefix="/task2", tags=["Task 2 - Big graph"])


class EgoGraphRequest(BaseModel):
    entry: str
    jaccard_threshold: float = 0.3


@router.post("/ego_graph")
def build_ego_graph(params: EgoGraphRequest):
    """
    1. Calcule les voisins de la protéine `entry` via Jaccard sur InterPro.
    2. Construit un sous-graphe local dans Neo4j (center + voisins).
    3. Retourne les infos (liste de voisins + poids).
    """
    try:
        center, neighbors = compute_neighbors(
            entry=params.entry,
            threshold=params.jaccard_threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    summary = push_ego_graph_to_neo4j(center, neighbors)

    return {
        "center": center,
        "neighbors": neighbors,
        "summary": summary,
    }
