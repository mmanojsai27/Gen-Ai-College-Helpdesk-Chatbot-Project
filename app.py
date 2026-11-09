
import re
from pathlib import Path

import streamlit as st

from rag_system import (
    load_college_data,
    split_into_chunks,
    create_search_index,
    search_college_info,
)

from ai_response import generate_answer_stream


# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="ABC Institute Helpdesk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------
# Initialize session state
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Light"


# --------------------------------
# Theme selection
# --------------------------------

with st.sidebar:

    st.markdown("## 🎓 College Helpdesk")
    st.caption("Your college information assistant")
    st.divider()

    st.markdown("### 🎨 Appearance")

    selected_theme = st.radio(
        "Choose your theme",
        options=["☀️ Light Mode", "🌙 Dark Mode"],
        index=0 if st.session_state.theme == "Light" else 1,
        key="theme_selector",
    )

    st.session_state.theme = (
        "Light"
        if selected_theme == "☀️ Light Mode"
        else "Dark"
    )


# --------------------------------
# Theme colors
# --------------------------------

if st.session_state.theme == "Dark":

    BG = "#0B1120"
    SURFACE = "#151F32"
    TEXT = "#F1F5F9"
    MUTED = "#A8B6CC"
    BORDER = "#334155"
    INPUT_BG = "#111827"
    SIDEBAR_BG = "#101A2D"
    ACCENT = "#60A5FA"
    HERO_START = "#172554"
    HERO_END = "#1D4ED8"

else:

    BG = "#F4F7FC"
    SURFACE = "#FFFFFF"
    TEXT = "#1E293B"
    MUTED = "#64748B"
    BORDER = "#DCE4EF"
    INPUT_BG = "#FFFFFF"
    SIDEBAR_BG = "#EDF3FF"
    ACCENT = "#2563EB"
    HERO_START = "#172554"
    HERO_END = "#2563EB"


# --------------------------------
# Custom CSS
# --------------------------------

