from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ml.annotation_task import annotate_protein

router = APIRouter(prefix="/task4", tags=["Task 4 - Annotation"])


class AnnotationRequest(BaseModel):
    entry: str = Field(..., description="Identifiant UniProt (champ Entry)")
    jaccard_threshold: float = Field(0.3, ge=0.0, le=1.0)
    label_field: str = Field("EC number", description="Ex: 'EC number' ou champ GO si présent")
    top_k: int = Field(5, ge=1, le=50)
    max_neighbors: int = Field(200, ge=1, le=5000)
    persist: bool = False


@router.post("/annotate")
def annotate(req: AnnotationRequest):
    try:
        return annotate_protein(
            entry=req.entry.strip(),
            jaccard_threshold=req.jaccard_threshold,
            label_field=req.label_field,
            top_k=req.top_k,
            max_neighbors=req.max_neighbors,
            persist=req.persist,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
