Smart Search Engine (Google + GenAI Powered)

A next-gen desktop Smart Search Engine built with Python & Tkinter.
It combines the Google Custom Search API for powerful search with Generative AI (Hugging Face Zero-Shot Classifier) for scam/risk detection — making it especially safe for elderly users.


---

✨ Features

🔎 Google Custom Search Integration

Search across General, Shopping, and News.

Fetches results with title, snippet, image, and links.


🎤 Voice Search
Speak your queries using Google Speech Recognition.

💡 Smart Suggestions
Google-like auto-complete suggestions while typing.

🖼 Rich Result Viewer

Scrollable results with images and snippets.

Double-click to open in browser.


🧓 Elder-Friendly GenAI Safety Mode

Uses keyword filters and Hugging Face AI (facebook/bart-large-mnli).

Detects scam, financial fraud, personal info risks.

Triggers a silent Gmail alert to trusted contacts.

Runs in background, user is not notified.


⚡ Smooth UX

Multi-threaded searches (no freezing).

Results load in batches for speed.




---

📸 Screenshots

(Add screenshots here)


---

🚀 Installation

1. Clone repo

git clone https://github.com/yourusername/smart-search-engine.git
cd smart-search-engine


2. Install dependencies

pip install -r requirements.txt


3. Configure keys Edit smart_search.py:

self.API_KEY = "YOUR_GOOGLE_API_KEY"
self.CX_MAP = {
    "General": "YOUR_GENERAL_CX_ID",
    "Shopping": "YOUR_SHOPPING_CX_ID",
    "News": "YOUR_NEWS_CX_ID"
}
self.HF_API_KEY = "YOUR_HUGGINGFACE_TOKEN"  # For GenAI risk detection
self.sender_email = "YOUR_GMAIL"
self.sender_password = "YOUR_GMAIL_APP_PASSWORD"
self.recipient_email = "ALERT_RECIPIENT_EMAIL"




---

📦 Requirements

Python 3.8+

Google Custom Search JSON API

Hugging Face Inference API token (for GenAI scam detection)

Gmail App Password (for alerts)


Python Packages

tkinter
pillow
requests
speechrecognition


---

▶️ Usage

Run the app:

python smart_search.py

Choose a mode:

Normal Mode → Standard Google-powered search.

Aged Mode → Scam-aware GenAI search + silent email alerts.



---

⚠️ Security Notes

Keep API keys and Gmail passwords private.

Use App Passwords for Gmail.

Hugging Face free tier may have rate limits.

This is a prototype / proof-of-concept.



---

📌 Roadmap

[ ] Add Image & Video search

[ ] Local database (SQLite/PostgreSQL) for history

[ ] Browser extension version

[ ] Multi-language voice input



---

🤝 Contributing

Contributions are welcome! Fork the repo and open a PR.


---

📜 License

MIT License. Free to use & modify.

