"""Screenshot key views at laptop and phone width, light and dark.
Usage: python3 course/screenshots.py  (needs playwright + Chrome)"""
import http.server
import os
import socketserver
import threading

from playwright.sync_api import sync_playwright

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "tmp", "shots")
os.makedirs(OUT, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), H)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
views = ["home", "ch01", "ch12", "ch13", "ch17", "ch29", "drills", "map"]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for scheme, w, h in [("light", 1280, 900), ("dark", 1280, 900), ("light", 390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h}, color_scheme=scheme)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for v in views:
            pg.goto(f"http://127.0.0.1:{port}/#{v}")
            pg.wait_for_timeout(400)
            overflow = pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
            if overflow:
                errs.append(f"horizontal overflow {v} {w}")
            pg.screenshot(path=os.path.join(OUT, f"{v}-{scheme}-{w}.png"), full_page=(v in ("ch12", "ch13", "ch17")))
    b.close()
srv.shutdown()
print("errors:", errs or "none")
