# 🤖 Assistant IA pour Dirigeants

> **Projet réalisé dans le cadre d'un stage chez Skill4Mind, en partenariat avec l'ECE Paris, durant le Bachelor 2.**

**Assistant IA pour Dirigeants** est une application web conversationnelle intelligente conçue pour accompagner les dirigeants dans l'**analyse de documents d'entreprise**, la recherche d'informations et la **prise de décision**.

L'application combine des **modèles de langage (LLM)** avec une architecture **RAG (Retrieval-Augmented Generation)** afin de produire des réponses contextualisées à partir de documents internes aux formats **PDF, DOCX et TXT**.

Le projet intègre également un système d'authentification, une gestion persistante des conversations et une isolation des données entre utilisateurs.

---

# 📌 Présentation

L'objectif du projet est de développer un assistant conversationnel capable d'accompagner les dirigeants dans leurs réflexions professionnelles en exploitant leurs documents d'entreprise.

L'application fonctionne selon deux modes principaux.

### 💬 Conversation générale

Pour les questions ne nécessitant pas d'informations provenant des documents, la requête est directement transmise au modèle de langage.

```text
Utilisateur
    ↓
Interface conversationnelle
    ↓
Backend Flask
    ↓
Hugging Face Router API
    ↓
LLM
    ↓
Réponse
```

### 📚 Analyse documentaire avec RAG

Lorsqu'une question nécessite des informations présentes dans les documents de l'utilisateur, le système recherche les passages les plus pertinents avant de les transmettre au modèle.

```text
Documents PDF / DOCX / TXT
            ↓
     Extraction du texte
            ↓
         Nettoyage
            ↓
     Découpage en chunks
            ↓
       Vectorisation
            ↓
         ChromaDB
            ↓
    Recherche sémantique
            ↓
   Contexte documentaire
            ↓
    Hugging Face Router
            ↓
        LLM
            ↓
Réponse contextualisée
```

---

# 🎯 Objectifs

Le projet avait pour objectifs de :

* Développer un assistant conversationnel destiné aux dirigeants.
* Faciliter l'analyse de documents professionnels.
* Exploiter des modèles de langage pour produire des réponses en langage naturel.
* Implémenter une architecture **RAG** permettant de contextualiser les réponses.
* Permettre l'import de documents **PDF, DOCX et TXT**.
* Fournir une interface conversationnelle moderne et intuitive.
* Permettre à chaque utilisateur de disposer d'un espace personnel.
* Isoler les documents, conversations et messages entre utilisateurs.
* Intégrer un modèle de langage via **Hugging Face Router API**.
* Concevoir une architecture backend modulaire et évolutive.

---

# ✨ Fonctionnalités principales

## 🤖 Assistant conversationnel

* Interface conversationnelle de type assistant IA.
* Génération de réponses via un LLM.
* Support du Markdown.
* Affichage dynamique des messages.
* Effet de frappe sur les réponses.
* Bouton de copie des réponses.
* Auto-scroll.
* Redimensionnement automatique de la zone de saisie.

## 💬 Gestion des conversations

* Création de conversations.
* Navigation entre plusieurs conversations.
* Renommage des conversations.
* Suppression des conversations.
* Historique persistant côté serveur.
* Suppression en cascade des messages associés.

## 📄 Analyse documentaire

L'utilisateur peut importer des documents aux formats :

* `.pdf`
* `.docx`
* `.txt`

Les documents sont ensuite extraits, nettoyés, découpés et indexés afin d'être exploités par le système RAG.

## 🔎 Réponses contextualisées et sourcées

Lorsque la réponse s'appuie sur des documents, les passages pertinents sont transmis au modèle de langage et les sources utilisées sont retournées au frontend.

L'utilisateur peut ainsi identifier les documents ayant servi à générer la réponse.

---

# 🧠 Architecture RAG

Le système RAG permet au modèle de langage d'utiliser les documents de l'utilisateur comme contexte.

Le pipeline est organisé comme suit :

