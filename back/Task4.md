# **Task 4 – Annotation automatique de fonctions (Propagation de labels / Recommandation)**

## Objectif
Cette tâche vise à **prédire automatiquement la fonction** d’une protéine **non annotée** (ou partiellement annotée) en exploitant les **protéines similaires** dans le graphe.
Dans notre projet, la similarité entre protéines est basée sur les domaines **InterPro** et mesurée par la **similarité de Jaccard**.

Cette tâche correspond à un problème de **classification multi-label** (une protéine peut avoir plusieurs fonctions) et se rapproche d’un système de **recommandation / label propagation** sur graphe.

---

## Données et hypothèses
- Les protéines sont stockées dans MongoDB (Task 1).
- Chaque protéine peut contenir :
  - `InterPro` : liste/chaine des domaines (utilisée pour la similarité)
  - `EC number` : annotation fonctionnelle (label) utilisée pour l’apprentissage/recommandation
- Certaines protéines n’ont **pas** de `EC number` : ce sont les protéines à annoter.

---

## Principe de la méthode (simple, efficace, sans entraînement lourd)
On utilise une **propagation de labels pondérée** :

1) On choisit une protéine cible `u` (par son `Entry`).
2) On calcule ses voisins `v` (protéines similaires) en utilisant les domaines `InterPro` :
   - On compare les ensembles de domaines InterPro et on calcule :
     **Jaccard(u, v) = |Du ∩ Dv| / |Du ∪ Dv|**
3) On garde uniquement les voisins dont la similarité ≥ `jaccard_threshold`.
4) On récupère les labels des voisins (par défaut : `EC number`).
5) Chaque voisin vote pour ses labels, avec un poids égal au score Jaccard :
   - **score(label) = Σ poids(u,v) pour tous les voisins v possédant label**
6) On renvoie les **Top-K labels** ayant les meilleurs scores.
7) (Optionnel) on peut enregistrer les prédictions dans MongoDB (`persist=true`).

✅ Avantage : c’est une approche “ML graphe” **semi-supervisée** mais légère :
pas besoin d’entraîner un modèle, on exploite directement la structure du graphe.

---

## Implémentation backend (FastAPI)

### Fichiers ajoutés
- `back/ml/annotation_task.py`
  - Contient l’algorithme de propagation de labels :
    - parsing multi-label (EC number séparés par `; , |`)
    - calcul des scores pondérés
    - renvoi des prédictions
    - option `persist` pour sauvegarder dans MongoDB
- `back/routers/annotation.py`
  - Router FastAPI pour exposer l’endpoint Task 4
- `back/main.py`
  - Inclusion du router Task 4

---

## Endpoint Task 4

### **POST `/task4/annotate`**
Cet endpoint annote une protéine à partir de son voisinage.

#### Payload (exemple)
```json
{
  "entry": "A0A024QYR9",
  "jaccard_threshold": 0.2,
  "label_field": "EC number",
  "top_k": 5,
  "max_neighbors": 500,
  "persist": false
}
