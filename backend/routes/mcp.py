from fastapi import APIRouter, HTTPException
from backend.utils.helpers import mcp_file_save
from backend.routes.documents import documents_store

router = APIRouter()

@router.post("/file/save/{doc_id}")
async def save_document(doc_id: str):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    content = documents_store[doc_id]["text"]
    resp = mcp_file_save(doc_id, content)
    return resp

@router.get("/search")
async def search_docs(query: str):
    """Stub search: just checks if query is in any doc text."""
    results = []
    for doc_id, doc in documents_store.items():
        if query.lower() in doc["text"].lower():
            results.append({"doc_id": doc_id, "filename": doc["filename"]})
    return {"query": query, "results": results}
