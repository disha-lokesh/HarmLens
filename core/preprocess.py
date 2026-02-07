"""
Text preprocessing for content moderation
"""

import re
import langdetect


def clean_text(text: str) -> dict:
    """
    Clean and normalize input text
    
    Args:
        text: Raw input text
        
    Returns:
        dict with cleaned_text, original_text, language
    """
    # Keep original for highlighting
    original = text.strip()
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = cleaned.strip()
    
    # Detect language
    try:
        lang = langdetect.detect(cleaned)
    except:
        lang = "unknown"
    
    return {
        "original": original,
        "cleaned": cleaned,
        "lowercase": cleaned.lower(),
        "language": lang
    }


def get_sentences(text: str) -> list:
    """
    Split text into sentences for analysis
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]
