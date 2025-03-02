import os
import json
import logging
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import uuid

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

def flatten_clauses(clause_obj):
    """
    Recursively flattens a clause that may contain nested 'subclauses'.
    Returns a list of {'id': str, 'text': str}.
    """
    flattened = [{
        "id": clause_obj["id"],
        "text": clause_obj["text"]
    }]

    # If there are subclauses, recurse
    if "subclauses" in clause_obj and clause_obj["subclauses"]:
        for sub in clause_obj["subclauses"]:
            flattened.extend(flatten_clauses(sub))

    return flattened


def load_clauses(clauses_dir):
    """
    Load all extracted clauses from JSON files in a directory.
    """
    all_clauses = []

    for filename in os.listdir(clauses_dir):
        if filename.lower().endswith(".json"):
            filepath = os.path.join(clauses_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)  # data should be a list of clauses
                    if not isinstance(data, list):
                        logger.warning(f"File {filename} did not contain a list. Skipping.")
                        continue
                    
                    for clause_obj in data:
                        # Flatten and add to the main list
                        all_clauses.extend(flatten_clauses(clause_obj))
                
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON in file: {filename}")
    
    return all_clauses



def add_clauses_to_vectordb(collection, clauses_dir):
    logger.info("Loading extracted clauses")
    clauses = load_clauses(clauses_dir)

    documents = []
    metadatas = []
    ids = []
    
    for clause in clauses:
        documents.append(clause["text"])
        metadatas.append({"clause_id": clause["id"]})
        unique_id = f"{clause['id']}-{uuid.uuid4()}"
        ids.append(unique_id)
    
    logger.info(f"Adding {len(documents)} clauses to Chroma collection.")
    
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    else:
        logger.warning("No clauses found. Nothing was added to the collection.")