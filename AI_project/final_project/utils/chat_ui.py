"""Shared persistent chat UI for the grounded RAG assistant."""

from __future__ import annotations

import streamlit as st

from utils.api_client import api_query_rag, backend_health
from utils.app_store import (
    add_message,
    create_conversation,
    delete_conversation,
    list_conversations,
    list_messages,
)
from utils.rbac import current_job_role, current_user_id
from utils.roles import get_role_config
from rag_chatbot.session_store import retrieve


def render_chat_workspace(audience: str = "IT"):
    user_id = current_user_id()
    if not user_id:
        st.error("Session is missing a user id. Please log in again.")
        st.stop()

    role = current_job_role()
    project = st.session_state.get("selected_project") or {}
    prediction = st.session_state.get("prediction_detail")
    if not isinstance(prediction, dict):
        prediction = None
        if project:
            prediction = {
                "risk_level": project.get("risk_level"),
                "risk_score": project.get("risk_score"),
                "confidence": project.get("confidence"),
                "probabilities": project.get("probabilities"),
                "contributing_factors": project.get("contributing_factors"),
                "predicted_class": project.get("risk_level"),
            }
    api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
    can_delete = bool(get_role_config(role).get("can_delete_chats"))

    if "active_conversation_id" not in st.session_state:
        convos = list_conversations(user_id)
        if convos:
            st.session_state.active_conversation_id = convos[0]["id"]
        else:
            created = create_conversation(user_id, "New chat")
            st.session_state.active_conversation_id = created["id"]

    convos = list_conversations(user_id)
    titles = {c["id"]: c["title"] for c in convos}
    ids = [c["id"] for c in convos]

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        selected = st.selectbox(
            "Chat history",
            options=ids,
            format_func=lambda i: titles.get(i, i),
            index=ids.index(st.session_state.active_conversation_id) if st.session_state.active_conversation_id in ids else 0,
        )
        if selected != st.session_state.active_conversation_id:
            st.session_state.active_conversation_id = selected
            st.rerun()
    with c2:
        if st.button("New chat", use_container_width=True):
            created = create_conversation(user_id, "New chat")
            st.session_state.active_conversation_id = created["id"]
            st.rerun()
    with c3:
        if can_delete and st.button("Delete chat", use_container_width=True):
            delete_conversation(user_id, st.session_state.active_conversation_id)
            st.session_state.pop("active_conversation_id", None)
            st.rerun()

    cid = st.session_state.active_conversation_id
    history = list_messages(user_id, cid)

    for message in history:
        with st.chat_message(message["role"] if message["role"] in ("user", "assistant") else "assistant"):
            st.markdown(message["content"])
            details = message.get("sources") or []
            if details:
                with st.expander("Sources", expanded=False):
                    for src in details:
                        if isinstance(src, dict):
                            st.caption(f"• {src.get('type', 'document').replace('_', ' ').title()}: {src.get('label', src)}")
                        else:
                            st.caption(f"• {src}")

    pending = None
    if history and history[-1]["role"] == "user":
        # If last user message has no following assistant, generate
        pending = history[-1]["content"]

    question = st.chat_input("Ask about this project, uploaded documents, or the ML risk forecast...")
    if question:
        add_message(user_id, cid, "user", question, [])
        st.rerun()

    if pending and (len(history) == 1 or history[-1]["role"] == "user"):
        # avoid double-answer: only generate when last is user
        if history[-1]["role"] == "user":
            _generate_reply(user_id, cid, pending, history[:-1], role, project, prediction, api_base, audience)


def _generate_reply(user_id, cid, question, history_context, role, project, prediction, api_base, audience):
    with st.chat_message("assistant"):
        with st.spinner("Retrieving from your documents and project knowledge..."):
            try:
                chunks = retrieve(question, top_k=8, history=history_context, role=role)
                api_res = None
                if backend_health(api_base):
                    api_res = api_query_rag(
                        question,
                        chunks,
                        chat_history=history_context,
                        base_url=api_base,
                        project=project,
                        prediction=prediction,
                    )
                if api_res and "answer" in api_res:
                    result = api_res
                else:
                    from rag_chatbot.chatbot import answer_with_context
                    result = answer_with_context(
                        question,
                        chunks,
                        history=history_context,
                        project=project,
                        prediction=prediction,
                    )
                answer = result.get("answer", "I couldn't find this information in the available project knowledge.")
                source_details = result.get("source_details") or [
                    {"type": "document", "label": s, "filename": s} for s in result.get("sources", [])
                ]
            except Exception as e:
                answer = f"I couldn't complete this answer from the available project knowledge. ({e})"
                source_details = []

        st.markdown(answer)
        if source_details:
            with st.expander("Sources", expanded=True):
                for src in source_details:
                    if isinstance(src, dict):
                        st.caption(f"• {src.get('type', 'document').replace('_', ' ').title()}: {src.get('label', src)}")
                    else:
                        st.caption(f"• {src}")

    add_message(user_id, cid, "assistant", answer, source_details)
    st.rerun()
