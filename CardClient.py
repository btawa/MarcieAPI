import time
import logging

from makejson import pull_ffdecks_promos, pull_square_cards
from database import CardDatabase


class CardClient():
    def __init__(self):
        self.cards = []
        self.lastfetch = time.time()
        self.lock = False
        self.db = CardDatabase()
        self.last_selective_sync_results = None
        
        # Simulation flags for testing
        self.simulate_square_down = False
        self.simulate_ffdecks_down = False

    def pull_new_cards(self):
        """Fetch cards from APIs and upsert to database"""
        start_time = time.time()
        logging.info("=== Starting card sync process ===")
        
        try:
            # Try Square first (priority source)
            logging.info("Fetching cards from Square API...")
            square_start = time.time()
            try:
                if self.simulate_square_down:
                    logging.warning("SIMULATION: Square API is down (simulated)")
                    raise Exception("Simulated Square API outage")
                
                square_cards = pull_square_cards()
                square_fetch_time = time.time() - square_start
                logging.info(f"Square API fetch completed: {len(square_cards)} cards in {square_fetch_time:.1f}s")
                
                if square_cards:
                    logging.info("Saving Square cards to database...")
                    db_start = time.time()
                    self.db.save_cards(square_cards, 'square')
                    db_time = time.time() - db_start
                    logging.info(f"Square cards saved to database in {db_time:.1f}s")
                else:
                    logging.warning("No Square cards received")
            except Exception as e:
                logging.error(f"Failed to fetch from Square API: {e}")
            
            # Try FFDecks (supplementary source)
            logging.info("Fetching promos from FFDecks API...")
            ffdecks_start = time.time()
            try:
                if self.simulate_ffdecks_down:
                    logging.warning("SIMULATION: FFDecks API is down (simulated)")
                    raise Exception("Simulated FFDecks API outage")
                
                ffdecks_promos = pull_ffdecks_promos()
                ffdecks_fetch_time = time.time() - ffdecks_start
                logging.info(f"FFDecks API fetch completed: {len(ffdecks_promos)} promos in {ffdecks_fetch_time:.1f}s")
                
                if ffdecks_promos:
                    logging.info("Saving FFDecks promos to database...")
                    db_start = time.time()
                    self.db.save_cards(ffdecks_promos, 'ffdecks')
                    db_time = time.time() - db_start
                    logging.info(f"FFDecks promos saved to database in {db_time:.1f}s")
                else:
                    logging.info("No FFDecks promos to save")
            except Exception as e:
                logging.error(f"Failed to fetch from FFDecks API: {e}")
            
            # Load all cards from database into memory
            logging.info("Loading all cards from database into memory...")
            load_start = time.time()
            self.cards = self.db.get_all_cards()
            load_time = time.time() - load_start
            self.lastfetch = time.time()
            
            total_time = time.time() - start_time
            logging.info(f"Database load completed: {len(self.cards)} cards in {load_time:.1f}s")
            logging.info(f"=== Card sync completed successfully in {total_time:.1f}s total ===")
            
        except Exception as e:
            logging.error(f"Error during card sync: {e}")
            # If everything fails, try to load existing data from database
            try:
                logging.info("Attempting to load cards from database cache...")
                self.cards = self.db.get_all_cards()
                logging.info(f"Loaded {len(self.cards)} cards from database cache")
            except Exception as db_error:
                logging.error(f"Failed to load from database: {db_error}")
                self.cards = []
        
        finally:
            self.lock = False
            logging.info("Card sync lock released")

    def pull_new_cards_selective(self):
        """Fetch cards from APIs and only save new ones (not already in DB)"""
        start_time = time.time()
        logging.info("=== Starting selective card sync process ===")
        
        try:
            sync_results = {}
            
            # Try Square first (priority source)
            logging.info("Fetching cards from Square API...")
            square_start = time.time()
            try:
                if self.simulate_square_down:
                    logging.warning("SIMULATION: Square API is down (simulated)")
                    raise Exception("Simulated Square API outage")
                
                square_cards = pull_square_cards()
                square_fetch_time = time.time() - square_start
                logging.info(f"Square API fetch completed: {len(square_cards)} cards in {square_fetch_time:.1f}s")
                
                if square_cards:
                    logging.info("Selectively saving Square cards to database...")
                    db_start = time.time()
                    result = self.db.save_new_cards_only(square_cards, 'square')
                    db_time = time.time() - db_start
                    sync_results['square'] = result
                    logging.info(f"Square selective sync completed in {db_time:.1f}s: {result['new_cards']} new, {result['skipped_cards']} skipped")
                else:
                    logging.warning("No Square cards received")
                    sync_results['square'] = {'total_fetched': 0, 'new_cards': 0, 'skipped_cards': 0, 'success': False}
            except Exception as e:
                logging.error(f"Failed to fetch from Square API: {e}")
                sync_results['square'] = {'total_fetched': 0, 'new_cards': 0, 'skipped_cards': 0, 'success': False, 'error': str(e)}
            
            # Try FFDecks (supplementary source)
            logging.info("Fetching promos from FFDecks API...")
            ffdecks_start = time.time()
            try:
                if self.simulate_ffdecks_down:
                    logging.warning("SIMULATION: FFDecks API is down (simulated)")
                    raise Exception("Simulated FFDecks API outage")
                
                ffdecks_promos = pull_ffdecks_promos()
                ffdecks_fetch_time = time.time() - ffdecks_start
                logging.info(f"FFDecks API fetch completed: {len(ffdecks_promos)} promos in {ffdecks_fetch_time:.1f}s")
                
                if ffdecks_promos:
                    logging.info("Selectively saving FFDecks promos to database...")
                    db_start = time.time()
                    result = self.db.save_new_cards_only(ffdecks_promos, 'ffdecks')
                    db_time = time.time() - db_start
                    sync_results['ffdecks'] = result
                    logging.info(f"FFDecks selective sync completed in {db_time:.1f}s: {result['new_cards']} new, {result['skipped_cards']} skipped")
                else:
                    logging.info("No FFDecks promos to save")
                    sync_results['ffdecks'] = {'total_fetched': 0, 'new_cards': 0, 'skipped_cards': 0, 'success': True}
            except Exception as e:
                logging.error(f"Failed to fetch from FFDecks API: {e}")
                sync_results['ffdecks'] = {'total_fetched': 0, 'new_cards': 0, 'skipped_cards': 0, 'success': False, 'error': str(e)}
            
            # Load all cards from database into memory
            logging.info("Loading all cards from database into memory...")
            load_start = time.time()
            self.cards = self.db.get_all_cards()
            load_time = time.time() - load_start
            self.lastfetch = time.time()
            
            total_time = time.time() - start_time
            total_new_cards = sum(result.get('new_cards', 0) for result in sync_results.values())
            total_skipped_cards = sum(result.get('skipped_cards', 0) for result in sync_results.values())
            
            logging.info(f"Database load completed: {len(self.cards)} cards in {load_time:.1f}s")
            logging.info(f"=== Selective card sync completed in {total_time:.1f}s total: {total_new_cards} new, {total_skipped_cards} skipped ===")
            
            # Store results for status endpoint
            self.last_selective_sync_results = {
                'total_new_cards': total_new_cards,
                'total_skipped_cards': total_skipped_cards,
                'sync_details': sync_results,
                'total_cards_after_sync': len(self.cards)
            }
            
            return sync_results
            
        except Exception as e:
            logging.error(f"Error during selective card sync: {e}")
            # If everything fails, try to load existing data from database
            try:
                logging.info("Attempting to load cards from database cache...")
                self.cards = self.db.get_all_cards()
                logging.info(f"Loaded {len(self.cards)} cards from database cache")
            except Exception as db_error:
                logging.error(f"Failed to load from database: {db_error}")
                self.cards = []
            return {'error': str(e)}
        
        finally:
            self.lock = False
            logging.info("Selective card sync lock released")

    def init(self):
        """Initialize client - load from database only"""
        # Load existing data from database
        try:
            self.cards = self.db.get_all_cards()
            if self.cards:
                logging.info(f"Loaded {len(self.cards)} cards from database on startup")
                self.lastfetch = "loaded from database"
            else:
                logging.info("No existing cards found in database")
                self.lastfetch = "never"
        except Exception as e:
            logging.error(f"Failed to load initial data from database: {e}")
            self.cards = []
            self.lastfetch = "never"

