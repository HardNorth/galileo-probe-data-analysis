#!/usr/bin/env python3
"""
Simple HTTP server to serve the interactive chart and CSV files.
Run this script and open http://localhost:8000/interactive_chart.html in your browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

# Change to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()


def main():
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"Starting server at http://localhost:{PORT}")
            print(f"Open http://localhost:{PORT} in your browser")
            print("Press Ctrl+C to stop the server")

            # Try to open the browser automatically
            try:
                webbrowser.open(f"http://localhost:{PORT}")
            except Exception:
                pass

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {PORT} is already in use. Please stop the other server or use a different port.")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main()
