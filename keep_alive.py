from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import os
import json

status_callback = None

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status = status_callback() if status_callback else {"status": "unknown"}
            body = json.dumps(status, default=str).encode("utf-8")
            http_status = 200 if status.get("healthy", False) else 503

            self.send_response(http_status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    # ดึงค่า Port จาก Render ถ้าไม่มีให้ใช้ 8080
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    server.serve_forever()

def keep_alive(get_status=None):
    global status_callback
    status_callback = get_status

    t = Thread(target=run_server)
    t.daemon = True
    t.start()
