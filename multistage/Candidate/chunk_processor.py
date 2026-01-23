import ollama
from Candidate.schemas.RawExperience import RawExperienceItem
from pydantic import TypeAdapter
from typing import List
import pathlib    
from Shared.llm_wrapper import OllamaService

def recover_identity(chunks, chat_client: ollama.Client):
    """
    Consolidates header and footer info to find the candidate's name and links.
    """
    # We combine 'contact_info' and 'other' because links often hide at the bottom
    search_text = chunks.get('CONTACT_INFO', '') + "\n" + chunks.get('OTHER', '')
    #print(f"DEBUG - Searching for name", search_text)
    prompt = f"""
    You are an Identity Recovery Agent. Look at this text from a resume.
    
    ### TASK:
    Extract the candidate's full name. 
    CLUE: If not explicitly stated, check the usernames in LinkedIn/GitHub links or the Personal Website URL.
    
    ### TEXT:
    {search_text}
    
    ### RETURN JSON ONLY:
    {{
      "full_name": "extracted name",
      "email": "extracted email",
      "linkedin": "url",
      "github": "url"
    }}
    """
    
    return OllamaService().thinking_json_reply(prompt)    
  

def extract_raw_experience(experience_text, chat_client: ollama.Client):
    """
    Extracts raw dates and titles from the combined experience text.
    """

    schema = TypeAdapter(List[RawExperienceItem]).json_schema()
    
    prompt = f"""
   You are a Chronological Reconstruction Specialist for an ATS. 

### LOGIC RULES:
1. DATE INHERITANCE: If a project or role (like 'SCBTIMS') is listed without specific dates, infer them from the preceding section. If the role immediately prior ended in 06/2016, and this entry follows it, assign the start_date as '06/2016'.
2. ONGOING STATUS: If a role is the first one listed and lacks an end date, or if its content suggests current involvement (e.g., 'Was responsible for... Worked with...'), mark end_date_raw as 'Present'.
3. RAW TRANSCRIPTION: Extract 'start_date_raw' and 'end_date_raw' as found or inferred. Do NOT calculate months.
4. While calculating domains, try to infer from technologies and responsibilities.
5. Do not guess or invent any information not present in the text. If no information is available for a certain column, use null or an empty list as appropriate.
6. If you see role end date indicating "Present", "Ongoing", "Current", or similar, use "Present" as end_date_raw. You must set end_date_raw to either a date string or "Present". If you cannot determine, use null.
7. Respect field names given in the OUTPUT SCHEMA, do not change them.
8. Follow the OUTPUT SCHEMA strictly. Return JSON only. 

### SKILL EXTRACTION RULES:
- Extract ALL mentioned technologies, tools, languages, frameworks, platforms, and methodologies.
- Do NOT normalize names.
- Do NOT infer skills.
- Use the exact spelling as found in text.
- Attach a source tag:
  - technology_list
  - skills_section
  - responsibility
  
### INPUT TEXT:
{experience_text}

### OUTPUT SCHEMA (JSON):
{schema}
    """
    
    # save_path = pathlib.Path(__file__).parent.parent / "temp" / "raw_experience_prompt.txt" 
    # save_path.parent.mkdir(parents=True, exist_ok=True)
    # with open(save_path, 'w', encoding='utf-8') as f:
    #     f.write(prompt)

    return OllamaService().thinking_json_reply(prompt)
    
    # save_path = pathlib.Path(__file__).parent / "output" / "raw_experience_.json"
    # save_path.parent.mkdir(parents=True, exist_ok=True)
    # with open(save_path, 'w', encoding='utf-8') as f:
    #     import json
    #     json.dump(response['message']['content'], f, indent=2)      
   