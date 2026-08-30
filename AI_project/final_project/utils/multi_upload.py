"""Multi-document ingest used by IT and Non-IT upload pages."""

from __future__ import annotations

import streamlit as st

from rag_chatbot.session_store import clear_index
from utils.app_store import delete_document, documents_as_text_map, list_documents, save_document
from utils.document_intelligence import DocumentValidationError, SUPPORTED_EXTENSIONS, process_document
from utils.rbac import current_user_id
from utils.roles import get_role_config, normalize_job_role


SUPPORTED_TYPES = sorted({ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS})


def sync_session_documents(user_id: str) -> dict[str, str]:
    mapping = documents_as_text_map(user_id)
    st.session_state.documents = mapping
    st.session_state.document_records = list_documents(user_id)
    st.session_state["rag_ready"] = False
    return mapping


def render_document_library():
    user_id = current_user_id()
    if not user_id:
        return
    docs = list_documents(user_id)
    st.session_state.document_records = docs
    if not docs:
        st.info("No documents uploaded yet.")
        return
    st.write("### Uploaded documents")
    for d in docs:
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1:
            st.markdown(f"**{d['filename']}**")
            notes = (d.get("metadata") or {}).get("parse_notes") or []
            ocr = (d.get("metadata") or {}).get("ocr_used")
            extras = []
            if ocr:
                extras.append("OCR used")
            if notes:
                extras.append("; ".join(notes[:2]))
            if extras:
                st.caption(" · ".join(extras))
        with c2:
            st.caption(f"{d.get('size_bytes', 0):,} bytes · {d.get('created_at', '')}")
        with c3:
            role = normalize_job_role(st.session_state.get("job_role"))
            if get_role_config(role).get("can_delete_docs") and st.button("Delete", key=f"del_{d['id']}"):
                delete_document(user_id, d["id"])
                sync_session_documents(user_id)
                clear_index()
                st.rerun()


def ingest_uploaded_files(files) -> tuple[str, list[dict]]:
    """Validate, parse, persist, and return combined indexed text plus parse results."""
    user_id = current_user_id()
    if not user_id:
        raise RuntimeError("Not authenticated")
    combined = []
    results = []
    project_id = str(st.session_state.get("selected_project_id") or "")
    for uploaded in files:
        data = uploaded.getvalue()
        try:
            parsed = process_document(uploaded.name, data)
        except DocumentValidationError as e:
            results.append({"filename": uploaded.name, "error": str(e)})
            continue
        saved = save_document(
            user_id=user_id,
            filename=uploaded.name,
            content=data,
            extracted_text=parsed.get("indexed_text") or "",
            metadata={
                "parse_notes": parsed.get("parse_notes"),
                "ocr_used": parsed.get("ocr_used"),
                "tables": parsed.get("tables", [])[:15],
                "visuals": parsed.get("visuals", [])[:15],
                "extension": parsed.get("extension"),
            },
            project_id=project_id or None,
            mime=parsed.get("mime") or "",
        )
        results.append(
            {
                "filename": uploaded.name,
                "id": saved["id"],
                "duplicate": saved.get("duplicate"),
                "ocr_used": parsed.get("ocr_used"),
                "notes": parsed.get("parse_notes"),
                "tables": len(parsed.get("tables") or []),
                "indexed_chars": len(parsed.get("indexed_text") or ""),
            }
        )
        if parsed.get("indexed_text"):
            combined.append(f"\n\n===== {uploaded.name} =====\n{parsed['indexed_text']}")
    sync_session_documents(user_id)
    clear_index()
    st.session_state["rag_ready"] = False
    st.session_state["rag_chunk_count"] = 0
    return "\n".join(combined).strip(), results
