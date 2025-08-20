r"""
Advanced card code parser that preserves all information from Square's codes.
Handles reprints, legacy cards, boss cards, starter cards, etc.
"""
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedCardCode:
    """Structured representation of a parsed card code."""
    full_code: str           # Complete original code: "11-062R/PR-055"
    base_code: str           # Base card identifier: "11-062"  
    primary_rarity: str      # Primary rarity: "R"
    variant_type: str        # Type of variant: "reprint", "legacy", "boss", "starter", "normal"
    secondary_code: Optional[str] = None    # Secondary code if present: "PR-055"
    secondary_rarity: Optional[str] = None  # Secondary rarity if present
    
    def __str__(self):
        return self.full_code


class CardCodeParser:
    """Parses and normalizes FFTCG card codes."""
    
    @staticmethod
    def parse_code(raw_code: str) -> ParsedCardCode:
        """
        Parse a raw card code into structured components.
        
        Examples:
        - "11-062R/PR-055" -> reprint with promo variant
        - "Re-001H/12-002H" -> legacy reprint  
        - "B-001" -> boss card
        - "1-187S" -> starter card
        - "1-001H" -> normal card
        """
        if not raw_code:
            return ParsedCardCode(
                full_code="", base_code="", primary_rarity="", variant_type="unknown"
            )
        
        full_code = raw_code.strip()
        
        # Handle slash-separated codes (reprints)
        if '/' in full_code:
            return CardCodeParser._parse_reprint_code(full_code)
        
        # Handle Re- prefix (legacy reprints)
        elif full_code.startswith('Re-'):
            return CardCodeParser._parse_legacy_code(full_code)
        
        # Handle B- prefix (boss cards)
        elif full_code.startswith('B-'):
            return CardCodeParser._parse_boss_code(full_code)
        
        # Handle PR- prefix (promo cards)  
        elif full_code.startswith('PR-'):
            return CardCodeParser._parse_promo_code(full_code)
        
        # Handle C- prefix (special cards)
        elif full_code.startswith('C-'):
            return CardCodeParser._parse_special_code(full_code)
        
        # Handle normal cards (possibly with starter suffix)
        else:
            return CardCodeParser._parse_normal_code(full_code)
    
    @staticmethod
    def _parse_reprint_code(code: str) -> ParsedCardCode:
        """Parse reprint codes like '11-062R/PR-055'."""
        parts = code.split('/')
        primary_part = parts[0].strip()
        secondary_part = parts[1].strip() if len(parts) > 1 else None
        
        # Parse primary part (e.g., "11-062R")
        base_code, primary_rarity = CardCodeParser._extract_base_and_rarity(primary_part)
        
        # Parse secondary part if present
        secondary_code = None
        secondary_rarity = None
        if secondary_part:
            secondary_code, secondary_rarity = CardCodeParser._extract_base_and_rarity(secondary_part)
        
        return ParsedCardCode(
            full_code=code,
            base_code=base_code,
            primary_rarity=primary_rarity,
            variant_type="reprint",
            secondary_code=secondary_code,
            secondary_rarity=secondary_rarity
        )
    
    @staticmethod
    def _parse_legacy_code(code: str) -> ParsedCardCode:
        """Parse legacy codes like 'Re-001H/12-002H'."""
        # Remove Re- prefix for base code extraction
        without_prefix = code[3:]  # Remove "Re-"
        
        if '/' in without_prefix:
            parts = without_prefix.split('/')
            primary_part = parts[0].strip()
            secondary_part = parts[1].strip()
            
            base_code, primary_rarity = CardCodeParser._extract_base_and_rarity(primary_part)
            secondary_code, secondary_rarity = CardCodeParser._extract_base_and_rarity(secondary_part)
            
            return ParsedCardCode(
                full_code=code,
                base_code=f"Re-{base_code}",
                primary_rarity=primary_rarity,
                variant_type="legacy",
                secondary_code=secondary_code,
                secondary_rarity=secondary_rarity
            )
        else:
            base_code, primary_rarity = CardCodeParser._extract_base_and_rarity(without_prefix)
            return ParsedCardCode(
                full_code=code,
                base_code=f"Re-{base_code}",
                primary_rarity=primary_rarity,
                variant_type="legacy"
            )
    
    @staticmethod
    def _parse_boss_code(code: str) -> ParsedCardCode:
        """Parse boss codes like 'B-001'."""
        base_code, rarity = CardCodeParser._extract_base_and_rarity(code)
        
        return ParsedCardCode(
            full_code=code,
            base_code=base_code,
            primary_rarity=rarity or "B",  # Boss cards use B rarity
            variant_type="boss"
        )
    
    @staticmethod
    def _parse_promo_code(code: str) -> ParsedCardCode:
        """Parse promo codes like 'PR-055'."""
        return ParsedCardCode(
            full_code=code,
            base_code=code,
            primary_rarity="P",  # Promos use P rarity
            variant_type="promo"
        )
    
    @staticmethod
    def _parse_special_code(code: str) -> ParsedCardCode:
        """Parse special codes like 'C-001'."""
        return ParsedCardCode(
            full_code=code,
            base_code=code,
            primary_rarity="T",  # Special cards often use T (tournament/special)
            variant_type="special"
        )
    
    @staticmethod
    def _parse_normal_code(code: str) -> ParsedCardCode:
        """Parse normal codes like '1-001H' or '1-187S'."""
        base_code, rarity = CardCodeParser._extract_base_and_rarity(code)
        
        # Determine if it's a starter card
        variant_type = "starter" if rarity == "S" else "normal"
        
        return ParsedCardCode(
            full_code=code,
            base_code=base_code,
            primary_rarity=rarity,
            variant_type=variant_type
        )
    
    @staticmethod
    def _extract_base_and_rarity(code_part: str) -> Tuple[str, str]:
        """
        Extract base code and rarity from a code part.
        
        Examples:
        - "11-062R" -> ("11-062", "R")
        - "1-187S" -> ("1-187", "S") 
        - "B-001" -> ("B-001", "")
        """
        if not code_part:
            return "", ""
        
        # Check if last character is a rarity letter
        if len(code_part) > 1 and code_part[-1].isalpha():
            # Common rarity suffixes
            if code_part[-1] in "HRLCSPB":
                return code_part[:-1], code_part[-1]
        
        # No rarity suffix found
        return code_part, ""


# Convenience functions
def parse_card_code(raw_code: str) -> ParsedCardCode:
    """Parse a card code into structured components."""
    return CardCodeParser.parse_code(raw_code)


def get_base_code(raw_code: str) -> str:
    """Get the base code for grouping purposes."""
    return CardCodeParser.parse_code(raw_code).base_code


def get_variant_type(raw_code: str) -> str:
    """Get the variant type of a card."""
    return CardCodeParser.parse_code(raw_code).variant_type