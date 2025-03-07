import logging

logger = logging.getLogger(__name__)

def create_template_prompt(sop_text, retrieved_chunks):
    """
    Build a single prompt by combining the full SOP text with all retrieved regulatory clauses.
    
    :param sop_text: The full original SOP text.
    :param retrieved_chunks: A list of dicts, each with:
        - "chunk_text": the chunk of SOP text (not used here), and 
        - "relevant_clauses": a list of clause dicts with keys "id", "text", "metadata", etc.
    :return: A formatted prompt string ready to send to the LLM.
    """
    # Use a dict to deduplicate clauses by their 'id'
    clause_map = {}
    for chunk in retrieved_chunks:
        for clause in chunk.get("relevant_clauses", []):
            # Here we assume each clause dict has an 'id'
            clause_id = clause.get("id")
            if clause_id and clause_id not in clause_map:
                clause_map[clause_id] = clause

    # Format all unique clauses into a string
    clauses_formatted = "\n".join(
        f"- ID: {clause['id']}\n  Text: {clause['text']}\n  Source: {clause.get('metadata', {}).get('doc_id', 'N/A')}"
        for clause in clause_map.values()
    )

    prompt = f"""
You are a regulatory compliance expert.

Below is the original Standard Operating Procedure (SOP) text, followed by a list of regulatory clauses retrieved from the database.
Your task is to produce an annotated version of the SOP text. In the annotated version, insert inline notes (e.g., in square brackets)
to highlight where the SOP meets or fails to meet the regulatory requirements, referencing the corresponding clause IDs.

=== SOP TEXT ===
{sop_text}

=== RETRIEVED REGULATORY CLAUSES ===
{clauses_formatted}

Please provide a detailed compliance analysis. Structure your output in Markdown Format.
"""
    return prompt

def generate_report(sop_path, retrieved_chunks, anthropic_client):
    """
    Generates a report by analyzing the SOP (Standard Operating Procedure) text and retrieved chunks using the provided anthropic client.

    Args:
        sop_path (str): The file path to the SOP document.
        retrieved_chunks (list): A list of text chunks retrieved for analysis.
        anthropic_client (object): An instance of the anthropic client used to invoke the analysis API.

    Returns:
        object: The response from the anthropic client after processing the prompt.
    """
    # Call the API. If the client returns an object, adjust to access its content.
    logger.info("Start generating analysis of the SOP...")
    with open(sop_path, "r", encoding="utf-8") as f:
        sop_text = f.read()
    prompt = create_template_prompt(sop_text, retrieved_chunks)
    response = anthropic_client.invoke(prompt)
    return response

def save_markdown(content, file_path="output/annotated_sop_report.md"):
    """
    Saves the provided Markdown content to a file.
    
    :param content: Markdown formatted text to save.
    :param file_path: Path to the file where the content will be saved (should end with '.md').
    """
    logger.info(f"Results saved as markdown file to path {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)