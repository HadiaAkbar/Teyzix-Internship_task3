def search_chunks(chunks: list, query: str, top_k: int = 5) -> list:
    """Simple keyword-based search — works fully offline, no external embeddings API
    required. Returns list of (index, text, score)."""
    if not chunks:
        return []

    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    results = []
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        chunk_words = set(chunk_lower.split())
        
        # Calculate overlap score
        overlap = len(query_words & chunk_words)
        if overlap > 0:
            score = overlap / len(query_words)
            results.append((i, chunk, float(score)))
    
    ranked = sorted(results, key=lambda x: x[2], reverse=True)
    return ranked[:top_k]
