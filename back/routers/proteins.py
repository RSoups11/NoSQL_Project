from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from document_db.create_mongodb import mongo_load_tsv, get_protein_by_fields, get_collection

router = APIRouter()

class ProteinQuery(BaseModel):
    entry: str = ""
    protein_name: str = ""
    entry_name: str = ""
    organism: str = ""
    sequence: str = ""
    ec_number: str = ""
    interpro: str = ""

@router.post("/proteins/search", tags=["Task 1 - Proteins"])
async def search_proteins(data: ProteinQuery):
    dico = {}

    if data.entry:
        dico["Entry"] = data.entry
    if data.protein_name:
        dico["Protein names"] = data.protein_name
    if data.entry_name:
        dico["Entry Name"] = data.entry_name
    if data.organism:
        dico["Organism"] = data.organism
    if data.sequence:
        dico["Sequence"] = data.sequence
    if data.ec_number:
        dico["EC number"] = data.ec_number
    if data.interpro:
        dico["InterPro"] = data.interpro

    return get_protein_by_fields(dico)

@router.post("/task1/load", tags=["Task 1"])
async def load_default_data():
    try:
        inserted = mongo_load_tsv()  
        return {"message": "MongoDB populated", "inserted": inserted}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/task1/load/{file_name}", tags=["Task 1"])
async def load_named_file(file_name: str):
    try:
        # parents[2] = repository root; data/ is at the root level
        project_root = Path(__file__).resolve().parents[2]
        file_path = project_root / "data" / file_name

        inserted = mongo_load_tsv(str(file_path))
        return {"message": "MongoDB populated", "inserted": inserted, "file": str(file_path)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", tags=["Statistics"])
async def get_stats():
    """
    Calcule des statistiques globales sur les protéines :
    - Total de protéines
    - Protéines avec/sans domaine (InterPro)
    - Protéines avec/sans fonction (EC number)
    """
    try:
        col = get_collection()

        # Total de protéines
        total = col.count_documents({})

        # Protéines sans domaine (InterPro vide ou absent)
        without_domain = col.count_documents({"InterPro": {"$in": ["", None]}})
        with_domain = total - without_domain

        # Protéines sans fonction (EC number vide ou absent)
        without_fct = col.count_documents({"EC number": {"$in": ["", None]}})
        with_fct = total - without_fct

        return {
            "totalProt": total,
            "protWithDomain": with_domain,
            "protWithoutDomain": without_domain,
            "protWithFct": with_fct,
            "protWithoutFct": without_fct,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
