from openai import OpenAI
import ollama

OPENAI_API_KEY = "" #can fetch API key from .env here.
if(len(OPENAI_API_KEY)>0):
    client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding_openAI(text):
    """Generates a vector embedding for the given text."""
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def get_embedding(text):
    """Generates a 768-dimensional vector using local Ollama instance."""       
    # nomic-embed-text is highly rated for technical/long-form text    
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response['embedding']