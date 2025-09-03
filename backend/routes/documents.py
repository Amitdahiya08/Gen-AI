import os, uuid
from fastapi import APIRouter, UploadFile, HTTPException
from backend.agents.parser_agent import ParserAgent
from backend.agents.summarizer_agent import SummarizerAgent
from backend.agents.entity_agent import EntityAgent
from backend.agents.validation_agent import ValidationAgent
from backend.utils.exceptions import UnsupportedFileFormatError

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

documents_store = {}  # in-memory (later Postgres)

@router.post("/upload")
async def upload_document(file: UploadFile):
    if not file.filename.endswith((".pdf", ".docx", ".html")):
        raise UnsupportedFileFormatError("Unsupported file format")

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Agents
    parser = ParserAgent()
    summarizer = SummarizerAgent()
    entity_agent = EntityAgent()
    validator = ValidationAgent()

    # Parse
    text = parser.parse(file_path)

    # Summarize
    summary = summarizer.summarize_document(text)
    if not validator.validate_summary(summary):
        summary = validator.rollback_summary()

    # Entities
    entities = entity_agent.extract(text)
    if not validator.validate_entities(entities):
        entities = {"error": validator.rollback_entities()}

    documents_store[doc_id] = {
        "filename": file.filename,
        "text": text,
        "summary": summary,
        "entities": entities,
    }

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "summary": summary,
        "entities": entities,
    }
