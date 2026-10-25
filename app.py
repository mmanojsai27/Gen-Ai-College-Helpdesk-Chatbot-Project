
import re
import streamlit as st

from rag_system import (
    load_college_data,
    split_into_chunks,
    create_search_index,
    search_college_info,
)
from ai_response import generate_answer


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
# Theme colors and custom CSS
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


st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    .stApp [data-testid="stAppViewContainer"] {{
        background-color: {BG};
    }}

    .main .block-container {{
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background-color: {BG};
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
        color: {MUTED};
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
        background-color: {SIDEBAR_BG};
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li {{
        color: {TEXT} !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }}

    [data-testid="stChatInput"] {{
        background-color: {INPUT_BG};
        border: 1px solid {BORDER};
        border-radius: 14px;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {TEXT} !important;
        background-color: {INPUT_BG} !important;
        caret-color: {ACCENT};
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {MUTED} !important;
        opacity: 1;
    }}

    .stApp input,
    .stApp textarea {{
        color: {TEXT} !important;
        background-color: {INPUT_BG} !important;
        border-color: {BORDER} !important;
    }}

    .stApp .stButton > button {{
        background-color: {SURFACE};
        color: {TEXT} !important;
        border: 1px solid {BORDER};
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
        transition: border-color 0.2s ease;
    }}

    .stApp .stButton > button:hover {{
        border-color: {ACCENT};
        color: {ACCENT} !important;
    }}

    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stCheckbox"] label {{
        color: {TEXT} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    [data-testid="stExpander"] summary {{
        color: {TEXT} !important;
    }}

    [data-testid="stAlert"] {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}

    .info-card {{
        background-color: {SURFACE};
        padding: 16px;
        border-radius: 12px;
        border: 1px solid {BORDER};
        margin-bottom: 10px;
    }}

    hr {{
        border-color: {BORDER} !important;
    }}

    .footer {{
        text-align: center;
        color: {MUTED} !important;
        font-size: 13px;
        padding-top: 25px;
        padding-bottom: 10px;
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
# Initialize RAG system
# --------------------------------

@st.cache_resource
def initialize_rag():
    college_text = load_college_data()
    chunks = split_into_chunks(college_text)
    index = create_search_index(chunks)
    return chunks, index


try:
    chunks, index = initialize_rag()
except Exception as error:
    st.error(
        f"Could not initialize the knowledge base: {error}"
    )
    st.stop()


# --------------------------------
# Sidebar controls and information
# --------------------------------

with st.sidebar:
    st.divider()

    st.markdown("### 💬 Chat controls")

    if st.button(
        "🧹 Clear Chat",
        use_container_width=True,
        type="primary",
    ):
        st.session_state.messages = []
        st.session_state.pop("pending_question", None)
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
        "This chatbot uses a sample college knowledge base. "
        "Confirm important information with the college."
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

    suggestion_columns = st.columns(2)

    for i, suggestion in enumerate(suggestions):
        with suggestion_columns[i % 2]:
            if st.button(
                f"💡 {suggestion}",
                key=f"suggestion_{i}",
                use_container_width=True,
            ):
                st.session_state.pending_question = suggestion
                st.rerun()


# --------------------------------
# Normalize text safely
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
# Greeting and conversation responses
# --------------------------------

def get_special_response(question):
    normalized = normalize_text(question)
    compact = normalized.replace(" ", "")

    is_greeting = (
        normalized in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        }
        or re.fullmatch(r"h+i+", normalized) is not None
        or re.fullmatch(r"h+e+y+", normalized) is not None
        or re.fullmatch(r"h+e+l+o+", normalized) is not None
        or any(
            compact.startswith(greeting)
            for greeting in (
                "goodmorning",
                "goodafternoon",
                "goodevening",
            )
        )
    )

    if is_greeting:
        return (
            "Hello! 👋 Welcome to ABC Institute of Technology's "
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
        "The current college knowledge base does not provide "
        "verified salary package details or a confirmed list of "
        "recruiting companies. Please contact the placement cell "
        "for accurate information."
    )


# --------------------------------
# Display previous chat messages
# --------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------
# Chat input and suggested questions
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

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    answer = get_special_response(question)
    best_result = None
    ai_used = False
    results = []

    if answer is None:
        try:
            results = search_college_info(
                question,
                chunks,
                index,
                top_k=3,
            )

            if results:
                best_result = results[0]

            if best_result and best_result["score"] >= 0.50:
                relevant_chunks = [
                    result["text"]
                    for result in results
                    if result["score"] >= 0.35
                ]

                relevant_context = "\n\n".join(
                    relevant_chunks
                )

                try:
                    answer = generate_answer(
                        question=question,
                        context=relevant_context,
                    )

                    if answer and answer.strip():
                        ai_used = True
                    else:
                        answer = (
                            "Sorry, I couldn't generate an answer. "
                            "Please try asking in a different way."
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

            else:
                if is_placement_question(question):
                    answer = placement_fallback()
                else:
                    answer = (
                        "Sorry, I couldn't find relevant information "
                        "about that question in the college knowledge "
                        "base. 😕\n\n"
                        "Try asking about admissions, departments, "
                        "fees, hostel facilities, library, or placements."
                    )

        except Exception as error:
            print(
                f"Retrieval error: "
                f"{type(error).__name__}: {error}"
            )

            answer = (
                "Sorry, I couldn't search the college information "
                "right now. Please try again."
            )

    # --------------------------------
    # Save and display assistant answer
    # --------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)

        # Display retrieved source information
        if best_result is not None:
            with st.expander("🔍 View retrieval details"):
                st.markdown("### 📚 Best matching source")

                st.markdown(
                    f"**Source:** {best_result.get('source', 'College Information')}"
                )

                st.write(
                    f"Similarity score: "
                    f"{best_result['score']:.3f}"
                )

                st.write(
                    "Generative AI used: "
                    f"{'Yes' if ai_used else 'No'}"
                )

                st.caption(
                    f"Matching information: {best_result['text']}"
                )

                # Display other retrieved sources
                if len(results) > 1:
                    st.divider()
                    st.markdown("### Other retrieved sources")

                    for result in results[1:]:
                        st.markdown(
                            f"**Source:** "
                            f"{result.get('source', 'College Information')}"
                        )

                        st.write(
                            f"Similarity score: {result['score']:.3f}"
                        )

                        st.caption(result["text"])


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
