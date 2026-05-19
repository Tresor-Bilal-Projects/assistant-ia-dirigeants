#  README — Assistant IA pour dirigeants

---

## 1. Présentation du projet

Ce projet est un **assistant conversationnel intelligent destiné à des dirigeants d’entreprise**.

Il permet d’interagir en langage naturel avec une IA capable de générer des réponses structurées, orientées analyse et prise de décision.

Le système repose actuellement sur une intégration d’un modèle de langage via l’API **Hugging Face Router**, avec une évolution progressive vers une architecture **RAG (Retrieval Augmented Generation)** basée sur des documents internes.

---

## 2. Objectif du projet

* Créer un assistant IA pour la prise de décision en entreprise
* Fournir une interface conversationnelle type SaaS
* Permettre l’analyse de questions stratégiques
* Préparer l’intégration de documents internes (RAG)
* Évoluer vers un produit IA utilisable en environnement professionnel

---

## 3. État actuel du projet

Le projet est actuellement en phase :

> **MVP fonctionnel avec assistant IA connecté**

### ✔ Backend (fonctionnel)

* API `/chat` opérationnelle
* Intégration Hugging Face Router API
* Génération de réponses IA
* Gestion des erreurs de base
* Structure modulaire en Python

### ⚠ Frontend (en cours d’amélioration)

* Interface chat type SaaS (ChatGPT-like)
* Messages utilisateur / assistant fonctionnels
* Animation de réponse (typing effect)
* Auto-scroll des messages
* Auto-resize textarea (fonctionnel mais instable selon certains cas)
* Upload de fichiers côté frontend (non connecté backend)
* Bouton copier (fonctionnel mais affichage perfectible)
* UX globale en phase de stabilisation

---

## 4. Architecture du projet

### Backend (Flask)

**Technologies :**

* Python
* Flask
* Hugging Face Router API
* dotenv

**Rôle :**

* gestion des routes API
* communication avec le modèle IA
* traitement des messages utilisateur
* retour des réponses JSON

**Endpoint principal :**

* `/chat`

---

### Frontend

**Technologies :**

* HTML
* CSS
* JavaScript (modularisé)

**Rôle :**

* interface utilisateur type SaaS
* envoi des messages vers l’API `/chat`
* affichage dynamique des réponses IA
* gestion UX (loading, typing, scroll)

---

## 5. Modèle IA utilisé

* Hugging Face Router API
* Modèle : `meta-llama/Llama-3.1-8B-Instruct`

Ce modèle est utilisé pour générer des réponses conversationnelles adaptées à un assistant professionnel.

---

## 6. Sécurité

* utilisation de variables d’environnement (`.env`)
* aucune clé API exposée dans le code
* `.env` ignoré via `.gitignore`
* fichier `.env.example` fourni

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
│   │   ├── app.js

├── tests/
└── README.md
```

---

## 8. Fonctionnalités principales

### Backend

* API `/chat` fonctionnelle
* intégration IA via Hugging Face
* génération de réponses
* gestion des erreurs

### Frontend

* interface chat SaaS
* affichage dynamique des messages
* animation de réponse (typing)
* auto-scroll des conversations
* textarea avec auto-resize (à stabiliser)
* système d’upload frontend (non connecté backend)
* bouton copier (fonctionnel mais perfectible)

---

## 9. Améliorations en cours (Frontend UX)

* stabilisation du textarea (comportement inconsistent selon input)
* amélioration du rendu des messages
* correction du positionnement du bouton copier
* optimisation du scroll automatique
* nettoyage de la structure DOM des messages
* amélioration générale de la stabilité UI

---

## 10. Prochaines étapes

### Backend

* amélioration du prompt système
* ajout mémoire conversationnelle
* endpoint `/upload`
* extraction PDF / TXT
* intégration RAG (documents internes)

### Frontend

* stabilisation complète UI
* sidebar historique des conversations
* dark mode
* amélioration UX type SaaS mature
* connexion upload frontend ↔ backend

---

## 11. Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/Nathandev19/assistant-ia-dirigeants.git
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

| Membre        | Rôle                        |
| ------------- | --------------------------- |
| Nathan        | Backend / IA / architecture |
| Trésor        | Frontend / UX               |
| Pierre-Thyrel | Données / tests             |
| Lina          | Documentation               |

---

## 13. Conclusion

Le projet est actuellement un **MVP fonctionnel** avec une base solide côté backend.

Le frontend est en phase d’ajustement et de stabilisation pour atteindre une expérience utilisateur fluide de type SaaS (ChatGPT-like).

