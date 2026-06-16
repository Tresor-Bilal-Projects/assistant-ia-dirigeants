"""Indexe le document de démo pour tester le RAG sans passer par l'UI."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.services.ingestion import ingest_file


def main():
    sample = ROOT / "data" / "sample_entreprise.txt"

    if not sample.exists():
        raise FileNotFoundError(f"Fichier introuvable : {sample}")

    result = ingest_file(str(sample), sample.name)
    print("Document de démo indexé :")
    print(f"  - fragments : {result['chunks']}")
    print(f"  - caractères : {result['characters']}")


if __name__ == "__main__":
    main()
