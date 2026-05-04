from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import os

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    # ดึงค่า Port จาก Render ถ้าไม่มีให้ใช้ 8080
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    server.serve_forever()

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()