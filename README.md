📖 Smart Search Engine (Elder-Friendly)

A Python-based smart search app powered by Google Custom Search API with voice input, suggestions, scam alerts, and dual user modes (Normal / Elder-Friendly).


---

🚀 Features

🔍 Google Custom Search integration

🎤 Voice input support

💡 Auto-suggestions while typing

🖼️ Results with images, titles, snippets, and links

👵 Elder-friendly mode with scam keyword detection

📧 Silent email alerts for risky searches (in Elder mode)



---

🛠️ Requirements

Make sure you have Python 3.7+ installed.
Install dependencies with:

pip install pillow requests SpeechRecognition


---

⚙️ Setup

1. Get a Google Custom Search API Key → Google API Console.


2. Create a Custom Search Engine (CX ID) → CSE Dashboard.


3. Open the code and paste your API key & CX IDs in:

self.API_KEY = "YOUR_API_KEY"
self.CX_MAP = {
    "General": "CX_ID",
    "Shopping": "CX_ID",
    "News": "CX_ID"
}


4. (Optional) Configure Gmail for silent scam alerts:

self.sender_email = "your@gmail.com"
self.sender_password = "your-app-password"
self.recipient_email = "recipient@gmail.com"




---

▶️ Run

python Search_engine_Main.py

Then choose Normal User or Aged User mode.

⚠️this is an open source project .you can edit for your own purposes.
Future suggestions and contributions are welcome.