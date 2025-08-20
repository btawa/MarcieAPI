"""
Image URL generation utilities.
Handles creating image URLs for cards based on codes and patterns.
"""
import re
from typing import List, Dict, Any


class ImageURLGenerator:
    """Generates image URLs for cards."""
    
    MARCIE_API_BASE = "https://storage.googleapis.com/marcieapi-images/"
    MARCIE_API_JP_BASE = "https://storage.googleapis.com/marcieapi-images/jp/"
    
    @classmethod
    def generate_english_url(cls, card: Dict[str, Any]) -> str:
        """Generate English image URL for a card."""
        from card_code_parser import parse_card_code
        
        # Parse the full code to get clean base code and rarity
        full_code = card.get('Code', '')
        parsed = parse_card_code(full_code)
        
        base_code = parsed.base_code
        rarity = parsed.primary_rarity
        
        # Handle slash codes (reprints) - use the first/primary version
        if '/' in full_code:
            return f"{cls.MARCIE_API_BASE}{base_code}{rarity}_eg.jpg"
        
        # Handle special rarities (P, B) that don't use rarity suffix
        elif rarity in ["P", "B"]:
            return f"{cls.MARCIE_API_BASE}{base_code}_eg.jpg"
        
        # Standard format: base_code + rarity + _eg.jpg
        else:
            return f"{cls.MARCIE_API_BASE}{base_code}{rarity}_eg.jpg"
    
    @classmethod
    def generate_japanese_url(cls, english_url: str) -> str:
        """Generate Japanese image URL from English URL pattern."""
        # Extract card pattern from English URL
        pattern = re.compile(r'([0-9]+)(-[0-9]+)([A-Z])')
        match = pattern.search(english_url)
        
        if match:
            set_num = match.group(1)
            card_num = match.group(2)  
            rarity = match.group(3)
            return f"{cls.MARCIE_API_JP_BASE}{set_num}{card_num}{rarity}.png"
        
        return None
    
    @classmethod
    def add_image_urls(cls, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add image URLs to list of cards."""
        for card in cards:
            # Generate English URL
            english_url = cls.generate_english_url(card)
            card['image_url'] = english_url
            
            # Generate Japanese URL
            japanese_url = cls.generate_japanese_url(english_url)
            card['image_url_jp'] = japanese_url
        
        return cards