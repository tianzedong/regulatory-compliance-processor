import os
import json
import logging
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from collections import defaultdict
import math
from typing import List, Dict
from tqdm import tqdm




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


def load_clauses(clauses_dir: str) -> List[Dict]:
    """
    Load all extracted clauses from JSON files in a directory.
    Each file's name is used to derive doc_id (stripping last 8 chars if present).
    Returns a list of {'doc_id':..., 'id':..., 'text':...}.
    """
    all_clauses = []
    for filename in os.listdir(clauses_dir):
        if filename.lower().endswith(".json"):
            filepath = os.path.join(clauses_dir, filename)
            doc_id, _ = os.path.splitext(filename)

            # If you only remove "_clauses" if it exists:
            if doc_id.endswith("_clauses"):
                doc_id = doc_id[:-8]  # remove last 8 chars

            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON in file: {filename}")
                    continue

                if not isinstance(data, list):
                    logger.warning(f"File {filename} did not contain a list. Skipping.")
                    continue

                for clause_obj in data:
                    flattened = flatten_clauses(clause_obj)
                    for item in flattened:
                        item["doc_id"] = doc_id
                        all_clauses.append(item)
    return all_clauses


def assign_unique_ids(clauses: List[Dict]) -> List[Dict]:
    """
    For each clause, combine doc_id + id into a base_id, then if repeated,
    append a numeric suffix: e.g., 'DOC-1.1-2' for a 2nd occurrence in the same dataset.
    Updates clauses in place, returns the same list.
    """
    id_counter = defaultdict(int)
    for clause in clauses:
        base_id = f"{clause['doc_id']}-{clause['id']}"
        id_counter[base_id] += 1
        # If first occurrence, stable_id = base_id
        if id_counter[base_id] == 1:
            clause["stable_id"] = base_id
        else:
            # Append suffix for repeated base_id
            clause["stable_id"] = f"{base_id}-{id_counter[base_id]}"
    return clauses


def chunked_upsert(collection: object, data: List[Dict], chunk_size: int = 1000):
    """
    Upsert data into Chroma in batches, showing progress via tqdm.
    Each item in 'data' should have 'stable_id', 'text', and 'doc_id', 'id'.
    """
    total = len(data)
    if total == 0:
        logger.warning("No data to upsert.")
        return

    logger.info(f"Starting upsert of {total} items in chunks of {chunk_size}.")
    with tqdm(total=total, desc="Upserting clauses", unit="clause") as pbar:
        for i in range(0, total, chunk_size):
            batch = data[i : i + chunk_size]
            documents = [item["text"] for item in batch]
            metadatas = [{"doc_id": item["doc_id"], "clause_id": item["id"]} for item in batch]
            ids = [item["stable_id"] for item in batch]

            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            pbar.update(len(batch))

    logger.info(f"Completed upsert. Collection count is now {collection.count()}.")


def add_clauses_to_vectordb(collection: object, clauses_dir: str, chunk_size: int = 1000):
    """
    Main entry: loads clauses from a directory, assigns unique stable IDs,
    then upserts them to the collection in batches.
    """
    logger.info("Loading extracted clauses...")
    clauses = load_clauses(clauses_dir)
    logger.info(f"Loaded {len(clauses)} clauses from {clauses_dir}.")

    if not clauses:
        logger.warning("No clauses found. Exiting.")
        return

    logger.info("Assigning unique IDs (doc_id + clause_id + optional suffix).")
    clauses = assign_unique_ids(clauses)

    logger.info(f"Beginning chunked upsert with batch size={chunk_size}.")
    chunked_upsert(collection, clauses, chunk_size)