```text
                 ┌─────────────────┐
                 │     Document    │
                 │ PDF / DOCX / TXT│
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Extraction texte│
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Nettoyage       │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Chunking        │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Vectorisation   │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │    ChromaDB     │
                 └────────┬────────┘
                          │
                          │ Recherche
                          ↓
                 ┌─────────────────┐
                 │ Chunks pertinents│
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Contexte +      │
                 │ question        │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │      LLM        │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │ Réponse finale  │
                 └─────────────────┘
```

---

# 🔎 Stratégies de recherche

Le système adapte la récupération documentaire au type de question.

| Type de question          | Exemple                             | Stratégie                                               |
| ------------------------- | ----------------------------------- | ------------------------------------------------------- |
| **Non documentaire**      | « Bonjour, qui es-tu ? »            | Aucune recherche documentaire                           |
| **Question précise**      | « Quel est le prix du produit X ? » | Recherche vectorielle ciblée                            |
| **Synthèse globale**      | « Résume le document »              | Récupération du contenu pertinent du document           |
| **Suivi conversationnel** | « Et les prix ? »                   | Utilisation du contexte documentaire et conversationnel |

Pour les questions précises, le système effectue une recherche vectorielle Top-K et peut récupérer le chunk suivant afin de préserver le contexte lorsque des informations complémentaires sont réparties sur plusieurs fragments.

Pour les demandes de synthèse globale, le système peut récupérer le contenu du document actif dans son ordre de lecture.

Les seuils de pertinence sont configurables dans `config.py`.

---

# 📄 Traitement des documents

Le projet prend en charge l'extraction de contenu depuis :

* **PDF** via `pypdf`
* **DOCX** via `python-docx`
* **TXT**

Une étape de nettoyage permet de traiter certains documents dont l'extraction produit un texte dégradé.

Un cas particulier a notamment été pris en compte pour certains PDF générés avec des outils de conception tels que **Canva ou InDesign**, dans lesquels les caractères peuvent être extraits séparément à cause du kerning.

Le système détecte ce comportement et applique un nettoyage conditionnel afin de reconstruire correctement les mots sans modifier les documents normalement extraits.

---

# 🗄️ Stockage des données

L'application utilise deux systèmes de stockage complémentaires, chacun ayant un rôle distinct.

## MySQL — Données applicatives

**MySQL** constitue la base de données relationnelle de l'application.

Elle stocke notamment :

* les utilisateurs ;
* les documents ;
* les conversations ;
* les messages ;
* les relations entre les différentes ressources.

Le projet a initialement été développé avec **SQLite**, puis migré vers **MySQL** afin d'utiliser une solution serveur mieux adaptée à une application web multi-utilisateur et à un éventuel déploiement.

L'accès à la base est réalisé via **Flask-SQLAlchemy**, qui permet de manipuler les données à travers des modèles Python.

Les principaux modèles sont :

```text
User
Document
Conversation
Message
```

## 🧠 ChromaDB — Données vectorielles

**ChromaDB** est utilisé comme base vectorielle pour le système RAG.

Contrairement à MySQL, ChromaDB ne gère pas les comptes ou les conversations. Son rôle est de stocker les représentations vectorielles des fragments de documents afin de permettre une **recherche sémantique**.

Chaque utilisateur dispose d'une collection vectorielle dédiée :

```text
user_<id>
```

Cette organisation permet d'isoler les connaissances documentaires entre les différents utilisateurs.

### Rôle des différents composants

| Composant                   | Rôle                                                                    |
| --------------------------- | ----------------------------------------------------------------------- |
| **MySQL**                   | Données applicatives structurées                                        |
| **Flask-SQLAlchemy**        | Accès aux données MySQL                                                 |
| **ChromaDB**                | Recherche vectorielle et stockage des données documentaires vectorisées |
| **Flask**                   | Backend, API et logique applicative                                     |
| **Hugging Face Router API** | Accès au modèle de langage                                              |
| **RAG**                     | Récupération de contexte documentaire avant génération                  |

---

