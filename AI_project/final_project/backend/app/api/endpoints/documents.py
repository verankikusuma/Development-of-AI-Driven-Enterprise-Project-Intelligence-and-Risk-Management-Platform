from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.api.deps import get_current_user
from utils.app_store import delete_document, get_document, list_documents, save_document
from utils.document_intelligence import process_document, DocumentValidationError
from utils.roles import get_role_config

router = APIRouter()


@router.get("")
def list_my_documents(user=Depends(get_current_user)):
    docs = list_documents(user["id"])
    for d in docs:
        d.pop("extracted_text", None)
    return {"documents": docs}


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    project_id: Optional[str] = Form(default=None),
    user=Depends(get_current_user),
):
    if not can_upload(user):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents")
    results = []
    for f in files:
        data = await f.read()
        try:
            parsed = process_document(f.filename, data)
        except DocumentValidationError as e:
            results.append({"filename": f.filename, "error": str(e)})
            continue
        saved = save_document(
            user_id=user["id"],
            filename=f.filename,
            content=data,
            extracted_text=parsed.get("indexed_text") or "",
            metadata={
                "parse_notes": parsed.get("parse_notes"),
                "ocr_used": parsed.get("ocr_used"),
                "tables": parsed.get("tables", [])[:20],
                "visuals": parsed.get("visuals", [])[:20],
                "extension": parsed.get("extension"),
            },
            project_id=project_id,
            mime=parsed.get("mime") or (f.content_type or ""),
        )
        results.append({"filename": f.filename, "document": {k: v for k, v in saved.items() if k != "extracted_text"}})
    return {"results": results}


@router.get("/{doc_id}")
def get_my_document(doc_id: str, user=Depends(get_current_user)):
    doc = get_document(user["id"], doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def remove_document(doc_id: str, user=Depends(get_current_user)):
    if not get_role_config(user["job_role"]).get("can_delete_docs"):
        raise HTTPException(status_code=403, detail="Your role cannot delete documents")
    if not delete_document(user["id"], doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"ok": True}


def can_upload(user: dict) -> bool:
    from utils.roles import can_access_page
    return can_access_page(user["job_role"], "upload") or can_access_page(user["job_role"], "ragbot")
