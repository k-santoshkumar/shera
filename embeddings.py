import os
from langchain.embeddings import HuggingFaceEmbeddings #type:ignore
from langchain.vectorstores import Chroma #type:ignore
from langchain_core.documents import Document #type:ignore
from typing import List

def initialize_embeddings():
    """Initialize HuggingFace embeddings."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        encode_kwargs={"normalize_embeddings": True}
    )

def update_vector_store(new_docs: List[Document], persist_dir="./chroma_store"):
    """Create or update vector store with documents."""
    embeddings = initialize_embeddings()
    
    if os.path.exists(persist_dir):
        # Update existing store
        vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
        vector_store.add_documents(new_docs)
    else:
        # Create new store
        vector_store = Chroma.from_documents(
            documents=new_docs,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})