import urllib.parse
from datetime import datetime

def format_item_whatsapp_card(item, base_url="http://localhost:5000"):
    """
    Formats a single Lost/Found item into an eye-catching, zero-typing WhatsApp broadcast card.
    """
    item_type = item['type'].upper()
    is_found = item['type'].lower() == 'found'
    
    emoji = "🟢 📢 [NEW FOUND ITEM]" if is_found else "🔴 🔍 [LOST ITEM REPORTED]"
    action_note = "If this belongs to you, claim it below with your Student ID." if is_found else "If you spotted this, please report or hand it over to Campus Security."
    
    claim_link = f"{base_url}/item/{item['id']}"
    
    text = f"""{emoji}
*JSPM UNIVERSITY LOST & FOUND HUB*
━━━━━━━━━━━━━━━━━━━━━
🏷️ *Item:* {item['title']}
📂 *Category:* {item['category']}
📍 *Location:* {item['location']}
🎨 *Color/Brand:* {item.get('primary_color', 'N/A')} | {item.get('brand', 'N/A')}
🕒 *Reported At:* {item['date_reported']}

📝 *Details:*
_{item.get('description', 'No extra details provided')}_

{action_note}
🔗 *View & Claim:* {claim_link}
━━━━━━━━━━━━━━━━━━━━━
_🤖 Automated via JSPM CampuSleuth (Zero-Typing System)_
"""
    return text.strip()

def generate_whatsapp_share_url(message_text, phone_number=""):
    """
    Generates a wa.me URL for instant one-click sharing without typing anything.
    If phone_number is empty, it opens WhatsApp for the user to pick any group/chat.
    """
    encoded_text = urllib.parse.quote(message_text)
    if phone_number:
        clean_phone = "".join(filter(str.isdigit, phone_number))
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    return f"https://api.whatsapp.com/send?text={encoded_text}"

def generate_daily_digest(found_items, lost_items, date_str=None, base_url="http://localhost:5000"):
    """
    Creates a single consolidated daily bulletin message.
    Solves the problem of coordinators typing repetitive messages all day.
    """
    if not date_str:
        date_str = datetime.now().strftime("%d %b %Y")
        
    found_lines = []
    for i, it in enumerate(found_items[:7], 1):
        found_lines.append(f"{i}️⃣ *{it['title']}* \n   📍 {it['location']} | ID #{it['id']}")
        
    if not found_lines:
        found_lines = ["_No new found items reported today._"]
        
    lost_lines = []
    for i, it in enumerate(lost_items[:5], 1):
        lost_lines.append(f"• *{it['title']}* ({it['location']})")
        
    if not lost_lines:
        lost_lines = ["_No active lost reports pending._"]

    digest = f"""📢 *JSPM UNIVERSITY - DAILY LOST & FOUND BULLETIN*
🗓️ *Date:* {date_str}
━━━━━━━━━━━━━━━━━━━━━━━━
🟢 *ITEMS RECOVERED TODAY ({len(found_items)}):*
{chr(10).join(found_lines)}

🔴 *RECENT LOST ALERTS ({len(lost_items)}):*
{chr(10).join(lost_lines)}

━━━━━━━━━━━━━━━━━━━━━━━━
🏛️ *Central Retrieval Desk:* Campus Security Main Gate / Student Welfare Office
🌐 *Live Portal & Smart Matching:* {base_url}
_⚡ Automated Daily Digest • Saves 100% Manual Typing Time_
"""
    return digest.strip()
