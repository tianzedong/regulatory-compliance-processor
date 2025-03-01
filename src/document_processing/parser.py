from pdfminer.high_level import extract_text
import os
import logging
from pathlib import Path
import docx
import json
import re

logger = logging.getLogger(__name__)

def parse_pdf(pdf_path):
    logger.info(f"Parsing PDF: {pdf_path}")
    try:
        text = extract_text(pdf_path)
        if not text.strip():
            logger.warning(f"No text extracted from {pdf_path}")
        return text
            
    except Exception as e:
        logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
        raise


def parse_regulatory_documents(regulatory_dir, output_dir):
    logger.info(f"Processing regulatory documents from {regulatory_dir}")
    
    parsed_reg_dir = os.path.join(output_dir, "parsed_regulation_files")
    os.makedirs(parsed_reg_dir, exist_ok=True)
    
    documents = {}
    pdf_files = [f for f in os.listdir(regulatory_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {regulatory_dir}")
        return documents
    
    logger.info(f"Found {len(pdf_files)} regulatory PDF files")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(regulatory_dir, pdf_file)
        
        try:
            text = parse_pdf(pdf_path)
            doc_name = Path(pdf_file).stem
            output_file = os.path.join(parsed_reg_dir, f"{doc_name}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            documents[doc_name] = text
            logger.info(f"Successfully parsed and saved {doc_name}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")
    
    return documents


def parse_sop_document(sop_path, output_dir):
    """
    Very simple function to parse SOP document in DOCX format.
    
    Args:
        sop_path (str): Path to the SOP file
        output_dir (str): Directory to save parsed output
        
    Returns:
        str: Raw text content from the SOP
    """
    logger.info(f"Parsing SOP document: {sop_path}")
    
    # Create parsed_sop directory under the specified output_dir
    parsed_sop_dir = os.path.join(output_dir, "parsed_sop")
    os.makedirs(parsed_sop_dir, exist_ok=True)
    
    try:
        # Check file format
        if not sop_path.lower().endswith('.docx'):
            raise ValueError(f"Expected DOCX file format for SOP, got: {sop_path}")
        
        # Parse the document - simplest possible approach
        doc = docx.Document(sop_path)
        
        # Extract all text from paragraphs
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # Join with newlines
        content = '\n'.join(full_text)
        
        # Save the text content to a file
        sop_name = Path(sop_path).stem
        output_file = os.path.join(parsed_sop_dir, f"{sop_name}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Successfully extracted text from SOP and saved to: {output_file}")
        
        return content
        
    except Exception as e:
        logger.error(f"Error parsing SOP document {sop_path}: {str(e)}")
        raise