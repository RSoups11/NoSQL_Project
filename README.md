# NoSQL_Project

## Task 1

La tâche 1 consiste tout d'abord à stocker les protéines dans une base de données document avce MongoDB. Il faut être capable de peupler cette base données uniquement avec une seule requête.

## Task 2
Ici, il faut créer un graphe de protéines à l'aide d'une base de donnée orientée graphe tel que Neo4j. Pour ce faire, il faut notamment s'intérésser au domaine des protéines. Un noeud du réseau doit représenter une protéine et un lien entre 2 noeuds doit mettre en avant le dégré de similarité de domaine entre les deux protéines. Un noeud doit être identifié par un ensemble de Label (les annotations à propager), un ensemble de voisins et pour chaque voisons associer un poids. 

## Task 3
C'est ici que l'on utilise nos base de données avec des requêtes. 

**Document** : A partir de notre base document, il faudra pouvoir rechercher une protéines en particulier à partir de son identifiant et/ou nom et/ou description. 

**Graphe** : A partir de notre base graphe, il faudra pouvoir rechercher une protéines en particulier à partir de son identifiant et/ou nom et/ou description. A partir de cette rechercher l'utilisateur devra avoir une visualisation de cette protéines avec ces voisins et voisins de voisins (2 couche de voisinnage peut être ?).

## Taks 4 
Cette tâche est la tâche finale a envisager si possible. Le but est de faire une tache de classification/annotation sur les protéines. Pas toutes les protéines possède une annotation dans la colonne EC (Enzyme commission number) ou la colonne GO (Gene ontology). C'est donc une tache de classification multi-label. Il est possible de voir cette tache comme un problème de recommandation ou on doit recommander le bon lien pour connecter un noeud sans annotation à partir d'un noeud annoté comme exemple.

## Notation
Pour la notation, la moyenne (10/20) est assuré par avec la création de nos 2 databases qui stock nos données et nous les mets à disposition via des requêtes. 

- L'interface grahique avec un GUI intuitif rajoute 3 points.
- Une bonne visualisation des voisins rajoute 2 points.
- L'annotation de protéines sans label (label propagation) rajoute 3 points.
- Des statistiques variées rajoute 2 point.

L'évaluation consiste en 20 minutes de présentation tel que : 

- 5 minutes pour les choix techniques
- 15 minutes de demonstration live

