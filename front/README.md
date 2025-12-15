# NoSQL Proteins Explorer - Frontend

Application web en **HTML + CSS + JavaScript vanilla** pour explorer la base de données de protéines.

## Fonctionnalités

L'application propose 4 pages principales :

1. **Import** - Chargement de données TSV dans MongoDB
2. **Informations** - Recherche multi-critères de protéines
3. **Statistiques** - Vue d'ensemble des données
4. **Visualisation** - Ego-graph des protéines voisines (Neo4j)

---

## Prérequis

Avant de lancer le frontend, assurez-vous que :

### 1. MongoDB est démarré
```bash
# Vérifier que MongoDB tourne
mongosh --eval "db.version()"
```

### 2. Neo4j est démarré
```bash
# Vérifier Neo4j (selon votre installation)
# Par exemple : http://localhost:7474/browser/
```

### 3. Le backend FastAPI est lancé
```bash
cd back
uvicorn main:app --reload
```

L'API devrait être accessible sur : `http://127.0.0.1:8000`

Vous pouvez tester avec :
```bash
curl http://127.0.0.1:8000
```

Vous devriez recevoir : `{"message": "API running"}`

---

## Lancement du Frontend

### Méthode 1 : Serveur HTTP Python

```bash
cd front
python3 -m http.server 8080
```

Puis ouvrez votre navigateur sur : **http://localhost:8080**

### Méthode 2 : Serveur HTTP Node.js

Si vous avez Node.js installé :

```bash
cd front
npx http-server -p 8080
```

Puis ouvrez : **http://localhost:8080**

### Méthode 3 : Ouverture directe (peut avoir des limitations CORS)

Double-cliquez directement sur `index.html` dans votre explorateur de fichiers.

**Note :** Certaines fonctionnalités peuvent ne pas marcher avec cette méthode en raison des restrictions de sécurité des navigateurs. Préférez un serveur HTTP.

---

## Structure des fichiers

```
front/
├── index.html      # Structure HTML de l'application
├── styles.css      # Styles CSS
├── app.js          # Logique JavaScript
└── README.md       # Ce fichier
```

---

## Configuration

Par défaut, l'application se connecte au backend sur : `http://127.0.0.1:8000`

Si votre backend tourne sur un autre port ou une autre adresse, modifiez la constante dans [app.js](app.js:4) :

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```

---

## Guide d'utilisation

### Page Import

1. **Charger le fichier par défaut**
   - Cliquez sur "Charger le fichier par défaut"
   - Charge automatiquement `data/data_sample.tsv` dans MongoDB

2. **Charger un fichier spécifique**
   - Entrez le nom du fichier (ex: `data_sample.tsv`)
   - Le fichier doit exister dans le dossier `data/` du projet

3. **Prévisualiser les données**
   - Cliquez sur "Afficher les données"
   - Affiche toutes les protéines chargées

### Page Informations (Recherche)

1. Remplissez un ou plusieurs champs :
   - **Entry** : Identifiant UniProt (ex: `A0A024QYR9`)
   - **Protein name** : Nom de la protéine (ex: `kinase`)
   - **Entry name** : Nom d'entrée (ex: `PKD1_MOUSE`)
   - **Organism** : Organisme (ex: `Mus musculus`)
   - **Sequence** : Fragment de séquence (ex: `MERGG`)
   - **EC number** : Numéro EC (ex: `2.7.11.1`)
   - **InterPro** : Domaine InterPro (ex: `IPR000719`)

2. Cliquez sur **Rechercher**

3. Les résultats s'affichent dans un tableau

**Note :** La recherche est insensible à la casse et utilise des expressions régulières (contient).

### Page Statistiques

1. Cliquez sur **Rafraîchir les statistiques**

2. L'application affiche :
   - Total de protéines
   - Protéines avec/sans domaine (InterPro)
   - Protéines avec/sans fonction (EC number)

### Page Visualisation

1. Entrez un **Entry** de protéine (ex: `A0A024QYR9`)

2. Ajustez le **seuil de Jaccard** (entre 0 et 1, par défaut 0.3)
   - Plus le seuil est élevé, plus les voisins doivent être similaires

3. Cliquez sur **Afficher le graphe**

4. L'application affiche :
   - Informations sur la protéine centrale
   - Liste des voisins avec leur score de similarité Jaccard

---

## Résolution de problèmes

### Erreur : "Failed to fetch"

**Cause :** Le backend n'est pas accessible.

**Solution :**
- Vérifiez que le backend tourne : `curl http://127.0.0.1:8000`
- Vérifiez l'URL dans `app.js`
- Vérifiez les CORS (normalement déjà configuré dans le backend)

### Erreur : "Endpoint /stats not found"

**Cause :** L'endpoint `/stats` n'existe pas encore dans votre backend.

**Solution :**
L'endpoint a été ajouté dans [back/routers/proteins.py](../back/routers/proteins.py:63-93). Assurez-vous d'avoir redémarré le backend :

```bash
cd back
uvicorn main:app --reload
```

### Aucune donnée dans Import

**Cause :** MongoDB n'est pas démarré ou la collection est vide.

**Solution :**
1. Démarrez MongoDB
2. Importez des données via la page Import

### Erreur 404 sur le fichier TSV

**Cause :** Le fichier n'existe pas dans `data/`

**Solution :**
- Vérifiez que le fichier existe : `ls data/`
- Utilisez le nom exact (sensible à la casse)

---

## Technologies utilisées

- **HTML5** - Structure
- **CSS3** - Styles (design responsive)
- **JavaScript ES6+** - Logique (Fetch API, async/await)
- **FastAPI** - Backend API
- **MongoDB** - Base de données documentaire
- **Neo4j** - Base de données graphe

---

## Notes techniques

### API Endpoints utilisés

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Test de santé de l'API |
| POST | `/task1/load` | Charge le fichier par défaut |
| POST | `/task1/load/{file_name}` | Charge un fichier spécifique |
| POST | `/proteins/search` | Recherche de protéines |
| GET | `/stats` | Statistiques globales |
| POST | `/task2/ego_graph` | Graphe de voisinage |

### Format des données

Les protéines dans MongoDB ont les champs suivants :
- `Entry` : Identifiant UniProt
- `Protein names` : Nom de la protéine
- `Entry name` : Nom d'entrée
- `Organism` : Organisme
- `Sequence` : Séquence protéique
- `EC number` : Numéro de classification enzymatique
- `InterPro` : Domaines protéiques

---

## Développement

### Modification du style

Éditez [styles.css](styles.css) pour personnaliser l'apparence.

### Modification de la logique

Éditez [app.js](app.js) pour modifier le comportement.

### Ajout de nouvelles fonctionnalités

1. Ajoutez une nouvelle section dans `index.html`
2. Créez un bouton de navigation
3. Implémentez la logique dans `app.js`

---

## Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation MongoDB](https://www.mongodb.com/docs/)
- [Documentation Neo4j](https://neo4j.com/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

## Licence

Projet réalisé dans le cadre du cours NoSQL - RTT - 2022-2025

---

## Checklist de démarrage

- [ ] MongoDB est démarré
- [ ] Neo4j est démarré
- [ ] Backend FastAPI lancé (`uvicorn main:app --reload`)
- [ ] Serveur HTTP pour le frontend lancé
- [ ] Navigation vers http://localhost:8080
- [ ] Import de données effectué
- [ ] Recherche testée
- [ ] Statistiques affichées
- [ ] Visualisation testée

