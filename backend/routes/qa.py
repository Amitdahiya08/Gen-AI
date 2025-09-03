from fastapi import APIRouter, Query, HTTPException
from backend.routes.documents import documents_store
from backend.agents.qa_agent import QAAgent

router = APIRouter()

@router.get("/")
async def ask_question(doc_id: str, question: str = Query(...)):
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")

    qa_agent = QAAgent()
    doc_text = documents_store[doc_id]["text"]
    answer = qa_agent.ask(question, doc_text)
    return {"doc_id": doc_id, "question": question, "answer": answer}
