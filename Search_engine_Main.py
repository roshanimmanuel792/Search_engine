import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import requests
from io import BytesIO
import webbrowser
import threading
import queue
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

class SmartSearchApp:
    def __init__(self, root, user_type="normal"):
        self.root = root
        self.user_type = user_type
        self.root.title(f"Smart Search Engine - {user_type.capitalize()} Mode")
        self.root.geometry("950x640")
        self.root.configure(bg="white")

        # ====== API setup ======
        self.API_KEY = ""  # <-- Paste your API Key here
        self.CX_MAP = {
            "General": "",   # <-- Paste your CX ID for General
            "Shopping": "",  # <-- Paste your CX ID for Shopping
            "News": ""       # <-- Paste your CX ID for News
        }

        # ====== Email alert ======
        self.sender_email = ""       # <-- Your Gmail
        self.sender_password = ""    # <-- Your Gmail App Password
        self.recipient_email = ""    # <-- Recipient Email

        # ====== Risky keywords by mode ======
        if self.user_type == "aged":
            self.risky_keywords = [
                "otp", "pin", "credit card", "bank", "aadhar", "ssn",
                "password", "login help", "refund", "cash app", "transfer money"
            ]
        else:
            self.risky_keywords = []

        self.img_cache = {}
        self.search_queue = queue.Queue()
        self.is_searching = False
        self.selected_category = tk.StringVar(value="General")

        self.setup_ui()
        self.start_worker_thread()

    # ====== GUI ======
    def setup_ui(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("Treeview", font=("Helvetica", 11), rowheight=100)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        title_text = "Search App (Google Powered)"
        if self.user_type == "aged":
            title_text = "Search App (Elder-Friendly Mode)"
        ttk.Label(self.root, text=title_text, font=("Helvetica", 20, "bold")).pack(pady=10)

        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.entry = ttk.Entry(search_frame, width=50, font=("Helvetica", 12))
        self.entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.entry.bind("<Return>", lambda event: self.start_search())
        self.entry.bind("<KeyRelease>", self.show_suggestions)

        mic_btn = ttk.Button(search_frame, text="🎤", command=self.voice_input)
        mic_btn.pack(side="right", padx=(10, 5))

        self.search_button = ttk.Button(search_frame, text="Search", command=self.start_search)
        self.search_button.pack(side="right")

        category_menu = ttk.Combobox(search_frame, textvariable=self.selected_category,
                                     values=["General", "Shopping", "News"], width=10, state="readonly")
        category_menu.pack(side="right", padx=(0, 10))

        self.suggestion_listbox = tk.Listbox(self.root, height=5, font=("Helvetica", 11))
        self.suggestion_listbox.pack_forget()
        self.suggestion_listbox.bind("<<ListboxSelect>>", self.select_suggestion)

        self.status_label = ttk.Label(self.root, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 10))

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Image", "Title", "Snippet", "Link"), show="headings", height=6)
        self.tree.pack(side="left", fill="both", expand=True)

        for col in ("Image", "Title", "Snippet", "Link"):
            self.tree.heading(col, text=col)
            width = 100 if col == "Image" else 250 if col == "Title" else 300
            self.tree.column(col, anchor="center", width=width)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self.open_link)

        status_bar = ttk.Label(self.root, text="Double-click any result to open in browser", relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ====== Threads ======
    def start_worker_thread(self):
        threading.Thread(target=self.process_search_queue, daemon=True).start()

    def process_search_queue(self):
        while True:
            query = self.search_queue.get()
            if query is None:
                break
            self.root.after(0, lambda: self.update_ui_searching(True))
            try:
                all_results = self.fetch_google_search_results(query)
                self.root.after(0, lambda results=all_results: self.update_results(results))
            except Exception as e:
                pass  # Silent fail
            finally:
                self.root.after(0, lambda: self.update_ui_searching(False))
                self.search_queue.task_done()

    def update_ui_searching(self, is_searching):
        self.is_searching = is_searching
        if is_searching:
            self.progress.start(10)
            self.search_button.configure(state="disabled")
            self.status_label.configure(text="Searching...")
        else:
            self.progress.stop()
            self.search_button.configure(state="normal")
            self.status_label.configure(text="")

    def update_results(self, results):
        self.tree.delete(*self.tree.get_children())
        self.img_cache.clear()

        if not results:
            self.tree.insert("", "end", values=("", "No results found", "", ""))
            return

        self.add_batch_results(results, 0, 3)

    def add_batch_results(self, results, start_idx, batch_size):
        end_idx = min(start_idx + batch_size, len(results))
        batch = results[start_idx:end_idx]

        for item in batch:
            img_url, title, snippet, link = item
            img = None

            if img_url:
                try:
                    response = requests.get(img_url, timeout=3)
                    img = Image.open(BytesIO(response.content)).resize((60, 80))
                    img = ImageTk.PhotoImage(img)
                    self.img_cache[title] = img
                except:
                    img = None

            row_id = self.tree.insert("", "end", values=("", title, snippet, link), tags=(title,))
            if img:
                self.tree.item(row_id, image=img)

        if end_idx < len(results):
            self.root.after(10, lambda: self.add_batch_results(results, end_idx, batch_size))

    # ====== Search ======
    def start_search(self):
        query = self.entry.get().strip()
        self.suggestion_listbox.pack_forget()
        if not query:
            return
        if self.is_searching:
            return
        if self.user_type == "aged":
            self.check_for_risky_query(query)
        self.search_queue.put(query)

    def check_for_risky_query(self, query):
        for keyword in self.risky_keywords:
            if keyword.lower() in query.lower():
                self.trigger_alert(query)
                break

    # ====== Silent alert ======
    def trigger_alert(self, query):
        subject = "⚠️ Alert: Risky Search Detected"
        body = f"""
Hi,

A sensitive search query was detected on the Smart Search app:

🔍 Search Query: "{query}"
📅 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

Please check on your loved one and ensure they are safe from online scams.

– Smart Search Alert System
"""
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
        except:
            pass  # Silent fail, no pop-ups

    # ====== Google Search ======
    def fetch_google_search_results(self, query):
        API_KEY = self.API_KEY
        category = self.selected_category.get()
        CX = self.CX_MAP.get(category, "")

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}&safe=high"
        res = requests.get(url, timeout=5)
        data = res.json()
        results = []

        for item in data.get("items", []):
            title = item.get("title", "N/A")
            link = item.get("link", "")
            snippet = item.get("snippet", "No description")
            image_url = item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", "")
            results.append((image_url, title, snippet, link))

        return results

    # ====== Open link ======
    def open_link(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            link = self.tree.item(item)["values"][3]
            if link:
                webbrowser.open(link)

    # ====== Voice Input ======
    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.config(text="Listening...")
            self.root.update()
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, text)
                self.start_search()
            except:
                pass
            finally:
                self.status_label.config(text="")

    # ====== Suggestions ======
    def show_suggestions(self, event):
        query = self.entry.get().strip()
        if not query:
            self.suggestion_listbox.pack_forget()
            return
        url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={query}"
        try:
            res = requests.get(url)
            suggestions = res.json()[1]
            self.suggestion_listbox.delete(0, tk.END)
            for item in suggestions:
                self.suggestion_listbox.insert(tk.END, item)
            self.suggestion_listbox.place(x=self.entry.winfo_rootx() - self.root.winfo_rootx(),
                                          y=self.entry.winfo_rooty() - self.root.winfo_rooty() + 30,
                                          width=self.entry.winfo_width())
            self.suggestion_listbox.lift()
            self.suggestion_listbox.pack()
        except:
            self.suggestion_listbox.pack_forget()

    def select_suggestion(self, event):
        if self.suggestion_listbox.curselection():
            index = self.suggestion_listbox.curselection()[0]
            value = self.suggestion_listbox.get(index)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, value)
            self.suggestion_listbox.pack_forget()
            self.start_search()

# ====== Multi-mode Selector ======
def launch_mode_selector():
    setup_root = tk.Tk()
    setup_root.title("Smart Search Setup")
    setup_root.geometry("400x200")

    tk.Label(setup_root, text="Choose User Mode", font=("Helvetica", 16)).pack(pady=20)

    def launch_app(user_type):
        setup_root.destroy()
        root = tk.Tk()
        SmartSearchApp(root, user_type)
        root.mainloop()

    tk.Button(setup_root, text="Normal User", width=20,
              command=lambda: launch_app("normal")).pack(pady=10)
    tk.Button(setup_root, text="Aged User", width=20,
              command=lambda: launch_app("aged")).pack(pady=10)

    setup_root.mainloop()

def main():
    launch_mode_selector()

if __name__ == "__main__":
    main()
