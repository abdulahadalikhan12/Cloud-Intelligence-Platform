"""
Vector search service: FAISS-based semantic search over city intelligence data.
Uses sentence-transformers for embedding generation.
"""

import numpy as np

from app.config import get_settings
from app.models.schemas import SemanticSearchResult

settings = get_settings()

_index = None
_embedder = None
_city_docs: list[dict] = []
_initialized = False


def _get_embedder():
    """Lazy-load the sentence transformer model."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer

            _embedder = SentenceTransformer(settings.VECTOR_MODEL_NAME)
        except ImportError:
            print("Warning: sentence-transformers not installed. Semantic search disabled.")
            return None
    return _embedder


def build_index(cities_data: list[dict]):
    """
    Build FAISS index from city intelligence summaries.
    Each city gets a text document describing its environmental profile.
    """
    global _index, _city_docs, _initialized

    embedder = _get_embedder()
    if embedder is None:
        _initialized = True
        return

    try:
        import faiss
    except ImportError:
        print("Warning: faiss-cpu not installed. Semantic search disabled.")
        _initialized = True
        return

    _city_docs = []
    texts = []

    for city in cities_data:
        doc_text = _generate_city_doc(city)
        _city_docs.append(
            {
                "city": city.get("name", "Unknown"),
                "country": city.get("country", "Unknown"),
                "lat": city.get("lat", 0),
                "lon": city.get("lon", 0),
                "text": doc_text,
            }
        )
        texts.append(doc_text)

    if not texts:
        _initialized = True
        return

    # Generate embeddings
    embeddings = embedder.encode(texts, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype="float32")

    # Build FAISS index (flat L2 for simplicity with <1000 entries)
    dim = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim on normalized vectors)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    _index.add(embeddings)

    _initialized = True
    print(f"Vector Service: Indexed {len(texts)} city documents (dim={dim})")


def _generate_city_doc(city: dict) -> str:
    """Generate a descriptive text document for a city."""
    name = city.get("name", "Unknown")
    country = city.get("country", "Unknown")
    continent = city.get("continent", "Unknown")
    pop = city.get("population", 0)
    lat = city.get("lat", 0)

    # Climate zone estimation based on latitude
    abs_lat = abs(lat)
    if abs_lat < 10:
        climate = "tropical equatorial climate with high humidity and rainfall year-round"
    elif abs_lat < 23.5:
        climate = "tropical climate with warm temperatures and distinct wet/dry seasons"
    elif abs_lat < 35:
        climate = "subtropical climate with hot summers and mild winters"
    elif abs_lat < 50:
        climate = "temperate climate with moderate temperatures and four distinct seasons"
    elif abs_lat < 60:
        climate = "continental climate with cold winters and warm summers"
    else:
        climate = "subarctic or polar climate with long cold winters"

    pop_desc = ""
    if pop:
        if pop > 10_000_000:
            pop_desc = "megacity with very high population density"
        elif pop > 5_000_000:
            pop_desc = "major metropolitan area"
        elif pop > 1_000_000:
            pop_desc = "large city"
        else:
            pop_desc = "medium-sized city"

    return (
        f"{name} is a {pop_desc} in {country}, {continent}. "
        f"It has a {climate}. "
        f"Located at latitude {lat:.1f}, longitude {city.get('lon', 0):.1f}."
    )


def semantic_search(query: str, top_k: int = 5) -> list[SemanticSearchResult]:
    """Search for cities matching a natural language query."""
    if _index is None or not _city_docs:
        return []

    embedder = _get_embedder()
    if embedder is None:
        return []

    import faiss as faiss_lib

    # Encode query
    query_vec = embedder.encode([query])
    query_vec = np.array(query_vec, dtype="float32")
    faiss_lib.normalize_L2(query_vec)

    # Search
    k = min(top_k, len(_city_docs))
    scores, indices = _index.search(query_vec, k)

    results = []
    for i in range(k):
        idx = indices[0][i]
        if idx < 0 or idx >= len(_city_docs):
            continue
        doc = _city_docs[idx]
        results.append(
            SemanticSearchResult(
                city=doc["city"],
                country=doc["country"],
                lat=doc["lat"],
                lon=doc["lon"],
                score=round(float(scores[0][i]), 4),
                summary=doc["text"],
            )
        )

    return results


def get_index_size() -> int:
    """Return number of indexed documents."""
    return len(_city_docs) if _city_docs else 0
