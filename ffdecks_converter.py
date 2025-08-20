"""
FFDecks API data converter.
Converts raw FFDecks API data into standardized card format.
"""
import re
import roman
from typing import List, Dict, Any, Optional
from text_normalizer import FFDecksNormalizer


class FFDecksCardConverter:
    """Converts FFDecks API data to standardized format."""
    
    @staticmethod
    def convert_element(element_data: Any, elements_data: List[str]) -> Optional[str]:
        """Handle FFDecks dual element logic."""
        if element_data is not None:
            return FFDecksNormalizer.normalize_text(element_data)
        
        # Handle multi-element cards
        if elements_data and len(elements_data) > 0:
            normalized_elements = [FFDecksNormalizer.normalize_text(elem) for elem in elements_data]
            return "/".join(normalized_elements)
        
        return None
    
    @staticmethod
    def convert_set_from_code(code: str) -> Optional[str]:
        """Determine set from card code."""
        if not code:
            return None
            
        # Promo cards have no set
        if re.match(r'^PR-', code):
            return None
        
        # Extract set number and convert to Roman numeral
        match = re.match(r'^\d+', code)
        if match:
            set_number = int(match.group(0))
            return f'Opus {roman.toRoman(set_number)}'
        
        return None
    
    @classmethod
    def convert_card(cls, raw_card: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single raw FFDecks card to standardized format."""
        converted = {}
        
        # Basic fields
        converted['Code'] = FFDecksNormalizer.normalize_text(raw_card.get('serial_number', ''))
        converted['Name_EN'] = FFDecksNormalizer.normalize_text(raw_card.get('name', ''))
        converted['Cost'] = raw_card.get('cost', 0)
        
        # Rarity (take first character)
        rarity = FFDecksNormalizer.normalize_text(raw_card.get('rarity', ''))
        converted['Rarity'] = rarity[0] if rarity else 'T'
        
        # Boolean fields
        converted['Ex_Burst'] = raw_card.get('is_ex_burst', False)
        converted['Multicard'] = raw_card.get('is_multi_playable', False)
        
        # Text fields
        converted['Job_EN'] = FFDecksNormalizer.normalize_text(raw_card.get('job', ''))
        converted['Type_EN'] = FFDecksNormalizer.normalize_text(raw_card.get('type', ''))
        converted['Category_1'] = FFDecksNormalizer.normalize_text(raw_card.get('category', ''))
        converted['Power'] = raw_card.get('power')
        
        # Handle element logic
        converted['Element'] = cls.convert_element(
            raw_card.get('element'), 
            raw_card.get('elements', [])
        )
        
        # Set from code
        converted['Set'] = cls.convert_set_from_code(converted['Code'])
        
        # Handle abilities text
        abilities = raw_card.get('abilities', [])
        if abilities:
            text_lines = []
            for ability in abilities:
                normalized = FFDecksNormalizer.normalize_text(str(ability))
                if normalized:
                    text_lines.append(normalized)
            converted['Text_EN'] = text_lines if text_lines else None
        else:
            converted['Text_EN'] = None
        
        return converted


def convert_ffdecks_cards(raw_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert list of raw FFDecks cards to standardized format."""
    return [FFDecksCardConverter.convert_card(card) for card in raw_cards]