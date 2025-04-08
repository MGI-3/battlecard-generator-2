from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from flask_cors import CORS
import requests
import mysql.connector
from datetime import datetime
from website_crawler import WebsiteCrawler
import os
import json
import tempfile
import traceback
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from perplexity_analyzer import PerplexityAnalyzer
from document_processor import DocumentProcessor
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Perplexity Analyzer with proper error handling
try:
    perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
    if not perplexity_api_key:
        print("WARNING: PERPLEXITY_API_KEY not found in environment variables")
    perplexity_analyzer = PerplexityAnalyzer(perplexity_api_key)
except Exception as e:
    print(f"Error initializing Perplexity Analyzer: {e}")
    perplexity_analyzer = None

document_processor = DocumentProcessor()

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'omdeore007',  # Change this
    'database': 'battlecards'
}


# Initialize database
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            scraped_text LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS battlecards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scrape_id INT,
            problem_area VARCHAR(255),
            problem_description TEXT,
            differentiator TEXT,
            case_studies JSON,
            FOREIGN KEY (scrape_id) REFERENCES scrape_history(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255),
            google_uid VARCHAR(255),
            display_name VARCHAR(255),
            is_google_user BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            display_name VARCHAR(255),
            company VARCHAR(255),
            role VARCHAR(255),
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            activity_type ENUM('website_scrape', 'document_upload', 'battlecard_view', 'battlecard_download') NOT NULL,
            activity_data JSON,
            scrape_id INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scrape_id) REFERENCES scrape_history(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            billing_interval VARCHAR(20) DEFAULT 'month',
            features JSON,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            plan_id INT NOT NULL,
            stripe_customer_id VARCHAR(255),
            stripe_subscription_id VARCHAR(255),
            status VARCHAR(50) NOT NULL,
            current_period_start DATETIME,
            current_period_end DATETIME,
            cancel_at_period_end BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                subscription_id INT NOT NULL,
                stripe_invoice_id VARCHAR(255),
                amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) NOT NULL,
                payment_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id)
            )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

with app.app_context():
    init_db()

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (email, password_hash) VALUES (%s, %s)',
            (email, password_hash)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Unhandled error: {str(error)}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# @app.route('/api/scrape', methods=['POST'])
# def scrape_website_crawler():
#     try:
#         url = request.json.get('url')
#         max_pages = request.json.get('max_pages', 10)  # Default to 10 pages if not specified
        
#         if not url:
#             return jsonify({'error': 'URL is required'}), 400

#         # Initialize the crawler
#         crawler = WebsiteCrawler(base_url=url, max_pages=max_pages)
        
#         # Crawl the website
#         crawler.crawl()
        
#         # Get the combined text from all pages
#         text = crawler.get_combined_text()
        
#         # Number of pages crawled
#         pages_crawled = len(crawler.page_contents)
        
#         # Use Perplexity API to analyze the text and generate battlecards
#         battlecards = []
        
#         if perplexity_analyzer:
#             try:
#                 print("Analyzing text with Perplexity API...")
#                 battlecards = perplexity_analyzer.analyze_text(text)
#                 print(f"Generated {len(battlecards)} battlecards using Perplexity API")
                
#                 # Print case study info for debugging
#                 for i, card in enumerate(battlecards):
#                     case_studies = card.get('case_studies', [])
#                     print(f"Card {i+1} has {len(case_studies)} case studies")
                    
#             except Exception as e:
#                 print(f"Error using Perplexity API: {e}")
#                 print(traceback.format_exc())
        
#         # If Perplexity failed or returned no battlecards, create a basic one
#         if not battlecards:
#             print("Using basic analysis as fallback")
#             battlecards = [{
#                 "problem_area": "Website Analysis",
#                 "problem_description": "Analysis of the provided website content.",
#                 "differentiator": "Key information extracted from the website.",
#                 "case_studies": []
#             }]

#         # Store in database
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
        
#         # Insert scraped text
#         cursor.execute(
#             'INSERT INTO scrape_history (url, scraped_text) VALUES (%s, %s)',
#             (url, text[:65000])  # Limit text size for DB
#         )
#         scrape_id = cursor.lastrowid
        
#         # Store battlecards
#         for card in battlecards:
#             cursor.execute('''
#                 INSERT INTO battlecards 
#                 (scrape_id, problem_area, problem_description, differentiator, case_studies)
#                 VALUES (%s, %s, %s, %s, %s)
#             ''', (
#                 scrape_id,
#                 card.get('problem_area', ''),
#                 card.get('problem_description', ''),
#                 card.get('differentiator', ''),
#                 json.dumps(card.get('case_studies', []))
#             ))
        
