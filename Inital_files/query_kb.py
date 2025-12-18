import faiss
import pickle
from sentence_transformers import SentenceTransformer

from config.settings import EMBED_MODEL, TOP_K


INDEX_PATH = "embeddings/faiss.index"
META_PATH = "embeddings/metadata.pkl"


def load_kb():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def search(query, index, metadata, embedder, k=TOP_K):
    query_embedding = embedder.encode([query]).astype("float32")
    _, indices = index.search(query_embedding, k)

    results = []
    for idx in indices[0]:
        results.append(metadata[idx])

    return results


if __name__ == "__main__":
    print("🔍 Loading knowledge base...")
    index, metadata = load_kb()
    embedder = SentenceTransformer(EMBED_MODEL)

    print("✅ KB loaded successfully\n")

    while True:
        query = input("Enter your legal query (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break

        results = search(query, index, metadata, embedder)

        print("\n📄 Retrieved Context:\n")
        for i, res in enumerate(results, 1):
            print(f"--- Result {i} (from {res['source_file']}) ---")
            print(res["text"][:1000])
            print("\n")
