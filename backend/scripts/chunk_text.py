from nltk.tokenize import sent_tokenize
import nltk
nltk.download("punkt")

def chunk_text(text, max_words=450, overlap=50):
    sentences = sent_tokenize(text)
    chunks = []
    current = []

    for sent in sentences:
        current.append(sent)
        if len(" ".join(current).split()) >= max_words:
            chunks.append(" ".join(current))
            current = current[-overlap:]

    if current:
        chunks.append(" ".join(current))

    return chunks
