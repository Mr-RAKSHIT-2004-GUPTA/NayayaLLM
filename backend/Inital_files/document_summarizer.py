from groq import Groq
import re

client = Groq()

CHUNK_SIZE = 1200
MAX_TOKENS = 256

SUMMARY_PROMPT = (
    "You are a legal summarization assistant. "
    "Summarize the following judgment excerpt concisely and factually. "
    "Do not add facts."
)

def chunk_text(text, size=CHUNK_SIZE):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])


def summarize_chunk(chunk):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": chunk}
        ],
        temperature=0.1,
        max_tokens=MAX_TOKENS
    )
    return response.choices[0].message.content


def summarize_document(text):
    partial_summaries = []
    for chunk in chunk_text(text):
        partial_summaries.append(summarize_chunk(chunk))

    return "\n".join(partial_summaries)
