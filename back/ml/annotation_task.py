from __future__ import annotations
from typing import Any, Dict, List, Tuple
from collections import defaultdict

from document_db.create_mongodb import get_collection
from graph_db.big_graph import compute_neighbors


def _parse_labels(raw: Any) -> List[str]:
    """
    Transforme un champ multi-label en liste.
    Dans tes TSV, EC number est souvent une string (ex: "1.1.1.1; 2.7.11.1")
    On supporte aussi ',', '|', espaces.
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    s = str(raw).strip()
    if not s:
        return []
    for sep in [";", ",", "|"]:
        s = s.replace(sep, " ")
    parts = [p.strip() for p in s.split() if p.strip()]
    # dédoublonnage en gardant l’ordre
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def annotate_protein(
    entry: str,
    jaccard_threshold: float = 0.3,
    label_field: str = "EC number",
    top_k: int = 5,
    max_neighbors: int = 200,
    persist: bool = False,
) -> Dict[str, Any]:
    """
    Prédit des labels (EC number / GO terms…) pour une protéine `entry`
    en utilisant les voisins (Jaccard sur InterPro) et un vote pondéré.

    - neighbors: compute_neighbors(entry, threshold) (déjà optimisé + cache) :contentReference[oaicite:1]{index=1}
    - score(label) = somme des poids des voisins qui possèdent ce label
    - multi-label : chaque voisin peut contribuer à plusieurs labels

    Retourne un JSON prêt à envoyer au front.
    """
    if top_k <= 0:
        top_k = 5
    if max_neighbors <= 0:
        max_neighbors = 200

    # 1) Voisinage (Task2)
    center_meta, neighbors = compute_neighbors(entry=entry, threshold=jaccard_threshold)
    neighbors = neighbors[:max_neighbors]

    col = get_collection()

    # 2) Récupère labels de la cible + labels des voisins en 1 seule requête MongoDB ($in)
    entries = [entry] + [n["entry"] for n in neighbors]
    projection = {"_id": 0, "Entry": 1, label_field: 1, "Protein names": 1, "Organism": 1}
    docs = list(col.find({"Entry": {"$in": entries}}, projection))

    by_entry: Dict[str, Dict[str, Any]] = {d["Entry"]: d for d in docs}
    target_doc = by_entry.get(entry, {})
    target_labels = _parse_labels(target_doc.get(label_field, ""))

    # 3) Si déjà labellisée : on renvoie aussi l’info (utile au front)
    already_labeled = len(target_labels) > 0

    # 4) Vote pondéré sur les labels des voisins
    label_scores: Dict[str, float] = defaultdict(float)
    label_support: Dict[str, int] = defaultdict(int)

    used_neighbors = 0
    total_weight = 0.0

    for n in neighbors:
        n_entry = n["entry"]
        w = float(n.get("weight", 0.0))
        if w <= 0:
            continue

        n_doc = by_entry.get(n_entry)
        if not n_doc:
            continue

        n_labels = _parse_labels(n_doc.get(label_field, ""))
        if not n_labels:
            continue

        used_neighbors += 1
        total_weight += w

        for lab in n_labels:
            label_scores[lab] += w
            label_support[lab] += 1

    # 5) Normalisation simple (optionnelle mais pratique pour comparer)
    # score_norm = score / somme des poids utilisés (si >0)
    predictions = []
    if total_weight > 0:
        for lab, sc in label_scores.items():
            predictions.append(
                {
                    "label": lab,
                    "score": sc,
                    "score_norm": sc / total_weight,
                    "support": label_support[lab],
                }
            )
        predictions.sort(key=lambda x: x["score"], reverse=True)
        predictions = predictions[:top_k]

    result = {
        "center": center_meta,  # entry/name/organism (vient de big_graph.py) :contentReference[oaicite:2]{index=2}
        "entry": entry,
        "label_field": label_field,
        "already_labeled": already_labeled,
        "existing_labels": target_labels,
        "jaccard_threshold": jaccard_threshold,
        "neighbors_found": len(neighbors),
        "neighbors_used_for_vote": used_neighbors,
        "predictions": predictions,
        "note": (
            "Aucun voisin labellisé trouvé (augmente le seuil ou vérifie les données)."
            if used_neighbors == 0
            else ""
        ),
    }

    # 6) Option: écrire la prédiction dans MongoDB
    if persist and predictions:
        col.update_one(
            {"Entry": entry},
            {
                "$set": {
                    "Predicted": {
                        "label_field": label_field,
                        "jaccard_threshold": jaccard_threshold,
                        "top_k": top_k,
                        "predictions": predictions,
                    }
                }
            },
        )

    return result
