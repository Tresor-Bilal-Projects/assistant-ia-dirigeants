import requests

from config import HF_API_URL, HF_CHAT_MODEL, HF_TOKEN


def chat_completion(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> str:
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN manquant. Ajoutez votre clé Hugging Face dans le fichier .env.")

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": HF_CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(
        HF_API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"HF error HTTP {response.status_code}: {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"]
