import os
import shutil
from typing import List
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

VECTOR_DB_PATH = os.path.join(os.getcwd(), "qa_agent", "chroma_db")

def load_documents(file_paths: List[str]) -> List[Document]:
    """
    Loads documents from the provided file paths.
    Supports .txt, .md, .json.
    """
    documents = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".txt":
                loader = TextLoader(path, encoding="utf-8")
                documents.extend(loader.load())
            elif ext == ".md":
                loader = UnstructuredMarkdownLoader(path)
                documents.extend(loader.load())
            elif ext == ".json":
                # For JSON, we might want a specific schema, but generic text loading works for now
                loader = TextLoader(path, encoding="utf-8") 
                documents.extend(loader.load())
            else:
                # Fallback to text loader
                loader = TextLoader(path, encoding="utf-8")
                documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return documents

def create_vector_db(documents: List[Document], force_rebuild: bool = False):
    """
    Creates or updates the Chroma vector database.
    """
    if force_rebuild and os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    splits = text_splitter.split_documents(documents)

    # Embeddings
    # Using a small, fast model for local usage
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create/Update Vector Store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    return vectorstore

def get_vector_store():
    """
    Returns the existing vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if os.path.exists(VECTOR_DB_PATH):
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
    return None
