"""Upload endpoints for the PDF ingestion workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from copy import deepcopy
from pathlib import Path
from threading import Lock
import logging
import os
import json
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.ragger import Ragger

app = FastAPI(title="PDF RAG")
app.mount("/static", StaticFiles(directory="static"), name="static")
UPLOAD_DIRECTORY = Path("uploads")
jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = Lock()
ragger = Ragger()
TOP_K = 3
RELEVANCE_THRESHOLD = 0.70
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """The only input accepted by the document question endpoint."""

    question: str


def _answer_for_question(question: str) -> tuple[str, list[dict[str, Any]]]:
    """Retrieve context and apply the same relevance policy as ``/chat``."""
    chunks = ragger.search(question, top_k=TOP_K)
    top_score = float(chunks[0]["similarity_score"]) if chunks else 0.0
    logger.info("chat retrieval question=%r top_score=%.4f", question, top_score)
    sources = [_source_from_chunk(chunk) for chunk in chunks]
    if top_score < RELEVANCE_THRESHOLD:
        return "문서에서 답을 찾지 못했습니다.", sources
    return _generate_answer(question, chunks), sources


def _source_from_chunk(chunk: dict[str, Any]) -> dict[str, Any]:
    """Expose useful provenance without leaking the internal top-score value."""
    text = str(chunk.get("text", ""))
    return {
        "original_filename": chunk.get("original_filename", chunk.get("stored_filename", "")),
        "stored_filename": chunk.get("stored_filename", ""),
        "page": chunk.get("page", 0),
        "text": text[:300],
        "similarity_score": float(chunk.get("similarity_score", 0.0)),
    }


def _generate_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    """Ask OpenAI to answer strictly from the retrieved document passages."""
    from openai import OpenAI

    context = "\n\n".join(
        f"[{chunk.get('stored_filename', '')} p.{chunk.get('page', '')}] {chunk.get('text', '')}"
        for chunk in chunks
    )
    completion = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")).chat.completions.create(
        model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
        messages=[
            {"role": "system", "content": "Answer only from the supplied document context. If it is insufficient, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return completion.choices[0].message.content or "문서 근거로 답변을 만들 수 없습니다."


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _new_job(job_id: str) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "files": [],
        "total_chunks": 0,
        "created_at": _now(),
        "finished_at": None,
    }


def run_ingestion(job_id: str, uploads: list[tuple[str, bytes]]) -> None:
    """Run slow parsing/indexing after the HTTP response has been returned."""
    with _jobs_lock:
        jobs[job_id]["status"] = "processing"
    try:
        result = ragger.ingest_many(uploads, UPLOAD_DIRECTORY)
        with _jobs_lock:
            job = jobs[job_id]
            job["files"] = result["files"]
            job["total_chunks"] = result["total_chunks"]
            job["progress"] = 100
            job["status"] = result["status"]
            job["finished_at"] = _now()
    except Exception as exc:  # Keep a failed background task observable to callers.
        with _jobs_lock:
            job = jobs[job_id]
            job["status"] = "failed"
            job["error"] = str(exc)
            job["finished_at"] = _now()


@app.get("/upload", response_class=HTMLResponse)
async def upload_page() -> str:
    """Serve a small, no-build upload page for first-time users."""
    return """<!doctype html><title>PDF upload</title><h1>PDF 업로드</h1>
<form action='/ingest' method='post' enctype='multipart/form-data'>
<input type='file' name='files' accept='application/pdf,.pdf' multiple required>
<button type='submit'>적재 시작</button></form>"""


@app.get("/", response_class=HTMLResponse)
async def chat_page() -> FileResponse:
    """Serve the beginner-friendly chat UI."""
    return FileResponse("templates/chat.html", media_type="text/html")


@app.post("/ingest", status_code=202)
async def ingest(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
) -> dict[str, str]:
    """Accept up to three PDFs and queue their ingestion immediately."""
    if not files or len(files) > 3:
        raise HTTPException(status_code=422, detail="Upload between 1 and 3 PDF files.")

    uploads: list[tuple[str, bytes]] = []
    for file in files:
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=415, detail="Only PDF files are supported.")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=422, detail=f"{filename} is empty.")
        uploads.append((filename, content))

    job_id = str(uuid4())
    with _jobs_lock:
        jobs[job_id] = _new_job(job_id)
    background_tasks.add_task(run_ingestion, job_id, uploads)
    return {"job_id": job_id}


@app.get("/ingest/{job_id}")
async def get_ingestion_job(job_id: str) -> dict[str, Any]:
    """Return the current in-memory state for an ingestion job."""
    with _jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Ingestion job not found.")
        # Background ingestion mutates nested file records, so hand callers a snapshot.
        return deepcopy(job)


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:
    """Answer a non-empty question using the three closest document chunks."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    answer, sources = _answer_for_question(question)
    return {"answer": answer, "sources": sources}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Return an SSE answer followed by its provenance and a completion event."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question must not be empty.")

    return _streaming_answer(question)


@app.get("/chat/stream")
async def chat_stream_events(question: str = Query(...)) -> StreamingResponse:
    """GET variant for the browser's native EventSource client."""
    clean_question = question.strip()
    if not clean_question:
        raise HTTPException(status_code=422, detail="Question must not be empty.")
    return _streaming_answer(clean_question)


def _streaming_answer(question: str) -> StreamingResponse:
    def events() -> Any:
        answer, sources = _answer_for_question(question)
        yield f"event: answer\ndata: {json.dumps({'text': answer}, ensure_ascii=False)}\n\n"
        yield f"event: sources\ndata: {json.dumps(sources, ensure_ascii=False)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
