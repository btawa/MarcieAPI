"""
Text normalization utilities for FFTCG card data.
Handles Unicode characters, special symbols, and formatting.
"""
import re

class TextNormalizer:
    """Handles all text normalization and character replacement."""
    
    # Unicode character mappings
    UNICODE_REPLACEMENTS = {
        # Brackets
        "\u300a": "(",  # Left double angle bracket
        "\u300b": ")",  # Right double angle bracket
        
        # Special symbols
        "&middot;": "\u00B7",  # Middle dot
        "\u25CB": "True",      # White circle (bubble)
        "\u3007": "True",      # Ideographic number zero
        "\u2015": "",          # Horizontal bar
        "\u00fa": "u",         # u with acute accent (Cuchulainn)
        
        # Element symbols (Japanese kanji to English)
        "\u571F": "Earth",     # 土
        "\u6c34": "Water",     # 水
        "\u706b": "Fire",      # 火
        "\u98a8": "Wind",      # 風
        "\u6c37": "Ice",       # 氷
        "\u5149": "Light",     # 光
        "\u95c7": "Dark",      # 闇
        "\u96f7": "Lightning", # 雷
        
        # Fullwidth numbers to normal numbers
        "\uFF10": "0", "\uFF11": "1", "\uFF12": "2", "\uFF13": "3", "\uFF14": "4",
        "\uFF15": "5", "\uFF16": "6", "\uFF17": "7", "\uFF18": "8", "\uFF19": "9",
        
        # Special game terms
        "\u4E00\u822C": "Generic",    # 一般
        "\u30C0\u30EB": "Dull",       # ダル (tap symbol)
        "\u300a\u0053\u300b": "[Special]",  # Special switch
    }
    
    # Regex patterns for markup removal/replacement
    MARKUP_PATTERNS = [
        # Remove special ability markup [[s]]text[[/]]
        (r"\[\[s\]\](.*?)\[\[/\]\]", r"\1"),
        
        # Remove italics markup [[i]]text[[/]]
        (r"\[\[i\]\](.*?)\[\[/\]\]", r"\1"),
        
        # EX Burst formatting
        (r"\[\[ex\]\]EX BURST\s*\[\[/\]\]\s*", "[EX BURST] "),
        (r"\[\[ex\]\]EX BURS\s*\[\[/\]\]T\s*", "[EX BURST] "),  # Handle typo
        (r"^EX BURST", "[EX BURST]"),
        
        # Line breaks
        (r"\[\[br\]\]", "\n"),
        
        # Clean up double quotes (Yuri 7-128 issue)
        (r'""', '"'),
    ]
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Apply all text normalizations to a string."""
        if not text:
            return text
            
        # Apply Unicode replacements
        for old, new in cls.UNICODE_REPLACEMENTS.items():
            text = text.replace(old, new)
        
        # Apply regex patterns
        for pattern, replacement in cls.MARKUP_PATTERNS:
            text = re.sub(pattern, replacement, text)
            
        return text
    
    @classmethod
    def normalize_boolean_field(cls, value: str) -> bool:
        """Convert text boolean indicators to actual booleans."""
        normalized = cls.normalize_text(str(value))
        return normalized in ("True", "1")


class FFDecksNormalizer:
    """Handles FFDecks-specific text normalization."""
    
    FFDECKS_REPLACEMENTS = {
        # Special symbols
        '{s}': '[Special]',
        '{x}': '[EX BURST]',
        '{d}': '(Dull)',
        
        # Elements
        '{a}': '(Water)',
        '{w}': '(Wind)',
        '{e}': '(Earth)',
        '{f}': '(Fire)',
        '{i}': '(Ice)',
        '{l}': '(Lightning)',
        
        # Numbers
        '{0}': '(0)', '{1}': '(1)', '{2}': '(2)', '{3}': '(3)', '{4}': '(4)',
        '{5}': '(5)', '{6}': '(6)', '{7}': '(7)', '{8}': '(8)', '{9}': '(9)',
        
        # Clean up unwanted characters
        '*': '', '%': '', '~': '',
        '\u2015': '-',  # Horizontal bar
        '\u00fa': 'u',  # u with acute accent
    }
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Apply FFDecks-specific normalizations."""
        if not text:
            return text
            
        for old, new in cls.FFDECKS_REPLACEMENTS.items():
            text = text.replace(old, new)
            
        return text