from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Tuple, Any

from document_db.create_mongodb import get_collection
from graph_db.neo4j_client import get_driver, init_constraints


def parse_domains(interpro_field: str) -> List[str]:
    """
    Les domaines InterPro sont séparés par ';'
    ex : 'IPR0001;IPR0002;IPR0003'
    """
    if not interpro_field:
        return []
    parts = [p.strip() for p in interpro_field.split(";")]
    return [p for p in parts if p]


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = a & b
    if not inter:
        return 0.0
    union = a | b
    return len(inter) / len(union)


def _load_indexes() -> Tuple[Dict[str, set], Dict[str, Dict[str, Any]], Dict[str, set]]:
    """
    Charge toutes les protéines depuis MongoDB et construit :
      - protein_domains[entry] = set(domains)
      - protein_meta[entry] = {"name": ..., "organism": ...}
      - domain_index[domain] = set(entries)
    """
    collection = get_collection()
    cursor = collection.find(
        {},
        {
            "_id": 0,
            "Entry": 1,
            "Protein names": 1,
            "Organism": 1,
            "InterPro": 1,
        },
    )

    protein_domains: Dict[str, set] = {}
    protein_meta: Dict[str, Dict[str, Any]] = {}
    domain_index: Dict[str, set] = defaultdict(set)

    for doc in cursor:
        entry = doc.get("Entry")
        interpro_raw = doc.get("InterPro", "")
        domains = set(parse_domains(interpro_raw))
        if not entry or not domains:
            continue

        organism = doc.get("Organism", "")

        protein_domains[entry] = domains
        protein_meta[entry] = {
            "entry": entry,
            "name": doc.get("Protein names", ""),
            "organism": organism,
        }
        for d in domains:
            domain_index[d].add(entry)

    return protein_domains, protein_meta, domain_index


@lru_cache(maxsize=1)
def get_indexes() -> Tuple[Dict[str, set], Dict[str, Dict[str, Any]], Dict[str, set]]:
    """
    Cache en mémoire les index. Chargé une seule fois
    par lancement du backend, puis réutilisé.
    """
    return _load_indexes()


def compute_neighbors(entry: str, threshold: float) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Calcule les voisins d'une protéine donnée en utilisant l'index en mémoire.
    Retourne :
      - center: métadonnées de la protéine centrale
      - neighbors: liste de dicts {entry, name, organism, weight}
    """
    protein_domains, protein_meta, domain_index = get_indexes()

    if entry not in protein_domains:
        raise ValueError(f"Entry '{entry}' introuvable ou sans domaines InterPro")

    target_domains = protein_domains[entry]

    # Union des listes d'entries pour chacun des domaines de la protéine
    candidates = set()
    for d in target_domains:
        candidates |= domain_index.get(d, set())
    if entry in candidates:
        candidates.remove(entry)

    neighbors: List[Dict[str, Any]] = []
    for cand in candidates:
        w = jaccard(target_domains, protein_domains[cand])
        if w >= threshold:
            meta = protein_meta[cand]
            neighbors.append(
                {
                    "entry": meta["entry"],
                    "name": meta["name"],
                    "organism": meta["organism"],
                    "weight": w,
                }
            )

    # On peut trier les voisins par score décroissant
    neighbors.sort(key=lambda x: x["weight"], reverse=True)

    center = protein_meta[entry]
    return center, neighbors


def push_ego_graph_to_neo4j(center: Dict[str, Any], neighbors: List[Dict[str, Any]]) -> Dict[str, Any]:
    driver = get_driver()
    init_constraints()

    center_entry = center["entry"]

    with driver.session() as session:
        # On garde Neo4j petit : on efface les anciens noeuds
        session.run("MATCH (n:Protein) DETACH DELETE n")

        nodes = [center] + neighbors
        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Protein {entry: row.entry})
            SET p.name = row.name,
                p.organism = row.organism
            """,
            rows=nodes,
        )

        edges = [
            {"source": center_entry, "target": n["entry"], "weight": n["weight"]}
            for n in neighbors
        ]

        if edges:
            session.run(
                """
                UNWIND $edges AS edge
                MATCH (c:Protein {entry: edge.source})
                MATCH (n:Protein {entry: edge.target})
                MERGE (c)-[r:SIMILAR]->(n)
                SET r.weight = edge.weight
                """,
                edges=edges,
            )

    return {
        "center_entry": center_entry,
        "num_neighbors": len(neighbors),
    }
