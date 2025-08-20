"""
Square Enix API data converter.
Converts raw Square API data into standardized card format.
"""
import re
from typing import List, Dict, Any, Optional
from text_normalizer import TextNormalizer


class SquareCardConverter:
    """Converts Square Enix API data to standardized format."""
    
    @staticmethod
    def convert_power(power_value: str) -> Optional[int]:
        """Convert power field, handling special cases."""
        if not power_value or power_value.strip() == "":
            return None
        
        # Check for dash characters indicating no power
        if re.search(r'[\u2015\u2212\u002D\uFF0D\u30FC]', power_value):
            return None
            
        try:
            return int(power_value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def convert_code(code_value: str) -> tuple[str, Optional[str]]:
        """
        Convert code field using the improved parser.
        Returns (full_code, rarity_override)
        """
        from card_code_parser import parse_card_code
        
        if not code_value:
            return code_value, None
        
        parsed = parse_card_code(code_value)
        
        # Return full code (preserving all info) and any rarity override
        rarity_override = None
        if parsed.variant_type in ["boss", "starter", "special"]:
            rarity_override = parsed.primary_rarity
            
        return parsed.full_code, rarity_override
    
    @staticmethod
    def convert_element(element_data: Any) -> Optional[str]:
        """Convert element field, handling both list and string formats."""
        if not element_data:
            return None
            
        if isinstance(element_data, list):
            # Join multiple elements with /
            normalized_elements = [TextNormalizer.normalize_text(elem) for elem in element_data]
            return "/".join(normalized_elements)
        else:
            return TextNormalizer.normalize_text(str(element_data))
    
    @staticmethod
    def convert_text(text_data: str) -> Optional[List[str]]:
        """Convert text field, splitting into lines and cleaning."""
        if not text_data:
            return None
            
        # Normalize and split into lines
        normalized_text = TextNormalizer.normalize_text(text_data)
        lines = normalized_text.split('\n')
        
        # Clean up whitespace on each line
        cleaned_lines = []
        for line in lines:
            cleaned = re.sub(r'^\s+', '', line)  # Leading whitespace
            cleaned = re.sub(r'\s+$', '', cleaned)  # Trailing whitespace
            if cleaned:  # Only add non-empty lines
                cleaned_lines.append(cleaned)
        
        return cleaned_lines if cleaned_lines else None
    
    @staticmethod
    def convert_set(set_data: Any) -> Optional[str]:
        """Convert set field, handling both list and string formats."""
        if not set_data:
            return None
            
        # Handle list format (new Square API behavior)
        if isinstance(set_data, list) and len(set_data) > 0:
            return str(set_data[0])
        
        return str(set_data)
    
    @classmethod
    def convert_card(cls, raw_card: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single raw Square card to standardized format."""
        converted = {}
        
        # Handle code and potential rarity override
        code, rarity_override = cls.convert_code(raw_card.get('code', ''))
        converted['Code'] = code
        
        # Handle rarity (with potential override from code)
        rarity = raw_card.get('rarity', '')
        if rarity_override:
            converted['Rarity'] = rarity_override
        elif rarity:
            converted['Rarity'] = rarity[0] if rarity else 'T'
        else:
            converted['Rarity'] = 'T'
        
        # Convert other fields
        converted['Element'] = cls.convert_element(raw_card.get('element'))
        converted['Name_EN'] = TextNormalizer.normalize_text(raw_card.get('name_en', ''))
        
        # Handle cost
        cost = raw_card.get('cost')
        converted['Cost'] = int(cost) if cost else 0
        
        # Boolean fields
        converted['Multicard'] = TextNormalizer.normalize_boolean_field(raw_card.get('multicard', ''))
        converted['Ex_Burst'] = TextNormalizer.normalize_boolean_field(raw_card.get('ex_burst', ''))
        
        # Other text fields
        converted['Type_EN'] = TextNormalizer.normalize_text(raw_card.get('type_en', ''))
        converted['Category_1'] = TextNormalizer.normalize_text(raw_card.get('category_1', ''))
        converted['Job_EN'] = TextNormalizer.normalize_text(raw_card.get('job_en', ''))
        
        # Complex fields
        converted['Power'] = cls.convert_power(raw_card.get('power', ''))
        converted['Text_EN'] = cls.convert_text(raw_card.get('text_en', ''))
        converted['Set'] = cls.convert_set(raw_card.get('set'))
        
        return converted


def convert_square_cards(raw_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert list of raw Square cards to standardized format."""
    return [SquareCardConverter.convert_card(card) for card in raw_cards]