#         conn.commit()
#         cursor.close()
#         conn.close()

#         try:
#             user_id = request.json.get('user_id')
#             print(f"Recording activity for user: {user_id}")
#             if user_id:
#                 cursor = conn.cursor()
#                 activity_data = json.dumps({'url': url, 'pages_crawled': pages_crawled})
#                 print(f"Activity data: {activity_data}")
                
#                 cursor.execute(
#                     'INSERT INTO activity_history (user_id, activity_type, activity_data, scrape_id) VALUES (%s, %s, %s, %s)',
#                     (
#                         user_id,
#                         'website_scrape',
#                         activity_data,
#                         scrape_id
#                     )
#                 )
#                 conn.commit()
#                 cursor.close()
#                 print("Activity recorded successfully")
#         except Exception as e:
#             print(f"Error recording activity: {str(e)}")
#             print(traceback.format_exc())

#         return jsonify({
#             'battlecards': battlecards,
#             'pages_crawled': pages_crawled,
#             'crawled_urls': list(crawler.visited_urls)
#         })

#     except requests.RequestException as e:
#         return jsonify({'error': f'Failed to fetch website: {str(e)}'}), 400
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         print(traceback.format_exc())
#         return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# In app.py
# @app.route('/api/scrape', methods=['POST'])
# def scrape_website():
#     try:
#         url = request.json.get('url')
#         max_pages = request.json.get('max_pages', 10)
#         user_id = request.json.get('user_id')  # Get user ID from request
        
#         if not url:
#             return jsonify({'error': 'URL is required'}), 400

#         # Initialize the crawler and perform scraping
#         crawler = WebsiteCrawler(base_url=url, max_pages=max_pages)
#         crawler.crawl()
#         text = crawler.get_combined_text()
#         pages_crawled = len(crawler.page_contents)
        
#         # Generate battlecards
#         battlecards = []
#         if perplexity_analyzer:
#             try:
#                 battlecards = perplexity_analyzer.analyze_text(text)
#                 print(f"Generated {len(battlecards)} battlecards using Perplexity API")
#             except Exception as e:
#                 print(f"Error using Perplexity API: {e}")
#                 print(traceback.format_exc())
        
#         # Fallback if needed
#         if not battlecards:
#             battlecards = [{
#                 "problem_area": "Website Analysis",
#                 "problem_description": "Analysis of the provided website content.",
#                 "differentiator": "Key information extracted from the website.",
#                 "case_studies": []
#             }]
        
#         # Store in database
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
        
#         try:
#             # Insert scraped text
#             cursor.execute(
#                 'INSERT INTO scrape_history (url, scraped_text) VALUES (%s, %s)',
#                 (url, text[:65000])
#             )
#             scrape_id = cursor.lastrowid
            
#             # Store battlecards
#             for card in battlecards:
#                 cursor.execute('''
#                     INSERT INTO battlecards 
#                     (scrape_id, problem_area, problem_description, differentiator, case_studies)
#                     VALUES (%s, %s, %s, %s, %s)
#                 ''', (
#                     scrape_id,
#                     card.get('problem_area', ''),
#                     card.get('problem_description', ''),
#                     card.get('differentiator', ''),
#                     json.dumps(card.get('case_studies', []))
#                 ))
            
#             # Record activity if user is logged in
#             if user_id:
#                 cursor.execute('SELECT id FROM users WHERE google_uid = %s', (user_id,))
#                 user_record = cursor.fetchone()
#                 user_row = cursor.fetchone()
#                 activity_data = {
#                     'url': url,
#                     'pages_crawled': pages_crawled
#                 }
#                 if user_row:
#                     internal_user_id = user_row[0]  # This is the integer ID from your users table
#                     cursor.execute(
#                         'INSERT INTO activity_history (user_id, activity_type, activity_data, scrape_id) VALUES (%s, %s, %s, %s)',
#                         (
#                             internal_user_id,  # Use the internal ID, not the Firebase UID
#                             'website_scrape',
#                             json.dumps(activity_data),
#                             scrape_id
#                         )
#                     )
#                 if user_record:
#                     db_user_id = user_record[0]  # Get the database user ID
#                     cursor.execute(
#                         'INSERT INTO activity_history (user_id, activity_type, activity_data, scrape_id) VALUES (%s, %s, %s, %s)',
#                         (
#                             db_user_id,  # Use the database user ID
#                             'website_scrape',
#                             json.dumps(activity_data),
#                             scrape_id
#                         )
#                     )
#                 print(f"Recording activity for user {user_id}")
#                 activity_data = {
#                     'url': url,
#                     'pages_crawled': pages_crawled
#                 }
#                 cursor.execute(
#                     'INSERT INTO activity_history (user_id, activity_type, activity_data, scrape_id) VALUES (%s, %s, %s, %s)',
#                     (
#                         user_id,
#                         'website_scrape',
#                         json.dumps(activity_data),
#                         scrape_id
#                     )
#                 )
#                 print(f"Activity recorded with scrape_id {scrape_id}")
            
