import os
import json
import logging
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from collections import defaultdict



logger = logging.getLogger(__name__)

def initialize_chroma_collection(
        collection_name="regulatory-clauses", 
        persist_directory="local_db"
):
    """
    Initialize a ChromaDB collection with an embedding function.
    Returns the collection object.
    """
    logger.info("Initializing ChromaDB Collection with an embedding function")
    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=persist_directory)

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
    Each file's name is used as a doc_id prefix for its clauses.
    Returns a list of clauses, where each clause has:
      {
        "id": "1.1",            # original JSON ID
        "text": "...",
        "doc_id": "filename"    # derived from filename
      }
    """
    all_clauses = []

    for filename in os.listdir(clauses_dir):
        if filename.lower().endswith(".json"):
            filepath = os.path.join(clauses_dir, filename)
            doc_id, _ = os.path.splitext(filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)  # Expect a list of clauses
                    if not isinstance(data, list):
                        logger.warning(f"File {filename} did not contain a list. Skipping.")
                        continue

                    for clause_obj in data:
                        flattened = flatten_clauses(clause_obj)

                        for item in flattened:
                            item["doc_id"] = doc_id[:-8] # remove last eight chars which are "_clauses"
                            all_clauses.append(item)

                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON in file: {filename}")

    return all_clauses


def add_clauses_to_vectordb(collection, clauses_dir):
    """
    Loads clauses from clauses_dir and adds them to the given Chroma collection.
    Combines doc_id + clause_id for a stable ID, and if it appears multiple times,
    we append a numeric suffix to keep them unique.
    """
    logger.info("Loading extracted clauses")
    clauses = load_clauses(clauses_dir)

    documents = []
    metadatas = []
    ids = []

    # Track how many times each base ID appears
    id_counter = defaultdict(int)

    for clause in clauses:
        base_id = f"{clause['doc_id']}-{clause['id']}"
        id_counter[base_id] += 1
        if id_counter[base_id] == 1:
            stable_id = base_id
        else:
            stable_id = f"{base_id}-{id_counter[base_id]}"

        documents.append(clause["text"])
        metadatas.append({
            "doc_id": clause["doc_id"],
            "clause_id": clause["id"]
        })
        ids.append(stable_id)

    logger.info(f"Adding {len(documents)} clauses to Chroma collection.")

    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    else:
        logger.warning("No clauses found. Nothing was added to the collection.")

    logger.info(f"Collection now has {collection.count()} items.")