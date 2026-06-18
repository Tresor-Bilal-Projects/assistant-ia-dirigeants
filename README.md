# Assistant IA pour Dirigeants

---

# 1. Présentation du projet

Assistant IA pour Dirigeants est une application web conversationnelle destinée à accompagner les dirigeants d'entreprise dans leurs réflexions stratégiques, opérationnelles et décisionnelles.

L'application permet d'interagir en langage naturel avec un modèle d'intelligence artificielle via une interface moderne de type assistant SaaS.

Le projet repose sur l'intégration d'un modèle de langage via Hugging Face Router API, couplée à une architecture **RAG** (Retrieval-Augmented Generation) fonctionnelle : chaque utilisateur importe ses propres documents internes (PDF, TXT, DOCX) et obtient des réponses contextualisées et sourcées, isolées de celles des autres utilisateurs.

---

# 2. Objectifs du projet

L'objectif du projet est de :

* Fournir un assistant conversationnel professionnel pour les dirigeants
* Faciliter l'analyse et la prise de décision à partir des documents internes de l'entreprise
* Offrir une expérience utilisateur moderne de type SaaS
* Permettre à chaque utilisateur de disposer d'un espace personnel isolé : ses documents, ses conversations, son historique
* Garantir qu'aucun utilisateur ne puisse accéder aux données d'un autre
* Développer une solution IA fiable, sourcée et adaptée aux besoins des entreprises

---

# 3. État actuel du projet

Le projet est actuellement au stade :

> Authentification, isolation multi-utilisateur et pipeline RAG fonctionnels, validés par des tests manuels en conditions réelles. L'interface de gestion documentaire avancée et le durcissement sécurité pour une mise en production restent à construire.

---

## ✔ Backend

Le backend assure :

* Authentification complète (inscription, connexion, déconnexion) via Flask-Login
* Isolation stricte des données par utilisateur, vérifiée côté serveur sur chaque endpoint
* Pipeline RAG complet : extraction, découpage, indexation vectorielle, recherche, génération
* Création et gestion des routes API Flask (`/chat`, `/upload`, `/api/conversations`, `/api/documents`, `/api/account`, `/api/rag/status`)
* Intégration avec l'API Hugging Face Router
* Gestion des requêtes utilisateur et génération de réponses IA contextualisées et sourcées
* Gestion des erreurs serveur
* Structuration du prompt système, avec adaptation selon la présence ou non de contexte documentaire
* Architecture backend modulaire (blueprints, services séparés)

---

## ✔ Frontend

Le frontend dispose des fonctionnalités suivantes :

* Interface conversationnelle type ChatGPT
* Design SaaS moderne (dark mode)
* Pages de connexion et d'inscription cohérentes avec le branding de l'application
* Affichage dynamique des messages
* Support Markdown
* Typing effect
* Auto-scroll
* Auto-resize du textarea
* Bouton copier sur les réponses IA
* Upload de documents intégré au chat, avec retour visuel sur l'indexation
* Affichage des sources documentaires sous chaque réponse sourcée
* Gestion des conversations (création, recherche, renommage, suppression)
* Historique des conversations persistant en base, propre à chaque utilisateur
* Sidebar interactive
* Architecture JavaScript modulaire

---

# 4. Architecture du projet

## Backend

### Technologies

* Python
* Flask (organisé en blueprints)
* Flask-SQLAlchemy (modèles relationnels)
* Flask-Login (authentification, sessions)
* Flask-WTF (formulaires, protection CSRF)
* ChromaDB (base vectorielle, persistante, isolée par utilisateur)
* pypdf / python-docx (extraction de documents)
* Hugging Face Router API (inférence du modèle de langage)
* python-dotenv

### Responsabilités

* API REST `/chat`, `/upload`, et API privée `/api/*` (conversations, documents, compte)
* Authentification et gestion de session
* Pipeline RAG : extraction → nettoyage → découpage → indexation → recherche → génération
* Isolation des données par `user_id` à chaque étape (fichiers, base vectorielle, base relationnelle)
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

