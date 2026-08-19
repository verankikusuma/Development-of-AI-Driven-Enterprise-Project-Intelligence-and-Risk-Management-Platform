# RAG Chatbot Module — AI Project Intelligence & Risk Advisor

Implements the architecture:

```
Documents -> Text Extraction -> Chunking -> Embeddings -> Vector Database
-> Retriever -> Relevant Project Information -> LLM -> Answer
```

Stack (chosen so this runs identically on any machine — nothing local, nothing paid):

| Component | Choice | Why |
|---|---|---|
| LLM | Gemini Flash (`gemini-2.5-flash`) | Free tier, no credit card, cloud API |
| Embeddings | Gemini `text-embedding-004` | Same key as the LLM, generous free quota |
| Vector DB | Qdrant Cloud (free tier) | Free forever, no credit card, cloud-hosted |

## Setup

1. **Get a Gemini API key** — free, no card required: https://aistudio.google.com/apikey
2. **Get a free Qdrant Cloud cluster**: https://cloud.qdrant.io — create a free-tier cluster, grab its URL and an API key.
3. Install dependencies:
   ```bash
   pip install google-genai qdrant-client pypdf python-docx python-dotenv streamlit
   ```
4. Create a `.env` file in your project root:
   ```
   GEMINI_API_KEY=your-gemini-key
   QDRANT_URL=https://your-cluster-url.cloud.qdrant.io
   QDRANT_API_KEY=your-qdrant-key
   ```
5. Place this `rag_chatbot/` folder inside your existing project (next to your other modules).

## Usage

```python
from rag_chatbot import ingest_project_documents, ask

# Run once whenever project documents are added/updated
ingest_project_documents("/path/to/project/documents")

# Run per user question
result = ask("What's driving the schedule risk on this project?")
print(result["answer"])
print(result["sources"])
```

For Streamlit, see `streamlit_snippet.py` — it's a drop-in tab you add
alongside your existing risk dashboard, not a separate app.

## Notes / caveats

- **Free Qdrant clusters auto-suspend after 1 week of inactivity** and
  get deleted after 4 weeks. Fine for active development; if this sits
  untouched (e.g. before a demo or interview), reactivate the cluster
  from the Qdrant console first.
- **Free-tier Gemini usage may be used by Google to improve their
  models** (per their terms) — don't ingest sensitive/confidential
  project data into the free tier if that's a concern for your use case.
- Re-running `ingest_project_documents` on the same files overwrites
  their old chunks (IDs are derived from filename + chunk index), so
  it's safe to re-ingest after document updates.
- If your project already has a document text-extraction step upstream
  (for the risk model), swap `ingestion.py` for that instead of
  duplicating parsing logic.