# 🔐 Isolation multi-utilisateur

L'application applique une isolation des données à plusieurs niveaux.

### Base relationnelle

Les utilisateurs, documents, conversations et messages sont associés à un `user_id`.

### Fichiers

Les documents uploadés sont stockés dans un espace propre à chaque utilisateur :

```text
data/uploads/<user_id>/
```

### Base vectorielle

Chaque utilisateur dispose de sa propre collection ChromaDB :

```text
user_<id>
```

### Contrôle d'accès

Les endpoints vérifient côté serveur que les ressources demandées appartiennent bien à l'utilisateur connecté.

Une tentative d'accès à une ressource appartenant à un autre utilisateur retourne une réponse `404` afin de ne pas révéler son existence.

---

# 🛡️ Sécurité

Plusieurs mécanismes de sécurité ont été intégrés au projet :

* Authentification avec **Flask-Login**.
* Hachage des mots de passe avec **Werkzeug**.
* Protection CSRF avec **Flask-WTF**.
* Variables sensibles stockées dans l'environnement.
* Clés API absentes du dépôt Git.
* Sessions sécurisées.
* Cookies `HttpOnly`.
* Politique `SameSite`.
* Validation des fichiers uploadés.
* Limitation de la taille des fichiers.
* Vérification des droits d'accès côté serveur.
* Isolation des données entre utilisateurs.
* Suppression en cascade des ressources associées.

Pour un déploiement de production à grande échelle, des mécanismes supplémentaires pourraient être ajoutés, notamment :

* Rate limiting.
* En-têtes de sécurité et CSP.
* Chiffrement au repos des documents sensibles.
* Journalisation et monitoring.
* Protection renforcée contre les prompt injections.
* Déploiement HTTPS avec cookies `Secure`.

---

# 🏗️ Architecture du projet

```text
assistant-ia-dirigeants/
│
├── app.py
├── api_routes.py
├── auth.py
├── config.py
├── extensions.py
├── forms.py
├── models.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── modules/
│   ├── llm/
│   │   ├── hf_client.py
│   │   └── system_prompt.py
│   │
│   ├── services/
│   │   ├── document_parser.py
│   │   ├── ingestion.py
│   │   ├── rag.py
│   │   ├── user_files.py
│   │   └── vectorstore.py
│   │
│   └── utils/
│       └── chunking.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── static/
│   ├── css/
│   └── js/
│
├── data/
├── vectorstore/
├── scripts/
├── tests/
│
└── README.md
```

---

# ⚙️ Backend

Le backend est développé avec **Flask** et organisé autour de plusieurs composants modulaires.

### Responsabilités principales

* Authentification et gestion des sessions.
* Gestion des utilisateurs.
* Gestion des documents.
* Gestion des conversations.
* API conversationnelle.
* Pipeline RAG.
* Communication avec le modèle de langage.
* Persistance des données.
* Contrôle des permissions.
* Gestion des erreurs.

### Routes principales

```text
/chat
/upload

/api/conversations
/api/documents
/api/account
/api/rag/status
```

---

# 🎨 Frontend

Le frontend repose sur :

* **HTML5**
* **CSS3**
* **JavaScript ES6 Modules**
* **Marked.js**

### Fonctionnalités

* Interface conversationnelle.
* Pages d'inscription et de connexion.
* Sidebar des conversations.
* Affichage dynamique des messages.
* Rendu Markdown.
* Affichage des sources documentaires.
* Upload de documents.
* Communication avec l'API Flask.
* Gestion des conversations.
* Interface de type SaaS.

---

# 🤖 Modèle de langage

### Fournisseur

**Hugging Face Router API**

### Modèle par défaut

```text
Qwen/Qwen2.5-7B-Instruct
```

Le modèle est configurable via :

```env
HF_CHAT_MODEL=Qwen/Qwen2.5-7B-Instruct
```

Le token Hugging Face est fourni via :

```env
HF_TOKEN=...
```

Le modèle reçoit directement les questions générales ou, lorsqu'un contexte documentaire est disponible, la question accompagnée des passages récupérés par le système RAG.

