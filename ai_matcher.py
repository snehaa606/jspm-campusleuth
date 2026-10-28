import re

CATEGORIES = [
    'Electronics', 'Identity Cards', 'Bottles', 'Keys', 
    'Bags & Wallets', 'Books & Notes', 'Clothing/Accessories', 'Others'
]

CAMPUS_LOCATIONS = [
    'Main Canteen (Near Nescafe)',
    'Central Library - Ground/1st Floor',
    'Computer Dept - Labs & Classrooms',
    'Mechanical Engineering Building',
    'Civil Engineering Building',
    'Pharmacy Wing & Labs',
    'MBA & Management Block',
    'Main Auditorium / Seminar Hall',
    'Campus Parking Bay (A/B/C)',
    'Sports Ground / Gymnasium',
    'Security Main Gate'
]

COMMON_COLORS = ['Black', 'Blue', 'Silver', 'White', 'Red', 'Grey', 'Green', 'Yellow', 'Pink', 'Brown']

def calculate_match_score(item_a, item_b):
    """
    Computes a match probability score (0 to 100) between a Lost item and a Found item.
    """
    score = 0
    reasons = []

    # 1. Category check (High weight: 40 points)
    if item_a.get('category') and item_b.get('category'):
        if item_a['category'].lower() == item_b['category'].lower():
            score += 40
            reasons.append(f"Category matches ({item_a['category']})")

    # 2. Color check (Weight: 20 points)
    color_a = (item_a.get('primary_color') or '').strip().lower()
    color_b = (item_b.get('primary_color') or '').strip().lower()
    if color_a and color_b and (color_a in color_b or color_b in color_a):
        score += 20
        reasons.append(f"Color matches ({color_a.capitalize()})")

    # 3. Brand check (Weight: 20 points)
    brand_a = (item_a.get('brand') or '').strip().lower()
    brand_b = (item_b.get('brand') or '').strip().lower()
    if brand_a and brand_b and (brand_a in brand_b or brand_b in brand_a):
        score += 20
        reasons.append(f"Brand matches ({brand_a.capitalize()})")

    # 4. Location proximity check (Weight: 10 points)
    loc_a = (item_a.get('location') or '').strip().lower()
    loc_b = (item_b.get('location') or '').strip().lower()
    if loc_a and loc_b:
        words_a = set(re.findall(r'\w+', loc_a))
        words_b = set(re.findall(r'\w+', loc_b))
        common_loc = words_a.intersection(words_b) - {'near', 'the', 'and', 'floor', 'block', 'building', 'dept'}
        if common_loc:
            score += 10
            reasons.append("Reported in similar campus zone")

    # 5. Title & Description keyword overlap (Weight: 10 points)
    text_a = f"{item_a.get('title', '')} {item_a.get('description', '')}".lower()
    text_b = f"{item_b.get('title', '')} {item_b.get('description', '')}".lower()
    words_a = set(re.findall(r'\b[a-z]{3,}\b', text_a))
    words_b = set(re.findall(r'\b[a-z]{3,}\b', text_b))
    stop_words = {'found', 'lost', 'near', 'table', 'floor', 'with', 'this', 'that', 'have', 'from', 'area'}
    common_words = (words_a.intersection(words_b)) - stop_words

    if len(common_words) >= 2:
        score += 10
        reasons.append(f"Keywords match: {', '.join(list(common_words)[:3])}")
    elif len(common_words) == 1:
        score += 5
        reasons.append(f"Keyword match: {list(common_words)[0]}")

    return min(score, 100), reasons

def find_potential_matches(target_item, candidate_items, min_threshold=40):
    """
    Scans candidate items to find potential matches for target_item.
    """
    matches = []
    for cand in candidate_items:
        # Only compare open items and opposite types (lost vs found)
        if cand['type'] != target_item['type'] and cand['status'] != 'returned':
            score, reasons = calculate_match_score(target_item, cand)
            if score >= min_threshold:
                matches.append({
                    'item': cand,
                    'score': score,
                    'reasons': reasons
                })
    
    # Sort descending by match score
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def smart_autotag_from_text(text):
    """
    Extracts category, color, and keywords from a quick sentence
    e.g. "Found black boat airdopes in canteen"
    """
    text_lower = text.lower()
    detected_cat = 'Others'
    detected_color = ''
    detected_brand = ''

    if any(k in text_lower for k in ['airdopes', 'earbuds', 'headphone', 'charger', 'laptop', 'phone', 'mobile', 'calculator']):
        detected_cat = 'Electronics'
    elif any(k in text_lower for k in ['id card', 'id-card', 'prn', 'admit card', 'identity']):
        detected_cat = 'Identity Cards'
    elif any(k in text_lower for k in ['bottle', 'flask', 'milton', 'tupperware', 'sipper']):
        detected_cat = 'Bottles'
    elif any(k in text_lower for k in ['key', 'keys', 'bike key', 'car key']):
        detected_cat = 'Keys'
    elif any(k in text_lower for k in ['wallet', 'purse', 'pouch', 'bag', 'backpack']):
        detected_cat = 'Bags & Wallets'
    elif any(k in text_lower for k in ['book', 'notes', 'register', 'file', 'manual']):
        detected_cat = 'Books & Notes'

    for col in COMMON_COLORS:
        if col.lower() in text_lower:
            detected_color = col
            break

    brands = ['boat', 'milton', 'hp', 'dell', 'lenovo', 'apple', 'samsung', 'fastrack', 'casio', 'hero', 'honda']
    for b in brands:
        if b in text_lower:
            detected_brand = b.capitalize()
            break

    return {
        'category': detected_cat,
        'color': detected_color,
        'brand': detected_brand
    }
