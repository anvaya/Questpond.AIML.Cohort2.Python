import numpy as np
from pyodbc import Connection

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Convert inputs to float arrays if they are strings or other non-numeric types
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    
    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    return float(dot_product / (norm_a * norm_b))

def vector_search(query_text, vector_index, embed_fn):
    query_embedding = embed_fn(query_text)

    best_match = None
    best_score = 0.0

    for entry in vector_index:
        score = cosine_similarity(query_embedding, entry.embedding)

        if score > best_score:
            best_score = score
            best_match = entry

    return best_match, best_score