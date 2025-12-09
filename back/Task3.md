# **Task3 – Requêtes sur les bases de protéines (MongoDB + Neo4j)**

Objectif : permettre aux utilisateurs d’interroger les deux bases :
1. **Document store (MongoDB)** : recherche par identifiant / nom / description.
2. **Graphe (Neo4j)** : recherche d’une protéine, voisins et voisins de voisins.
3. **Statistiques** : volume, proteines labellisees/non-labellisees, isolement.
4. **Visualisation** : ego-graphe autour d’une proteine.

---

# Prerequis

- **Task 1** deja executee (MongoDB peuplee via `/task1/load`).
- **Task 2** deja en place (Neo4j installe et accessible sur http://localhost:7474).
- MongoDB et Neo4j doivent etre demarres.

---

# Lancer le backend FastAPI

Dans `~/nosql/NoSQL_Project/back` :

```bash
uvicorn main:app  # ou uvicorn main:app --reload si votre limite inotify est augmentee
```

Attendu : `Application startup complete` sur http://127.0.0.1:8000  
Si vous voyez un message "OS file watch limit reached", relancez simplement sans `--reload`.

Docs interactives : http://127.0.0.1:8000/docs

---

# Lancer le frontend

Dans un autre terminal, depuis la racine du projet :

```bash
cd front
python3 -m http.server 8080
```

Ouvrir : http://localhost:8080  
Ce front consomme les endpoints ci-dessous.

---

# Endpoints utilises pour Task 3

## 1) Recherche MongoDB (document store)

- **Endpoint** : `POST /proteins/search`
- **Payload exemple** :
```json
{
  "entry": "",
  "protein_name": "kinase",
  "entry_name": "",
  "organism": "",
  "sequence": "",
  "ec_number": "",
  "interpro": ""
}
```
- **Usage rapide (curl)** :
```bash
curl -X POST http://127.0.0.1:8000/proteins/search \
  -H "Content-Type: application/json" \
  -d '{"protein_name":"kinase"}'
```

## 2) Graphe Neo4j (ego-graphe)

- **Endpoint** : `POST /task2/ego_graph`
- **Payload exemple** :
```json
{
  "entry": "A0A024QYR9",
  "jaccard_threshold": 0.3
}
```
- **Usage rapide (curl)** :
```bash
curl -X POST http://127.0.0.1:8000/task2/ego_graph \
  -H "Content-Type: application/json" \
  -d '{"entry":"A0A024QYR9","jaccard_threshold":0.3}'
```
Retourne le noeud central, ses voisins et cree l’ego-graphe dans Neo4j.

## 3) Statistiques globales

- **Endpoint** : `GET /stats`
- **Usage** :
```bash
curl http://127.0.0.1:8000/stats
```
Retourne total de proteines, avec/sans domaine InterPro, avec/sans EC number.

---

# Parcours utilisateur (front)

1. **Import** : si besoin, charger `data_sample.tsv` ou `data.tsv` (bouton ou saisie) -> alimente Mongo via `/task1/load` ou `/task1/load/<fichier>`.
2. **Informations** : formulaire de recherche -> appelle `/proteins/search`.
3. **Statistiques** : bouton de rafraichissement -> appelle `/stats`.
4. **Visualisation** : saisie d’un `entry` + seuil Jaccard -> appelle `/task2/ego_graph`, puis affiche l’ego-graphe (Neo4j stocke le sous-graphe).

---

# Verification rapide

- Backend actif : `curl http://127.0.0.1:8000` -> `{"message":"API running"}`.
- Import OK : `curl -X POST http://127.0.0.1:8000/task1/load` -> JSON avec `inserted`.
- Recherche OK : `curl -X POST .../proteins/search -d '{"entry":"A0A024QYR9"}'`.
- Graphe OK : `curl -X POST .../task2/ego_graph -d '{"entry":"A0A024QYR9","jaccard_threshold":0.3}'` et verifiez dans Neo4j Browser.

---

# En cas de souci

- **Limite inotify** lors du `--reload` : lancer `uvicorn main:app` sans reload, ou augmenter la limite (sysctl).
- **TSV introuvable** : verifier que le fichier est dans `~/nosql/NoSQL_Project/data/` et que le nom passe a `/task1/load/<fichier>` est correct.
- **Neo4j** : assurez-vous qu’il tourne et que les creds sont corrects si vous avez modifie la config par defaut.