# 📄 Docfetch-AI

🚀 Live App: https://docfetch-ai.onrender.com

Docfetch-AI is an AI-powered document assistant that lets you upload files and ask questions in plain English. Instead of manually searching through long PDFs or notes, you can simply ask a question and get accurate, context-aware answers instantly.

It is built using a Retrieval-Augmented Generation (RAG) pipeline, which combines document search with AI reasoning to deliver precise responses based on your uploaded content.



## ✨ Features

- 📂 Upload PDF and text files easily
- 💬 Ask questions in natural language (just like chatting)
- 🔍 Smart semantic search using embeddings
- 🧠 AI-generated answers based on your documents
- ⚡ Fast and efficient backend processing
- 🌐 Live deployed and accessible from anywhere
- 📊 Scalable architecture using vector search



## 🏗️ How It Works

Docfetch-AI follows a simple but powerful RAG workflow:

1. **Upload Document**
   - You upload a PDF or text file

2. **Split into Chunks**
   - The document is broken into smaller, meaningful sections

3. **Convert to Embeddings**
   - Each chunk is transformed into a vector representation

4. **Store in Vector Database**
   - These embeddings are saved for fast similarity search

5. **Ask a Question**
   - You enter a natural language query

6. **Retrieve Relevant Context**
   - The system finds the most relevant chunks from your document

7. **Generate Answer**
   - An AI model uses the retrieved context to generate a final response


## 🛠️ Tech Stack

- **Python** – Core backend logic
- **FastAPI / Streamlit** – API and user interface
- **Vector Database (Qdrant / FAISS)** – Stores and searches embeddings
- **HuggingFace / OpenAI / Gemini APIs** – Powering AI responses
- **LangChain / LlamaIndex** – RAG pipeline orchestration
- **Docker** – Containerization for deployment
- **Render** – Hosting the live application

