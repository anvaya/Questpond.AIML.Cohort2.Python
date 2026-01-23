import ollama
import json
import time
from typing import Optional, Dict, Any, List, Union
from jsonschema import validate, ValidationError as JsonSchemaValidationError

QUICK_CHAT_MODEL =  'gpt-oss:20b-cloud' # 'qwen3-next:80b-cloud' #'qwen3:1.7b'
THINKING_CHAT_MODEL = 'qwen3-next:80b-cloud' #'qwen3-next:80b-cloud' #'qwen3:14b'
DEFAULT_RETRY_COUNT = 1
DEFAULT_RETRY_DELAY_SECONDS = 2

class OllamaServiceError(Exception):
    """Custom exception for Ollama service errors."""
    pass


class OllamaService:
    """
    Centralized service for Ollama API calls with retry logic and JSON schema validation.
    """

    def __init__(
        self,
        host: str = 'http://localhost:11434',
        default_retry_count: int = DEFAULT_RETRY_COUNT,
        default_retry_delay: float = DEFAULT_RETRY_DELAY_SECONDS
    ):
        """
        Initialize the Ollama service.

        Args:
            host: Ollama server host URL
            default_retry_count: Default number of retry attempts (default: 1)
            default_retry_delay: Default delay between retries in seconds (default: 2)
        """
        self.client = ollama.Client(host=host)
        self.default_retry_count = default_retry_count
        self.default_retry_delay = default_retry_delay

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = THINKING_CHAT_MODEL,
        think: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None,
        extract_json: bool = False
    ) -> Union[ollama.ChatResponse, Dict[str, Any]]:
        """
        Execute a chat completion with retry logic and optional JSON schema validation.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (default: qwen3:14b)
            think: Enable thinking mode (default: False)
            json_schema: Optional JSON schema to validate the response against
            retry_count: Number of retry attempts (default: uses service default)
            retry_delay: Delay between retries in seconds (default: uses service default)
            extract_json: If True, attempts to extract JSON from response content

        Returns:
            Dict containing the Ollama response

        Raises:
            OllamaServiceError: If all retry attempts fail or validation fails
        """
        retry_count = retry_count if retry_count is not None else self.default_retry_count
        retry_delay = retry_delay if retry_delay is not None else self.default_retry_delay

        last_error = None

        for attempt in range(retry_count + 1):
            try:
                response = self.client.chat(
                    model=model,
                    messages=messages,
                    options={'num_gpu': 999, 'think': think}
                )

                # Extract JSON if requested
                if extract_json:
                    response = self._extract_json_from_response(response)

                # Validate against schema if provided
                if json_schema is not None:
                    self._validate_response(response, json_schema)

                return response

            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"All {retry_count + 1} attempts failed.")

        # If we get here, all retries failed
        error_msg = f"Failed after {retry_count + 1} attempts. Last error: {str(last_error)}"
        raise OllamaServiceError(error_msg)

    def generate_embedding(
        self,
        prompt: str,
        model: str = 'nomic-embed-text',
        retry_count: Optional[int] = None,
        retry_delay: Optional[float] = None
    ) -> List[float]:
        """
        Generate an embedding for the given text with retry logic.

        Args:
            prompt: Text to generate embedding for
            model: Embedding model name (default: nomic-embed-text)
            retry_count: Number of retry attempts (default: uses service default)
            retry_delay: Delay between retries in seconds (default: uses service default)

        Returns:
            List of floats representing the embedding

        Raises:
            OllamaServiceError: If all retry attempts fail
        """
        retry_count = retry_count if retry_count is not None else self.default_retry_count
        retry_delay = retry_delay if retry_delay is not None else self.default_retry_delay

        last_error = None

        for attempt in range(retry_count + 1):
            try:
                response = self.client.embeddings(model=model, prompt=prompt)
                return response['embedding']

            except Exception as e:
                last_error = e
                if attempt < retry_count:
                    print(f"Embedding generation attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"All {retry_count + 1} embedding attempts failed.")

        error_msg = f"Embedding generation failed after {retry_count + 1} attempts. Last error: {str(last_error)}"
        raise OllamaServiceError(error_msg)

    def _extract_json_from_response(self, response: Union[ollama.ChatResponse, Dict[str, Any]]) -> Union[ollama.ChatResponse, Dict[str, Any]]:
        """
        Attempt to extract JSON from the response message content.

        Args:
            response: Ollama chat response (ChatResponse or dict-like object)

        Returns:
            Response with parsed JSON content if successful

        Raises:
            OllamaServiceError: If JSON extraction fails
        """
        try:
            if 'message' in response and 'content' in response['message']:
                content = response['message']['content']

                # Try to parse as JSON directly
                try:
                    parsed_json = json.loads(content)
                    response['message']['content'] = parsed_json
                    return response
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        if json_end != -1:
                            json_str = content[json_start:json_end].strip()
                            parsed_json = json.loads(json_str)
                            response['message']['content'] = parsed_json
                            return response
                    elif '```' in content:
                        json_start = content.find('```') + 3
                        json_end = content.find('```', json_start)
                        if json_end != -1:
                            json_str = content[json_start:json_end].strip()
                            parsed_json = json.loads(json_str)
                            response['message']['content'] = parsed_json
                            return response

            # If no JSON found, return original response
            return response

        except Exception as e:
            raise OllamaServiceError(f"Failed to extract JSON from response: {str(e)}")

    def _validate_response(self, response: Union[ollama.ChatResponse, Dict[str, Any]], schema: Dict[str, Any]) -> None:
        """
        Validate the response content against a JSON schema.

        Args:
            response: Ollama chat response (ChatResponse or dict-like object)
            schema: JSON schema to validate against

        Raises:
            OllamaServiceError: If validation fails
        """
        try:
            content = None

            # Extract content from response
            if 'message' in response and 'content' in response['message']:
                content = response['message']['content']
            elif 'content' in response:
                content = response['content']

            if content is None:
                raise OllamaServiceError("No content found in response to validate")

            # Validate against schema
            validate(instance=content, schema=schema)

        except JsonSchemaValidationError as e:
            raise OllamaServiceError(f"JSON schema validation failed: {e.message}")
        except Exception as e:
            raise OllamaServiceError(f"Response validation error: {str(e)}")

    """
    Utility function to get a json response
    from the LLM using the QUICK model
    """
    def fast_json_reply(self, prompt, retry_count=3):
        response = self.chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            model=QUICK_CHAT_MODEL,        
            extract_json=True,        
            retry_count=3
        )        
        return response['message']['content']

    """
    Utility function to get a json response
    from the LLM using the THINKING model
    """    
    def thinking_json_reply(self, prompt, retry_count=3):
        response = self.chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            model=THINKING_CHAT_MODEL,        
            extract_json=True,        
            retry_count=3,
            think=True
        )        
        return response['message']['content']
        

# Maintain backward compatibility with existing code
class llm:
    """
    Backward compatibility wrapper for existing code.
    Deprecated: Use OllamaService instead for new code.
    """

    Ollama_client = ollama.Client(
        host='http://localhost:11434',
    )

    def chat_completion(self, messages, model=THINKING_CHAT_MODEL, think: bool = False):
        return self.Ollama_client.chat(
            model=model, messages=messages,
            options={'num_gpu': 999, 'think': think}
        )


# Convenience function to get a default service instance
_default_service: Optional[OllamaService] = None


def get_ollama_service() -> OllamaService:
    """
    Get a singleton instance of the Ollama service.

    Returns:
        OllamaService instance
    """
    global _default_service
    if _default_service is None:
        _default_service = OllamaService()
    return _default_service