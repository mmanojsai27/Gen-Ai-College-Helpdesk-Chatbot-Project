
from pathlib import Path
import re

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------
# File path and embedding model
# --------------------------------

DATA_FILE = Path(__file__).parent / "data" / "college_info.txt"

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# Load college information
# --------------------------------

def load_college_data():
    """Read college information from the text file."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"College information file not found: {DATA_FILE}"
        )

    return DATA_FILE.read_text(encoding="utf-8")


# --------------------------------
# Extract source title
# --------------------------------

def get_source_title(section):
    """Extract a useful title from a college information section."""

    lines = section.strip().splitlines()

    for line in lines:
        line = line.strip()

        # Match headings such as '2. ADMISSIONS'
        match = re.match(r"^(\d+)\.\s*(.+)$", line)

        if match:
            return f"{match.group(1)}. {match.group(2).strip()}"

    # Handle the document's main heading.
    if "COLLEGE INFORMATION" in section.upper():
        return "College Overview"

    return "College Information"


# --------------------------------
# Split information into chunks
# --------------------------------

def split_into_chunks(text, chunk_size=120, overlap=30):
    """Split college information into chunks with source titles."""

    # Split before numbered headings such as '1. GENERAL INFORMATION'
    sections = re.split(
        r"(?m)(?=^\d+\.\s+)",
        text.strip(),
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        source = get_source_title(section)
        words = section.split()

        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end]).strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "source": source,
                })

            if end >= len(words):
                break

            start += chunk_size - overlap

    return chunks


# --------------------------------
# Create FAISS search index
# --------------------------------

def create_search_index(chunks):
    """Create normalized embeddings and a FAISS index."""

    if not chunks:
        raise ValueError(
            "No text chunks found in the college information file."
        )

    texts = [
        chunk["text"] if isinstance(chunk, dict) else chunk
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index


# --------------------------------
# Search relevant college information
# --------------------------------

def search_college_info(question, chunks, index, top_k=3):
    """Return matching text, source title, and similarity score."""

    if not isinstance(question, str) or not question.strip():
        return []

    if not chunks:
        return []

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32",
    )

    k = min(top_k, len(chunks))
    scores, indices = index.search(question_embedding, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        chunk = chunks[int(idx)]

        if isinstance(chunk, dict):
            chunk_text = chunk["text"]
            source = chunk.get("source", "College Information")
        else:
            chunk_text = chunk
            source = get_source_title(chunk_text)

        results.append({
            "text": chunk_text,
            "source": source,
            "score": float(score),
        })

    return results


# --------------------------------
# Test RAG independently
# --------------------------------

if __name__ == "__main__":
    print("Loading college information...")

    college_text = load_college_data()
    chunks = split_into_chunks(college_text)
    index = create_search_index(chunks)

    print(f"\nCreated {len(chunks)} text chunks.")
    print("RAG retrieval system is ready!")

    while True:
        question = input(
            "\nAsk a college question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        results = search_college_info(
            question,
            chunks,
            index,
            top_k=3,
        )

        print("\nRelevant information:")

        for result in results:
            print(f"\nSource: {result['source']}")
            print(f"Similarity score: {result['score']:.3f}")
            print(result["text"])
