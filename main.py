import argparse
import logging
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from src.parser import parse_regulatory_documents, parse_sop_document
from src.extractor import extract_clauses
from src.vector_db import initialize_chroma_collection, add_clauses_to_vectordb
from langchain_anthropic import ChatAnthropic
import json
import chromadb

def setup_logging():
    """Set up basic logging configuration."""
    os.makedirs("logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/processing_{timestamp}.log"
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Regulatory Compliance Document Processor")
    parser.add_argument("sop_path", help="Path to the SOP file (default: data/sop.pdf)")
    parser.add_argument("regulatory_path", help="Path to the folder containing regulatory documents")
    
    args = parser.parse_args()
    logger = setup_logging()
    load_dotenv()

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create output directory for parsed data
    parsed_data_dir = "parsed_data"
    os.makedirs(parsed_data_dir, exist_ok=True)

    clauses_dir = "clauses"
    os.makedirs(clauses_dir, exist_ok=True)
    
    # Log basic information
    logger.info("Starting Regulatory Compliance Document Processor")
    logger.info(f"SOP Path: {args.sop_path}")
    logger.info(f"Regulatory Documents Path: {args.regulatory_path}")
    logger.info(f"Output Directory: {output_dir}")

    # init LangChain Client
    logger.info("Initializing LangChain Anthropic client")
    anthropic_client = ChatAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20240620",
        temperature=0.1
    )

    try:
        # Import and call document processing modules
        logger.info("Document processing phase starting...")

        # parse SOP (DOCS)
        # parse_sop_document(args.sop_path, parsed_data_dir)

        # parse regulation files (PDF)
        # parse_regulatory_documents(args.regulatory_path, parsed_data_dir)

        # extract clauses from parsed regulation files
        # extract_clauses("parsed_data/parsed_regulation_files", clauses_dir)

        # Init VectorDB to stored extracted clauses
        collection = initialize_chroma_collection()
        add_clauses_to_vectordb(collection, clauses_dir, chunk_size=300)


        # TODO: Analyize SOP using Langchain + Anthropic API

        # TODO: Generate Report using Langchain + Anthropic API
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.exception(f"An error occurred during processing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()