* Interface utilisateur (chat, authentification)
* Gestion des conversations
* Affichage des messages et des sources documentaires
* Upload de fichiers
* Communication avec le backend (requêtes CSRF-aware)
* Persistance des données côté serveur (plus de dépendance à `localStorage` pour l'historique)

---

# 5. Modèle IA utilisé

### Fournisseur

Hugging Face Router API

### Modèle

```plaintext id="model_fix"
Qwen/Qwen2.5-7B-Instruct
```

Configurable via la variable d'environnement `HF_CHAT_MODEL`. Le modèle `meta-llama/Llama-3.1-8B-Instruct` reste une alternative possible mais n'est pas celui actuellement déployé par défaut (accès "gated" sur Hugging Face, non débloqué pour ce projet).

Le modèle génère des réponses adaptées à un contexte professionnel et décisionnel, et s'appuie sur les documents internes de l'utilisateur lorsqu'un contexte RAG est disponible.

---

# 6. Fonctionnement global

## Sans document (conversation générale)

1. L'utilisateur envoie un message via l'interface
2. Flask reçoit la requête `/chat`
3. Le système détecte qu'aucun contexte documentaire n'est pertinent (salutation, question générale)
4. Le backend transmet directement la requête au modèle IA via Hugging Face
5. La réponse est renvoyée et affichée dans l'interface

## Avec documents (RAG)

1. L'utilisateur a préalablement importé un ou plusieurs documents, indexés dans sa collection vectorielle personnelle
2. L'utilisateur envoie une question
3. Le système classe la question (précise, synthèse globale, ou suivi conversationnel) et choisit la stratégie de récupération adaptée (voir §7)
4. Les passages pertinents sont récupérés dans la collection ChromaDB de l'utilisateur uniquement
5. Un prompt enrichi (question + extraits documentaires) est envoyé au modèle IA
6. Le modèle génère une réponse synthétisée à partir des extraits fournis
7. La réponse, accompagnée des sources utilisées, est renvoyée et affichée dans l'interface

---

# 7. Fonctionnement du RAG en détail

Chaque question est d'abord classée en une des quatre catégories suivantes, avant toute recherche documentaire :

| Type de question | Exemple | Stratégie |
|---|---|---|
| **Non-documentaire** | "Bonjour", "qui es-tu ?" | Aucune recherche — réponse directe du modèle |
| **Précise** | "Quel est le prix de l'ErgoZen V3 ?" | Recherche vectorielle ciblée (Top-K) + récupération du chunk suivant (évite qu'un nom et son prix soient scindés entre deux chunks adjacents) |
| **Synthèse globale** | "Liste tous les produits", "résume le document" | Récupération de l'intégralité du document actif, dans l'ordre de lecture |
| **Suivi conversationnel** | "Et les prix ?" (après "quels sont les produits ?") | Si un document est actif : même stratégie que la synthèse globale. Sinon : recherche ciblée avec seuil assoupli |

Chaque stratégie a son propre seuil de distance vectorielle, calibré empiriquement (voir `config.py`). Le prompt système interdit explicitement au modèle de demander des clarifications lorsqu'un contexte documentaire est fourni : il doit synthétiser directement ce qui est disponible et signaler ce qui est absent plutôt que de l'inventer.

L'extraction de texte gère aussi un cas particulier : certains PDF générés par des outils de design (Canva, InDesign) extraient chaque lettre séparément à cause du kerning. Un nettoyage conditionnel détecte et corrige automatiquement ce problème sans affecter les documents extraits normalement.

---

# 8. Gestion des conversations

* Création automatique de conversations
* Historique persistant en base de données (SQLite), propre à chaque utilisateur
* Renommage et suppression
* Navigation multi-conversations
* Suppression en cascade : effacer une conversation efface ses messages associés

---

# 9. Isolation multi-utilisateur

* Une collection ChromaDB dédiée par utilisateur (`user_<id>`) — isolation structurelle, pas seulement un filtre applicatif
* Fichiers uploadés stockés par utilisateur (`data/uploads/<user_id>/<nom_interne_aléatoire>`)
* Conversations, messages et documents rattachés en base à un `user_id`, avec vérification d'appartenance sur chaque endpoint
* Toute tentative d'accès à une ressource d'un autre utilisateur renvoie `404`, sans révéler son existence
* Suppression en cascade (compte, conversation, document → tout le contenu associé, y compris les chunks vectoriels et les fichiers physiques)

---

# 10. Sécurité

* Mots de passe hachés (Werkzeug), jamais stockés en clair
* Variables d'environnement pour les clés API et secrets
* Aucune clé exposée dans le code source
* Séparation frontend / backend
* Fichier `.env` ignoré par Git
* Sessions sécurisées (cookies `HttpOnly`, `SameSite=Lax`)
* Protection CSRF sur les formulaires d'authentification
* Isolation des données vérifiée côté serveur, jamais côté client uniquement
* Validation du format et de la taille des fichiers uploadés

### À compléter avant une mise en production réelle

* Rate limiting (brute-force sur login, abus d'upload/chat)
* Chiffrement au repos des documents sensibles
* Journalisation des accès
* Défense renforcée contre l'injection de prompt
* En-têtes de sécurité (CSP), cookies `Secure` (nécessite HTTPS)

Cadre de référence : RGPD (UE 2016/679), recommandations CNIL, OWASP Top 10, OWASP LLM Top 10.

---

# 11. Structure du projet

```plaintext id="structure_final"
assistant-ia-dirigeants/

├── app.py                          # point d'entrée Flask, routes /, /chat, /upload
├── api_routes.py                   # API privée : conversations, documents, compte
├── auth.py                         # blueprint authentification
├── config.py
├── extensions.py                   # instances Flask-SQLAlchemy / Login / WTF
├── forms.py                        # formulaires WTForms (login, register)
├── models.py                       # modèles SQLAlchemy (User, Document, Conversation, Message)
├── requirements.txt
├── .env.example

├── modules/
│   ├── llm/
│   │   ├── hf_client.py
│   │   └── system_prompt.py
│   ├── services/
│   │   ├── document_parser.py      # extraction PDF/TXT/DOCX + nettoyage kerning
│   │   ├── ingestion.py            # pipeline extraction → chunking → indexation
│   │   ├── rag.py                  # détection d'intention + construction du contexte
│   │   ├── user_files.py           # stockage des fichiers isolé par utilisateur
│   │   └── vectorstore.py          # accès ChromaDB isolé par utilisateur
│   └── utils/
│       └── chunking.py

├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html

├── static/
│   ├── css/
│   └── js/

└── README.md
```

---

# 12. Fonctionnalités principales

## Backend

* Authentification (inscription, connexion, déconnexion)
* Isolation multi-utilisateur (fichiers, base vectorielle, base relationnelle)
* API conversationnelle
* Pipeline RAG complet (extraction, chunking, indexation, recherche adaptative, génération)
* Intégration IA via Hugging Face
* Génération de réponses contextuelles et sourcées
* Gestion des erreurs
* Architecture modulaire

## Frontend

* Pages de connexion et d'inscription
* Interface type assistant SaaS
* Affichage dynamique des messages et des sources
* Upload de documents intégré au chat
* Support Markdown
* Gestion multi-conversations
* Historique persistant côté serveur
* UX interactive moderne

---

# 13. Prochaines étapes

## Backend

* Interface de gestion documentaire dédiée (liste, statut d'indexation, document actif)
* Page Paramètres utilisateur (modification du profil, export de données)
* Rate limiting sur les endpoints sensibles
* Migrations de base versionnées (Flask-Migrate / Alembic) — actuellement `db.create_all()`
* Suite de tests automatisés formalisée (pytest)
* Déploiement production (HTTPS, WSGI, configuration durcie)

## Frontend

* Responsive mobile
* Notifications utilisateur
* Vue dédiée de gestion des documents (au-delà de l'upload via le chat)
* Optimisation UX/UI continue

---

# 14. Installation et lancement

## 1. Cloner le projet

```bash
git clone https://github.com/NosProjets-Tech/assistant-ia-dirigeants.git
cd assistant-ia-dirigeants
```

## 2. Créer l'environnement virtuel et installer les dépendances

```bash
python -m venv venv

# Windows
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Configurer l'environnement

```bash
cp .env.example .env
```

Éditez `.env` : renseignez `SECRET_KEY` (générée via la commande ci-dessous) et `HF_TOKEN` (clé API Hugging Face).

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 4. Initialiser la base de données

```bash
# Windows
$env:FLASK_APP="app"
python -m flask init-db

# macOS / Linux
export FLASK_APP=app
python -m flask init-db
```

## 5. Lancer l'application

```bash
python -m flask run --debug
```

L'application est accessible sur `http://127.0.0.1:5000`. La page d'accueil redirige vers la connexion si aucune session active n'existe.

### Réinitialiser le vector store (développement uniquement)

```bash
python -m flask reset-rag
```

Supprime uniquement l'ancienne collection globale héritée d'avant l'isolation multi-utilisateur (`company_docs`). Les collections par utilisateur (`user_<id>`) et les fichiers uploadés ne sont jamais affectés par cette commande.

---

# 15. Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | Oui | Clé Flask pour les sessions et la protection CSRF |
| `HF_TOKEN` | Oui | Token Hugging Face pour l'inférence du modèle |
| `HF_CHAT_MODEL` | Non | Modèle utilisé (défaut : `Qwen/Qwen2.5-7B-Instruct`) |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Non | Paramètres de découpage des documents (défaut : 500 / 50) |
| `TOP_K` | Non | Nombre de chunks récupérés pour une question précise (défaut : 4) |
| `MAX_UPLOAD_MB` | Non | Taille maximale d'un fichier uploadé (défaut : 10) |

Liste complète avec valeurs par défaut dans `.env.example` et `config.py`.

---

# 16. Tests réalisés

Les corrections du pipeline RAG ont été validées par une combinaison de scripts ciblés et, systématiquement, de tests manuels dans l'interface réelle — un test purement scripté s'est révélé insuffisant à deux reprises pendant le développement (un cas passait les assertions automatiques tout en produisant une réponse incorrecte à l'écran).

Couverture actuelle :

* Récupération correcte sur requêtes de synthèse, questions précises et questions de suivi
* Non-déclenchement du RAG sur salutations et questions hors-domaine
* Isolation cross-utilisateur : accès refusé sur ressource d'autrui, accès autorisé sur sa propre ressource, absence de fuite de contenu entre comptes
* Extraction robuste face à des PDF à mise en page non standard

Une suite `pytest` formalisée (unitaire + intégration) reste à écrire pour automatiser cette couverture de façon pérenne.

---

# 17. Équipe et répartition des tâches

Le projet a été réalisé dans un cadre académique collaboratif.

| Membre        | Rôle principal                                                                                                               |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Nathan        | Backend, API Flask, intégration IA, logique métier, architecture serveur, préparation RAG                                    |
| Trésor        | Backend (API Flask), intégration IA, Frontend, UX/UI, architecture JavaScript, gestion des conversations, persistance locale |
| Pierre-Thyrel | Tests, validation fonctionnelle, support technique                                                                           |
| Lina          | Documentation, organisation projet, suivi des livrables                                                                      |

Encadrement : ECE Paris / Skills4Mind — Dr. Taha Ridène, M. Vincent Ferré (Groupe Asten).

---

# 18. Conclusion

Le projet constitue une application fonctionnelle d'assistant IA destiné aux dirigeants, combinant une interface moderne, une authentification complète, une isolation stricte des données par utilisateur et un pipeline RAG opérationnel capable d'exploiter les documents internes de l'entreprise pour produire des réponses contextualisées, sourcées et vérifiables.

Il représente une base solide pour évoluer vers une interface de gestion documentaire avancée et une solution SaaS complète orientée entreprise, prête pour une mise en production après durcissement sécurité.