---

# 🔄 Fonctionnement global

## Sans document

```text
Utilisateur
     ↓
Question
     ↓
Flask
     ↓
Aucun contexte documentaire nécessaire
     ↓
Hugging Face Router
     ↓
LLM
     ↓
Réponse
```

## Avec document

```text
Utilisateur
     ↓
Question
     ↓
Flask
     ↓
Analyse de la requête
     ↓
Recherche dans ChromaDB
     ↓
Chunks pertinents
     ↓
Construction du contexte
     ↓
Hugging Face Router
     ↓
LLM
     ↓
Réponse + sources
```

---

# 🧪 Tests et validation

Le fonctionnement du projet a été validé à travers des tests ciblés et des tests manuels réalisés directement dans l'application.

Les principaux scénarios vérifiés comprennent :

* Questions précises sur les documents.
* Synthèses globales.
* Questions de suivi.
* Questions ne nécessitant pas le RAG.
* Import de fichiers PDF, DOCX et TXT.
* Extraction de documents présentant des problèmes de mise en forme.
* Isolation des données entre utilisateurs.
* Contrôle d'accès aux conversations et documents.
* Gestion de l'indexation documentaire.
* Affichage correct des sources dans l'interface.

Une attention particulière a été portée à la validation du comportement réel de l'application, notamment pour les scénarios où un pipeline RAG peut produire un résultat techniquement valide mais une réponse utilisateur incorrecte.

---

# 👨‍💻 Contributions

Le projet a été réalisé dans le cadre d'une expérience professionnelle collaborative chez **Skill4Mind**.

## Trésor — Backend, IA & Frontend

Contributions principales :

* Développement du **backend avec Flask**.
* Développement et amélioration de l'**interface conversationnelle**.
* Intégration des modèles de langage via **Hugging Face Router API**.
* Implémentation de la **gestion des conversations**.
* Mise en place du **rendu Markdown**.
* Participation à l'architecture générale de l'application.
* Participation à la structuration du projet.
* Optimisation de l'expérience utilisateur.
* Amélioration de la stabilité de l'application.

## Équipe

| Membre            | Contributions principales                                                     |
| ----------------- | ----------------------------------------------------------------------------- |
| **Nathan**        | Backend, API Flask, intégration IA, logique métier, architecture serveur, RAG |
| **Trésor**        | Backend Flask, intégration IA, frontend, UX/UI, conversations, rendu Markdown |
| **Pierre-Thyrel** | Tests, validation fonctionnelle, support technique                            |
| **Lina**          | Documentation, organisation du projet, suivi des livrables                    |

### Encadrement

**Skill4Mind / ECE Paris**

* Dr. Taha Ridène
* M. Vincent Ferré

---

# 🛠️ Technologies utilisées

| Domaine                       | Technologies            |
| ----------------------------- | ----------------------- |
| **Langage**                   | Python                  |
| **Backend**                   | Flask                   |
| **ORM / Base de données**     | Flask-SQLAlchemy, MySQL |
| **Authentification**          | Flask-Login, Flask-WTF  |
| **Intelligence artificielle** | LLM, RAG                |
| **LLM Provider**              | Hugging Face Router API |
| **Modèle**                    | Qwen2.5-7B-Instruct     |
| **Base vectorielle**          | ChromaDB                |
| **Traitement documentaire**   | pypdf, python-docx      |
| **Frontend**                  | HTML5, CSS3, JavaScript |
| **Markdown**                  | Marked.js               |

---

# 🚀 Installation

## 1. Cloner le projet

```bash
git clone https://github.com/NosProjets-Tech/assistant-ia-dirigeants.git
cd assistant-ia-dirigeants
```

## 2. Créer l'environnement virtuel

### Windows

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 4. Configurer l'environnement

Copier le fichier `.env.example` :

```bash
cp .env.example .env
```

Puis renseigner les variables nécessaires, notamment :

