# 📚 Retrieval-Augmented Q&A Assistant – Module 1 Project (AAIDC)

This project implements a clean, production-ready Retrieval-Augmented Generation (RAG) system that loads domain documents, chunks them with overlap, embeds them using Google Generative AI, stores vectors in ChromaDB, and generates grounded answers strictly from retrieved context — minimizing hallucinations.

Built as part of the Ready Tensor – Agentic AI Developer Certification (Module 1).

---

# 🎯 What You’ll Build

A fully functional RAG pipeline that can:
Load your own .txt documents
Chunk text using smart sentence-aware logic + overlap
Create embeddings using Google text-embedding-004
Store vectors persistently in ChromaDB
Retrieve the most relevant document chunks for any question
Generate accurate answers using Gemini 2.5 Flash
Avoid hallucinations using strict context-only responses
Handle failures using retry and deduplication mechanisms

## ✅ Project Features
✔ Loads and preprocesses `.txt` documents  
✔ Sentence-aware chunking with overlap (prevents context loss)  
✔ Query preprocessing (lowercasing, trimming, punctuation cleaning)  
✔ Embedding via Google Generative AI (text-embedding-004)  
✔ Vector storage & similarity search using ChromaDB  
✔ Retry logic to handle embedding API timeouts  
✔ RAG generation using Gemini 2.5 Flash  
✔ Duplicated chunks removed during context assembly  
✔ Safe fallback response  

"I don't have enough information from the documents."

---

# 📝 Implementation Steps (Complete Guide)

These steps match your actual functions and file structure.

Step 1 — Prepare Your Documents

📁 Folder: data/
Replace sample documents with your own text files:

data/
├── topic1.txt
├── topic2.txt
└── topic3.txt


Each file should contain plain text you want your RAG system to search.

Step 2 — Document Loading

📄 File: src/app.py
🔧 Function: load_documents()

What it does:
Reads every .txt file inside /data
Strips whitespace
Attaches metadata (source: filename)
Returns a structured list for ingestion

Step 3 — Text Chunking With Overlap

📄 File: src/vectordb.py
🔧 Function: chunk_text()

Your implementation includes:
Sentence-aware splitting
Approx. 500-character chunk size
40-character overlap to preserve continuity
Natural punctuation-based segmentation
This greatly improves retrieval quality.

Step 4 — Document Ingestion

📄 File: src/vectordb.py
🔧 Function: add_documents()

What happens internally:
Documents are chunked
Embeddings created using text-embedding-004
Stored in ChromaDB with metadata:
source
chunk_index
length
Retry logic handles API timeouts (504 errors)

Step 5 — Similarity Search

📄 File: src/vectordb.py
🔧 Function: search()

Responsibilities:
Embed the user query
Perform vector similarity search
Retrieve top-k relevant chunks
Return structured results (docs, metadatas, distances)

Step 6 — RAG Prompt Template

📄 File: src/app.py

Your prompt enforces:
Use only retrieved context
2–4 sentence focused answers
No hallucinations
Optional single source citation
This ensures grounded, consistent responses.

Step 7 — RAG Query Pipeline

📄 File: src/app.py
🔧 Function: query()

Pipeline steps:
Embed user question
Retrieve relevant chunks
Deduplicate by (source, chunk_index)
Assemble context
Pass prompt to Gemini

Return:
final answer
retrieved chunks
metadata
source list

🛠 Debug mode:

python src/app.py --q "Your Question" --dump-context


## 📁 Project Structure

![alt text](<Project Structure-1.png>)


### ✅ ⚙️ Setup & Installation

## 1️⃣ Create & activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

2️⃣ Install dependencies
python -m pip install -r requirements.txt

3️⃣ Configure Environment Variables
Create a .env file in the project root (same folder as src/ and requirements.txt):
GOOGLE_API_KEY=your_google_api_key_here
✅ .env is ignored by Git (protected)
✅ .env.example is provided for reference


✅ Running the Application
python .\src\app.py --q "What are VAEs used for?"
python .\src\app.py --q "What is the difference between VAEs and autoencoders?"
python .\src\app.py --q "How do transformers model long-range dependencies?"

To view retrieved chunks (debug mode):
python .\src\app.py --q "What are VAEs used for?" --dump-context

# 🧪 Experiments & Evaluation (Summary)

🔬 14.1 Experimental Setup

CPU: Intel Core i3
RAM: 8 GB
OS: Windows
Embedding Model: text-embedding-004
Vector DB: ChromaDB
LLM: Gemini 2.5 Flash
Chunk size: 500 chars + 40 overlap
Retrieval: top-k = 3

🧭 14.2 Evaluation Methodology

Evaluated based on:
Retrieval relevance
Grounding accuracy
Overlap continuity impact
Robustness to malformed queries
Behavior under failure modes
Deduplication correctness

📊 14.3 Metrics Used

Manual relevance scoring
Grounding accuracy (Yes/No)
Overlap continuity score
Robustness & retry success
Zero hallucination validation

# 🧰 Tech Stack
Python 3.9+
LangChain Core
LangChain Google GenAI
Google Embedding Model: text-embedding-004
Gemini 2.5 Flash (LLM)
ChromaDB (vector storage)
dotenv for secure environment configuration

# 📄 License
This project is licensed under the MIT License.
See the [LICENSE] file for details

👤 Author
Suraj Mahale
AI & Salesforce Developer
GitHub:https://github.com/sbm-11-SFDC
