import os
import shutil
from typing import List

from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Absolute path to the persistent Chroma DB folder
VECTOR_DB_PATH = os.path.join(os.getcwd(), "qa_agent", "chroma_db")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_documents(file_paths: List[str]) -> List[Document]:
    """Load .txt, .md, and .json files into LangChain Document objects.

    Args:
        file_paths: List of absolute or relative file paths.
    Returns:
        List[Document] containing the loaded text.
    """
    documents: List[Document] = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".txt":
                loader = TextLoader(path, encoding="utf-8")
            elif ext == ".md":
                loader = UnstructuredMarkdownLoader(path)
            elif ext == ".json":
                # Load JSON as plain text – you can replace this with a schema‑aware loader later
                loader = TextLoader(path, encoding="utf-8")
            else:
                # Fallback to generic text loader
                loader = TextLoader(path, encoding="utf-8")
            documents.extend(loader.load())
        except Exception as e:
            print(f"[ERROR] Failed to load {path}: {e}")
    return documents

def _get_embedding_function() -> HuggingFaceEmbeddings:
    """Create the embedding model used throughout the project.

    Using ``all-MiniLM-L6-v2`` provides a good speed/accuracy trade‑off for
    local CPU inference.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ---------------------------------------------------------------------------
# Vector store creation / retrieval
# ---------------------------------------------------------------------------
def _reset_chroma_client(path: str) -> None:
    """Reset a persistent Chroma client to close any open file handles.

    This is a best‑effort operation; if the client cannot be instantiated we
    simply ignore the error – the subsequent ``shutil.rmtree`` will still run.
    """
    try:
        from chromadb import PersistentClient
        client = PersistentClient(path=path)
        client.reset()
    except Exception as e:
        print(f"[WARN] Unable to reset Chroma client: {e}")

def create_vector_db(documents: List[Document], force_rebuild: bool = False) -> Chroma:
    """Create or rebuild the Chroma vector store safely.

    * ``force_rebuild`` – delete the existing DB folder and start fresh.
    * On Windows the DB folder can be locked; we first reset the persistent
      client and then attempt removal, falling back to ``ignore_errors=True``.
    """
    embeddings = _get_embedding_function()

    if force_rebuild and os.path.isdir(VECTOR_DB_PATH):
        _reset_chroma_client(VECTOR_DB_PATH)
        try:
            shutil.rmtree(VECTOR_DB_PATH)
        except PermissionError as pe:
            print(f"[WARN] PermissionError while deleting DB folder: {pe}. Retrying with ignore_errors.")
            shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)
        except Exception as e:
            print(f"[ERROR] Unexpected error while removing DB folder: {e}")

    if not os.path.isdir(VECTOR_DB_PATH):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
        chunks = text_splitter.split_documents(documents)
        db = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=VECTOR_DB_PATH)
        print("[INFO] Vector database created at", VECTOR_DB_PATH)
        return db
    else:
        print("[INFO] Loading existing vector database from", VECTOR_DB_PATH)
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

def get_vector_store() -> Chroma | None:
    """Return the existing vector store if it has been created, otherwise ``None``.
    """
    if not os.path.isdir(VECTOR_DB_PATH):
        return None
    embeddings = _get_embedding_function()
    return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
