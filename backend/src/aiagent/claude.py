import os
import re
import json
from anthropic import Anthropic

# Default configuration constants
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 300


class ClaudeClient:
    """Wrapper for Claude API interactions"""
    
    def __init__(self, api_key=None, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS):
        """
        Initialize Claude API client
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens in response
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        
        # Configuration state
        self.system_context = None
        self.messages = []
        
        # Response state
        self._raw_response = None
        self._parsed_data = None
    
    def configure(self, context, message):
        """
        Configure the instance with system context and user message
        
        Args:
            context: System prompt/context
            message: User message (string or list of message dicts)
        """
        self.system_context = context
        
        # Handle both single message string and message array
        if isinstance(message, str):
            self.messages = [{"role": "user", "content": message}]
        else:
            self.messages = message
    
    def query(self):
        """
        Execute the API call to Claude
        
        Raises:
            ValueError: If context or messages not configured
        """
        if not self.system_context:
            raise ValueError("System context not configured. Call configure() first.")
        if not self.messages:
            raise ValueError("Messages not configured. Call configure() first.")
        
        # Make API call
        self._raw_response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_context,
            messages=self.messages
        )
        
        # Parse response
        self._parsed_data = self._parse_response(self._raw_response.content[0].text)
    
    def response(self):
        """
        Get the message component from the last query
        
        Returns:
            str: Claude's response message
        
        Raises:
            RuntimeError: If query() hasn't been called yet
        """
        if self._parsed_data is None:
            raise RuntimeError("No response available. Call query() first.")
        
        return self._parsed_data.get('message', '')
    
    def movies(self):
        """
        Get the recommended movies array from the last query
        
        Returns:
            list: Array of movie recommendation dicts with id, title, year, genre, reason
        
        Raises:
            RuntimeError: If query() hasn't been called yet
        """
        if self._parsed_data is None:
            raise RuntimeError("No response available. Call query() first.")
        
        return self._parsed_data.get('recommendations', [])
    
    def _parse_response(self, response_text):
        """
        Parse Claude's JSON response
        
        Args:
            response_text: Raw text response from Claude
        
        Returns:
            dict: Parsed data with 'message' and 'recommendations' keys
        """
        # Try to extract JSON from response text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return {
                    'message': parsed.get('message', ''),
                    'recommendations': parsed.get('recommendations', [])
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback if JSON parsing fails
        return {'message': response_text, 'recommendations': []}
