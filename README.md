# Regulatory Compliance Document Processor

## Overview

This tool analyzes Standard Operating Procedures (SOPs) against regulatory documents to ensure compliance. It uses natural language processing and semantic search to:
1. Parse regulatory documents and SOPs
2. Extract regulatory clauses from documents
3. Find clauses relevant to the SOP
4. Generate a compliance analysis report with recommendations

## Features
- Document Parsing: Extract text from PDF regulatory documents and SOPs
- Clause Extraction: Identify and isolate specific regulatory clauses
- Semantic Search: Use vector embedding to find relevant regulations
- Compliance Analysis: Determine SOP compliance with regulatory requirements
- Report Generation: Create detailed compliance reports with recommendations

## Set up
```Bash
# Clone the repository
git clone https://github.com/tianzedong/regulatory-compliance-processor
cd regulatory-compliance-processor

# Create and activate conda environment
conda create -n regulatory-env python=3.11
conda activate regulatory-env

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following environment variables:

```bash
# API keys for language models
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# we also use langsmith to trace LLM's input&output
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=your_langsmith_project_name
```

## Usage 
``` Bash
# first time running
python main.py path/to/sop.docx path/to/regulations/folder --add_new_clauses

# if you want to skip adding clauses
python main.py path/to/sop.docx path/to/regulations/folder
```
Note that upserting clauses could take 5-6 mins for the first time running the code. 

## Technologies
This project leverages several technologies to analyze regulatory compliance:

- Python: Core programming language
- LangChain: Framework for working with large language models
- Anthropic Claude: LLM for understanding regulatory context and generating compliance insights
- ChromaDB: Vector database for semantic search of regulatory clauses
- Sentence Transformers: For generating embeddings of regulatory text
- PyPDF2/docx: Document parsing for regulatory documents and SOPs
- LangSmith: For tracing and monitoring LLM performance
