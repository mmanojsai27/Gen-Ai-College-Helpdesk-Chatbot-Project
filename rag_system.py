
import re
from pathlib import Path

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# --------------------------------
# File paths and embedding model
# --------------------------------

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "college_info.txt"

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# Load TXT and PDF college information
# --------------------------------

def load_college_data():
    """Load college information from TXT and PDF files."""

    documents = []

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Load TXT knowledge base
    if DATA_FILE.exists():

        text = DATA_FILE.read_text(
            encoding="utf-8"
        )

        if text.strip():
            documents.append(text)

    # Load all PDFs in the data directory
    pdf_files = sorted(
        DATA_DIR.glob("*.pdf")
    )

    for pdf_file in pdf_files:

        try:

            reader = PdfReader(
                str(pdf_file)
            )

            for page_number, page in enumerate(
                reader.pages,
                start=1,
            ):

                page_text = page.extract_text() or ""

                if page_text.strip():

                    documents.append(
                        f"[[PDF_SOURCE: {pdf_file.name} | PAGE: {page_number}]]\n"
                        f"{page_text}"
                    )

        except Exception as error:

            print(
                f"Could not read {pdf_file.name}: "
                f"{type(error).__name__}: {error}"
            )

    if not documents:

        raise FileNotFoundError(
            "No readable college information found. "
            "Add college_info.txt or PDF files to the data folder."
        )

    return "\n\n".join(documents)


# --------------------------------
# Extract source title
# --------------------------------

def get_source_title(section):
    """Get a readable title for a knowledge-base section."""

    lines = section.strip().splitlines()

    for line in lines:

        line = line.strip()

        match = re.match(
            r"^(\d+)\.\s+(.+)$",
            line,
        )

        if match:

            return (
                f"{match.group(1)}. "
                f"{match.group(2).strip()}"
            )

    if "COLLEGE INFORMATION" in section.upper():
        return "College Overview"

    return "College Information"


# --------------------------------
# Split information into chunks
# --------------------------------

def split_into_chunks(
    text,
    chunk_size=180,
    overlap=40,
):
    """
    Create overlapping chunks while preserving source metadata.

    TXT:
        Split using numbered headings.

    PDF:
        Preserve PDF filename and page number.
    """

    if not isinstance(text, str) or not text.strip():
        return []

    if chunk_size <= 0:

        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if overlap < 0 or overlap >= chunk_size:

        raise ValueError(
            "overlap must be zero or greater and smaller than chunk_size."
        )

    chunks = []

    document_blocks = []

    current_lines = []
    current_pdf_source = None
    current_page = None

    pdf_marker = re.compile(
        r"^\[\[PDF_SOURCE:\s*(.*?)\s*\|\s*PAGE:\s*(\d+)\]\]$"
    )

    # --------------------------------
    # Separate TXT and PDF page blocks
    # --------------------------------

    for line in text.splitlines():

        marker = pdf_marker.match(
            line.strip()
        )

        if marker:

            if current_lines:

                document_blocks.append({
                    "text": "\n".join(
                        current_lines
                    ).strip(),

                    "source": current_pdf_source,
                    "page": current_page,
                })

            current_pdf_source = marker.group(1).strip()

            current_page = int(
                marker.group(2)
            )

            current_lines = []

        else:

            current_lines.append(line)

    # Save final document block
    if current_lines:

        document_blocks.append({
            "text": "\n".join(
                current_lines
            ).strip(),

            "source": current_pdf_source,
            "page": current_page,
        })

    # --------------------------------
    # Process document blocks
    # --------------------------------

    for block in document_blocks:

        block_text = block["text"]

        if not block_text:
            continue

        if block["source"]:

            # Keep every PDF page separate
            sections = [block_text]

            source_titles = [
                block["source"]
            ]

        else:

            # Split TXT using numbered headings
            sections = re.split(
                r"(?m)(?=^\s*\d+\.\s+)",
                block_text.strip(),
            )

            sections = [
                section.strip()
                for section in sections
                if section.strip()
            ]

            source_titles = [
                get_source_title(section)
                for section in sections
            ]

        # --------------------------------
        # Create overlapping chunks
        # --------------------------------

        for section, source in zip(
            sections,
            source_titles,
        ):

            # Remove standalone numbered lines
            section = re.sub(
                r"(?m)^\s*\d+\s*$",
                "",
                section,
            ).strip()

            words = section.split()

            start = 0

            while start < len(words):

                end = min(
                    start + chunk_size,
                    len(words),
                )

                chunk_text = " ".join(
                    words[start:end]
                ).strip()

                # Ignore empty or number-only chunks
                if (
                    chunk_text
                    and not re.fullmatch(
                        r"[\d\s.]+",
                        chunk_text,
                    )
                ):

                    chunk = {
                        "text": chunk_text,
                        "source": source,
                    }

                    # Preserve PDF page number
                    if block["page"] is not None:

                        chunk["page"] = block["page"]

                    chunks.append(chunk)

                if end >= len(words):
                    break

                start += chunk_size - overlap

    return chunks


