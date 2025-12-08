from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from document_db.create_mongodb import mongo_load_tsv, get_protein_by_fields

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
        # parents[1] = back/
        back_dir = Path(__file__).resolve().parents[1]
        file_path = back_dir / "data" / file_name

        inserted = mongo_load_tsv(str(file_path))
        return {"message": "MongoDB populated", "inserted": inserted, "file": str(file_path)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
