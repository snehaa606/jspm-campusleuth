import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

import database
from ai_matcher import (
    CATEGORIES, CAMPUS_LOCATIONS, COMMON_COLORS, 
    find_potential_matches, smart_autotag_from_text
)
from whatsapp_service import (
    format_item_whatsapp_card, generate_whatsapp_share_url, generate_daily_digest
)

app = Flask(__name__)
app.secret_key = 'jspm-lost-found-secret-key-2026'

# Configuration for image uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
database.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_common():
    return {
        'CATEGORIES': CATEGORIES,
        'CAMPUS_LOCATIONS': CAMPUS_LOCATIONS,
        'COMMON_COLORS': COMMON_COLORS
    }

@app.route('/')
def index():
    query_type = request.args.get('type', 'all')
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')

    conn = database.get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM items WHERE 1=1"
    params = []

    if query_type in ['found', 'lost']:
        sql += " AND type = ?"
        params.append(query_type)

    if category:
        sql += " AND category = ?"
        params.append(category)

    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")

    if status_filter != 'all':
        sql += " AND status = ?"
        params.append(status_filter)

    if search:
        sql += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ? OR brand LIKE ?)"
        wild = f"%{search}%"
        params.extend([wild, wild, wild, wild])

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    items = [dict(row) for row in cursor.fetchall()]

    # Statistics calculation
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'returned'")
    returned_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'found' AND status = 'open'")
    active_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'lost' AND status = 'open'")
    active_lost = cursor.fetchone()[0]

    conn.close()

    success_rate = int((returned_items / total_items * 100)) if total_items > 0 else 0
    # Average typing time per WhatsApp message = 3.5 minutes. Total time saved!
    hours_saved = round((total_items * 3.5) / 60, 1)

    stats = {
        'total': total_items,
        'returned': returned_items,
        'active_found': active_found,
        'active_lost': active_lost,
        'success_rate': success_rate,
        'hours_saved': hours_saved
    }

    return render_template('index.html', 
                           items=items, 
                           stats=stats,
                           active_type=query_type,
                           selected_category=category,
                           selected_location=location,
                           selected_status=status_filter,
                           search_query=search)

@app.route('/report/found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Others')
        location = request.form.get('location', 'JSPM Campus')
        color = request.form.get('primary_color', '')
        brand = request.form.get('brand', '')
        description = request.form.get('description', '')
        reporter_name = request.form.get('reporter_name', 'Campus Member')
        reporter_phone = request.form.get('reporter_phone', '')
        reporter_email = request.form.get('reporter_email', '')
        secret_question = request.form.get('secret_question', '')
        secret_answer = request.form.get('secret_answer', '').strip().lower()
        custom_image_url = request.form.get('image_url', '').strip()

        # Handle file upload or custom image
        final_image_url = custom_image_url
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                timestamp_prefix = datetime.now().strftime('%Y%m%d%H%M%S_')
                saved_filename = timestamp_prefix + fname
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))
                final_image_url = url_for('static', filename=f'uploads/{saved_filename}')

        if not final_image_url:
            # Default placeholder image per category
            placeholders = {
                'Electronics': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80',
                'Identity Cards': 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&auto=format&fit=crop&q=80',
                'Bottles': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80',
                'Keys': 'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=600&auto=format&fit=crop&q=80',
                'Bags & Wallets': 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80',
                'Books & Notes': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80'
            }
            final_image_url = placeholders.get(category, 'https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=600&auto=format&fit=crop&q=80')

        # Generate 4-digit claim PIN
        claim_otp = str(random.randint(1000, 9999))
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        tags = f"{title}, {category}, {location}, {color}, {brand}".lower()

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO items (
            type, title, category, description, location, primary_color, brand,
            date_reported, status, reporter_name, reporter_phone, reporter_email,
            image_url, secret_question, secret_answer, claim_otp, tags
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            'found', title, category, description, location, color, brand,
            now, 'open', reporter_name, reporter_phone, reporter_email,
            final_image_url, secret_question, secret_answer, claim_otp, tags
        ))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash("Found item registered successfully! Broadcast card generated below.", "success")
        return redirect(url_for('item_detail', item_id=item_id))

    return render_template('report_found.html')

