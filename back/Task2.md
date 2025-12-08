
---

# **Task2 – Construction du graphe de protéines**

Ce document décrit l’installation, le setup, le lancement et l’utilisation de la **Tâche 2**, ainsi que la justification technique de l’approche **big data** retenue.

**Important** :
Cette tâche **doit être exécutée après la Tâche 1**, car elle s’appuie sur la base MongoDB contenant l’ensemble des protéines et leurs domaines InterPro.

---

# **Prérequis & Installations nécessaires**

### Avoir exécuté Task 1 au préalable

Avant de lancer Task 2, la base MongoDB doit être initialisée via :

* `POST /task1/load` dans FastAPI Swagger
  -> Cela insère toutes les protéines dans la base `proteins_data.proteins`.

---

### Installation de Neo4j

La Task 2 nécessite Neo4j pour afficher un **sous-graphe local** autour d’une protéine.

#### Installation via apt (Ubuntu / Debian)

```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo "deb https://debian.neo4j.com stable 5" | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j
```

Démarrer Neo4j :

```bash
sudo systemctl start neo4j
sudo systemctl enable neo4j
```

Accéder au Browser :

[http://localhost:7474](http://localhost:7474)

---

# **Setup du Backend**

Le backend repose sur FastAPI.

Lancer le serveur :

```bash
cd back
uvicorn main:app --reload
```

La documentation interactive est disponible ici :

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# **Utilisation de la Task 2**

La Task 2 repose sur **un seul endpoint** :

### `POST /task2/ego_graph`

Il permet :

1. d’identifier les **voisins** d’une protéine (selon la similarité de Jaccard sur InterPro),
2. de créer dans Neo4j un **sous-graphe local** (ego-graph) composé :

   * du nœud central,
   * de ses voisins pertinents,
   * des relations pondérées `SIMILAR`.

### Exemple de requête JSON :

```json
{
  "entry": "A0A024QYR9",
  "jaccard_threshold": 0.3
}
```

### Exemple de réponse :

```json
{
  "center": {
    "entry": "A0A024QYR9",
    "name": "Phosphatidylinositol...",
    "organism": ""
  },
  "neighbors": [
    {
      "entry": "A0A1V0DNR6",
      "name": "Phosphatidylinositol...",
      "organism": "",
      "weight": 1
    }
  ],
  "summary": {
    "center_entry": "P12345",
    "num_neighbors": 12
  }
}
```

### Visualisation du graphe dans Neo4j

Dans Neo4j Browser :

```cypher
MATCH (p:Protein)-[r:SIMILAR]->(n)
RETURN p, r, n;
```

Vous verrez uniquement le **mini-graphe construit pour cette requête**.

---

# 4. **Technique Big Data : Justification & Implémentation**

## 4.1. Problème de l’approche naïve

Construire un graphe complet nécessiterait :

* de comparer **toutes les paires** de protéines,
* calcul de Jaccard pour chaque paire → **O(n²)**
* stockage d’un graphe potentiellement gigantesque dans Neo4j → non scalable.

Exemple :
100 000 protéines → 5 milliards de comparaisons → impossible en mémoire / en temps raisonnable.

👉 **C’est pour cela que nous n’avons PAS construit de graphe global.**

---

## 4.2. Approche Big Data retenue

Notre approche est basée sur trois idées clés :

### **1) Index inversé en mémoire**

Au lieu de comparer toutes les protéines :

* On parse les domaines InterPro une fois,
* On construit un index :

```python
protein_domains[entry] = {"IPR0001", "IPR0002", ...}
protein_meta[entry] = {"name": "...", "organism": "..."}
domain_index[domain] = {"P12345", "A54321", ...}
```

Cet index est chargé **une seule fois** au premier appel (`@lru_cache`).

---

### **2) Recherche des voisins en O(n) ou moins**

Pour une protéine donnée `entry` :

1. On récupère ses domaines.
2. On extrait les candidats en ne prenant **que ceux qui partagent au moins un domaine** :

```python
candidates = set()
for d in target_domains:
    candidates |= domain_index[d]
```

→ Plus besoin d’examiner toutes les protéines.

3. On calcule Jaccard seulement sur ces candidats.

### Code utilisé :

```python
def compute_neighbors(entry, threshold):
    protein_domains, protein_meta, domain_index = get_indexes()

    target_domains = protein_domains[entry]

    # Candidats = toutes les protéines partageant au moins un domaine
    candidates = set()
    for d in target_domains:
        candidates |= domain_index.get(d, set())
    candidates.discard(entry)

    neighbors = []
    for cand in candidates:
        w = jaccard(target_domains, protein_domains[cand])
        if w >= threshold:
            neighbors.append({
                "entry": cand,
                "weight": w,
                "name": protein_meta[cand]["name"],
                "organism": protein_meta[cand]["organism"],
            })

    return center, sorted(neighbors, key=lambda x: x["weight"], reverse=True)
```

👉 Le temps de calcul dépend des **vrais voisins potentiels**, pas de n².

---

### **3) Sous-graphe local dans Neo4j**

Au lieu de stocker tout le graphe, on stocke uniquement le voisinage demandé.

Code utilisé :

```python
def push_ego_graph_to_neo4j(center, neighbors):
    session.run("MATCH (n:Protein) DETACH DELETE n")  # Neo4j propre

    session.run("""
        UNWIND $rows AS row
        MERGE (p:Protein {entry: row.entry})
        SET p.name = row.name, p.organism = row.organism
    """, rows=[center] + neighbors)

    session.run("""
        UNWIND $edges AS edge
        MATCH (c:Protein {entry: edge.source})
        MATCH (n:Protein {entry: edge.target})
        MERGE (c)-[r:SIMILAR]->(n)
        SET r.weight = edge.weight
    """, edges=[{"source": center["entry"], "target": n["entry"], "weight": n["weight"]} for n in neighbors])
```

Résultat :

* Neo4j ne contient jamais plus que quelques nœuds.
* La visualisation est **à la demande**, scalable, instantanée.

---

# 5. Résumé de la démarche Big Data

| Problème                                        | Solution                                        |
| ----------------------------------------------- | ----------------------------------------------- |
| Construction d’un graphe global O(n²) ingérable | Calcul local, à la demande                      |
| Trop de comparaisons                            | Index inversé sur InterPro                      |
| Trop d’arêtes                                   | Seulement les voisins pertinents                |
| Neo4j trop lourd                                | Sous-graphe local réinitialisé à chaque requête |
| Mémoire importante                              | Cache LRU + peu de stockage en Neo4j            |

👉 Notre solution respecte parfaitement l’attendu du sujet :
**idée + implémentation concrète d’une solution scalable**, capable de traiter un dataset massif sans explosion de complexité.

---

# 6. Conclusion

La Task 2 implémente une **approche big data réelle** :

* index en mémoire,
* calcul du voisinage linéaire,
* sous-graphe local dans Neo4j,
* API simple pour la visualisation.

Cette approche est **beaucoup plus scalable** que la construction brute d'un graphe complet, et parfaitement adaptée à une démo de projet NoSQL.

---

Si tu veux, je peux maintenant rédiger :

* un **Task3.md**,
* un **README global**,
* ou préparer les phrases pour ta **soutenance** (explications courtes et efficaces).
