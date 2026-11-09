🎓 College Helpdesk Chatbot

An AI-powered College Helpdesk Chatbot built using Python, Streamlit, Retrieval-Augmented Generation (RAG), FAISS, Sentence Transformers, and Groq API.

The chatbot helps students get answers to common college-related questions, including admissions, departments, fees, hostel facilities, placements, and library information.

It retrieves relevant information from college documents before generating answers using an AI language model.

🚀 Features

AI-powered question answering: Answers student questions using Groq.

Retrieval-Augmented Generation (RAG): Retrieves relevant college information before generating answers.

PDF and TXT support: Loads information from text files and PDF documents.

FAISS vector search: Finds relevant information using semantic similarity.

Source tracking: Displays source documents and PDF page numbers.

Conversation history: Maintains previous messages during the session.

Follow-up questions: Uses conversation context to understand follow-up queries.

Greeting detection: Handles greetings, thank-you messages, and goodbyes.

Live response streaming: Displays AI responses progressively.

Automatic knowledge-base refresh: Detects changes to TXT and PDF files and refreshes the search index.

Error handling: Handles missing API keys, invalid credentials, and API failures.

Light and dark themes: Provides a customizable interface.

🛠️ Technologies Used

Technology

Purpose

Python

Backend programming

Streamlit

Web application interface

FAISS

Vector similarity search

Sentence Transformers

Text embeddings

all-MiniLM-L6-v2

Embedding model

Groq API

AI-generated responses

PyPDF

PDF text extraction

NumPy

Numerical operations

python-dotenv

Environment variable management

🏗️ Project Architecture

Student Question
       |
       v
 Streamlit Interface
       |
       v
 Question Processing
       |
       v
 RAG Retrieval System
       |
       v
 Sentence Transformer
       |
       v
 FAISS Vector Search
       |
       v
 Relevant College Documents
       |
       v
 Groq AI Model
       |
       v
 Context-Based Answer
       |
       v
 Display Answer and Sources

📁 Project Structure

College-Helpdesk-Chatbot/
│
├── app.py
├── rag_system.py
├── ai_response.py
│
├── data/
│   ├── college_info.txt
│   ├── admission_notification.pdf
│   ├── college_handbook.pdf
│   └── fee_structure.pdf
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

⚙️ Installation and Setup

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

Replace the placeholder with your actual GitHub repository URL.

2. Navigate to the project folder

cd College-Helpdesk-Chatbot

3. Create a virtual environment

python -m venv venv

4. Activate the virtual environment

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

5. Install dependencies

pip install -r requirements.txt

🔑 Environment Configuration

Create a .env file in the project root directory.

Add the following configuration:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_MAX_TOKENS=500

Replace the placeholder with your own Groq API key.

Important: Never upload your actual .env file or API key to GitHub.

The .env.example file contains placeholder configuration for other developers.

▶️ Run the Application

Start the Streamlit application:

python -m streamlit run app.py

Open the URL displayed in your terminal, usually:

http://localhost:8501

📚 Knowledge Base Management

The chatbot retrieves information from the data/ directory.

Supported formats:

.txt

.pdf

Adding new college information

Open the data/ folder.

Add or update college_info.txt.

Add new college PDF documents when required.

Save the changes.

Ask a question about the updated information.

The application detects changes to the knowledge-base files and refreshes its retrieval index.

Important: Use accurate and verified college information. Remove outdated documents when they are no longer valid.

🧠 Retrieval-Augmented Generation (RAG)

The application uses the following process:

Loads college information from TXT and PDF files.

Extracts text from PDF pages.

Splits documents into overlapping text chunks.

Converts chunks into vector embeddings using Sentence Transformers.

Stores embeddings in a FAISS similarity-search index.

Retrieves relevant chunks based on student questions.

Sends retrieved information to the Groq language model.

Generates a response based on the supplied college context.

Displays the answer along with retrieval details.

The current retrieval configuration uses a similarity threshold of 0.35 and retrieves up to three relevant chunks for answer generation.

This threshold is an initial development setting based on manual testing, not a universally calibrated accuracy measure.

🧪 Testing and Validation

The following functional tests were performed during development.

Test Question / Scenario

Expected Result

Actual Result

Good morning, how can I apply for admission?

Greeting and admission guidance

Passed

What documents are needed for admission?

Required document list

Passed

What are the hostel charges?

No invented fee; administration confirmation

Passed

What is the CSE fee?

Department-specific fee retrieval

Passed

Where is the college located?

Location retrieval

Passed

What departments are available?

Department list

Passed

What is the placement package?

Missing information fallback

Passed

What is the admission deadline?

Missing information fallback

Passed

What documents are needed for that?

Context-aware follow-up

Passed

Thank you

Friendly response

Passed

Library index-refresh test

Retrieves newly added information

Passed

Streaming response test

Displays response progressively

Passed

Missing API key

Displays configuration error

Passed

Invalid API key

Displays authentication error

Passed

Additional validation

Python syntax compilation was successful for app.py, rag_system.py, and ai_response.py.

PDF ingestion and retrieval were tested.

PDF source filename and page metadata are preserved by the retrieval pipeline.

Source details and conversation messages were checked during application testing.

API rate-limit and temporary service-failure scenarios still require separate verification.

⚠️ Limitations

Answer accuracy depends on the quality and completeness of the uploaded college documents.

Missing information cannot be reliably supplied by the chatbot.

Groq API availability and usage limits may affect response generation.

PDF files containing scanned images may require OCR before their text can be retrieved.

The current college information contains sample development data, including the CSE fee and location. These must be replaced with verified official information before production use.

The chatbot is intended to provide informational assistance and should not replace official college communication.

🔮 Future Enhancements

Student login and authentication.

Admin dashboard for managing college documents.

Database integration.

OCR support for scanned PDFs.

Multilingual student support.

Improved analytics and feedback collection.

WhatsApp or website integration.

👨‍💻 Developed By

M Manoj Sai
Jaswanth Ande 
G 

Python Full Stack Developer

Project

College Helpdesk Chatbot

Core Technologies

Python | Streamlit | RAG | FAISS | Sentence Transformers | Groq AI

This project was developed to demonstrate the practical implementation of Retrieval-Augmented Generation for an AI-powered college information and student-support system