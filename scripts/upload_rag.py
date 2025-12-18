import faiss
import re
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer


# ======================================================
# CONFIG
# ======================================================
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CHARS_PER_CHUNK = 1200
TOP_K = 3
TEMPERATURE = 0.1
MAX_TOKENS_QA = 512
MAX_TOKENS_SUMMARY = 256

client = Groq()   # uses GROQ_API_KEY env variable
embedder = SentenceTransformer(EMBED_MODEL)


# ======================================================
# TEXT HELPERS
# ======================================================
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK):
    chunks = []
    current = ""
    for sentence in text.split(". "):
        if len(current) + len(sentence) <= max_chars:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks


# ======================================================
# BUILD TEMP FAISS INDEX (SESSION LEVEL)
# ======================================================
def build_temp_index(text: str):
    chunks = chunk_text(clean_text(text))
    embeddings = embedder.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, chunks


# ======================================================
# QA (UPLOAD RAG)
# ======================================================
QA_SYSTEM_PROMPT = (
    "You are a legal research assistant. "
    "Answer the question strictly using the provided document excerpts. "
    "If the answer is not found, say: "
    "'Not found in the provided document.'"
)


def ask_question(index, chunks, question: str):
    q_emb = embedder.encode([question]).astype("float32")
    _, idxs = index.search(q_emb, TOP_K)

    context = "\n\n".join([chunks[i] for i in idxs[0]])

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": QA_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"}
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS_QA
    )

    return response.choices[0].message.content


# ======================================================
# SECTION-WISE SUMMARY (RAG-BASED)
# ======================================================
SECTION_QUERIES = {
    "Procedural History": "Summarize the procedural history of the case.",
    "Issues Involved": "Summarize the legal issues involved in the case.",
    "Court Directions": "Summarize the directions issued by the court.",
    "Reasoning": "Summarize the reasoning given by the court.",
    "Final Decision": "Summarize the final decision and outcome of the case."
}


def summarize_by_sections(text: str):
    index, chunks = build_temp_index(text)
    section_summaries = {}

    for section, query in SECTION_QUERIES.items():
        section_summaries[section] = ask_question(index, chunks, query)

    return section_summaries


# ======================================================
# FULL DOCUMENT SUMMARY (MAP–REDUCE)
# ======================================================
SUMMARY_PROMPT = (
    "You are a legal summarization assistant. "
    "Summarize the following legal judgment excerpt concisely and factually. "
    "Do not add new information."
)

FINAL_SUMMARY_PROMPT = (
    "You are a legal analyst. "
    "Combine the following partial summaries into a single, coherent summary "
    "of the judgment. "
    "Do NOT use templates, headings, placeholders, or formal judgment formatting. "
    "Write in paragraph form only. "
    "Do NOT invent court names, dates, petition numbers, or signatures. "
    "Use only information explicitly present in the summaries."
)



def summarize_document(text: str):
    chunks = chunk_text(clean_text(text))
    partial_summaries = []

    # Step 1: Summarize each chunk
    for chunk in chunks:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": chunk}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_SUMMARY
        )
        partial_summaries.append(response.choices[0].message.content)

    # Step 2: Merge summaries
    merged_text = "\n".join(partial_summaries)

    final_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": FINAL_SUMMARY_PROMPT},
            {"role": "user", "content": merged_text}
        ],
        temperature=TEMPERATURE,
        max_tokens=512
    )

    return final_response.choices[0].message.content


# ======================================================
# MAIN (LOCAL TESTING)
# ======================================================
if __name__ == "__main__":
    with open("sample_judgment.txt", "r", encoding="utf-8") as f:
        document_text = f.read()

    print("\n📄 Uploaded document loaded successfully.")
    index, chunks = build_temp_index(document_text)

    while True:
        mode = input("\nChoose mode (qa / section / summary / exit): ").strip().lower()

        if mode == "exit":
            break

        elif mode == "qa":
            question = input("Enter your question: ")
            answer = ask_question(index, chunks, question)
            print("\n📘 Answer:\n")
            print(answer)

        elif mode == "section":
            print("\n📘 Section-wise Summary:\n")
            sections = summarize_by_sections(document_text)
            for title, content in sections.items():
                print(f"\n🔹 {title}:\n{content}")

        elif mode == "summary":
            print("\n📘 Complete Document Summary:\n")
            print(summarize_document(document_text))

        else:
            print("❌ Invalid option. Choose qa / section / summary / exit.")
