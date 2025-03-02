import os
import json
import logging
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

logger = logging.getLogger(__name__)

def initialize_chroma_collection(collection_name="regulatory-clauses"):
    """
    Initialize a ChromaDB collection with an embedding function.
    Returns the collection object.
    """
    logger.info("Initializing ChromaDB Collection with an embedding function")
    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef
    )
    return collection


def load_clauses(clauses_dir):
    """
    Load all extracted clauses from JSON files in a directory.
    """
    clauses = []
    for filename in os.listdir(clauses_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(clauses_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                clauses.extend(json.load(f))

    if not clauses:
        logger.warning(f"No clauses found in {clauses_dir}. Skipping insertion.")
    
    return clauses



def add_clauses_to_vectordb(collection, clauses_dir):
    logger.info("Loading extracted clauses")
    clauses = load_clauses(clauses_dir)

    ids = [clause["id"] for clause in clauses]
    metadatas = [{"source": clause.get("source", "unknown")} for clause in clauses]
    documents = [clause["text"] for clause in clauses]

    logger.info(f"Inserting {len(clauses)} clauses into ChromaDB...")
    
    # No need to manually generate embeddings, ChromaDB will handle it
    collection.add(
        ids=ids,
        metadatas=metadatas,
        documents=documents
    )

    logger.info("Successfully stored clauses in ChromaDB.")
