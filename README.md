# Assistant IA pour dirigeants

---

## 1. Présentation du projet

Ce projet est un **assistant conversationnel intelligent destiné à des dirigeants d’entreprise**.

Il permet d’interagir en langage naturel avec une IA capable de générer des réponses structurées, orientées analyse et prise de décision.

Le système repose actuellement sur une intégration d’un modèle de langage via l’API **Hugging Face Router**, avec une évolution progressive vers une architecture **RAG (Retrieval Augmented Generation)** basée sur des documents internes.

---

## 2. Objectif du projet

- Créer un assistant IA pour la prise de décision en entreprise
- Fournir une interface conversationnelle type SaaS
- Permettre l’analyse de questions stratégiques
- Préparer l’intégration de documents internes (RAG)
- Évoluer vers un produit IA utilisable en environnement professionnel

---

## 3. État actuel du projet

Le projet est actuellement en phase :

> **MVP fonctionnel avec assistant IA connecté**

---

### ✔ Backend (stable)

- API `/chat` fonctionnelle
- Intégration Hugging Face Router API
- Génération de réponses IA
- Structure backend modulaire (Flask)
- Gestion basique des erreurs

---

### ⚠ Frontend (en cours de stabilisation UX/UI)

Le frontend a été récemment amélioré avec une refonte UX/UI type SaaS :

- Interface chat type ChatGPT-like
- Design dark SaaS modernisé
- Affichage dynamique des messages
- Support Markdown (titres, listes, code blocks)
- Auto-scroll des messages
- Auto-resize textarea
- Typing effect stabilisé
- Bouton copier fonctionnel sur messages bot
- Amélioration globale de la fluidité UI

---

### État fonctionnel global

- Chat IA entièrement fonctionnel
- UI stable mais encore en phase d’optimisation
- Historique des conversations : structure en place (JS modulable), non finalisé UX

---

## 4. Architecture du projet

### Backend (Flask)

**Technologies :**
- Python
- Flask
- Hugging Face Router API
- dotenv

**Rôle :**
- gestion des routes API
- communication avec le modèle IA
- traitement des messages utilisateur
- retour des réponses JSON

**Endpoint principal :**
- `/chat`

---

### Frontend

**Technologies :**
- HTML
- CSS
- JavaScript (modularisé)

**Rôle :**
- interface utilisateur type SaaS
- envoi des messages vers l’API `/chat`
- affichage dynamique des réponses IA
- gestion UX (loading, typing, scroll)

---

## 5. Modèle IA utilisé

- Hugging Face Router API
- Modèle : `meta-llama/Llama-3.1-8B-Instruct`

Ce modèle est utilisé pour générer des réponses conversationnelles adaptées à un assistant professionnel.

---

## 6. Sécurité

- utilisation de variables d’environnement (`.env`)
- aucune clé API exposée dans le code
- `.env` ignoré via `.gitignore`
- fichier `.env.example` fourni

---

## 7. Structure du projet

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
│   ├── utils/

├── templates/
│   ├── base.html
│   ├── index.html

├── static/
│   ├── css/
│   │   ├── chat.css
│   │   ├── style.css
│   ├── js/
│   │   ├── chat.js
│   │   ├── api.js
│   │   ├── ui.js
│   │   ├── upload.js
│   │   ├── conversationManager.js
        ├── storage.js

├── tests/
└── README.md
````

---

## 8. Fonctionnalités principales

### Backend

* API `/chat` fonctionnelle
* intégration IA via Hugging Face
* génération de réponses
* gestion des erreurs

---

### Frontend (mis à jour récemment)

* interface chat SaaS type ChatGPT
* refonte CSS (UI plus moderne et stable)
* affichage dynamique des messages
* animation de réponse (typing effect stabilisé)
* auto-scroll conversation amélioré
* textarea auto-resize corrigé
* système d’upload frontend (non connecté backend)
* bouton copier stable et mieux positionné

---

## 9. Améliorations récentes (Frontend UX/UI)

Travail réalisé récemment :

* Refonte CSS vers un design SaaS plus moderne et sombre
* Stabilisation du DOM des messages (moins de re-render instable)
* Correction du typing effect (meilleure gestion du contenu dynamique)
* Amélioration du rendu Markdown (code, listes, titres)
* Correction du comportement du textarea (auto-resize fluide)
* Correction du positionnement du bouton envoyer
* Stabilisation du bouton copier (UX + affichage + copie propre)
* Amélioration globale de la fluidité UI

---

## 10. Prochaines étapes

### Backend

* amélioration du prompt système
* ajout mémoire conversationnelle
* endpoint `/upload`
* extraction PDF / TXT
* intégration RAG (documents internes)

---

### Frontend

- finalisation du système d’historique de conversations (sidebar + persistence)
- intégration complète du `conversationManager.js`
- connexion UI ↔ storage (localStorage)
- dark mode avancé
- amélioration UX type SaaS mature
- micro-interactions UI (niveau produit)

---

## 11. Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/Tresor-Bilal-Projects/assistant-ia-dirigeants.git
cd assistant-ia-dirigeants
```

### 2. Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration environnement

```bash
cp .env.example .env
```

### 5. Lancer l’application

```bash
python app.py
```

---

## 12. Répartition du travail

| Membre        | Rôle principal |
|---------------|----------------|
| Nathan        | Backend / IA (API, intégration Hugging Face, logique chat, architecture backend) |
| Trésor        | Frontend / UX (interface chat, UI/UX, styling, interactions utilisateur) |
| Pierre-Thyrel | Données / tests / support technique |
| Lina          | Documentation / organisation projet |

---

## 13. Conclusion

Le projet est actuellement un **MVP fonctionnel avec backend stable et frontend fortement amélioré récemment**.

Le travail effectué a principalement renforcé la **stabilité UI/UX (type SaaS ChatGPT-like)**, notamment sur le rendu des messages, le textarea, le bouton copier et la cohérence globale de l’interface.





