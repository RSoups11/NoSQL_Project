import pymongo
import pandas as pd
from pathlib import Path
from pymongo import ASCENDING
from typing import Dict, Any

MONGO_HOST = "localhost"
MONGO_PORT = 27017
DB_NAME = "proteins_data"
COLLECTION_NAME = "proteins"

# Chemin par défaut basé sur TON arborescence
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "data_sample.tsv"


def get_database():
    client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
    return client[DB_NAME]


def get_collection():
    db = get_database()
    return db[COLLECTION_NAME]


def init_indexes():
    col = get_collection()
    col.create_index([("Entry", ASCENDING)])
    col.create_index([("Protein names", ASCENDING)])
    col.create_index([("Entry Name", ASCENDING)])
    col.create_index([("Organism", ASCENDING)])
    col.create_index([("EC number", ASCENDING)])
    col.create_index([("InterPro", ASCENDING)])


def mongo_load_tsv(file_path: str | None = None) -> int:
    """
    Recharge la collection MongoDB depuis un TSV.
    - Drop si existe
    - Insert en bulk
    Retourne le nombre de documents insérés
    """
    path = Path(file_path) if file_path else DEFAULT_DATA_FILE

    if not path.exists():
        raise FileNotFoundError(f"TSV introuvable: {path}")

    db = get_database()

    if COLLECTION_NAME in db.list_collection_names():
        db[COLLECTION_NAME].drop()

    col = db[COLLECTION_NAME]

    df = pd.read_table(path, sep="\t")
    df = df.fillna("")

    records = df.to_dict("records")
    if records:
        col.insert_many(records)

    init_indexes()
    return len(records)


def get_protein_by_fields(filters: Dict[str, str]):
    """
    Recherche multi-champs avec regex insensible à la casse.
    -> Si on cherche organism="Mouse", ça matche "Mus musculus (Mouse)".
    """
    col = get_collection()
    query: Dict[str, Any] = {}

    for key, value in filters.items():
        value = value.strip()
        if not value:
            continue

        # On échappe le texte et on utilise un regex "contient", insensible à la casse
        query[key] = {
            "$regex": value,
            "$options": "i",  # case-insensitive
        }

    cursor = col.find(query, {"_id": 0})
    return list(cursor)
