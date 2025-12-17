import pymongo
import pandas as pd
from pathlib import Path
from pymongo import ASCENDING
from typing import Dict, Any

MONGO_HOST = "localhost"
MONGO_PORT = 27017
DB_NAME = "proteins_data"
COLLECTION_NAME = "proteins"

# Chemin par défaut 
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "data_sample.tsv"


def get_database():
    """Connexion MongoDB -> retourne la base DB_NAME."""
    client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
    return client[DB_NAME]


def get_collection():
    """Retourne la collection MongoDB utilisée (proteins)."""
    db = get_database()
    return db[COLLECTION_NAME]


def init_indexes():
    """Crée des index pour accélérer les recherches sur les champs fréquents."""
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
    - Si un fichier est donné -> on le prend
    - Sinon -> on prend DEFAULT_DATA_FILE
    - On supprime (drop) l’ancienne collection si elle existe
    - On insère toutes les lignes en une fois (bulk insert)
    Retourne le nombre de documents insérés
    """
    # Choix du fichier TSV
    path = Path(file_path) if file_path else DEFAULT_DATA_FILE

    # vérifier que le tsv existe 
    if not path.exists():
        raise FileNotFoundError(f"TSV introuvable: {path}")

    db = get_database()

    # Si la collection existe déjà, on la supprime pour repartir propre
    if COLLECTION_NAME in db.list_collection_names():
        db[COLLECTION_NAME].drop()
        
    # On récupère la collection vide
    col = db[COLLECTION_NAME]

    # Lecture du TSV en DataFrame pandas
    df = pd.read_table(path, sep="\t")
    # Remplace les valeurs manquantes (NaN) par une chaîne vide
    df = df.fillna("")
    
    # Conversion en liste de dictionnaires (1 ligne = 1 document MongoDB)
    records = df.to_dict("records")
    # Insertion en masse (beaucoup plus rapide que ligne par ligne)
    if records:
        col.insert_many(records)
        
    # Création des index après insertion
    init_indexes()
    # Nombre de documents insérés
    return len(records)


def get_protein_by_fields(filters: Dict[str, str]):
    """
    Recherche multi-champs avec regex insensible à la casse.
    -> Si on cherche organism="Mouse", ça matche "Mus musculus (Mouse)".
    """
    col = get_collection()
    query: Dict[str, Any] = {}

    # On parcourt les filtres envoyés par l’API/front
    for key, value in filters.items():
        value = value.strip()
        if not value:
            continue # si le champ est vide, on ignore

        # Recherche "contient" (regex) + insensible à la casse
        query[key] = {
            "$regex": value,
            "$options": "i",  
        }

    # On enlève _id de MongoDB dans le résultat pour le front
    cursor = col.find(query, {"_id": 0})
    return list(cursor)
