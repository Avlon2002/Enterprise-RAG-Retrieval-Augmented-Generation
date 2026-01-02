import streamlit as st
import os
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 1. LOAD ENVIRONMENT VARIABLES
# This keeps our keys secure and not hardcoded
load_dotenv()

OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME")

# 2. SETUP PAGE CONFIG
st.set_page_config(page_title="Enterprise Knowledge RAG", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Enterprise Knowledge RAG Engine")
st.markdown("### Secure Document Intelligence using Azure OpenAI")

# 3. SIDEBAR - FILE UPLOAD & PROCESSING
with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_file = st.file_uploader("Upload a PDF Report", type="pdf")
    
    if uploaded_file is not None:
        st.success("File Uploaded Successfully!")
        
        # Save file temporarily to disk (PyPDFLoader needs a file path)
        temp_file_path = f"./temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # --- PROCESS DOCUMENT ---
        if st.button("Process Document"):
            with st.spinner("Analyzing document... (Splitting & Embedding)"):
                
                # A. Load PDF
                loader = PyPDFLoader(temp_file_path)
                data = loader.load()
                
                # B. Split Text into Chunks
                # Why? LLMs have context limits. We need small pieces of text.
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200 # Overlap ensures context isn't lost between cuts
                )
                chunks = text_splitter.split_documents(data)
                
                # C. Create Embeddings (The "Math" representation of text)
                embeddings = AzureOpenAIEmbeddings(
                    azure_deployment=EMBEDDING_DEPLOYMENT,
                    openai_api_version=OPENAI_API_VERSION,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_API_KEY
                )
                
                # D. Create Vector Store (FAISS)
                # This stores the math vectors locally for fast searching
                vector_store = FAISS.from_documents(chunks, embeddings)
                
                # Save vector store to session state so it persists
                st.session_state.vector_store = vector_store
                st.success(f"Processed {len(chunks)} chunks. Ready to Chat!")
                
                # Cleanup temp file
                os.remove(temp_file_path)

# 4. CHAT INTERFACE
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about your document..."):
    
    # Check if document is processed
    if "vector_store" not in st.session_state:
        st.error("⚠️ Please upload and process a document first.")
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 5. RAG LOGIC (Retrieval + Generation)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                
                # Initialize LLM (GPT-4 / GPT-3.5)
                llm = AzureChatOpenAI(
                    azure_deployment=CHAT_DEPLOYMENT,
                    openai_api_version=OPENAI_API_VERSION,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_API_KEY,
                    temperature=0 # Temperature 0 means strict, factual answers
                )
                
                # Create the Retrieval Chain
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff", # "Stuff" puts all retrieved context into one prompt
                    retriever=st.session_state.vector_store.as_retriever(search_kwargs={"k": 3}), # Get top 3 chunks
                    return_source_documents=True # Important for citations
                )
                
                # Run the query
                response = qa_chain.invoke({"query": prompt})
                answer = response['result']
                source_docs = response['source_documents']
                
                # Format Sources
                unique_sources = set()
                for doc in source_docs:
                    page_num = doc.metadata.get('page', 'Unknown')
                    unique_sources.add(f"Page {page_num + 1}") # +1 because code counts from 0
                
                citation_text = f"\n\n**Sources:** {', '.join(unique_sources)}" if unique_sources else ""
                final_answer = answer + citation_text
                
                st.markdown(final_answer)
                
                # Add AI response to history
                st.session_state.messages.append({"role": "assistant", "content": final_answer})