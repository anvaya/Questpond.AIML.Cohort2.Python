from docling.document_converter import DocumentConverter
import ollama
import time
from Shared.llm_wrapper import OllamaService


# Common synonyms to make the system "smarter" before the LLM step
CATEGORY_MAP = {
    "work experience": "experience",
    "employment history": "experience",
    "professional background": "experience",
    "career history": "experience",
    "academic history": "education",
    "qualifications": "education",
    "technical skills": "skills",
    "expertise": "skills",
    "skills":"skills",
    "education":"education",
}

def get_universal_chunks(pdf_path):
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    
    chunks = {}
    current_label = "header_pii"
    chunks[current_label] = []
    
    for item, level in doc.iterate_items():
        # Safely handle the Pylance attribute issues
        # Section_header is a standard label in Docling for titles
        is_header = getattr(item, "label", None) == "section_header"
        text = getattr(item, "text", "").strip()
        
        if not text: continue

        if is_header:
            # NORMALIZE the header name using our map or lowercase it
            clean_text = text.lower()
            current_label = CATEGORY_MAP.get(clean_text, clean_text).replace(" ", "_")
            chunks[current_label] = []
        else:
            chunks[current_label].append(text)
            
    return {k: "\n".join(v) for k, v in chunks.items()}

def get_standardized_map(raw_headers, chat_client: ollama.Client):
    """
    Maps raw resume headers to standard ATS categories.
    """
    prompt = f"""
    You are a Section Labeler for an ATS. Map these raw headers to standard categories:
    CATEGORIES: [CONTACT_INFO, SUMMARY, EXPERIENCE, EDUCATION, SKILLS, OTHER]
    
    INPUT: {raw_headers}
    
    RULES:
    1. Return VALID JSON only. 
    2. Format: {{"raw_header": "CATEGORY"}}
    """    
    return OllamaService().thinking_json_reply(prompt)   

def prepare_normalized_chunks(pdf_path, ollama_client: ollama.Client):
    """
    Normalizes resume chunks into ATS categories.
    """   
    chat_client = ollama_client
    retry_count = 3
    retry_delay = 2
    normalized_chunks = { "EXPERIENCE": "", "EDUCATION": "", "CONTACT_INFO": "", "SKILLS": "", "SUMMARY": "", "OTHER": "" }

    for attempt in range(retry_count + 1):
        try:
            raw_chunks = get_universal_chunks(pdf_path) # Get raw chunks first
            raw_headers = list(raw_chunks.keys())       # Extract raw headers   
            
            # 2. Get the mapping (e.g., {"Academia": "EDUCATION"})
            mapping = get_standardized_map(raw_headers, chat_client=chat_client)

            # 3. Create the Normalized Dictionary
            normalized_chunks = { "EXPERIENCE": "", "EDUCATION": "", "CONTACT_INFO": "", "SKILLS": "", "SUMMARY": "", "OTHER": "" }

            for raw_header, category in mapping.items():
                if category in normalized_chunks and raw_header in raw_chunks:
                    # CRITICAL FIX: Prepend the header itself! 
                    # This adds the Job Title and Dates back into the text.
                    header_text = f"\n### SECTION: {raw_header} ###\n"
                    content_text = raw_chunks[raw_header]
                    
                    # Append so we don't overwrite previous roles
                    normalized_chunks[category] += header_text + content_text        
        except Exception as e:
            last_error = e
            if attempt < retry_count:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:                
                print(f"All {retry_count + 1} attempts failed.")
                raise(last_error)
  
    # Now check your experience text before calling the LLM
    #print(f"DEBUG - Experience Text Length: {len(normalized_chunks['EXPERIENCE'])}")    
    return normalized_chunks