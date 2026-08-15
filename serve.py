"""
Simple HTTP Server for ContentForensics Report Viewer
This script starts a local web server to serve the report viewer HTML file.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

# Configuration
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler to set proper CORS headers"""

    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    """Start the HTTP server and open the browser"""

    # Change to the script's directory
    os.chdir(DIRECTORY)

    # Check if report.json exists
    if not os.path.exists('report.json'):
        print("⚠️  Warning: report.json not found!")
        print("   Please run main.py first to generate a report.")
        print()

    # Create the server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/report_veiwer.html"

        print("=" * 60)
        print("🚀 ContentForensics Report Viewer Server")
        print("=" * 60)
        print(f"📂 Serving from: {DIRECTORY}")
        print(f"🌐 Server running at: http://localhost:{PORT}")
        print(f"📊 Report viewer: {url}")
        print()
        print("💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        print()

        # Open the browser
        print("Opening browser...")
        webbrowser.open(url)

        # Start serving
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()

