# Assistant IA pour Dirigeants

---

# 1. Présentation du projet

Assistant IA pour Dirigeants est une application web conversationnelle destinée à accompagner les dirigeants d'entreprise dans leurs réflexions stratégiques, opérationnelles et décisionnelles.

L'application permet d'interagir en langage naturel avec un modèle d'intelligence artificielle via une interface moderne de type assistant SaaS.

Le projet repose sur l'intégration d'un modèle de langage via Hugging Face Router API et est conçu pour évoluer vers une architecture RAG (Retrieval-Augmented Generation) permettant l’exploitation de documents internes d’entreprise.

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

> MVP fonctionnel avec interface conversationnelle et intégration IA opérationnelle.

---

## ✔ Backend

Le backend assure :

* Création et gestion des routes API Flask
* Intégration avec l’API Hugging Face Router
* Gestion des requêtes utilisateur
* Génération de réponses IA contextualisées
* Gestion des erreurs serveur
* Structuration du prompt système
* Architecture backend modulaire

---

## ✔ Frontend

Le frontend dispose des fonctionnalités suivantes :

* Interface conversationnelle type ChatGPT
* Design SaaS moderne (dark mode)
* Affichage dynamique des messages
* Support Markdown
* Typing effect
* Auto-scroll
* Auto-resize du textarea
* Bouton copier sur les réponses IA
* Gestion des conversations
* Sauvegarde locale (localStorage)
* Recherche, renommage et suppression des conversations
* Sidebar interactive
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

* API REST `/chat`
* Communication avec le modèle IA
* Traitement des requêtes utilisateur
* Retour des réponses JSON
* Gestion des erreurs

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
* Affichage des messages
* Communication avec le backend
* Persistance locale

---

# 5. Modèle IA utilisé

### Fournisseur

Hugging Face Router API

### Modèle

```plaintext id="model_fix"
meta-llama/Llama-3.1-8B-Instruct
```

Le modèle génère des réponses adaptées à un contexte professionnel et décisionnel.

---

# 6. Fonctionnement global

1. L’utilisateur envoie un message via l’interface
2. Flask reçoit la requête `/chat`
3. Le backend transmet la requête au modèle IA via Hugging Face
4. Le modèle génère une réponse structurée
5. La réponse est renvoyée et affichée dans l’interface

---

# 7. Gestion des conversations

* Création automatique de conversations
* Sauvegarde locale via localStorage
* Historique persistant
* Renommage et suppression
* Navigation multi-conversations

---

# 8. Sécurité

* Variables d’environnement pour les clés API
* Aucune clé exposée dans le code source
* Séparation frontend / backend
* Fichier `.env` ignoré

---

# 9. Structure du projet

```plaintext id="structure_final"
assistant-ia-dirigeants/

├── app.py
├── config.py
├── requirements.txt
├── .env.example

├── modules/
│   ├── llm/
│   ├── services/
│   └── utils/

├── templates/
│   └── index.html

├── static/
│   ├── css/
│   └── js/

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

## Frontend

* Interface type assistant SaaS
* Affichage dynamique des messages
* Support Markdown
* Gestion multi-conversations
* Sauvegarde locale automatique
* UX interactive moderne

---

# 11. Prochaines étapes

## Backend

* Amélioration du prompt système
* Mémoire conversationnelle serveur
* Endpoint `/upload`
* Indexation documentaire
* Intégration RAG

## Frontend

* Responsive mobile
* Notifications utilisateur
* Optimisation UX/UI
* Intégration RAG interface

---

# 12. Installation et lancement

## 1. Cloner le projet

```bash
git clone https://github.com/Tresor-Bilal-Projects/assistant-ia-dirigeants.git
cd assistant-ia-dirigeants
```

## 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 3. Configurer l’environnement

```bash
cp .env.example .env
```

Ajouter la clé API Hugging Face dans `.env`

## 4. Lancer l’application

```bash
python app.py
```

---

# 13. Équipe et répartition des tâches

Le projet a été réalisé dans un cadre académique collaboratif.

| Membre        | Rôle principal                                                                                                               |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Nathan        | Backend, API Flask, intégration IA, logique métier, architecture serveur, préparation RAG                                    |
| Trésor        | Backend (API Flask), intégration IA, Frontend, UX/UI, architecture JavaScript, gestion des conversations, persistance locale |
| Pierre-Thyrel | Tests, validation fonctionnelle, support technique                                                                           |
| Lina          | Documentation, organisation projet, suivi des livrables                                                                      |

---

# 14. Conclusion

Le projet constitue un MVP fonctionnel d’assistant IA destiné aux dirigeants, combinant une interface moderne et un modèle de langage capable d’analyse et de recommandation.

Il représente une base solide pour évoluer vers une architecture avancée de type RAG et une solution SaaS complète orientée entreprise.
