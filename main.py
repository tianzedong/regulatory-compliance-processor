import argparse
import logging
import os
import sys
from datetime import datetime
from src.document_processing.parser import parse_regulatory_documents


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

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create output directory for parsed data
    parsed_data_dir = "parsed_data"
    os.makedirs(parsed_data_dir, exist_ok=True)
    
    # Log basic information
    logger.info("Starting Regulatory Compliance Document Processor")
    logger.info(f"SOP Path: {args.sop_path}")
    logger.info(f"Regulatory Documents Path: {args.regulatory_path}")
    logger.info(f"Output Directory: {output_dir}")


    try:
        # Import and call document processing modules
        logger.info("Document processing phase starting...")

        # parse SOP (DOCS)

        # parse regulation files (PDF)
        parse_regulatory_documents(args.regulatory_path, parsed_data_dir)

        
        
        # # TODO: Import and call analysis modules
        # logger.info("Analysis phase starting...")
        # # from src.analysis import analyze_compliance
        # # compliance_results = analyze_compliance(sop_content, reg_documents)
        
        # # TODO: Import and call reporting modules
        # logger.info("Report generation phase starting...")
        # # from src.reporting import generate_report
        # # generate_report(compliance_results, output_dir)
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.exception(f"An error occurred during processing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()