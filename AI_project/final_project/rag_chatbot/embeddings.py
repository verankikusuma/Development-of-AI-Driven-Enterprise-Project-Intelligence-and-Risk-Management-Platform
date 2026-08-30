import time

from google import genai
from google.genai import types

from . import config

_client = None

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2  


def _get_client():
    global _client
    if _client is None:
        config.validate_config()
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _embed_batch_with_retry(client, batch, task_type):
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            result = client.models.embed_content(
                model=config.GEMINI_EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=config.EMBEDDING_DIM,
                ),
            )
            return [e.values for e in result.embeddings]
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF_SECONDS * (2 ** attempt))
    raise last_error


def embed_texts(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
    batch_size: int = 100,
    progress_callback=None,
) -> list[list[float]]:
    
    if not texts:
        return []
    client = _get_client()
    all_vectors = []
    total = len(texts)
    for i in range(0, total, batch_size):
        batch = texts[i:i + batch_size]
        all_vectors.extend(_embed_batch_with_retry(client, batch, task_type))
        if progress_callback:
            progress_callback(min(i + batch_size, total), total)
    return all_vectors


def embed_query(query: str) -> list[float]:
    return embed_texts([query], task_type="RETRIEVAL_QUERY")[0]