@app.route('/report/lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Others')
        location = request.form.get('location', 'JSPM Campus')
        color = request.form.get('primary_color', '')
        brand = request.form.get('brand', '')
        description = request.form.get('description', '')
        reporter_name = request.form.get('reporter_name', 'Student')
        reporter_phone = request.form.get('reporter_phone', '')
        reporter_email = request.form.get('reporter_email', '')
        custom_image_url = request.form.get('image_url', '').strip()

        final_image_url = custom_image_url
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                timestamp_prefix = datetime.now().strftime('%Y%m%d%H%M%S_')
                saved_filename = timestamp_prefix + fname
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], saved_filename))
                final_image_url = url_for('static', filename=f'uploads/{saved_filename}')

        if not final_image_url:
            final_image_url = 'https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=600&auto=format&fit=crop&q=80'

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        tags = f"{title}, {category}, {location}, {color}, {brand}".lower()

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO items (
            type, title, category, description, location, primary_color, brand,
            date_reported, status, reporter_name, reporter_phone, reporter_email,
            image_url, tags
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            'lost', title, category, description, location, color, brand,
            now, 'open', reporter_name, reporter_phone, reporter_email,
            final_image_url, tags
        ))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash("Lost item report submitted! The AI matcher is actively scanning for matches.", "info")
        return redirect(url_for('item_detail', item_id=item_id))

    return render_template('report_lost.html')

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("Item not found.", "danger")
        return redirect(url_for('index'))

    item = dict(row)

    # Get all counter items for matching
    target_counter_type = 'lost' if item['type'] == 'found' else 'found'
    cursor.execute("SELECT * FROM items WHERE type = ?", (target_counter_type,))
    counter_items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Calculate potential matches
    potential_matches = find_potential_matches(item, counter_items, min_threshold=40)

    # Format WhatsApp Card & Share Link
    host = request.host_url.rstrip('/')
    whatsapp_card = format_item_whatsapp_card(item, base_url=host)
    whatsapp_url = generate_whatsapp_share_url(whatsapp_card)

    return render_template('item_detail.html',
                           item=item,
                           matches=potential_matches,
                           whatsapp_card=whatsapp_card,
                           whatsapp_url=whatsapp_url)

@app.route('/claim/<int:item_id>', methods=['POST'])
def process_claim(item_id):
    claimant_name = request.form.get('claimant_name', '').strip()
    claimant_phone = request.form.get('claimant_phone', '').strip()
    submitted_answer = request.form.get('secret_answer', '').strip().lower()

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    # Check secret answer if configured
    expected_answer = (item['secret_answer'] or '').strip().lower()
    if expected_answer and expected_answer not in submitted_answer and submitted_answer not in expected_answer:
        conn.close()
        return jsonify({
            'success': False, 
            'message': 'Verification failed: The secret identifier answer does not match the item records. Please visit the Security Desk with your Student ID.'
        }), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
    UPDATE items 
    SET status = 'claimed', claimed_by_name = ?, claimed_by_phone = ?, claimed_at = ?
    WHERE id = ?
    ''', (claimant_name, claimant_phone, now, item_id))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Claim approved! Your claim verification OTP is: {item["claim_otp"]}. Present this to the Security Guard or Coordinator.',
        'claim_otp': item['claim_otp']
    })

@app.route('/daily-digest')
def daily_digest():
    conn = database.get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM items WHERE type = 'found' AND status = 'open' ORDER BY id DESC")
    found_items = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM items WHERE type = 'lost' AND status = 'open' ORDER BY id DESC")
    lost_items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    host = request.host_url.rstrip('/')
    digest_text = generate_daily_digest(found_items, lost_items, base_url=host)
    whatsapp_url = generate_whatsapp_share_url(digest_text)

    return render_template('daily_digest.html',
                           digest_text=digest_text,
                           whatsapp_url=whatsapp_url,
                           found_count=len(found_items),
                           lost_count=len(lost_items))

@app.route('/security-desk', methods=['GET', 'POST'])
def security_desk():
    conn = database.get_db()
    cursor = conn.cursor()

    message = None
    msg_type = None

    if request.method == 'POST':
        item_id = request.form.get('item_id', '').strip()
        entered_otp = request.form.get('claim_otp', '').strip()

        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()

        if not item:
            message = f"Item #{item_id} not found."
            msg_type = "danger"
        elif item['claim_otp'] != entered_otp:
            message = f"Invalid OTP for Item #{item_id}. Handoff cannot be approved."
            msg_type = "danger"
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("UPDATE items SET status = 'returned', claimed_at = ? WHERE id = ?", (now, item_id))
            conn.commit()
            message = f"Success! Item #{item_id} ('{item['title']}') marked as RETURNED. Handoff completed."
            msg_type = "success"

    cursor.execute("SELECT * FROM items ORDER BY id DESC")
    all_items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template('security_desk.html', items=all_items, message=message, msg_type=msg_type)

@app.route('/api/quick-tag', methods=['POST'])
def api_quick_tag():
    data = request.get_json() or {}
    text = data.get('text', '')
    tags = smart_autotag_from_text(text)
    return jsonify(tags)

@app.route('/api/check-match', methods=['POST'])
def api_check_match():
    data = request.get_json() or {}
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE type = 'found' AND status = 'open'")
    found_items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    matches = find_potential_matches(data, found_items, min_threshold=35)
    return jsonify({'matches': matches[:3]})

if __name__ == '__main__':
    print("==================================================================")
    print("  JSPM CampuSleuth is RUNNING!")
    print("  Open this link in your browser: http://127.0.0.1:5000")
    print("  Or: http://localhost:5000")
    print("  Keep this terminal window open while using the website!")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
