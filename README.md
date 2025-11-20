# 📚 RAG-Based AI Assistant – Module 1 Project (AAIDC)

This project implements a clean, production-ready Retrieval-Augmented Generation (RAG) pipeline that loads domain documents, chunks them with overlap, embeds them using Google Generative AI, stores vectors in ChromaDB, and generates answers grounded strictly in retrieved context — minimizing hallucinations.

Built as part of the Ready Tensor – Agentic AI Developer Certification (Module 1).

---

## ✅ Project Features
✔ Loads and preprocesses .txt documents
✔ Sentence-aware chunking with overlap (prevents context loss)
✔ Query preprocessing (lowercasing, trimming, punctuation cleaning)
✔ Embedding via Google Generative AI (text-embedding-004)
✔ Vector storage & similarity search using ChromaDB
✔ Retry logic to handle embedding API timeouts
✔ RAG generation using Gemini 2.5 Flash
✔ Duplicated chunks removed during context assembly
✔ Safe fallback response:

"I don't have enough information from the documents."

---

## 📁 Project Structure

![Project Structure](./Project%20Structure.jpg)


## ✅ ⚙️ Setup & Installation

1️⃣ Create & activate virtual environment
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

🧰 Tech Stack

Python 3.9+
LangChain Core
LangChain Google GenAI
Google Embedding Model: text-embedding-004
Gemini 2.5 Flash (LLM)
ChromaDB (vector storage)
dotenv for secure environment configuration

## 📄 License
This project is licensed under the **MIT License**.  
See the LICENSE file for details.

👤 Author
Suraj Mahale
AI & Salesforce Developer
GitHub: 
https://github.com/sbm-11-SFDC
