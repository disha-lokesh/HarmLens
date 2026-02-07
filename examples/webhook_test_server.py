"""
Webhook Test Server - REAL endpoint that receives HarmLens alerts
Run this to test webhook functionality
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
from datetime import datetime

# In-memory storage of received webhooks
received_webhooks = []


class WebhookHandler(BaseHTTPRequestHandler):
    """Simple HTTP server that receives webhook POSTs"""
    
    def do_POST(self):
        """Handle POST requests (webhooks)"""
        if self.path == '/webhook/alerts':
            # Read body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Log received webhook
            webhook_entry = {
                'received_at': datetime.now().isoformat(),
                'data': data
            }
            received_webhooks.append(webhook_entry)
            
            # Print to console (in production: send to Slack, email, SMS)
            print("\n" + "=" * 60)
            print("🚨 WEBHOOK RECEIVED!")
            print("=" * 60)
            print(json.dumps(data, indent=2))
            print("=" * 60 + "\n")
            
            # REAL ACTION: You would do something here
            if data.get('priority') == 'CRITICAL':
                print("🚨 CRITICAL ALERT: Sending to on-call moderator...")
            elif data.get('child_escalation'):
                print("👶 CHILD SAFETY ALERT: Escalating to specialist team...")
            elif data.get('priority') == 'HIGH':
                print("⚠️ HIGH PRIORITY: Adding to review queue...")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "received",
                "message": "Webhook processed successfully",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = f"""
            <h1>HarmLens Webhook Test Server</h1>
            <p>This server receives webhook alerts from HarmLens.</p>
            <p><strong>Endpoint:</strong> POST /webhook/alerts</p>
            <p><strong>Webhooks received:</strong> {len(received_webhooks)}</p>
            <hr>
            <h3>How to use:</h3>
            <ol>
                <li>Run this server: <code>python examples/webhook_test_server.py</code></li>
                <li>Set environment variable: <code>$env:WEBHOOK_HIGH_RISK='http://localhost:5000/webhook/alerts'</code></li>
                <li>Analyze high-risk content in HarmLens</li>
                <li>Watch alerts appear in this server's console!</li>
            </ol>
            """
            self.wfile.write(html.encode())
        elif self.path == '/webhook/history':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "total": len(received_webhooks),
                "webhooks": received_webhooks
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


if __name__ == '__main__':
    print("=" * 60)
    print("HarmLens Webhook Test Server")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Endpoint: POST /webhook/alerts")
    print("\nTo configure HarmLens to send here:")
    print("  $env:WEBHOOK_HIGH_RISK='http://localhost:5000/webhook/alerts'")
    print("=" * 60 + "\n")
    
    server = HTTPServer(('0.0.0.0', 5000), WebhookHandler)
    print("✅ Server ready - waiting for webhooks...\n")
    server.serve_forever()
