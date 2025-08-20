import sqlite3
import json
import time
import logging
from typing import List, Dict, Optional

class CardDatabase:
    def __init__(self, db_path: str = "cards.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Cards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    base_code TEXT,
                    base_rarity TEXT,
                    variant_type TEXT,
                    secondary_code TEXT,
                    secondary_rarity TEXT,
                    element TEXT,
                    name_en TEXT,
                    cost TEXT,
                    multicard BOOLEAN,
                    type_en TEXT,
                    category_1 TEXT,
                    text_en TEXT,
                    job_en TEXT,
                    power INTEGER,
                    ex_burst BOOLEAN,
                    set_name TEXT,
                    source TEXT,
                    image_url TEXT,
                    japanese_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fetch history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fetch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    card_count INTEGER,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
    
    def save_cards(self, cards: List[Dict], source: str) -> bool:
        """Save cards to database with batched upsert for better performance"""
        import time
        start_time = time.time()
        logging.info(f"Starting database save for {len(cards)} cards from {source}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare batch data
                logging.info("Parsing and preparing card data...")
                prep_start = time.time()
                batch_data = []
                for card in cards:
                    # Convert Text_EN list to string if needed
                    text_en = card.get('Text_EN')
                    if isinstance(text_en, list):
                        text_en = ' '.join(text_en) if text_en else None
                    
                    # Parse code for additional metadata
                    from card_code_parser import parse_card_code
                    parsed_code = parse_card_code(card.get('Code', ''))
                    
                    batch_data.append((
                        card.get('Code'),
                        parsed_code.base_code,
                        parsed_code.primary_rarity,
                        parsed_code.variant_type,
                        parsed_code.secondary_code,
                        parsed_code.secondary_rarity,
                        card.get('Element'),
                        card.get('Name_EN'),
                        card.get('Cost'),
                        card.get('Multicard'),
                        card.get('Type_EN'),
                        card.get('Category_1'),
                        text_en,
                        card.get('Job_EN'),
                        card.get('Power'),
                        card.get('Ex_Burst'),
                        card.get('Set'),
                        source,
                        card.get('image_url'),
                        card.get('image_url_jp')
                    ))
                
                prep_time = time.time() - prep_start
                logging.info(f"Card data prepared in {prep_time:.1f}s, executing batch insert...")
                
                # Batch insert with executemany for better performance
                insert_start = time.time()
                cursor.executemany('''
                    INSERT OR REPLACE INTO cards (
                        code, base_code, base_rarity, variant_type, secondary_code, secondary_rarity, element, name_en, cost, multicard, 
                        type_en, category_1, text_en, job_en, power, 
                        ex_burst, set_name, source, image_url, japanese_url,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', batch_data)
                insert_time = time.time() - insert_start
                logging.info(f"Batch insert completed in {insert_time:.1f}s")
                
                # Log successful fetch
                cursor.execute('''
                    INSERT INTO fetch_history (source, success, card_count)
                    VALUES (?, ?, ?)
                ''', (source, True, len(cards)))
                
                logging.info("Committing transaction...")
                conn.commit()
                
                total_time = time.time() - start_time
                logging.info(f"Database save completed successfully in {total_time:.1f}s total")
                return True
                
        except Exception as e:
            total_time = time.time() - start_time
            logging.error(f"Database save failed after {total_time:.1f}s: {e}")
            # Log failed fetch
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO fetch_history (source, success, card_count, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (source, False, 0, str(e)))
                conn.commit()
            return False
    
    def get_all_cards(self) -> List[Dict]:
        """Retrieve all cards from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cards ORDER BY code')
            
            cards = []
            for row in cursor.fetchall():
                card = {
                    'Code': row['code'],
                    'Rarity': row['base_rarity'],
                    'Element': row['element'],
                    'Name_EN': row['name_en'],
                    'Cost': row['cost'],
                    'Multicard': bool(row['multicard']) if row['multicard'] is not None else False,
                    'Type_EN': row['type_en'],
                    'Category_1': row['category_1'],
                    'Text_EN': row['text_en'],
                    'Job_EN': row['job_en'],
                    'Power': row['power'],
                    'Ex_Burst': bool(row['ex_burst']) if row['ex_burst'] is not None else False,
                    'Set': row['set_name'],
                    'image_url': row['image_url'],
                    'image_url_jp': row['japanese_url']
                }
                cards.append(card)
            
            return cards
    
    def get_cards_by_code_prefix(self, code_prefix: str) -> List[Dict]:
        """Get cards matching code prefix"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cards WHERE code LIKE ? ORDER BY code', (f'{code_prefix}%',))
            
            cards = []
            for row in cursor.fetchall():
                card = {
                    'Code': row['code'],
                    'Rarity': row['base_rarity'],
                    'Element': row['element'],
                    'Name_EN': row['name_en'],
                    'Cost': row['cost'],
                    'Multicard': bool(row['multicard']) if row['multicard'] is not None else False,
                    'Type_EN': row['type_en'],
                    'Category_1': row['category_1'],
                    'Text_EN': row['text_en'],
                    'Job_EN': row['job_en'],
                    'Power': row['power'],
                    'Ex_Burst': bool(row['ex_burst']) if row['ex_burst'] is not None else False,
                    'Set': row['set_name'],
                    'image_url': row['image_url'],
                    'image_url_jp': row['japanese_url']
                }
                cards.append(card)
            
            return cards
    
    def get_last_fetch_time(self, source: str) -> Optional[float]:
        """Get the timestamp of the last successful fetch for a source"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fetch_time FROM fetch_history 
                WHERE source = ? AND success = 1 
                ORDER BY fetch_time DESC LIMIT 1
            ''', (source,))
            
            result = cursor.fetchone()
            if result:
                return time.mktime(time.strptime(result[0], '%Y-%m-%d %H:%M:%S'))
            return None
    
    def is_data_stale(self, source: str, max_age_hours: int = 24) -> bool:
        """Check if data from source is stale"""
        last_fetch = self.get_last_fetch_time(source)
        if not last_fetch:
            return True
        
        current_time = time.time()
        return (current_time - last_fetch) > (max_age_hours * 3600)