# --------------------------------
# Create FAISS search index
# --------------------------------

def create_search_index(chunks):
    """Create normalized embeddings and FAISS similarity index."""

    if not chunks:

        raise ValueError(
            "No text chunks found in the college information."
        )

    texts = [
        chunk["text"]
        if isinstance(chunk, dict)
        else str(chunk)

        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32",
    )

    index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    index.add(embeddings)

    return index


# --------------------------------
# Department-specific relevance
# --------------------------------

DEPARTMENT_ALIASES = {

    "CSE": [
        "cse",
        "computer science and engineering",
        "computer science",
    ],

    "IT": [
        "it",
        "information technology",
    ],

    "ECE": [
        "ece",
        "electronics and communication engineering",
    ],

    "EEE": [
        "eee",
        "electrical and electronics engineering",
    ],

    "ME": [
        "me",
        "mechanical engineering",
    ],

    "CE": [
        "ce",
        "civil engineering",
    ],
}


# --------------------------------
# Identify requested department
# --------------------------------

def get_requested_department(question):
    """Identify a department explicitly mentioned in a question."""

    question_lower = question.lower()

    for code, aliases in DEPARTMENT_ALIASES.items():

        for alias in aliases:

            if alias in {
                "cse",
                "it",
                "ece",
                "eee",
                "me",
                "ce",
            }:

                pattern = (
                    r"(?<!\w)"
                    + re.escape(alias)
                    + r"(?!\w)"
                )

                if re.search(
                    pattern,
                    question_lower,
                ):

                    return code

            elif alias in question_lower:

                return code

    return None


# --------------------------------
# Department fee protection
# --------------------------------

def is_department_supported(
    question,
    chunk_text,
):
    """
    Prevent one department's fee from answering
    another department's fee question.
    """

    question_lower = question.lower()

    fee_keywords = [
        "fee",
        "fees",
        "tuition",
        "cost",
        "charges",
    ]

    is_fee_question = any(
        keyword in question_lower
        for keyword in fee_keywords
    )

    if not is_fee_question:
        return True

    requested_department = get_requested_department(
        question
    )

    if not requested_department:
        return True

    chunk_lower = chunk_text.lower()

    aliases = DEPARTMENT_ALIASES[
        requested_department
    ]

    for alias in aliases:

        if alias in {
            "cse",
            "it",
            "ece",
            "eee",
            "me",
            "ce",
        }:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                chunk_lower,
            ):

                return True

        elif alias in chunk_lower:

            return True

    return False


# --------------------------------
# Query intent detection
# --------------------------------

def is_location_question(question):
    """Identify questions asking for the college location."""

    question_lower = question.lower()

    location_terms = [
        "location",
        "located",
        "where is",
        "where's",
        "college address",
        "in which city",
    ]

    return any(
        term in question_lower
        for term in location_terms
    )


def is_hostel_question(question):
    """Identify questions related to hostel facilities."""

    question_lower = question.lower()

    hostel_terms = [
        "hostel",
        "accommodation",
        "mess fee",
        "mess charges",
    ]

    return any(
        term in question_lower
        for term in hostel_terms
    )


# --------------------------------
# Search college information
# --------------------------------

