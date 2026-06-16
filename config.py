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

# RAG relevance gating
# Chroma's default collection uses squared-L2 distance (lower = more similar).
# A retrieved chunk is only treated as relevant when its distance is at or
# below this threshold; otherwise it is discarded and the RAG context is empty.
# Empirically measured on the company docs (MiniLM default embeddings):
#   - genuine document questions score   <= ~1.12
#   - greetings / out-of-domain questions >= ~1.21
# 1.15 sits in that gap, keeping real questions while rejecting noise.
RAG_DISTANCE_THRESHOLD = float(os.getenv("RAG_DISTANCE_THRESHOLD", "1.15"))

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(VECTORSTORE_DIR).mkdir(parents=True, exist_ok=True)
