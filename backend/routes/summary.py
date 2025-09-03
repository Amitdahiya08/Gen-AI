from fastapi import APIRouter, HTTPException, Body
from backend.routes.documents import documents_store

router = APIRouter()

@router.get("/{doc_id}")
async def get_summary(doc_id: str):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": doc_id, "summary": documents_store[doc_id]["summary"]}

@router.post("/{doc_id}/update")
async def update_summary(doc_id: str, updated_summary: str = Body(..., embed=True)):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    documents_store[doc_id]["summary"] = updated_summary
    return {"doc_id": doc_id, "summary": updated_summary, "status": "updated"}
