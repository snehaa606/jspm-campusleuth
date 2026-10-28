# 🎓 JSPM CampuSleuth: AI-Powered Campus Lost & Found System
> **Solving the repetitive WhatsApp group typing burden for JSPM University.**

---

## 📌 1. The Core Problem & Motivation
In JSPM University (and many Indian campuses), lost and found items are handled through WhatsApp groups:
* **The "One Man" Burden:** A single coordinator or class representative spends **30 to 45 minutes every day** typing repetitive messages manually (*"Found keys near Canteen...", "Lost bag in Mechanical Building..."*).
* **Information Clutter:** Messages quickly get buried beneath regular class announcements, memes, and daily group conversations.
* **No Searchability:** If a student lost an item on Monday, they cannot easily search WhatsApp on Thursday without scrolling through thousands of messages.
* **Fake Claims & Fraud:** Anyone in the group can simply reply *"Bhai, this is mine"* and pick up expensive earbuds, calculators, or watches without verification.

---

## 💡 2. The Creative Solution: Zero-Typing Hub

**JSPM CampuSleuth** replaces chaotic WhatsApp typing with a **smart, automated ecosystem**:

1. **Zero-Typing Smart Auto-Fill:** 
   * When someone finds an item, they type 3 words (e.g., *"Found boat airdopes in canteen"*) or drop a photo.
   * The AI auto-extracts Category, Color, Brand, and JSPM Location instantly.
2. **One-Click WhatsApp Broadcast Cards:**
   * Automatically formats high-impact WhatsApp cards with emojis, verified location, and claim links.
   * **1-Click Share Button (`wa.me`):** Opens WhatsApp with the message ready to post. **0 characters typed by the coordinator!**
3. **Consolidated 6:00 PM Daily WhatsApp Bulletin:**
   * Instead of 15 separate messages throughout the day, the system generates a single clean daily digest of all found & lost items.
4. **Reverse AI Matching Engine:**
   * When a student reports a lost item, the system scans the database in real-time. If an item matches by 70%+, it triggers an instant alert!
5. **Anti-Theft Verification Shield:**
   * For valuable items (electronics, wallets, keys), the finder sets a secret question (*"What sticker is on the back?"*).
   * Claimant must answer correctly to unlock a 4-digit **Claim OTP**.
   * Security guard verifies the OTP at the gate before handing the item over.

---

## 🛠️ 3. Tech Stack

* **Backend & API:** Python (Flask)
* **Frontend:** HTML5, Modern Tailwind CSS (via CDN), FontAwesome Icons, Vanilla JS
* **Database:** SQLite3 (Built-in, zero configuration required)
* **Intelligence Layer:** Rule-based NLP extraction & Semantic scoring engine
* **Integration:** WhatsApp Web / Universal URI Handler (`api.whatsapp.com`)

---

## 🚀 4. How to Run the Project

### Step 1: Open Terminal in the Project Directory
```powershell
cd "c:\Users\Sneha Patil\Downloads\Sneha"
```

### Step 2: Initialize Database & Run Application
```powershell
python app.py
```

### Step 3: Open in Browser
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📱 5. Key Pages & Workflows to Demonstrate

| Route | Feature | Why It Matters for JSPM |
|---|---|---|
| `/` | **Campus Feed & Live Metrics** | Shows items by location (Canteen, Library, Mechanical Lab), and displays hours of typing saved. |
| `/report/found` | **Zero-Typing Found Form** | Test the "Auto-Fill" box by typing *"Found blue milton bottle in library"*. |
| `/report/lost` | **Lost Report + Live Matcher** | Type *"HP Laptop Charger"* and see the instant match banner pop up! |
| `/item/<id>` | **Broadcast Card & Claim** | See the formatted WhatsApp card and test the Secret Verification modal. |
| `/daily-digest` | **6:00 PM WhatsApp Digest** | Click "Share Directly to WhatsApp" to post the daily bulletin to class groups. |
| `/security-desk` | **Security Desk Handoff** | Enter Item ID and 4-digit Claim PIN to authorize physical pickup. |

---

## 🏆 6. Viva & Project Presentation Questions (Ready Answers)

### Q1: Why not just build a standalone mobile app?
> **Answer:** Most college students will not download a 50MB app just to report a lost water bottle. Our system integrates directly with **WhatsApp** (which 100% of students already use) through automated cards and wa.me links, while providing a fast web portal that works on any browser without installation.

### Q2: How does this solve the manual typing problem?
> **Answer:** Previously, the coordinator had to manually construct and type each WhatsApp message. With CampuSleuth, the system generates the exact WhatsApp card with formatting, emojis, tags, and links. With one click, it broadcasts the message or creates an automated 6 PM daily summary bulletin.

### Q3: How do you prevent theft or false claims?
> **Answer:** Through the **Ownership Shield**. The finder sets a secret question (e.g., *"What is the phone wallpaper?"* or *"What keychain is attached?"*). The claimant must provide the correct answer or show their JSPM Student ID. Upon verification, the system issues a **One-Time Claim PIN (OTP)** that must be checked by the Security Guard at the gate.
