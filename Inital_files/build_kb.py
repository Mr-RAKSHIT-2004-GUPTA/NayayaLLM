import os
import pickle
import numpy as np
import faiss
from tqdm import tqdm

from sentence_transformers import SentenceTransformer

from config.settings import (
    EXTRACTED_TEXT_PATH,
    EMBED_MODEL,
    CHUNK_SIZE_WORDS,
    CHUNK_OVERLAP
)

from scripts.clean_text import clean_text
from scripts.chunk_text import chunk_text


# ==============================
# CONFIG
# ==============================
BATCH_SIZE = 32                  # safe on CPU
MAX_CHUNKS = 20000               # fast demo (set None for full scale)
CHECKPOINT_EVERY = 10            # batches
EMBEDDINGS_DIR = "embeddings"

INDEX_PATH = os.path.join(EMBEDDINGS_DIR, "faiss.index")
META_PATH = os.path.join(EMBEDDINGS_DIR, "metadata.pkl")
STATE_PATH = os.path.join(EMBEDDINGS_DIR, "state.pkl")


# ==============================
# SETUP
# ==============================
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

embedder = SentenceTransformer(EMBED_MODEL)

dimension = embedder.get_sentence_embedding_dimension()


# ==============================
# LOAD OR INIT STATE
# ==============================
if os.path.exists(STATE_PATH):
    print("🔁 Resuming from checkpoint...")
    with open(STATE_PATH, "rb") as f:
        state = pickle.load(f)

    start_idx = state["next_chunk"]
    metadata = state["metadata"]
    index = faiss.read_index(INDEX_PATH)

else:
    print("🆕 Starting fresh KB build...")
    start_idx = 0
    metadata = []
    index = faiss.IndexFlatL2(dimension)


# ==============================
# COLLECT ALL CHUNKS
# ==============================
print("📦 Collecting and chunking documents...")

all_chunks = []

for filename in os.listdir(EXTRACTED_TEXT_PATH):
    file_path = os.path.join(EXTRACTED_TEXT_PATH, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        text = clean_text(f.read())

    chunks = chunk_text(text, CHUNK_SIZE_WORDS, CHUNK_OVERLAP)

    for chunk_id, chunk in enumerate(chunks):
        all_chunks.append({
            "text": chunk,
            "source_file": filename,
            "chunk_id": chunk_id
        })

if MAX_CHUNKS:
    all_chunks = all_chunks[:MAX_CHUNKS]

total_chunks = len(all_chunks)
print(f"✅ Total chunks to embed: {total_chunks}")


# ==============================
# EMBEDDING LOOP (WITH CHECKPOINT)
# ==============================
print("🚀 Building embeddings...")

for i in tqdm(range(start_idx, total_chunks, BATCH_SIZE), desc="Embedding"):
    batch = all_chunks[i:i + BATCH_SIZE]
    texts = [item["text"] for item in batch]

    embeddings = embedder.encode(texts)
    embeddings = np.array(embeddings).astype("float32")

    index.add(embeddings)

    for item in batch:
        metadata.append({
            "source_file": item["source_file"],
            "chunk_id": item["chunk_id"],
            "text": item["text"]
        })

    # --------------------------
    # CHECKPOINT SAVE
    # --------------------------
    if ((i // BATCH_SIZE) + 1) % CHECKPOINT_EVERY == 0:
        faiss.write_index(index, INDEX_PATH)

        with open(META_PATH, "wb") as f:
            pickle.dump(metadata, f)

        with open(STATE_PATH, "wb") as f:
            pickle.dump({
                "next_chunk": i + BATCH_SIZE,
                "metadata": metadata
            }, f)

        print(f"💾 Checkpoint saved at chunk {i + BATCH_SIZE}")


# ==============================
# FINAL SAVE
# ==============================
faiss.write_index(index, INDEX_PATH)

with open(META_PATH, "wb") as f:
    pickle.dump(metadata, f)

if os.path.exists(STATE_PATH):
    os.remove(STATE_PATH)

print("✅ Knowledge base build completed successfully.")
