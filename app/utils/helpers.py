import re
import json
from typing import Dict, Any, Optional, List

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Attempt to extract a JSON object from text"""
    if not text:
        return None
    
    # Try to find a JSON object in the text
    json_pattern = r'(\{[\s\S]*\}|\[[\s\S]*\])'
    match = re.search(json_pattern, text)
    
    if match:
        try:
            json_str = match.group(0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    return None

def format_error_message(error: Exception) -> str:
    """Format an exception into a user-friendly error message"""
    error_str = str(error)
    
    # Handle common error cases
    if "401" in error_str or "unauthorized" in error_str.lower():
        return "Authentication failed. Please check your API key."
    
    if "429" in error_str or "rate limit" in error_str.lower():
        return "Rate limit exceeded. Please try again later."
    
    if "timeout" in error_str.lower():
        return "Request timed out. Please try again."
    
    # Return the original error if no specific formatting is needed
    return error_str