#             conn.commit()
#         except Exception as e:
#             conn.rollback()
#             print(f"Database error: {e}")
#             raise e
#         finally:
#             cursor.close()
#             conn.close()

#         return jsonify({
#             'battlecards': battlecards,
#             'pages_crawled': pages_crawled,
#             'crawled_urls': list(crawler.visited_urls)
#         })

#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         print(traceback.format_exc())
#         return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_website():
    try:
        url = request.json.get('url')
        max_pages = request.json.get('max_pages', 25)  # Default increased to 25
        max_depth = request.json.get('max_depth', 3)   # Default of 3 levels deep
        
        # Get custom priorities if provided
        priority_keywords = request.json.get('priority_keywords')
        exclude_patterns = request.json.get('exclude_patterns')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Initialize the enhanced crawler
        crawler = WebsiteCrawler(
            base_url=url, 
            max_pages=max_pages,
            max_depth=max_depth,
            priority_keywords=priority_keywords,
            exclude_patterns=exclude_patterns
        )
        
        # Crawl the website
        crawler.crawl()
        
        # Get the crawl summary for frontend display
        crawl_summary = crawler.get_crawl_summary()
        
        # Get the combined text from all pages (ordered by relevance)
        text = crawler.get_combined_text()
        
        # Use Perplexity API to analyze the text and generate battlecards
        battlecards = []
        
        if perplexity_analyzer:
            try:
                print("Analyzing text with Perplexity API...")
                battlecards = perplexity_analyzer.analyze_text(text)
                print(f"Generated {len(battlecards)} battlecards using Perplexity API")
                
                # Print case study info for debugging
                for i, card in enumerate(battlecards):
                    case_studies = card.get('case_studies', [])
                    print(f"Card {i+1} has {len(case_studies)} case studies")
                    
            except Exception as e:
                print(f"Error using Perplexity API: {e}")
                print(traceback.format_exc())
        
        # If Perplexity failed or returned no battlecards, create a basic one
        if not battlecards:
            print("Using basic analysis as fallback")
            battlecards = [{
                "problem_area": "Website Analysis",
                "problem_description": "Analysis of the provided website content.",
                "differentiator": "Key information extracted from the website.",
                "case_studies": []
            }]

        # Store in database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Insert scraped text with metadata
        cursor.execute(
            'INSERT INTO scrape_history (url, scraped_text) VALUES (%s, %s)',
            (url, text[:65000])  # Limit text size for DB
        )
        scrape_id = cursor.lastrowid
        
        # Store battlecards
        for card in battlecards:
            cursor.execute('''
                INSERT INTO battlecards 
                (scrape_id, problem_area, problem_description, differentiator, case_studies)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                scrape_id,
                card.get('problem_area', ''),
                card.get('problem_description', ''),
                card.get('differentiator', ''),
                json.dumps(card.get('case_studies', []))
            ))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'battlecards': battlecards,
            'crawl_summary': crawl_summary
        })

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch website: {str(e)}'}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        cursor.close()
        conn.close()

        return jsonify({'message': 'Login successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    try:
        data = request.json
        email = data.get('email')
        uid = data.get('uid')
        display_name = data.get('displayName')

        if not email or not uid:
            return jsonify({'error': 'Email and UID are required'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if not user:
            # Create new user for Google authentication
            cursor.execute('''
                INSERT INTO users 
                (email, google_uid, display_name, is_google_user) 
                VALUES (%s, %s, %s, TRUE)
            ''', (email, uid, display_name))
        else:
            # Update existing user's Google UID
            cursor.execute('''
                UPDATE users 
                SET google_uid = %s, display_name = %s, is_google_user = TRUE 
                WHERE email = %s
            ''', (uid, display_name, email))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Authentication successful'}), 200

    except Exception as e:
        print(f"Google auth error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/profile/<uid>', methods=['GET'])
def get_profile(uid):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get user id from uid
        cursor.execute('SELECT id FROM users WHERE google_uid = %s OR id = %s', (uid, uid))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get profile data
        cursor.execute('''
            SELECT display_name, company, role
            FROM user_profiles
            WHERE user_id = %s
        ''', (user['id'],))
        
        profile = cursor.fetchone()
        
        cursor.close()
        conn.close()

        return jsonify(profile or {})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    try:
        data = request.json
        uid = data.get('uid')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get user id
        cursor.execute('SELECT id FROM users WHERE google_uid = %s OR id = %s', (uid, uid))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update or insert profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id, display_name, company, role)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            display_name = VALUES(display_name),
            company = VALUES(company),
            role = VALUES(role)
        ''', (user['id'], data.get('displayName'), data.get('company'), data.get('role')))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/api/user/battlecards/<int:scrape_id>', methods=['GET'])
