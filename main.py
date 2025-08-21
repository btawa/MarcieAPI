import json
import os
import re
import threading
from functools import wraps

from decouple import Config, RepositoryEnv
from flask import Flask, request, Response, render_template, redirect, url_for, session, flash
from urllib.parse import unquote
import roman

from CardClient import CardClient
from cube_list import opus10_cube, opus11_cube, opus12_cube, opus13_cube
from marcie_helper_new import *

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = '.env'
env_config = Config(RepositoryEnv(os.path.join(SCRIPT_PATH, ENV_FILE)))

card_client = CardClient()
card_client.init()
app = Flask(__name__)
app.secret_key = env_config.get('SECRET_KEY', 'dev-secret-key-change-in-production')


def checkAPI():
    """ This function is used to validate the API_KEY used in this API"""

    args = request.args

    if env_config.get('API_KEY') == args['api_key']:
        return True
    else:
        return False


def require_admin_auth(f):
    """Decorator to require admin authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/lastfetch', methods=['GET'])
def get_last_fetch():
    if checkAPI() is True:
        if card_client.lock is False:
            lastfetch = {'lastfetch': card_client.lastfetch}
        else:
            lastfetch = {'lastfetch': card_client.lastfetch, 'status': 'Fetch in progress'}

        return Response(response=json.dumps(lastfetch), status=200, mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/new', methods=['POST'])
def get_new_cards():
    if checkAPI() is True:
        try:
            if card_client.lock is False:
                card_client.lock = True

                # Use daemon thread to ensure cleanup on app shutdown
                x = threading.Thread(target=card_client.pull_new_cards, daemon=True)
                x.start()

                status = {'status': "Starting get_new_cards, this may take a while"}

                return Response(response=json.dumps(status), status=201, mimetype='application/json')
            else:
                status = {'status': "CardClient is locked, is something already running?"}
                return Response(response=json.dumps(status), status=409, mimetype='application/json')

        except Exception as e:
            # Reset lock on error and log the issue
            card_client.lock = False
            logging.error(f"Error in get_new_cards: {e}")
            return Response(status=500)
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/card/<code>')
def getCard(code):
    """ This function is used to grab a specific card by code"""

    card_list = []

    if checkAPI() is True:
        for card in card_client.cards:
            if re.search('^' + code, card['Code']):
                card_list.append(card)

        if len(card_list) == 1:
            return card_list[0]
        else:
            return Response(json.dumps(card_list), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


# Square no longer labels things in the format `Opus X`, so set is broken
# This will probably be deprecated and can just use `/card/15-` commenting out for now.

# @app.route('/api/set/<opus>')
# def getSet(opus):
#     """ This function is used to grab a whole set by opus number from the API"""
#
#     try:
#         opus = int(opus)
#     except:
#         return Response('500 Input is not a integer', 500)
#
#     if checkAPI() is True:
#         card_list = []
#         for card in card_client.cards:
#             if card['Set'] is None:
#                 pass
#             else:
#                 if int(opus) == int(roman.fromRoman(card['Set'].split()[1])):
#                     card_list.append(card)
#
#         return Response(json.dumps(card_list), mimetype='application/json')
#     else:
#         return Response('401 Unauthorized API Key', 401)


@app.route('/api/')
def getAllCards():
    """ This function will return all cards in the API"""

    if checkAPI() is True:
        return Response(json.dumps(card_client.cards), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/cube/<opusnum>')
def getCube(opusnum):
    """ This function will return a list of cards which are part of an all-star cube.  The cube information comes
    from cube_list.py which contains the list of each card code in the cube"""

    cube_cards = []

    if checkAPI() is True:
        if opusnum == '10':
            ourcube = opus10_cube
        elif opusnum == '11':
            ourcube = opus11_cube
        elif opusnum == '12':
            ourcube = opus12_cube
        elif opusnum == '13':
            ourcube = opus13_cube

        for carda in ourcube:
            for cardb in card_client.cards:
                if re.search('^' + carda, cardb['Code']):
                    cube_cards.append(cardb)

        return Response(json.dumps(cube_cards), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)

@app.route('/api/links/<opusnum>')
def get_square_images(opusnum):
    square_root_url = "https://fftcg.cdn.sewest.net/images/cards/full/"
    marcie_root_url = "https://storage.googleapis.com/marcieapi-images/"
    square_urls = []

    if checkAPI() is True:
        try:
            for card in card_client.cards:
                if re.search(r'^' + opusnum + '-', card['Code']):
                    # Get the image URL from database and convert to Square's CDN
                    image_url = card.get('image_url')
                    if image_url:
                        # Replace marcie API base URL with Square's CDN URL
                        square_url = image_url.replace(marcie_root_url, square_root_url)
                        square_urls.append(square_url)

        except:
            return Response('Bad Request', 400)

        finally:
            return Response(json.dumps(square_urls), mimetype='application/json')


@app.route('/admin/')
def admin_index():
    """Redirect /admin/ to cards page"""
    return redirect(url_for('admin_cards'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials against environment variables
        admin_username = env_config.get('ADMIN_USERNAME', 'admin')
        admin_password = env_config.get('ADMIN_PASSWORD', 'admin')
        
        if username == admin_username and password == admin_password:
            session['admin_authenticated'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_cards'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/cards')
@require_admin_auth
def admin_cards():
    """Web interface for card management"""
    page = int(request.args.get('page', 1))
    per_page = 20
    search_term = request.args.get('search', '').strip()
    
    # Filter cards based on search
    filtered_cards = card_client.cards
    if search_term:
        filtered_cards = [
            card for card in card_client.cards 
            if (search_term.lower() in (card.get('Code') or '').lower() or 
                search_term.lower() in (card.get('Name_EN') or '').lower())
        ]
    
    # Pagination
    total_cards = len(filtered_cards)
    total_pages = (total_cards + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    cards_page = filtered_cards[start_idx:end_idx]
    
    return render_template('card_list.html', 
                         cards=cards_page,
                         page=page,
                         total_pages=total_pages,
                         total_cards=total_cards,
                         per_page=per_page,
                         search_term=search_term)


@app.route('/admin/card/new', methods=['GET', 'POST'])
@require_admin_auth
def admin_add_card():
    """Add new card"""
    message = None
    success = False
    
    if request.method == 'POST':
        try:
            code = request.form.get('code', '').strip()
            if not code:
                message = "Card code is required"
            elif any(c['Code'] == code for c in card_client.cards):
                message = f"Card with code '{code}' already exists"
            else:
                # Create new card data
                new_card = {
                    'Code': code,
                    'Name_EN': request.form.get('name_en'),
                    'Element': request.form.get('element'),
                    'Cost': request.form.get('cost'),
                    'Type_EN': request.form.get('type_en'),
                    'Job_EN': request.form.get('job_en'),
                    'Power': int(request.form.get('power')) if request.form.get('power') else None,
                    'Category_1': request.form.get('category_1'),
                    'Set': request.form.get('set_name'),
                    'Multicard': bool(request.form.get('multicard')),
                    'Ex_Burst': bool(request.form.get('ex_burst')),
                    'image_url': request.form.get('image_url'),
                    'Text_EN': [line.rstrip('\r') for line in request.form.get('text_en').split('\n')] if request.form.get('text_en') else None
                }
                
                # Save to database
                result = card_client.db.add_card(new_card)
                if result:
                    # Add to memory as well
                    card_client.cards.append(new_card)
                    message = f"Card '{code}' created successfully!"
                    success = True
                else:
                    message = "Failed to create card in database"
                    
        except Exception as e:
            message = f"Error creating card: {str(e)}"
    
    # Create empty card template for form
    empty_card = {
        'Code': '', 'Name_EN': '', 'Element': '', 'Cost': '', 'Type_EN': '', 
        'Job_EN': '', 'Power': '', 'Category_1': '', 'Set': '', 
        'Multicard': False, 'Ex_Burst': False, 'image_url': '', 'Text_EN': ''
    }
    
    return render_template('card_add.html', 
                         card=empty_card, 
                         message=message, 
                         success=success)


@app.route('/admin/card/<path:code>', methods=['GET', 'POST'])
@require_admin_auth
def admin_edit_card(code):
    """Edit individual card"""
    # URL decode the card code to handle slashes
    code = unquote(code)
    # Find the card
    card = None
    for c in card_client.cards:
        if c['Code'] == code:
            card = c
            break
    
    if not card:
        return "Card not found", 404
    
    message = None
    success = False
    
    if request.method == 'POST':
        try:
            # Update card data from form
            updated_card = {
                'Code': code,  # Code cannot be changed
                'Name_EN': request.form.get('name_en'),
                'Element': request.form.get('element'),
                'Cost': request.form.get('cost'),
                'Type_EN': request.form.get('type_en'),
                'Job_EN': request.form.get('job_en'),
                'Power': int(request.form.get('power')) if request.form.get('power') else None,
                'Category_1': request.form.get('category_1'),
                'Set': request.form.get('set_name'),
                'Multicard': bool(request.form.get('multicard')),
                'Ex_Burst': bool(request.form.get('ex_burst')),
                'image_url': request.form.get('image_url'),
                'Text_EN': [line.rstrip('\r') for line in request.form.get('text_en').split('\n')] if request.form.get('text_en') else None
            }
            
            # Update in database
            result = card_client.db.update_card(code, updated_card)
            if result:
                # Update in memory as well
                for i, c in enumerate(card_client.cards):
                    if c['Code'] == code:
                        card_client.cards[i].update(updated_card)
                        break
                
                message = "Card updated successfully!"
                success = True
                card.update(updated_card)  # Update the card variable for display
            else:
                message = "Failed to update card in database"
                
        except Exception as e:
            message = f"Error updating card: {str(e)}"
    
    return render_template('card_edit.html', 
                         card=card, 
                         message=message, 
                         success=success)


@app.route('/admin/card/<path:code>/delete', methods=['POST'])
@require_admin_auth
def admin_delete_card(code):
    """Delete a card"""
    # URL decode the card code to handle slashes
    code = unquote(code)
    try:
        # Find the card first
        card_exists = any(c['Code'] == code for c in card_client.cards)
        if not card_exists:
            return "Card not found", 404
        
        # Delete from database
        result = card_client.db.delete_card(code)
        if result:
            # Remove from memory as well
            card_client.cards = [c for c in card_client.cards if c['Code'] != code]
            return redirect(url_for('admin_cards'))
        else:
            return "Failed to delete card from database", 500
            
    except Exception as e:
        logging.error(f"Error deleting card {code}: {e}")
        return f"Error deleting card: {str(e)}", 500


@app.route('/admin/management')
@require_admin_auth
def admin_management():
    """Database management page"""
    total_cards = card_client.db.get_card_count()
    
    # Get last fetch time from card_client if available
    last_fetch = getattr(card_client, 'lastfetch', None)
    if last_fetch and last_fetch != 'never':
        try:
            # Convert timestamp to readable format if it's a number
            if isinstance(last_fetch, (int, float)):
                import datetime
                last_fetch = datetime.datetime.fromtimestamp(last_fetch).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    return render_template('management.html', 
                         total_cards=total_cards,
                         last_fetch=last_fetch or 'Never')


@app.route('/admin/management/export')
@require_admin_auth
def admin_export_database():
    """Export complete database as JSON"""
    try:
        import datetime
        
        cards_data = card_client.cards
        response_data = json.dumps(cards_data, indent=2)
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"marcie_cards_backup_{timestamp}.json"
        
        response = Response(
            response_data,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        return response
        
    except Exception as e:
        logging.error(f"Error exporting database: {e}")
        return f"Error exporting database: {str(e)}", 500


@app.route('/admin/management/import', methods=['GET', 'POST'])
@require_admin_auth
def admin_import_database():
    """Import database from JSON backup"""
    # Redirect GET requests back to management page
    if request.method == 'GET':
        return redirect(url_for('admin_management'))
    
    message = None
    message_type = 'danger'
    
    try:
        # Check if database is empty
        if card_client.db.get_card_count() > 0:
            message = "Import rejected: Database is not empty. Can only import into an empty database to prevent conflicts."
        else:
            # Get uploaded file
            if 'backup_file' not in request.files:
                message = "No file uploaded"
            else:
                file = request.files['backup_file']
                if file.filename == '':
                    message = "No file selected"
                else:
                    # Read and parse JSON
                    file_content = file.read().decode('utf-8')
                    cards_data = json.loads(file_content)
                    
                    if not isinstance(cards_data, list):
                        message = "Invalid file format: Expected JSON array of cards"
                    else:
                        # Clear database and import new data
                        if card_client.db.save_cards(cards_data, 'import'):
                            # Update in-memory cards
                            card_client.cards = cards_data
                            message = f"Successfully imported {len(cards_data)} cards from backup"
                            message_type = 'success'
                        else:
                            message = "Failed to import cards to database"
    
    except json.JSONDecodeError:
        message = "Invalid JSON file"
    except Exception as e:
        logging.error(f"Error importing database: {e}")
        message = f"Error importing database: {str(e)}"
    
    # Redirect back with message
    total_cards = card_client.db.get_card_count()
    last_fetch = getattr(card_client, 'lastfetch', 'Never')
    
    return render_template('management.html',
                         total_cards=total_cards,
                         last_fetch=last_fetch,
                         message=message,
                         message_type=message_type)


@app.route('/admin/management/fetch', methods=['POST'])
@require_admin_auth
def admin_fetch_new_cards():
    """Admin endpoint to fetch new cards - requires admin authentication"""
    try:
        if card_client.lock is False:
            card_client.lock = True
            
            # Use daemon thread to ensure cleanup on app shutdown
            x = threading.Thread(target=card_client.pull_new_cards, daemon=True)
            x.start()
            
            status = {'status': "Starting get_new_cards, this may take a while"}
            return Response(response=json.dumps(status), status=201, mimetype='application/json')
        else:
            status = {'status': "CardClient is locked, is something already running?"}
            return Response(response=json.dumps(status), status=409, mimetype='application/json')
            
    except Exception as e:
        # Reset lock on error and log the issue
        card_client.lock = False
        logging.error(f"Error in admin_fetch_new_cards: {e}")
        status = {'status': f"Error: {str(e)}"}
        return Response(response=json.dumps(status), status=500, mimetype='application/json')


@app.route('/admin/management/clear', methods=['POST'])
@require_admin_auth
def admin_clear_database():
    """Admin endpoint to clear all cards from database - requires admin authentication"""
    try:
        # Get current count for logging
        current_count = card_client.db.get_card_count()
        
        # Clear the database
        if card_client.db.clear_database():
            # Clear in-memory cards as well
            card_client.cards = []
            
            logging.info(f"Admin {session.get('admin_username', 'unknown')} cleared database of {current_count} cards")
            
            response_data = {
                'success': True,
                'message': f'Successfully cleared {current_count} cards from database',
                'cleared_count': current_count
            }
            return Response(response=json.dumps(response_data), status=200, mimetype='application/json')
        else:
            response_data = {
                'success': False,
                'message': 'Failed to clear database'
            }
            return Response(response=json.dumps(response_data), status=500, mimetype='application/json')
            
    except Exception as e:
        logging.error(f"Error in admin_clear_database: {e}")
        response_data = {
            'success': False,
            'message': f'Error clearing database: {str(e)}'
        }
        return Response(response=json.dumps(response_data), status=500, mimetype='application/json')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000')
