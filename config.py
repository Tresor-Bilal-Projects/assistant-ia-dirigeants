import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Hugging Face
HF_API_URL = os.getenv("HF_API_URL", "https://router.huggingface.co/v1/chat/completions")
# Fallback Qwen (pas de gated access). Llama : meta-llama/Llama-3.1-8B-Instruct
HF_CHAT_MODEL = os.getenv("HF_CHAT_MODEL", "Qwen/Qwen2.5-7B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# RAG
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
UPLOAD_DIR = DATA_DIR / "uploads"
VECTORSTORE_DIR = str(BASE_DIR / os.getenv("VECTORSTORE_DIR", "vectorstore/chroma"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "company_docs")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(VECTORSTORE_DIR).mkdir(parents=True, exist_ok=True)
