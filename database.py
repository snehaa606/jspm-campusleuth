import sqlite3
import os
import shutil
from datetime import datetime

# Handle Vercel serverless writable storage (/tmp)
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/jspm_lost_found.db'
    bundled_db = os.path.join(os.path.dirname(__file__), 'jspm_lost_found.db')
    if not os.path.exists(DB_PATH) and os.path.exists(bundled_db):
        try:
            shutil.copyfile(bundled_db, DB_PATH)
        except Exception:
            pass
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'jspm_lost_found.db')

def get_db():
    # If on Vercel and DB doesn't exist yet, initialize it
    if os.environ.get('VERCEL') and not os.path.exists(DB_PATH):
        init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,                  -- 'found' or 'lost'
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        location TEXT NOT NULL,
        primary_color TEXT,
        brand TEXT,
        date_reported TEXT NOT NULL,
        status TEXT DEFAULT 'open',         -- 'open', 'claimed', 'returned'
        reporter_name TEXT NOT NULL,
        reporter_phone TEXT,
        reporter_email TEXT,
        image_url TEXT,
        secret_question TEXT,
        secret_answer TEXT,
        claim_otp TEXT,
        claimed_by_name TEXT,
        claimed_by_phone TEXT,
        claimed_at TEXT,
        tags TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        item_id INTEGER,
        description TEXT,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_sample_data(cursor)
        
    conn.commit()
    conn.close()

def seed_sample_data(cursor):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sample_items = [
        (
            'found',
            'Black boAt Airdopes 141 (Charging Case)',
            'Electronics',
            'Found near table #4 in the seating area. Minor scratch on the back lid.',
            'Main Canteen (Near Nescafe)',
            'Black',
            'boAt',
            now,
            'open',
            'Rohan Shinde (Staff Coordinator)',
            '9823456780',
            'rohan.s@jspm.edu.in',
            'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80',
            'What color is the silicone protective case or sticker?',
            'red devil sticker',
            '4829',
            None, None, None,
            'earbuds, boat, canteen, black, electronics'
        ),
        (
            'found',
            'JSPM Student ID Card (Computer Engg)',
            'Identity Cards',
            'Found on 2nd bench in Lab 204. Name on card matches Year 3 student.',
            'Computer Dept - Lab 204',
            'White/Blue',
            'JSPM University',
            now,
            'open',
            'Prof. Kulkarni',
            '9822001122',
            'kulkarni.comp@jspm.edu.in',
            'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&auto=format&fit=crop&q=80',
            'What is the last 3 digits of PRN number on card?',
            '742',
            '1953',
            None, None, None,
            'id card, prn, comp dept, lab'
        ),
        (
            'found',
            'Blue Milton Thermosteel Water Bottle (750ml)',
            'Bottles',
            'Kept on the reading table near reference section. Has a silver cap.',
            'Central Library - 1st Floor',
            'Blue',
            'Milton',
            now,
            'open',
            'Library Caretaker',
            '9876543210',
            'library@jspm.edu.in',
            'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80',
            'Is there any dent or name etched on base?',
            'small dent on bottom rim',
            '8314',
            None, None, None,
            'bottle, milton, library, blue'
        ),
        (
            'lost',
            'HP 65W Blue-Pin Laptop Charger',
            'Electronics',
            'Left behind during the seminar on Wednesday afternoon. Has a white cable tie.',
            'Main Auditorium / Seminar Hall',
            'Black',
            'HP',
            now,
            'open',
            'Sneha Patil (Student)',
            '9811223344',
            'sneha.p@jspm.edu.in',
            'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80',
            None, None, None,
            None, None, None,
            'hp, charger, laptop, audi, black'
        ),
        (
            'found',
            'Hero Honda Splendor Bike Keys with Iron Man Keychain',
            'Keys',
            'Found hanging near parking slot C-14.',
            'Campus Parking Bay C',
            'Silver/Red',
            'Hero',
            now,
            'returned',
            'Security Guard Ramu',
            '9890123456',
            'security@jspm.edu.in',
            'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=600&auto=format&fit=crop&q=80',
            'How many keys are in the ring?',
            '3 keys',
            '9921',
            'Aditya More',
            '9765432109',
            now,
            'keys, bike, parking, iron man'
        )
    ]
    
    cursor.executemany('''
    INSERT INTO items (
        type, title, category, description, location, primary_color, brand,
        date_reported, status, reporter_name, reporter_phone, reporter_email,
        image_url, secret_question, secret_answer, claim_otp,
        claimed_by_name, claimed_by_phone, claimed_at, tags
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', sample_items)
    
    cursor.execute('''
    INSERT INTO activity_log (action, item_id, description, timestamp)
    VALUES ('SYSTEM_INIT', 1, 'Initial JSPM Lost & Found database seeded', ?)
    ''', (now,))

if __name__ == '__main__':
    init_db()
    print("JSPM Lost & Found Database initialized successfully.")
