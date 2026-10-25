
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
    /* Main application background */
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

    /* Header and toolbar */
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background-color: {BG} !important;
    }}

    /* General text */
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

    /* Hero header */
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

    /* Sidebar */
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

    /* Chat messages */
    [data-testid="stChatMessage"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }}

    /* FIX: bottom fixed chat area */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {{
        background-color: {BG} !important;
    }}

    /* FIX: chat input outer container */
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

    /* FIX: text field and typed text */
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

    /* FIX: send button */
    [data-testid="stChatInput"] button {{
        background-color: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: none !important;
    }}

    [data-testid="stChatInput"] button svg {{
        fill: {TEXT} !important;
        color: {TEXT} !important;
    }}

    /* Other input fields */
    .stApp input,
    .stApp textarea {{
        color: {TEXT} !important;
        background-color: {INPUT_BG} !important;
        border-color: {BORDER} !important;
    }}

    /* Buttons */
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

    /* Radio buttons and checkboxes */
    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stCheckbox"] label {{
        color: {TEXT} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px;
    }}

    [data-testid="stExpander"] summary {{
        color: {TEXT} !important;
    }}

    /* Alerts */
    [data-testid="stAlert"] {{
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px;
    }}

    /* Horizontal lines */
    hr {{
        border-color: {BORDER} !important;
    }}

    /* Footer */
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
    st.error(f"Could not initialize the knowledge base: {error}")
    st.stop()


# --------------------------------
# Sidebar controls
# --------------------------------

with st.sidebar:
    st.divider()
    st.markdown("### 💬 Chat controls")

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("pending_question", None)
        st.rerun()

    st.write(f"**Messages:** {len(st.session_state.messages)}")

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

    return re.sub(r"[^\w\s]", "", text.lower()).strip()


# --------------------------------
# Greeting and conversation responses
# --------------------------------

def get_special_response(question):
    normalized = normalize_text(question)
    compact = normalized.replace(" ", "")

    is_greeting = (
        normalized in {
            "hi", "hello", "hey",
            "good morning", "good afternoon", "good evening",
        }
        or re.fullmatch(r"h+i+", normalized) is not None
        or re.fullmatch(r"h+e+y+", normalized) is not None
        or re.fullmatch(r"h+e+l+o+", normalized) is not None
        or any(
            compact.startswith(greeting)
            for greeting in (
                "goodmorning", "goodafternoon", "goodevening"
            )
        )
    )

    if is_greeting:
        return (
            "Hello! 👋 Welcome to ABC Institute of Technology's Helpdesk.\n\n"
            "How can I help you today? You can ask about admissions, "
            "departments, fees, hostel facilities, library, or placements."
        )

    if normalized in {
        "thank you", "thanks", "thankyou", "thanks a lot",
        "thank you so much", "thx",
    }:
        return (
            "You're welcome! 😊 I'm happy to help. "
            "Feel free to ask another college-related question."
        )

    if normalized in {
        "bye", "goodbye", "see you", "see you later", "take care",
    }:
        return (
            "Goodbye! 👋 Thank you for using the College Helpdesk. "
            "Have a great day!"
        )

    if normalized in {"how are you", "how are you doing"}:
        return (
            "I'm doing well, thank you! 😊 "
            "I'm here to help with your college-related questions."
        )

    return None


# --------------------------------
# Known-answer safeguards
# --------------------------------

