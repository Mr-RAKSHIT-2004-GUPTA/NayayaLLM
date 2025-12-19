import os
import faiss
import pickle
import re
from groq import Groq
from sentence_transformers import SentenceTransformer

from config.settings import EMBED_MODEL, TOP_K


# ======================================================
# CONFIG (TOKEN SAFE FOR GROQ FREE TIER)
# ======================================================
INDEX_PATH = "embeddings/faiss.index"
META_PATH = "embeddings/metadata.pkl"

MAX_CHARS_PER_CHUNK = 1200      # limit per retrieved chunk
MAX_CONTEXT_CHARS = 3000        # hard cap for total context
TEMPERATURE = 0.1
MAX_TOKENS = 512


# ======================================================
# LOAD KNOWLEDGE BASE
# ======================================================
index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

embedder = SentenceTransformer(EMBED_MODEL)


# ======================================================
# GROQ CLIENT (ENV VAR REQUIRED)
# ======================================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_CANDIDATES = [
    "llama-3.1-8b-instant",     # stable free-tier
    "mixtral-8x7b-32768"        # fallback
]


# ======================================================
# TEXT CLEANING HELPERS
# ======================================================
def clean_for_llm(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Downloaded on.*?\d{4}', '', text)
    return text.strip()


def trim_chunk(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> str:
    return text[:max_chars]


# ======================================================
# RETRIEVAL (WITH METADATA FOR CITATIONS)
# ======================================================
def retrieve(query: str, k: int = TOP_K):
    q_emb = embedder.encode([query]).astype("float32")
    _, idxs = index.search(q_emb, k)

    results = []
    for i in idxs[0]:
        results.append({
            "text": metadata[i]["text"],
            "source": metadata[i]["source_file"],
            "chunk_id": metadata[i]["chunk_id"]
        })
    return results


def build_context(results):
    context_blocks = []
    citations = []

    for r in results:
        cleaned = trim_chunk(clean_for_llm(r["text"]))
        context_blocks.append(cleaned)
        citations.append(f"{r['source']} (chunk {r['chunk_id']})")

    context = "\n\n".join(context_blocks)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    return context, citations


# ======================================================
# QUERY REWRITE (LEGAL LANGUAGE ALIGNMENT)
# ======================================================
QUERY_REWRITE_PROMPT = (
    "Rewrite the following legal question using formal judicial language "
    "commonly found in Indian court judgments. "
    "Do not answer the question.\n\n"
    "Question: {query}\n\n"
    "Rewritten Question:"
)

def rewrite_query(query: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": QUERY_REWRITE_PROMPT.format(query=query)}
            ],
            temperature=0.0,
            max_tokens=64
        )
        return response.choices[0].message.content.strip()
    except:
        return query


# ======================================================
# PROMPTS
# ======================================================
SYSTEM_PROMPT_QA = (
    "You are a legal research assistant. "
    "Answer the question strictly using the provided context from court judgments. "
    "Do not add external knowledge. "
    "If the answer is not clearly present in the context, say: "
    "'Not found in the provided judgment excerpts.' "
    "Be concise, factual, and legally precise."
)

SYSTEM_PROMPT_SUMMARY = (
    "You are a legal summarization assistant. "
    "Using only the provided judgment excerpts, "
    "write a concise and neutral legal summary. "
    "Do not introduce facts not present in the text."
)


# ======================================================
# LLM CALL (QA / SUMMARY WITH FALLBACK)
# ======================================================
def call_llm(context: str, query: str = None, mode: str = "qa"):
    messages = []

    if mode == "qa":
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_QA},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"}
        ]
    else:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_SUMMARY},
            {"role": "user", "content": f"Context:\n{context}\n\nSummary:"}
        ]

    for model in MODEL_CANDIDATES:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            print(f"✅ Using model: {model}")
            return response.choices[0].message.content
        except Exception:
            print(f"⚠️ Model failed: {model} → trying next")

    return "Model unavailable at the moment."


# ======================================================
# MAIN LOOP
# ======================================================
if __name__ == "__main__":
    print("✅ Legal RAG system ready (QA + Summarization + Citations)\n")

    while True:
        mode = input("Choose mode (qa / summary / exit): ").strip().lower()
        if mode == "exit":
            break

        user_query = input("Enter query: ").strip()

        rewritten_query = rewrite_query(user_query)
        print(f"\n🔁 Rewritten Query:\n{rewritten_query}\n")

        results = retrieve(rewritten_query)
        context, citations = build_context(results)

        answer = call_llm(
            context=context,
            query=rewritten_query if mode == "qa" else None,
            mode=mode
        )

        print("\n📘 Output:\n")
        print(answer)

        print("\n📌 Citations:")
        for c in citations:
            print("-", c)

        print("\n" + "-" * 60)
