import os
import requests

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from dotenv import load_dotenv

from modules.llm.system_prompt import SYSTEM_PROMPT

# =========================
# CONFIGURATION
# =========================

load_dotenv()

app = Flask(__name__)

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

HF_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# =========================
# ROUTES FRONTEND
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# =========================
# ROUTE CHAT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    print(">>> /chat appelé")

    try:
        data = request.get_json()

        if not data:
            return jsonify({"response": "Requête invalide"}), 400

        message = data.get("message", "").strip()

        if not message:
            return jsonify({"response": "Message vide"}), 400

        # =========================
        # PAYLOAD HF
        # =========================
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

            "temperature": 0.2,
            "max_tokens": 512
        }

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        # =========================
        # DEBUG HF RESPONSE
        # =========================
        try:
            result = response.json()
        except Exception:
            return jsonify({
                "response": "Erreur: réponse non JSON de Hugging Face"
            }), 500

        print("HF STATUS:", response.status_code)
        print("HF RESPONSE:", result)

        # =========================
        # ERREUR HF
        # =========================
        if response.status_code != 200:
            return jsonify({
                "response": f"Erreur HF ({response.status_code}) : {result}"
            }), 500

        # =========================
        # VALIDATION FORMAT
        # =========================
        if "choices" not in result:
            return jsonify({
                "response": f"Format HF inattendu : {result}"
            }), 500

        reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "response": reply
        })

    except Exception as e:
        return jsonify({
            "response": f"Erreur serveur: {str(e)}"
        }), 500


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)