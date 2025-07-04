from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
events = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if data and event_type:
        events.append({
            "type": event_type,
            "time": timestamp,
            "repo": data.get("repository", {}).get("full_name"),
            "details": data
        })
        print(f"✅ Received {event_type} at {timestamp}")
        return jsonify({"status": "received"}), 200
    return jsonify({"status": "ignored"}), 400

@app.route('/')
def index():
    return jsonify(events)

if __name__ == '__main__':
    app.run(port=5000)
