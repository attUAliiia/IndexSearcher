import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import requests
import time
import json
import os
from urllib.parse import urljoin


# default data 


USER_AGENTS = {
    "Normal User": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Admin-like": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/118.0"
}

GENERIC_WORDLIST = [
    "index.html", "index.php", "admin/", "admin.php", "panel/", "panel.php",
    "login.php", "dashboard/", "dashboard.php", "config.php", ".env",
    "backup.zip", "backup.sql", "database.php"
]

WORDPRESS_WORDLIST = [
    "wp-admin/", "wp-login.php", "wp-config.php",
    "wp-content/", "wp-includes/", "xmlrpc.php"
]

WP_DETECTION_PATHS = [
    "wp-login.php",
    "wp-admin/",
    "wp-content/"
]


# how it works lmomomomoamoamso
# 

class WebEnumeratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("directory scanner")
        self.root.geometry("920x600")

        self.running = False
        self.results = []
        self.wordlist = GENERIC_WORDLIST.copy()

        self.build_gui()

    # gui woohoo

    def build_gui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # target
        ttk.Label(frame, text="Target URL").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky="w")

        # user agent
        ttk.Label(frame, text="User-Agent").grid(row=1, column=0, sticky="w")
        self.ua_var = tk.StringVar(value="Normal User")
        ttk.Combobox(frame, textvariable=self.ua_var,
                     values=list(USER_AGENTS.keys()),
                     state="readonly").grid(row=1, column=1, sticky="w")

        # status codes
        ttk.Label(frame, text="Status Codes").grid(row=2, column=0, sticky="w")
        self.status_var = tk.StringVar(value="200")
        ttk.Combobox(frame, textvariable=self.status_var,
                     values=["200", "200,403", "200,301,302,403"],
                     state="readonly").grid(row=2, column=1, sticky="w")

        # rate limit
        ttk.Label(frame, text="Requests/sec").grid(row=3, column=0, sticky="w")
        self.rate_entry = ttk.Entry(frame, width=10)
        self.rate_entry.insert(0, "5")
        self.rate_entry.grid(row=3, column=1, sticky="w")

        # proxy
        ttk.Label(frame, text="Proxy (optional)").grid(row=4, column=0, sticky="w")
        self.proxy_entry = ttk.Entry(frame, width=30)
        self.proxy_entry.grid(row=4, column=1, sticky="w")

        # buttons
        ttk.Button(frame, text="Load Wordlist", command=self.load_wordlist).grid(row=5, column=0)
        ttk.Button(frame, text="Start Scan", command=self.start_scan).grid(row=5, column=1, sticky="w")
        ttk.Button(frame, text="Export TXT", command=lambda: self.export("txt")).grid(row=6, column=0)
        ttk.Button(frame, text="Export JSON", command=lambda: self.export("json")).grid(row=6, column=1, sticky="w")

        # output
        self.output = tk.Text(frame, height=20)
        self.output.grid(row=7, column=0, columnspan=2, sticky="nsew")

        frame.rowconfigure(7, weight=1)
        frame.columnconfigure(1, weight=1)

    # -------------------------
    # util
    # -------------------------

    def log(self, msg):
        self.output.insert("end", msg + "\n")
        self.output.see("end")

    
    # wordlist
    

    def load_wordlist(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        with open(path, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.wordlist.append(line)

        self.log(f"[+] Loaded custom wordlist: {path}")

    # -------------------------
    # WORDPRESS DETECTION
    # -------------------------

    def detect_wordpress(self, base_url, session):
        for path in WP_DETECTION_PATHS:
            try:
                r = session.get(urljoin(base_url + "/", path), timeout=5)
                if r.status_code in (200, 403):
                    return True
            except requests.RequestException:
                pass
        return False

    # -------------------------
    # SCAN
    # -------------------------

    def start_scan(self):
        if self.running:
            return

        self.running = True
        self.results.clear()
        self.output.delete("1.0", "end")

        thread = threading.Thread(target=self.scan)
        thread.daemon = True
        thread.start()

    def scan(self):
        base_url = self.url_entry.get().strip()
        if not base_url.startswith("http"):
            base_url = "http://" + base_url

        headers = {"User-Agent": USER_AGENTS[self.ua_var.get()]}
        status_filter = [int(x) for x in self.status_var.get().split(",")]
        delay = 1 / max(1, int(self.rate_entry.get()))

        proxies = None
        if self.proxy_entry.get():
            proxies = {
                "http": self.proxy_entry.get(),
                "https": self.proxy_entry.get()
            }

        session = requests.Session()
        session.headers.update(headers)
        if proxies:
            session.proxies.update(proxies)

        # WordPress detection
        if self.detect_wordpress(base_url, session):
            self.log("[+] WordPress detected — adding WP paths")
            self.wordlist.extend(WORDPRESS_WORDLIST)

        for path in self.wordlist:
            if not self.running:
                break

            url = urljoin(base_url + "/", path)

            try:
                r = session.get(url, timeout=6, allow_redirects=True)
                if r.status_code in status_filter:
                    self.results.append({
                        "url": url,
                        "status": r.status_code
                    })
                    self.log(f"[{r.status_code}] {url}")
            except requests.RequestException:
                pass

            time.sleep(delay)

        self.log("=== Scan Finished ===")
        self.running = False

    # -------------------------
    # EXPORT
    # -------------------------

    def export(self, mode):
        if not self.results:
            messagebox.showinfo("Export", "No results to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=f".{mode}")
        if not path:
            return

        if mode == "txt":
            with open(path, "w") as f:
                for r in self.results:
                    f.write(f"{r['status']} {r['url']}\n")

        elif mode == "json":
            with open(path, "w") as f:
                json.dump(self.results, f, indent=2)

        messagebox.showinfo("Export", f"Saved to {path}")

# =============================
# RUN
# =============================

if __name__ == "__main__":
    root = tk.Tk()
    app = WebEnumeratorApp(root)
    root.mainloop()
