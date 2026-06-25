import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from weather_api import get_weather

HOST = "127.0.0.1"
PORT = 5000


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/weather":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = (
                "<html><body><h1>Weather Cache Demo</h1>"
                "<p>Gunakan <code>/weather?city=Jakarta</code> untuk melihat response.</p>"
                "</body></html>"
            )
            self.wfile.write(html.encode("utf-8"))
            return

        params = parse_qs(parsed.query)
        city = params.get("city", ["Jakarta"])[0]
        result = get_weather(city)
        body = json.dumps(result, indent=2).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_server():
    server = HTTPServer((HOST, PORT), WeatherHandler)
    print(f"Server berjalan di http://{HOST}:{PORT}")
    print("Buka /weather?city=Jakarta untuk demo cache")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
