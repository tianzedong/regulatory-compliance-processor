import os
import pdfplumber
from docx import Document

def parse_docx(file_path):
    """
    Extracts text from a DOCX file using python-docx.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text from the DOCX file, or None if an error occurs.
    """
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return None
    
def parse_pdf(file_path):
    """
    Extracts text from a PDF file using pdfplumber.
    
    Args:
        file_path (str): Path to the PDF file.
    
    Returns:
        str: Extracted text, or None if an error occurs.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return None
    
def load_sop(sop_path):
    """Loads the SOP document (DOCX)."""
    return parse_docx(sop_path)

def load_regulatory_docs(directory):
    """Loads all PDF files from a directory."""
    docs = {}
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            text = parse_pdf(file_path)
            if text:
                docs[filename] = text
    return docs