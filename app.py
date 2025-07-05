from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# ✅ MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["events"]

# ✅ Webhook Route
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        event_type = request.headers.get('X-GitHub-Event')
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        author = None
        from_branch = None
        to_branch = None

        if event_type == "push":
            author = data.get("pusher", {}).get("name")
            to_branch = data.get("ref", "").split("/")[-1]

        elif event_type == "pull_request":
            pr = data.get("pull_request", {})
            action = data.get("action")
            author = pr.get("user", {}).get("login")
            from_branch = pr.get("head", {}).get("ref")
            to_branch = pr.get("base", {}).get("ref")

            if action == "closed" and pr.get("merged"):
                event_type = "merge"

        else:
            return jsonify({"message": "Unsupported event"}), 400

        if author:
            collection.insert_one({
                "author": author,
                "event": event_type,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            })
            print(f"✅ Stored {event_type} by {author} at {timestamp}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Render Frontend UI
@app.route('/')
def index():
    return render_template("index.html")

# ✅ Events API for frontend
@app.route('/events')
def get_events():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False)