def get_saved_battlecards(scrape_id):
    try:
        # Get user ID from request (you might use a token or session)
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Check if this scrape belongs to the user
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM activity_history
            WHERE user_id = %s AND scrape_id = %s
        ''', (user_id, scrape_id))
        
        result = cursor.fetchone()
        if not result or result['count'] == 0:
            return jsonify({'error': 'Unauthorized access to battlecards'}), 403
        
        # Get battlecards for this scrape
        cursor.execute('''
            SELECT 
                id,
                problem_area,
                problem_description,
                differentiator,
                case_studies
            FROM 
                battlecards
            WHERE 
                scrape_id = %s
        ''', (scrape_id,))
        
        battlecards = cursor.fetchall()
        
        # Parse JSON fields
        for card in battlecards:
            if isinstance(card['case_studies'], str):
                card['case_studies'] = json.loads(card['case_studies'])
        
        cursor.close()
        conn.close()
        
        return jsonify({'battlecards': battlecards})
        
    except Exception as e:
        print(f"Error retrieving battlecards: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
# @app.route('/api/scrape', methods=['POST'])
# def scrape_website():
#     try:
#         url = request.json.get('url')
#         if not url:
#             return jsonify({'error': 'URL is required'}), 400

#         # Fetch website content
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         # Parse HTML and extract text
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Remove script and style elements
#         for script in soup(["script", "style"]):
#             script.decompose()

#         # Get text content
#         text = soup.get_text(separator='\n', strip=True)

#         # Use Perplexity API to analyze the text and generate battlecards
#         battlecards = []
        
#         if perplexity_analyzer:
#             try:
#                 battlecards = perplexity_analyzer.analyze_text(text)
#                 print(f"Generated {len(battlecards)} battlecards using Perplexity API")
#             except Exception as e:
#                 print(f"Error using Perplexity API: {e}")
#                 print(traceback.format_exc())
#                 # Fall back to basic analysis if Perplexity fails
                
#         # If Perplexity failed or returned no battlecards, create a basic one
#         if not battlecards:
#             print("Using basic analysis as fallback")
#             battlecards = [{
#                 "problem_area": "Website Analysis",
#                 "problem_description": "Analysis of the provided website content.",
#                 "differentiator": "Key information extracted from the website.",
#                 "case_studies": []
#             }]

#         # Store in database
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
        
#         # Insert scraped text
#         cursor.execute(
#             'INSERT INTO scrape_history (url, scraped_text) VALUES (%s, %s)',
#             (url, text[:65000])  # Limit text size for DB
#         )
#         scrape_id = cursor.lastrowid
        
#         # Store battlecards
#         for card in battlecards:
#             cursor.execute('''
#                 INSERT INTO battlecards 
#                 (scrape_id, problem_area, problem_description, differentiator, case_studies)
#                 VALUES (%s, %s, %s, %s, %s)
#             ''', (
#                 scrape_id,
#                 card.get('problem_area', ''),
#                 card.get('problem_description', ''),
#                 card.get('differentiator', ''),
#                 json.dumps(card.get('case_studies', []))
#             ))
        
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({'battlecards': battlecards})