```env
SECRET_KEY=your_secret_key
HF_TOKEN=your_huggingface_token
DATABASE_URL=mysql+pymysql://user:password@localhost/database
```

Une clé secrète peut être générée avec :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 5. Initialiser la base de données

### Windows

```powershell
$env:FLASK_APP="app"
python -m flask init-db
```

### macOS / Linux

```bash
export FLASK_APP=app
python -m flask init-db
```

## 6. Lancer l'application

```bash
python -m flask run --debug
```

L'application est alors disponible sur :

```text
http://127.0.0.1:5000
```

---

# ⚙️ Variables d'environnement

| Variable        | Obligatoire | Description                        |
| --------------- | ----------- | ---------------------------------- |
| `SECRET_KEY`    | Oui         | Clé secrète Flask                  |
| `HF_TOKEN`      | Oui         | Token d'accès Hugging Face         |
| `HF_CHAT_MODEL` | Non         | Modèle LLM utilisé                 |
| `DATABASE_URL`  | Oui         | URL de connexion MySQL             |
| `CHUNK_SIZE`    | Non         | Taille des fragments documentaires |
| `CHUNK_OVERLAP` | Non         | Chevauchement entre les fragments  |
| `TOP_K`         | Non         | Nombre de chunks récupérés         |
| `MAX_UPLOAD_MB` | Non         | Taille maximale d'un fichier       |

Les autres paramètres sont disponibles dans `.env.example` et `config.py`.

---

# 📊 État du projet

## ✅ Projet finalisé

Le projet a atteint ses objectifs dans le cadre de l'expérience réalisée chez **Skill4Mind** pendant le **Bachelor 2 à l'ECE Paris**.

L'application dispose d'une architecture fonctionnelle comprenant :

* une interface conversationnelle ;
* un système d'authentification ;
* une gestion persistante des conversations ;
* l'import et le traitement de documents ;
* un pipeline RAG ;
* une base vectorielle ChromaDB ;
* une base relationnelle MySQL ;
* une intégration LLM via Hugging Face Router API ;
* une isolation des données entre utilisateurs ;
* des réponses contextualisées et sourcées.

Le projet constitue ainsi une **preuve de concept fonctionnelle d'un assistant IA orienté entreprise**, combinant développement web, intelligence artificielle générative, traitement documentaire et recherche sémantique.

---

# 🔮 Perspectives d'évolution

Bien que le projet soit finalisé dans son cadre initial, plusieurs évolutions pourraient permettre de poursuivre son développement.

### Backend

* Mise en place de migrations avec Flask-Migrate / Alembic.
* Ajout d'un système de rate limiting.
* Extension de la couverture des tests automatisés avec pytest.
* Monitoring et journalisation.
* Déploiement avec un serveur WSGI.
* Renforcement de la protection contre les prompt injections.

### Frontend

* Interface responsive mobile.
* Tableau de bord documentaire dédié.
* Gestion avancée des documents.
* Paramètres utilisateur.
* Notifications.
* Amélioration continue de l'UX/UI.

### Intelligence artificielle

* Évaluation automatique de la qualité des réponses RAG.
* Amélioration du classement des passages récupérés.
* Recherche hybride vectorielle et lexicale.
* Support de modèles LLM supplémentaires.
* Citations documentaires plus détaillées.
* Gestion de plusieurs sources de connaissances.

---

# 🎓 Contexte professionnel et académique

**Entreprise :** Skill4Mind
**Formation :** ECE Paris — Bachelor 2
**Nature :** Stage / expérience en entreprise
**Domaine :** Intelligence artificielle · Développement logiciel · LLM · RAG

### Encadrement

* **Dr. Taha Ridène**
* **M. Vincent Ferré**

Cette expérience a permis de mettre en pratique des compétences en **développement backend et frontend, conception d'API, intelligence artificielle générative, traitement documentaire, recherche vectorielle, bases de données, architecture logicielle et expérience utilisateur**.

---

# 📄 Licence

Projet réalisé dans le cadre d'une expérience en entreprise et d'un cursus académique.