st.markdown(
    f"""
    <style>
    .stApp,
    .stApp [data-testid="stAppViewContainer"] {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}

    .main .block-container {{
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background-color: {BG} !important;
    }}

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"] {{
        color: {TEXT};
    }}

    .stApp [data-testid="stCaptionContainer"] p,
    .stApp small {{
        color: {MUTED} !important;
    }}

    .hero {{
        background: linear-gradient(
            135deg,
            {HERO_START},
            {HERO_END}
        );
        padding: 30px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.16);
    }}

    .hero h1 {{
        color: #FFFFFF !important;
        font-size: 30px;
        margin: 0 0 10px 0;
    }}

    .hero p {{
        color: #E0EAFF !important;
        font-size: 16px;
        margin-bottom: 6px;
    }}

    .section-heading {{
        color: {TEXT} !important;
        font-size: 22px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }}

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {{
        background-color: {SIDEBAR_BG} !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: {TEXT} !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }}

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {{
        background-color: {BG} !important;
    }}

    [data-testid="stChatInput"] {{
        background-color: {INPUT_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] > div {{
        background-color: {INPUT_BG} !important;
        border-radius: 14px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {TEXT} !important;
        -webkit-text-fill-color: {TEXT} !important;
        background-color: {INPUT_BG} !important;
        caret-color: {ACCENT} !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {MUTED} !important;
        -webkit-text-fill-color: {MUTED} !important;
        opacity: 1 !important;
    }}

    [data-testid="stChatInput"] button {{
        background-color: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: none !important;
    }}

    [data-testid="stChatInput"] button svg {{
        fill: {TEXT} !important;
        color: {TEXT} !important;
    }}

    .stApp input,
    .stApp textarea {{
        color: {TEXT} !important;
        background-color: {INPUT_BG} !important;
        border-color: {BORDER} !important;
    }}

    .stApp .stButton > button {{
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
        transition: border-color 0.2s ease;
    }}

    .stApp .stButton > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
    }}

    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stCheckbox"] label {{
        color: {TEXT} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px;
    }}

    [data-testid="stExpander"] summary {{
        color: {TEXT} !important;
    }}

    [data-testid="stAlert"] {{
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px;
    }}

    hr {{
        border-color: {BORDER} !important;
    }}

    .footer {{
        text-align: center;
        color: {MUTED} !important;
        font-size: 13px;
        padding-top: 25px;
        padding-bottom: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------
# Header
# --------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🎓 ABC Institute of Technology</h1>
        <p><strong>College Helpdesk Chatbot</strong></p>
        <p>
            Your virtual assistant for admissions, departments,
            fees, hostel facilities, library and placements.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------
# Knowledge-base file detection
# --------------------------------

def get_knowledge_base_signature():

    data_dir = Path(__file__).parent / "data"

    files = [data_dir / "college_info.txt"]
    files.extend(data_dir.glob("*.pdf"))

    signature = tuple(
        (
            file.name,
            file.stat().st_size,
            file.stat().st_mtime_ns,
        )
        for file in sorted(
            files,
            key=lambda item: item.name.lower(),
        )
        if file.is_file()
    )

    return signature


@st.cache_resource
def initialize_rag(file_signature):

    college_text = load_college_data()

    chunks = split_into_chunks(college_text)

    if not chunks:
        raise ValueError(
            "No college information was found. "
            "Please add content to the TXT or PDF files in the data folder."
        )

    index = create_search_index(chunks)

    return chunks, index


try:

    file_signature = get_knowledge_base_signature()

    chunks, index = initialize_rag(file_signature)

except Exception as error:

    st.error(
        f"Could not initialize the knowledge base: {error}"
    )

    st.stop()


# --------------------------------
# Sidebar controls
# --------------------------------

with st.sidebar:

    st.divider()

    st.markdown("### 💬 Chat controls")

    if st.button(
        "🧹 Clear Chat",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.pop(
            "pending_question",
            None,
        )

        st.rerun()

    st.write(
        f"**Messages:** {len(st.session_state.messages)}"
    )

    st.divider()

    st.markdown("### 📚 Topics you can ask about")

    st.markdown(
        """
        - 🎓 Admissions
        - 🏢 Departments
        - 💰 Fees and scholarships
        - 🏠 Hostel facilities
        - 📖 Library
        - 💼 Placements
        """
    )

    st.divider()

    st.markdown("### ⚙️ Technology")

    st.markdown(
        """
        - **Streamlit:** User interface
        - **Sentence Transformers:** Text embeddings
        - **FAISS:** Similarity search
        - **Groq API:** AI-generated answers
        """
    )

    st.info(
        "This chatbot uses sample college information. "
        "Confirm important details with the college."
    )


# --------------------------------
# Welcome section
# --------------------------------

if not st.session_state.messages:

    st.markdown(
        '<div class="section-heading">'
        '👋 Welcome! How can I help?</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Choose a suggested question below or type your own "
        "question in the chat box."
    )

    suggestions = [
        "Tell me about the college",
        "What departments are available?",
        "How can I apply for admission?",
        "What is the highest package offered?",
    ]

    columns = st.columns(2)

    for i, suggestion in enumerate(suggestions):

        with columns[i % 2]:

            if st.button(
                f"💡 {suggestion}",
                key=f"suggestion_{i}",
                use_container_width=True,
            ):

                st.session_state.pending_question = suggestion

                st.rerun()


# --------------------------------
# Normalize text
# --------------------------------

def normalize_text(text):

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"[^\w\s]",
        "",
        text.lower(),
    ).strip()


# --------------------------------
# Greeting detection
# --------------------------------

def get_greeting_prefix(question):

    pattern = (
        r"^\s*(good morning|good afternoon|good evening|hello|hi|hey)"
        r"\b[\s,!.?]*"
    )

    match = re.match(
        pattern,
        question.strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    greeting = match.group(1).lower()

    greeting_responses = {
        "good morning": "Good morning! 😊",
        "good afternoon": "Good afternoon! 😊",
        "good evening": "Good evening! 😊",
        "hello": "Hello! 👋",
        "hi": "Hi! 👋",
        "hey": "Hey! 👋",
    }

    return greeting_responses.get(greeting, "")


def remove_greeting_prefix(question):

    pattern = (
        r"^\s*(good morning|good afternoon|good evening|hello|hi|hey)"
        r"\b[\s,!.?]*"
    )

    cleaned = re.sub(
        pattern,
        "",
        question.strip(),
        count=1,
        flags=re.IGNORECASE,
    ).strip()

    return cleaned if cleaned else question


# --------------------------------
# Conversation-aware follow-up support
# --------------------------------

def get_previous_conversation():

    messages = st.session_state.messages

    previous_user = None
    previous_assistant = None

    for message in reversed(messages):

        if (
            message["role"] == "assistant"
            and previous_assistant is None
        ):

            previous_assistant = message["content"]

        elif (
            message["role"] == "user"
            and previous_assistant is not None
        ):

            previous_user = message["content"]
            break

    if previous_user and previous_assistant:
        return previous_user, previous_assistant

    return None, None


def is_follow_up_question(question):

    normalized = normalize_text(question)

    follow_up_patterns = [
        r"\bwhat about\b",
        r"\bwhat documents\b",
        r"\bwhich documents\b",
        r"\bhow about\b",
        r"\bfor that\b",
        r"\babout that\b",
        r"\bwhat are the fees\b",
        r"\bwhat are the charges\b",
        r"\bwhat about the charges\b",
        r"\bhostel charges\b",
        r"\baccommodation charges\b",
        r"\bmess fees\b",
        r"\bcharges\b",
        r"\bhow much\b",
        r"\bthere\b",
        r"\bit\b",
        r"\bthat\b",
        r"\bthose\b",
        r"\bthem\b",
        r"\bmore details\b",
        r"\btell me more\b",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in follow_up_patterns
    )


def build_contextual_question(
    question,
    previous_user=None,
    previous_assistant=None,
):

    if not (
        previous_user
        and previous_assistant
        and is_follow_up_question(question)
    ):
        return question

    previous_topic = normalize_text(previous_user)
    current_question = normalize_text(question)

    if (
        "hostel" in previous_topic
        or "accommodation" in previous_topic
    ):

        if any(
            word in current_question
            for word in [
                "charge",
                "fee",
                "fees",
                "much",
                "cost",
                "price",
            ]
        ):

            return (
                "hostel accommodation charges fees "
                "hostel room rent mess fees "
                + question
            )

        return (
            f"hostel accommodation {previous_user} {question}"
        )

    if (
        "admission" in previous_topic
        or "apply" in previous_topic
    ):

        if (
            "document" in current_question
            or "certificate" in current_question
        ):

            return (
                "admission application required documents "
                "academic certificates identity proof "
                + question
            )

    return f"{previous_user} {question}"


# --------------------------------
# Greeting and conversation responses
# --------------------------------

def get_special_response(question):

    normalized = normalize_text(question)

    greeting_messages = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if (
        normalized in greeting_messages
        or re.fullmatch(r"h+i+", normalized)
        or re.fullmatch(r"h+e+y+", normalized)
        or re.fullmatch(r"h+e+l+o+", normalized)
    ):

        greeting = get_greeting_prefix(question) or "Hello! 👋"

        return (
            f"{greeting} Welcome to ABC Institute of Technology's "
            "Helpdesk.\n\n"
            "How can I help you today? You can ask about admissions, "
            "departments, fees, hostel facilities, library, or placements."
        )

    if normalized in {
        "thank you",
        "thanks",
        "thankyou",
        "thanks a lot",
        "thank you so much",
        "thx",
    }:

        return (
            "You're welcome! 😊 I'm happy to help. "
            "Feel free to ask another college-related question."
        )

    if normalized in {
        "bye",
        "goodbye",
        "see you",
        "see you later",
        "take care",
    }:

        return (
            "Goodbye! 👋 Thank you for using the College Helpdesk. "
            "Have a great day!"
        )

    if normalized in {
        "how are you",
        "how are you doing",
    }:

        return (
            "I'm doing well, thank you! 😊 "
            "I'm here to help with your college-related questions."
        )

    return None


# --------------------------------
# Placement-related fallback
# --------------------------------

def is_placement_question(question):

    normalized = normalize_text(question)

    keywords = [
        "highest package",
        "average package",
        "salary package",
        "placement package",
        "placement statistics",
        "which companies",
        "companies visit",
        "companies visiting",
        "recruiting companies",
        "company visits",
    ]

    return any(
        keyword in normalized
        for keyword in keywords
    )


def placement_fallback():

    return (
        "The current college knowledge base does not provide verified "
        "salary package details or a confirmed list of recruiting "
        "companies. Please contact the placement cell for accurate "
        "information."
    )


# --------------------------------
# Retrieval configuration
# --------------------------------

SIMILARITY_THRESHOLD = 0.35

MAX_RETRIEVED_CHUNKS = 3


# --------------------------------
# Detect API error responses
# --------------------------------

def is_ai_error_response(answer):

    if not isinstance(answer, str) or not answer.strip():
        return True

    error_prefixes = (
        "Groq authentication failed.",
        "Groq API configuration is missing.",
        "The AI service has reached its request limit.",
        "The AI model configuration or request may be incorrect.",
        "The AI service is temporarily unavailable.",
        "I'm temporarily unable to generate an answer.",
        "Sorry, I couldn't generate an answer",
        "Please enter a valid question.",
        "Please provide the college information context.",
    )

    return answer.strip().startswith(error_prefixes)


# --------------------------------
# Display saved retrieval sources
# --------------------------------

def display_retrieval_details(message):

    sources = message.get("sources", [])

    if not sources:
        return

    with st.expander("🔍 View retrieval details"):

        st.markdown("### 📚 Best matching source")

        best_source = sources[0]

        st.markdown(
            f"**Source:** "
            f"{best_source.get('source', 'College Information')}"
        )

        if best_source.get("page") is not None:
            st.write(f"**Page:** {best_source['page']}")

        st.write(
            f"Similarity score: "
            f"{best_source.get('score', 0):.3f}"
        )

        st.write(
            "Generative AI used: "
            f"{'Yes' if message.get('ai_used', False) else 'No'}"
        )

        st.caption(
            f"Matching information: "
            f"{best_source.get('text', '')}"
        )

        if len(sources) > 1:

            st.divider()

            st.markdown("### Other retrieved sources")

            for source in sources[1:]:

                st.markdown(
                    f"**Source:** "
                    f"{source.get('source', 'College Information')}"
                )

                if source.get("page") is not None:
                    st.write(f"**Page:** {source['page']}")

                st.write(
                    f"Similarity score: "
                    f"{source.get('score', 0):.3f}"
                )

                st.caption(source.get("text", ""))


# --------------------------------
# Display previous messages
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":
            display_retrieval_details(message)


# --------------------------------
# Chat input
# --------------------------------

typed_question = st.chat_input(
    "✍️ Ask anything about the college..."
)

question = st.session_state.pop(
    "pending_question",
    None,
)

if not question:
    question = typed_question


# --------------------------------
# Process question
# --------------------------------

if question and question.strip():

    question = question.strip()

    # Capture previous conversation BEFORE appending
    # the current user question.

    previous_user, previous_assistant = (
        get_previous_conversation()
    )

    # Save and display user question.

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Detect greeting separately.

    greeting_prefix = get_greeting_prefix(question)

    # Get special response.

    answer = get_special_response(question)

    ai_used = False
    streamed_in_ui = False

    results = []
    relevant_results = []

    # Remove greeting only for retrieval.

    search_question = remove_greeting_prefix(question)

    # Build contextual retrieval question.

    contextual_question = build_contextual_question(
        search_question,
        previous_user,
        previous_assistant,
    )

    # --------------------------------
    # Retrieval-first processing
    # --------------------------------

    if answer is None:

        try:

            results = search_college_info(
                contextual_question,
                chunks,
                index,
                top_k=5,
            )

            relevant_results = [
                result
                for result in results
                if (
                    result.get("score", 0)
                    >= SIMILARITY_THRESHOLD
                    or result.get("direct_match", False)
                )
            ][:MAX_RETRIEVED_CHUNKS]

            if relevant_results:

                relevant_chunks = []

                for result in relevant_results:

                    source_text = (
                        f"Source: "
                        f"{result.get('source', 'College Information')}\n"
                    )

                    if result.get("page") is not None:
                        source_text += (
                            f"Page: {result['page']}\n"
                        )

                    source_text += (
                        f"Information: "
                        f"{result.get('text', '')}"
                    )

                    relevant_chunks.append(source_text)

                relevant_context = "\n\n".join(
                    relevant_chunks
                )

                # Include previous conversation.

                conversation_context = ""

                if (
                    previous_user
                    and previous_assistant
                    and is_follow_up_question(search_question)
                ):

                    conversation_context = (
                        "\n\nPrevious conversation:\n"
                        f"User asked: {previous_user}\n"
                        f"Assistant answered: "
                        f"{previous_assistant[:800]}\n"
                        "Use this previous topic to understand "
                        "the current follow-up question. "
                        "Answer only from the retrieved college "
                        "information below.\n"
                    )

                # --------------------------------
                # Generate grounded streaming answer
                # --------------------------------

                try:

                    with st.chat_message("assistant"):

                        if greeting_prefix:
                            st.markdown(greeting_prefix)

                        streamed_answer = st.write_stream(
                            generate_answer_stream(
                                question=search_question,
                                context=(
                                    conversation_context
                                    + relevant_context
                                ),
                            ),
                            cursor="▌",
                        )

                    streamed_in_ui = True

                    if (
                        not isinstance(streamed_answer, str)
                        or not streamed_answer.strip()
                    ):

                        answer = (
                            "Sorry, I couldn't generate an answer "
                            "from the available college information. "
                            "Please try asking differently."
                        )

                        ai_used = False

                    else:

                        if greeting_prefix:

                            answer = (
                                greeting_prefix
                                + "\n\n"
                                + streamed_answer
                            )

                        else:

                            answer = streamed_answer

                        ai_used = not is_ai_error_response(
                            streamed_answer
                        )

                except Exception as error:

                    print(
                        f"AI generation error: "
                        f"{type(error).__name__}: {error}"
                    )

                    answer = (
                        "Sorry, I'm having trouble generating a "
                        "response right now. Please try again."
                    )

                    if greeting_prefix:
                        answer = greeting_prefix + "\n\n" + answer

                    ai_used = False
                    streamed_in_ui = False

            else:

                # --------------------------------
                # Fallback after retrieval fails
                # --------------------------------

                if is_placement_question(search_question):

                    answer = placement_fallback()

                else:

                    answer = (
                        "Sorry, I couldn't find sufficiently relevant "
                        "information in the college knowledge base. 😕\n\n"
                        "Please try asking about admissions, departments, "
                        "fees, hostel facilities, library, or placements."
                    )

                if greeting_prefix:
                    answer = greeting_prefix + "\n\n" + answer

        except Exception as error:

            print(
                f"Retrieval error: "
                f"{type(error).__name__}: {error}"
            )

            answer = (
                "Sorry, I couldn't search the college information "
                "right now. Please try again."
            )

            if greeting_prefix:
                answer = greeting_prefix + "\n\n" + answer

            ai_used = False
            streamed_in_ui = False

    # --------------------------------
    # Save source information
    # --------------------------------

    saved_sources = [
        {
            "source": result.get(
                "source",
                "College Information",
            ),
            "page": result.get("page"),
            "score": float(
                result.get("score", 0)
            ),
            "text": result.get("text", ""),
        }
        for result in relevant_results
    ]

    # --------------------------------
    # Save assistant message
    # --------------------------------

    assistant_message = {
        "role": "assistant",
        "content": answer,
        "sources": saved_sources,
        "ai_used": ai_used,
    }

    st.session_state.messages.append(
        assistant_message
    )

    # --------------------------------
    # Display answer and sources
    # --------------------------------

    if streamed_in_ui:

        with st.chat_message("assistant"):

            display_retrieval_details(
                assistant_message
            )

    else:

        with st.chat_message("assistant"):

            st.markdown(answer)

            display_retrieval_details(
                assistant_message
            )


# --------------------------------
# Footer
# --------------------------------

st.markdown(
    """
    <div class="footer">
        🎓 ABC Institute Helpdesk · Powered by RAG and Generative AI
    </div>
    """,
    unsafe_allow_html=True,
)
