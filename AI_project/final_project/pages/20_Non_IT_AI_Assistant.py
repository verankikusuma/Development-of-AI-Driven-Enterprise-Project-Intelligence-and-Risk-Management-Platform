import streamlit as st
from utils.ui import inject_css, page_header
from utils.api_client import backend_health, api_query_rag

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "Non-IT RAGBot - Business AI Assistant",
    "Ask strategic questions about your business project documents via backend API endpoints."
)

project = st.session_state.get("selected_project", {})
project_name = project.get("name", "Your Business Project") if project else "Your Business Project"
rag_ready = st.session_state.get("rag_ready", False)
documents = st.session_state.get("documents", {})
api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")

if not project and not documents:
    st.warning("No active Non-IT project found. Please upload a business document first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Go to Non-IT Document Upload")
    st.stop()

# ============================================================
# STATUS BAR & KNOWLEDGE BASE BUILDER
# ============================================================

col_info, col_status = st.columns([2.5, 1])

with col_info:
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 0.75rem 1.2rem; display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.2rem;"></span>        <div>
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Active Business Context</div>
            <div style="color: #ffffff; font-weight: 800; font-size: 1.05rem;">{project_name}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    if rag_ready:
        chunk_count = st.session_state.get("rag_chunk_count", 0)
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 0.75rem 1rem; text-align: center;">
            <div style="color: #34d399; font-weight: 800; font-size: 0.95rem;">Knowledge Base Ready</div>            <div style="color: #cbd5e1; font-size: 0.8rem;">{chunk_count} Chunks Indexed</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 0.75rem 1rem; text-align: center;">
            <div style="color: #fbbf24; font-weight: 800; font-size: 0.95rem;">Index Pending</div>            <div style="color: #cbd5e1; font-size: 0.8rem;">Click Build Below</div>
        </div>
        """, unsafe_allow_html=True)

if documents and not rag_ready:
    from rag_chatbot.session_store import build_index, clear_index
    with st.spinner("Building AI vector knowledge base index from uploaded dossier..."):
        try:
            clear_index()
            num_chunks = build_index(documents)
            st.session_state["rag_ready"] = True
            st.session_state["rag_chunk_count"] = num_chunks
            st.rerun()
        except Exception as e:
            st.error(f"Failed to build knowledge base: {e}")
            st.stop()

if not rag_ready:
    st.warning("Please upload and process a business document to activate RAGBot.")
    st.stop()

st.divider()

# ============================================================
# CHAT SESSION & STARTERS
# ============================================================

if "non_it_chat_history" not in st.session_state:
    st.session_state.non_it_chat_history = []

c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.subheader("Executive AI Advisor Conversation")
with c_head2:
    if st.session_state.non_it_chat_history:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.non_it_chat_history = []
            st.rerun()

if not st.session_state.non_it_chat_history:
    st.markdown("**Suggested Business Starter Queries:**")
    starters = [
        "What are the main operational risks?",
        "Summarize project scope and key deliverables.",
        "What is the budget allocation and overrun risk?",
        "What resource or vendor constraints exist?",
        "Provide an executive briefing for leadership."
    ]
    cols = st.columns(len(starters))
    for col, starter in zip(cols, starters):
        with col:
            if st.button(starter, use_container_width=True, key=f"nonit_start_{starter[:15]}"):
                st.session_state.non_it_chat_history.append({"role": "user", "content": starter})
                st.rerun()

# ============================================================
# RENDER CHAT HISTORY
# ============================================================

for message in st.session_state.non_it_chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.3rem;">📊</span>
                    <span style="color: #fbbf24; font-weight: 800; font-size: 0.98rem;">Business AI Advisor Answer</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(message["content"])
            
            if message.get("sources"):
                with st.expander("Referenced Document Sources & Context Snippets", expanded=False):
                    for src in message["sources"]:
                        st.caption(f"• Document: `{src}`")
                    if message.get("snippets"):
                        st.markdown("**Grounding Context Excerpts:**")
                        for snip in message["snippets"]:
                            st.caption(f"> *\"{snip[:220]}...\"*")

# ============================================================
# CHAT INPUT & API EXECUTION
# ============================================================

question = st.chat_input("Ask a strategic business question about your project...")

pending = None
if st.session_state.non_it_chat_history and st.session_state.non_it_chat_history[-1]["role"] == "user":
    pending = st.session_state.non_it_chat_history[-1]["content"]

active_question = question or pending

if question:
    st.session_state.non_it_chat_history.append({"role": "user", "content": question})
    st.rerun()

if active_question and st.session_state.non_it_chat_history[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Analyzing project knowledge base & query context..."):
            try:
                from rag_chatbot.session_store import retrieve
                history_context = st.session_state.non_it_chat_history[:-1] if len(st.session_state.non_it_chat_history) > 1 else []
                chunks = retrieve(active_question, history=history_context)
                snippets = [c["text"] for c in chunks[:3]] if chunks else []

                api_res = None
                if backend_health(api_base):
                    api_res = api_query_rag(active_question, chunks, chat_history=history_context, base_url=api_base)
                    
                if api_res and "answer" in api_res:
                    answer = api_res["answer"]
                    sources = api_res.get("sources", [])
                else:
                    from rag_chatbot.chatbot import answer_with_context
                    result = answer_with_context(active_question, chunks, history=history_context)
                    answer = result.get("answer", "I could not generate an answer.")
                    sources = result.get("sources", [])
            except Exception as e:
                answer = f"Error generating answer: {e}"
                sources = []
                snippets = []

        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.6rem;">
                <span style="font-size: 1.3rem;">📊</span>
                <span style="color: #fbbf24; font-weight: 800; font-size: 0.98rem;">Business AI Advisor Answer</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(answer)
        
        if sources:
            with st.expander("Referenced Document Sources & Context Snippets", expanded=False):
                for src in sources:
                    st.caption(f"• Document: `{src}`")
                if snippets:
                    st.markdown("**Grounding Context Excerpts:**")
                    for snip in snippets:
                        st.caption(f"> *\"{snip[:220]}...\"*")

    st.session_state.non_it_chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "snippets": snippets,
    })
    st.rerun()

