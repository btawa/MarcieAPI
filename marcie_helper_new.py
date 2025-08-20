"""
Clean, modular version of marcie_helper.
Uses separate modules for different concerns.
"""
import json
import logging
import requests
from typing import List, Dict, Any

from square_converter import convert_square_cards
from ffdecks_converter import convert_ffdecks_cards  
from image_url_generator import ImageURLGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')


def load_square_api(url: str) -> Dict[str, Any]:
    """Load data from Square Enix API."""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    # Square API expects this specific payload format
    payload = '{"language":"en","text":"","type":[],"element":[],"cost":[],"rarity":[],"power":[],"category_1":[],"set":[],"multicard":"","ex_burst":"","code":"","special":"","exactmatch":0}'
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error loading Square API: {e}")
        raise


def load_ffdecks_api(url: str) -> Dict[str, Any]:
    """Load data from FFDecks API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error loading FFDecks API: {e}")
        raise


def process_square_cards(square_url: str) -> List[Dict[str, Any]]:
    """
    Fetch and process cards from Square API.
    Returns standardized card format with image URLs.
    """
    # Load raw data
    raw_data = load_square_api(square_url)
    raw_cards = raw_data.get('cards', [])
    
    logging.info(f"Loaded {len(raw_cards)} raw cards from Square API")
    
    # Convert to standardized format
    converted_cards = convert_square_cards(raw_cards)
    
    # Remove duplicates by Code
    unique_cards = []
    seen_codes = set()
    for card in converted_cards:
        code = card.get('Code')
        if code and code not in seen_codes:
            seen_codes.add(code)
            unique_cards.append(card)
    
    logging.info(f"After deduplication: {len(unique_cards)} unique Square cards")
    
    # Add image URLs
    cards_with_images = ImageURLGenerator.add_image_urls(unique_cards)
    
    return cards_with_images


def process_ffdecks_promos(ffdecks_url: str) -> List[Dict[str, Any]]:
    """
    Fetch and process promo cards from FFDecks API.
    Returns only promo cards (PR-xxx codes).
    """
    # Load raw data
    raw_data = load_ffdecks_api(ffdecks_url)
    raw_cards = raw_data.get('cards', [])
    
    logging.info(f"Loaded {len(raw_cards)} raw cards from FFDecks API")
    
    # Convert to standardized format
    converted_cards = convert_ffdecks_cards(raw_cards)
    
    # Filter for promo cards only
    promo_cards = []
    for card in converted_cards:
        code = card.get('Code', '')
        if code.startswith('PR-'):
            promo_cards.append(card)
    
    logging.info(f"Filtered to {len(promo_cards)} promo cards from FFDecks")
    
    # Add image URLs
    promos_with_images = ImageURLGenerator.add_image_urls(promo_cards)
    
    return promos_with_images


# Legacy compatibility functions
def loadSquare(path: str) -> Dict[str, Any]:
    """Legacy compatibility - use load_square_api instead."""
    return load_square_api(path)


def loadFfdecks(path: str) -> Dict[str, Any]:
    """Legacy compatibility - use load_ffdecks_api instead."""
    return load_ffdecks_api(path)


def squaretomarcieapi2(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Legacy compatibility - use convert_square_cards instead."""
    return convert_square_cards(cards)


def ffdeckstomarcieapi(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Legacy compatibility - use convert_ffdecks_cards instead."""
    return convert_ffdecks_cards(cards)


def urlset(cards_list: List[Dict[str, Any]]) -> List[str]:
    """Legacy compatibility - get unique image URLs from cards."""
    urls = []
    for card in cards_list:
        if card.get('image_url'):
            urls.append(card['image_url'])
        if card.get('image_url_jp'):
            urls.append(card['image_url_jp'])
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(urls))


def addimageurltojson(cards_list: List[Dict[str, Any]], image_list: List[str]) -> List[Dict[str, Any]]:
    """Legacy compatibility - image URLs are now added automatically."""
    return ImageURLGenerator.add_image_urls(cards_list)


def addjapaneseurls(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Legacy compatibility - Japanese URLs are now added automatically.""" 
    return ImageURLGenerator.add_image_urls(cards)