def get_known_fact_response(question, college_text):
    """
    Answer specific questions only when the sample knowledge base
    supports the relevant information.
    """

    q = normalize_text(question)
    data = normalize_text(college_text)

    # Working days and opening hours
    asks_hours = any(term in q for term in [
        "working days", "working hours", "opening hours",
        "college timings", "college timing", "timings",
        "what time does the college", "when does the college open",
        "when does the college close",
    ])

    if asks_hours:
        has_days = "monday" in data and "saturday" in data
        has_hours = (
        ("9am" in data or "9 am" in data)
        and ("5pm" in data or "5 pm" in data)
    )

        if has_days and has_hours:
            return (
                "According to the current sample knowledge base, "
                "the institute operates Monday through Saturday, "
                "from 9:00 AM to 5:00 PM. Please confirm these timings "
                "with the college before relying on them."
            )

    # Fees: never invent an amount
    asks_fees = any(term in q for term in [
        "fee", "fees", "tuition", "cost of admission",
        "how much does", "how much is",
    ])

    if asks_fees:
        return (
            "The sample knowledge base does not specify exact fee "
            "amounts. Fees may depend on the course and admission "
            "category. Please contact the admissions office for the "
            "current fee structure and any applicable scholarships."
        )

    # Hostel: availability must not be asserted without confirmation
    asks_hostel = any(term in q for term in [
        "hostel", "accommodation", "mess fee", "room allocation",
    ])

    if asks_hostel:
        return (
            "The current sample knowledge base does not confirm "
            "hostel availability, room allocation, or accommodation "
            "charges. Please contact the college administration to "
            "confirm availability, fees, and hostel rules."
        )

    # Location: use only if it appears in the knowledge base
    asks_location = any(term in q for term in [
        "where is the college", "college location",
        "where is the institute", "which city",
        "where is abc institute",
    ])

    if asks_location:
        if "hyderabad" in data and "telangana" in data:
            return (
                "The sample knowledge base lists the institute as "
                "located in Hyderabad, Telangana, India. This is "
                "sample information and should be verified with the "
                "actual institution."
            )

        return (
            "The college location has not been confirmed in the "
            "current knowledge base."
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

    return any(keyword in normalized for keyword in keywords)


def placement_fallback():
    return (
        "The current college knowledge base does not provide verified "
        "salary package details or a confirmed list of recruiting "
        "companies. Please contact the placement cell for accurate "
        "information."
    )


# --------------------------------
# Display previous messages
# --------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------
# Chat input
# --------------------------------

typed_question = st.chat_input("✍️ Ask anything about the college...")

question = st.session_state.pop("pending_question", None)

if not question:
    question = typed_question


# --------------------------------
# Process question
# --------------------------------

if question and question.strip():
    question = question.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    answer = get_special_response(question)
    best_result = None
    ai_used = False
    results = []

    # Get college data for grounded known answers
    college_text = load_college_data()

    if answer is None:
        answer = get_known_fact_response(question, college_text)

    if answer is None and is_placement_question(question):
        answer = placement_fallback()

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

            # Conservative threshold for general RAG questions
            if best_result and best_result["score"] >= 0.50:
                relevant_chunks = [
                    (
                        f"Source: {result.get('source', 'College Information')}\n"
                        f"Information: {result['text']}"
                    )
                    for result in results
                    if result["score"] >= 0.35
                ]

                relevant_context = "\n\n".join(relevant_chunks)

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
                answer = (
                    "Sorry, I couldn't find sufficiently relevant "
                    "information in the college knowledge base. 😕\n\n"
                    "Try asking about admissions, departments, fees, "
                    "hostel facilities, library, or placements."
                )

        except Exception as error:
            print(
                f"Retrieval error: {type(error).__name__}: {error}"
            )
            answer = (
                "Sorry, I couldn't search the college information "
                "right now. Please try again."
            )

    # --------------------------------
    # Save and display answer
    # --------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

    with st.chat_message("assistant"):
        st.markdown(answer)

        if best_result is not None:
            with st.expander("🔍 View retrieval details"):
                st.markdown("### 📚 Best matching source")
                st.markdown(
                    f"**Source:** "
                    f"{best_result.get('source', 'College Information')}"
                )
                st.write(
                    f"Similarity score: {best_result['score']:.3f}"
                )
                st.write(
                    f"Generative AI used: {'Yes' if ai_used else 'No'}"
                )
                st.caption(
                    f"Matching information: {best_result['text']}"
                )

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
