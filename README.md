# Assistant IA pour Dirigeants

---

# 1. Présentation du projet

Assistant IA pour Dirigeants est une application web conversationnelle destinée à accompagner les dirigeants d'entreprise dans leurs réflexions stratégiques, opérationnelles et décisionnelles.

L'application permet d'interagir en langage naturel avec un modèle d'intelligence artificielle via une interface moderne inspirée des assistants conversationnels de nouvelle génération.

Le projet repose actuellement sur l'intégration d'un modèle de langage via Hugging Face Router API et est conçu pour évoluer vers une architecture RAG (Retrieval-Augmented Generation) permettant l'exploitation de documents internes d'entreprise.

---

# 2. Objectifs du projet

L'objectif du projet est de :

* Fournir un assistant conversationnel professionnel pour les dirigeants
* Faciliter l'analyse et la prise de décision
* Offrir une expérience utilisateur moderne de type SaaS
* Préparer l'intégration de bases documentaires internes
* Développer progressivement une solution IA adaptée aux besoins des entreprises

---

# 3. État actuel du projet

Le projet est actuellement au stade :

> MVP fonctionnel avec gestion complète des conversations et intégration IA opérationnelle.

---

## ✔ Backend

Le backend est fonctionnel et assure :

* Gestion des requêtes utilisateur
* Communication avec le modèle IA
* Génération des réponses
* Gestion des erreurs serveur
* Architecture Flask modulaire
* Configuration sécurisée via variables d'environnement
* Préparation de l'intégration RAG

---

## ✔ Frontend

Le frontend dispose actuellement des fonctionnalités suivantes :

* Interface conversationnelle type ChatGPT
* Design SaaS moderne (dark mode)
* Affichage dynamique des messages
* Support Markdown
* Typing effect
* Auto-scroll
* Auto-resize du textarea
* Bouton copier sur les réponses IA
* Gestion complète des conversations
* Sauvegarde locale des conversations
* Recherche de conversations
* Renommage des conversations
* Suppression des conversations
* Sidebar conversationnelle
* Architecture JavaScript modulaire

---

# 4. Architecture du projet

## Backend

### Technologies

* Python
* Flask
* Hugging Face Router API
* python-dotenv

### Responsabilités

* Gestion des routes API
* Communication avec le modèle IA
* Traitement des requêtes utilisateur
* Retour des réponses JSON
* Gestion des erreurs
* Préparation de l'intégration documentaire

### Endpoint principal

```plaintext
POST /chat
```

---

## Frontend

### Technologies

* HTML5
* CSS3
* JavaScript ES6 Modules
* Marked.js

### Responsabilités

* Interface utilisateur
* Gestion des conversations
* Affichage dynamique des messages
* Communication avec le backend
* Gestion du stockage local
* Gestion des interactions utilisateur

---

# 5. Architecture Frontend

Le frontend est organisé en modules indépendants :

```plaintext
static/js/

├── chat.js
├── api.js
├── ui.js
├── upload.js
├── conversationManager.js
├── storage.js
```

### chat.js

Gestion principale du chat :

* envoi des messages
* réception des réponses
* gestion des événements utilisateur

### api.js

Communication avec le backend :

* appels API
* upload de fichiers
* gestion des réponses serveur

### ui.js

Gestion de l'interface :

* affichage des messages
* rendu Markdown
* animations
* typing effect

### upload.js

Gestion des fichiers :

* sélection
* prévisualisation
* suppression

### storage.js

Persistance locale :

* création des conversations
* sauvegarde dans localStorage
* récupération des conversations

### conversationManager.js

Gestion de la sidebar :

* création de conversations
* recherche
* renommage
* suppression
* navigation entre conversations

---

# 6. Modèle IA utilisé

### Fournisseur

Hugging Face Router API

### Modèle actuel

```plaintext
meta-llama/Llama-3.1-8B-Instruct
```

Le modèle est utilisé pour générer des réponses conversationnelles adaptées à un contexte professionnel.

---

# 7. Gestion des conversations

Le système de gestion des conversations permet :