def search_college_info(
    question,
    chunks,
    index,
    top_k=3,
):
    """
    Search using the original question and intent-based queries.

    Returns:
        text
        source
        page (for PDFs)
        score
        direct_match
    """

    if (
        not isinstance(question, str)
        or not question.strip()
    ):

        return []

    if (
        not chunks
        or top_k <= 0
        or index is None
    ):

        return []

    search_queries = [
        question
    ]

    location_question = is_location_question(
        question
    )

    hostel_question = is_hostel_question(
        question
    )

    # --------------------------------
    # Add expanded search queries
    # --------------------------------

    if location_question:

        search_queries.append(
            "College location address where the college is "
            "located city state country"
        )

    if hostel_question:

        search_queries.append(
            "Hostel facilities hostel availability room allocation "
            "accommodation charges mess fees hostel office "
            "college administration"
        )

    # --------------------------------
    # Search using all query variations
    # --------------------------------

    candidate_scores = {}

    k = min(
        max(top_k * 5, 10),
        len(chunks),
    )

    for search_query in search_queries:

        question_embedding = model.encode(
            [search_query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        question_embedding = np.asarray(
            question_embedding,
            dtype="float32",
        )

        scores, indices = index.search(
            question_embedding,
            k,
        )

        for score, idx in zip(
            scores[0],
            indices[0],
        ):

            if idx < 0:
                continue

            idx = int(idx)

            score = float(score)

            if (
                idx not in candidate_scores
                or score > candidate_scores[idx]
            ):

                candidate_scores[idx] = score

    # --------------------------------
    # Prepare and rank results
    # --------------------------------

    results = []

    for idx, similarity_score in candidate_scores.items():

        chunk = chunks[idx]

        if isinstance(chunk, dict):

            chunk_text = chunk["text"]

        else:

            chunk_text = str(chunk)

        # Department fee protection
        if not is_department_supported(
            question,
            chunk_text,
        ):

            continue

        chunk_lower = chunk_text.lower()

        direct_match = False

        ranking_score = similarity_score

        # --------------------------------
        # Location relevance
        # --------------------------------

        if location_question:

            has_explicit_location = bool(
                re.search(
                    r"\blocation\s*:\s*\S+",
                    chunk_lower,
                )

                or re.search(
                    r"\blocated\s+in\s+\S+",
                    chunk_lower,
                )
            )

            if has_explicit_location:

                direct_match = True

                ranking_score += 0.20

        # --------------------------------
        # Hostel relevance
        # --------------------------------

        if (
            hostel_question
            and "hostel" in chunk_lower
        ):

            ranking_score += 0.10

        # --------------------------------
        # Prepare result
        # --------------------------------

        if isinstance(chunk, dict):

            result = {
                "text": chunk_text,

                "source": chunk.get(
                    "source",
                    "College Information",
                ),

                "score": similarity_score,

                "direct_match": direct_match,
            }

            if chunk.get("page") is not None:

                result["page"] = chunk["page"]

        else:

            result = {
                "text": chunk_text,

                "source": get_source_title(
                    chunk_text
                ),

                "score": similarity_score,

                "direct_match": direct_match,
            }

        results.append(
            (
                ranking_score,
                result,
            )
        )

    # --------------------------------
    # Sort by adjusted ranking score
    # --------------------------------

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        result
        for _, result in results[:top_k]
    ]


# --------------------------------
# Test RAG independently
# --------------------------------

if __name__ == "__main__":

    print(
        "Loading college information..."
    )

    college_text = load_college_data()

    chunks = split_into_chunks(
        college_text
    )

    index = create_search_index(
        chunks
    )

    print(
        f"\nCreated {len(chunks)} text chunks."
    )

    print(
        "RAG retrieval system is ready!"
    )

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

        print(
            "\nRelevant information:"
        )

        if not results:

            print(
                "No matching information found."
            )

            continue

        for result in results:

            print(
                f"\nSource: {result['source']}"
            )

            if "page" in result:

                print(
                    f"Page: {result['page']}"
                )

            print(
                f"Similarity score: "
                f"{result['score']:.3f}"
            )

            print(
                f"Direct match: "
                f"{result.get('direct_match', False)}"
            )

            print(
                result["text"]
            )
