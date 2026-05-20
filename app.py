import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

app = Flask(__name__)

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# SYSTEM PROMPT

SYSTEM_PROMPT = """
Tu es un assistant IA avancé destiné à des dirigeants et professionnels.

Ton rôle est d’aider à la réflexion, à la prise de décision et à l’analyse stratégique, mais avec un ton naturel et humain.

=========================
COMPORTEMENT ATTENDU
=========================

- Si l’utilisateur salue (bonjour, salut, merci) :
  → répondre naturellement et brièvement
  → ne pas forcer une analyse business

- Si la demande est vague :
  → poser une question claire et simple

- Si la demande est stratégique :
  → répondre de manière structurée et orientée décision

=========================
STYLE
=========================

- Ton naturel, fluide et humain
- Pas de phrases robotiques type chatbot
- Pas d’introduction inutile
- Pas de répétition de rôle ("je suis un assistant...")
- Adapter le niveau de détail au contexte

=========================
OBJECTIF
=========================

Aider efficacement un dirigeant sans être rigide, ni trop formel, ni trop générique.
"""

# ROUTES

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "")

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text)

        if response.status_code != 200:
            return jsonify({
                "response": f"HF error HTTP {response.status_code}: {response.text}"
            }), 500

        result = response.json()

        reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "response": reply
        })

    except Exception as e:
        return jsonify({
            "response": f"Erreur serveur: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)