* Création automatique d'un nouveau chat
* Sauvegarde locale via localStorage
* Conservation de l'historique après rechargement
* Recherche de conversations
* Renommage des conversations
* Suppression des conversations
* Navigation entre plusieurs conversations

---

# 8. Sécurité

Le projet applique actuellement les mesures suivantes :

* Utilisation de variables d'environnement
* Clés API non exposées
* Fichier `.env` ignoré par Git
* Fichier `.env.example` fourni
* Séparation frontend / backend

---

# 9. Structure du projet

```plaintext
assistant-ia-dirigeants/

├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore

├── data/
├── vectorstore/

├── modules/
│   ├── llm/
│   ├── services/
│   └── utils/

├── templates/
│   ├── base.html
│   └── index.html

├── static/
│   ├── css/
│   │   └── chat.css
│   │
│   └── js/
│       ├── api.js
│       ├── chat.js
│       ├── ui.js
│       ├── upload.js
│       ├── storage.js
│       └── conversationManager.js

├── tests/

└── README.md
```

---

# 10. Fonctionnalités principales

## Backend

* API conversationnelle
* Intégration IA via Hugging Face
* Génération de réponses contextuelles
* Gestion des erreurs
* Architecture modulaire
* Préparation de l'intégration RAG

---

## Frontend

* Interface type ChatGPT
* Affichage dynamique des messages
* Support Markdown
* Typing effect
* Auto-scroll
* Auto-resize du textarea
* Bouton copier
* Gestion multi-conversations
* Recherche de conversations
* Renommage
* Suppression
* Sauvegarde locale automatique
* Sidebar interactive

---

# 11. Améliorations récentes

Travaux réalisés récemment :

* Refonte complète de l'interface utilisateur
* Modernisation du design SaaS
* Stabilisation du rendu des messages
* Amélioration du support Markdown
* Optimisation du typing effect
* Amélioration du textarea auto-resize
* Ajout du bouton copier
* Mise en place du système de conversations
* Création de la sidebar conversationnelle
* Ajout de la recherche de conversations
* Ajout du renommage des conversations
* Ajout de la suppression des conversations
* Intégration du localStorage
* Modularisation avancée du frontend

---

# 12. Prochaines étapes

## Backend

* Amélioration du prompt système
* Mémoire conversationnelle serveur
* Endpoint `/upload`
* Extraction PDF
* Extraction TXT
* Indexation documentaire
* Vectorisation des documents
* Intégration RAG
* Gestion avancée du contexte utilisateur

---

## Frontend

* Amélioration responsive mobile
* Prévisualisation avancée des fichiers
* Notifications utilisateur
* Optimisation des performances
* Amélioration des animations UI
* Paramètres utilisateur
* Personnalisation de l'interface
* Intégration de la future couche RAG

---

# 13. Installation et lancement

## 1. Cloner le projet

```bash
git clone https://github.com/Tresor-Bilal-Projects/assistant-ia-dirigeants.git

cd assistant-ia-dirigeants
```

---

## 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 4. Configurer l'environnement

```bash
cp .env.example .env
```

Ajouter ensuite votre clé API dans le fichier `.env`.

---

## 5. Lancer l'application

```bash
python app.py
```

---

# 14. Répartition du travail

| Membre        | Rôle principal                                                                                                             |
| ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Nathan        | Backend, API Flask, intégration IA, logique métier, architecture serveur, préparation RAG                                  |
| Trésor        | Frontend, UX/UI, architecture JavaScript, gestion des conversations, persistance locale, intégration interface utilisateur |
| Pierre-Thyrel | Tests, validation fonctionnelle, support technique                                                                         |
| Lina          | Documentation, organisation projet, suivi des livrables                                                                    |

---

# 15. Conclusion

Le projet est aujourd'hui un MVP conversationnel fonctionnel intégrant un modèle d'intelligence artificielle, une interface moderne de type SaaS et un système complet de gestion des conversations.

Les prochaines évolutions visent principalement l'intégration d'une architecture RAG, l'exploitation de documents internes et l'amélioration continue de l'expérience utilisateur afin de proposer un assistant IA adapté aux besoins des dirigeants d'entreprise.
