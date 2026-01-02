# 🧠 Enterprise Knowledge RAG Engine
**Secure Document Intelligence using Azure OpenAI & LangChain**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-🦜️🔗-white?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 🚀 Project Overview
In consulting and industrial sectors, professionals spend up to **30% of their time** searching through massive PDF reports, compliance documents, and technical manuals.  

This project is an **Enterprise-Grade Retrieval-Augmented Generation (RAG) System**, allowing users to securely "chat" with internal documents and extract precise answers with **source citations**.  

Unlike public ChatGPT, this architecture ensures **data stays within the organization's Azure perimeter**, preventing any data leakage.

### Key Capabilities
- **Context-Aware Answers:** Finds exact paragraphs using vector embeddings.
- **Hallucination Reduction:** Answers only based on provided documents.
- **Source Citations:** Returns page numbers and source text for audit trails.

---

## 🏗️ System Architecture
The system follows a modern RAG pipeline:

```mermaid
graph LR
    A[PDF Document] -->|PyPDF Loader| B[Text Chunks]
    B -->|Azure Ada-002| C[Vector Embeddings]
    C -->|Store| D[FAISS Vector DB]
    E[User Query] -->|Embed Query| D
    D -->|Retrieve Top K Context| F[GPT-4 Prompt]
    F -->|Generate Answer| G[Streamlit UI]