#     except requests.RequestException as e:
#         return jsonify({'error': f'Failed to fetch website: {str(e)}'}), 400
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         print(traceback.format_exc())
#         return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Add new route for document processing
@app.route('/api/process-documents', methods=['POST'])
def process_documents():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400

        # Create a temporary directory to store uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            
            # Save uploaded files to temp directory
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_dir, filename)
                file.save(file_path)
                file_paths.append(file_path)
            
            # Process the documents
            extracted_texts = document_processor.process_multiple_files(file_paths)
            
            # Combine all texts for analysis
            combined_text = "\n\n".join(extracted_texts.values())
            
            # Use Perplexity API to analyze the text and generate battlecards
            battlecards = []
            
            if perplexity_analyzer:
                try:
                    print("Analyzing document text with Perplexity API...")
                    battlecards = perplexity_analyzer.analyze_text(combined_text)
                    print(f"Generated {len(battlecards)} battlecards using Perplexity API")
                except Exception as e:
                    print(f"Error using Perplexity API: {e}")
                    print(traceback.format_exc())
            
            # If Perplexity failed or returned no battlecards, create a basic one
            if not battlecards:
                print("Using basic analysis as fallback")
                battlecards = [{
                    "problem_area": "Document Analysis",
                    "problem_description": "Analysis of the provided documents.",
                    "differentiator": "Key information extracted from the documents.",
                    "case_studies": []
                }]

            # Store in database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Store document names as URL
            document_names = ", ".join(extracted_texts.keys())
            
            # Insert scraped text
            cursor.execute(
                'INSERT INTO scrape_history (url, scraped_text) VALUES (%s, %s)',
                (f"Uploaded documents: {document_names}", combined_text[:65000])
            )
            scrape_id = cursor.lastrowid
            
            # Store battlecards
            for card in battlecards:
                cursor.execute('''
                    INSERT INTO battlecards 
                    (scrape_id, problem_area, problem_description, differentiator, case_studies)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    scrape_id,
                    card.get('problem_area', ''),
                    card.get('problem_description', ''),
                    card.get('differentiator', ''),
                    json.dumps(card.get('case_studies', []))
                ))
            
            conn.commit()
            cursor.close()
            conn.close()

            try:
                user_id = request.json.get('user_id')
                if user_id:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO activity_history (user_id, activity_type, activity_data, scrape_id) VALUES (%s, %s, %s, %s)',
                        (
                            user_id,
                            'document_upload',
                            json.dumps({'documents': list(extracted_texts.keys())}),
                            scrape_id
                        )
                    )
                    conn.commit()
                    cursor.close()
            except Exception as e:
                print(f"Error recording activity: {e}")

            return jsonify({'battlecards': battlecards})

    except Exception as e:
        print(f"Document processing error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/user/history', methods=['GET'])
def get_user_activity_history():
    try:
        # Get user ID from request
        user_id = request.args.get('user_id')
        
        print(f"Fetching activity history for user: {user_id}")
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Query to get user's activity history
        query = '''
            SELECT 
                ah.id, 
                ah.activity_type, 
                ah.activity_data, 
                ah.created_at,
                sh.url,
                (SELECT COUNT(*) FROM battlecards b WHERE sh.id = b.scrape_id) as battlecard_count
            FROM 
                activity_history ah
            LEFT JOIN 
                scrape_history sh ON ah.scrape_id = sh.id
            WHERE 
                ah.user_id = %s
            ORDER BY 
                ah.created_at DESC
            LIMIT 50
        '''
        
        cursor.execute(query, (user_id,))
        activities = cursor.fetchall()
        
        print(f"Found {len(activities)} activities for user {user_id}")
        
        # Convert datetime objects to strings for JSON serialization
        for activity in activities:
            if activity['created_at']:
                activity['created_at'] = activity['created_at'].isoformat()
            
            # Parse activity_data if it's a string
            if activity['activity_data'] and isinstance(activity['activity_data'], str):
                try:
                    activity['activity_data'] = json.loads(activity['activity_data'])
                except json.JSONDecodeError:
                    activity['activity_data'] = {}
        
        cursor.close()
        conn.close()
        
        return jsonify({'activities': activities})
        
    except Exception as e:
        print(f"Error retrieving activity history: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/reset-database', methods=['POST'])
def reset_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Drop tables in reverse order of dependencies
        cursor.execute('DROP TABLE IF EXISTS activity_history')
        cursor.execute('DROP TABLE IF EXISTS battlecards')
        cursor.execute('DROP TABLE IF EXISTS scrape_history')
        cursor.execute('DROP TABLE IF EXISTS user_profiles')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reinitialize database
        init_db()
        
        return jsonify({'message': 'Database reset successful'}), 200
    except Exception as e:
        print(f"Error resetting database: {e}")
        return jsonify({'error': f'Failed to reset database: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)