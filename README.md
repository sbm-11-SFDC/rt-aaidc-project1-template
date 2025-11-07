# 📚 RAG-Based AI Assistant – Module 1 Project (AAIDC)

A Retrieval-Augmented Generation (RAG) system that loads domain documents, embeds them, stores them in a vector database, and answers user questions grounded only in the retrieved context.

This project was built as part of the Ready Tensor **Agentic AI Developer Certification – Module 1**.

---

## ✅ Project Features
✔ Loads and processes `.txt` documents  
✔ Chunks text into searchable fragments  
✔ Creates embeddings using **Google Generative AI embeddings**  
✔ Stores vectors in **ChromaDB**  
✔ Retrieves relevant chunks for a given query  
✔ LLM generates grounded answers using retrieved context  
✔ If context is insufficient, the model responds:
> `"I don't have enough information from the documents."`

---

## 📁 Project Structure

![alt text](<Project Structure.png>)

## ✅ Setup & Installation

### 1️⃣ Create & activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Configure Environment Variables
Create a .env file in the project root (same folder as src/ and requirements.txt):
GOOGLE_API_KEY=your_google_api_key_here
✅ .env is ignored by Git (protected)
✅ .env.example is provided for reference


✅ Running the Application
python .\src\app.py --q "What are VAEs used for?"
python .\src\app.py --q "What is the difference between VAEs and autoencoders?"
python .\src\app.py --q "How do transformers model long-range dependencies?"

✅ Tech Stack
Python 3.9+
LangChain
ChromaDB
Google Generative AI (embeddings + model)

## 📄 License
This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

👤 Author

Suraj Mahale
AI & Salesforce Developer
GitHub: 
https://github.com/sbm-11-SFDC
