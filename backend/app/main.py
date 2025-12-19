from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from scripts.upload_rag import (
    build_temp_index,
    ask_question,
    summarize_by_sections,
    summarize_document
)

app = FastAPI(title="Legal Document RAG API")

# --------------------------------------------------
# CORS (Firebase frontend support)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# DOCUMENT PROCESSING ENDPOINT
# --------------------------------------------------
@app.post("/document/process")
async def process_document(
    mode: str = Form(...),
    question: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either file or text")

    if mode not in ["qa", "section", "summary"]:
        raise HTTPException(status_code=400, detail="Invalid mode")

    # --------------------------------------------------
    # LOAD DOCUMENT TEXT
    # --------------------------------------------------
    if file:
        document_text = (await file.read()).decode("utf-8", errors="ignore")
    else:
        document_text = text

    if len(document_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Document text too short")

    # --------------------------------------------------
    # PROCESS BASED ON MODE
    # --------------------------------------------------
    if mode == "qa":
        if not question:
            raise HTTPException(status_code=400, detail="Question required for QA mode")

        index, chunks = build_temp_index(document_text)
        answer = ask_question(index, chunks, question)

        return {
            "mode": "qa",
            "answer": answer
        }

    elif mode == "section":
        sections = summarize_by_sections(document_text)
        return {
            "mode": "section",
            "sections": sections
        }

    elif mode == "summary":
        summary = summarize_document(document_text)
        return {
            "mode": "summary",
            "summary": summary
        }
