
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, requests

# ----------------- CONFIG -----------------
HF_TOKEN = "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"
MODEL = "HuggingFaceTB/SmolLM3-3B:hf-inference"

HF_URL = "https://router.huggingface.co/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ----------------- APP -----------------
app = Flask(__name__)
CORS(app)

# ----------------- DB -----------------
conn = sqlite3.connect("chat.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    text TEXT
)
""")
conn.commit()

# ----------------- AI FUNCTION -----------------
import re

def get_ai_reply(user_input):

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }

    try:
        res = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=60)

        print("HF STATUS:", res.status_code)
        print("HF RAW:", res.text)

        # ✅ Check HTTP status first
        if res.status_code != 200:
            return f"AI API Error: {res.status_code}"

        data = res.json()

        # ✅ Extract final message
        ai_text = data["choices"][0]["message"]["content"]

        # ✅ REMOVE <think> ... </think> chains
        ai_text = re.sub(r"<think>.*?</think>", "", ai_text, flags=re.DOTALL).strip()

        return ai_text

    except Exception as e:
        print("HF ERROR:", e)
        return "AI temporarily unavailable."


# ----------------- ROUTES -----------------

@app.route("/", methods=["GET"])
def home():
    return "✅ AI Chat Backend is running"

@app.route("/history", methods=["GET"])
def history():
    rows = cur.execute("SELECT sender, text FROM messages ORDER BY id").fetchall()
    return jsonify(rows)

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Message required"}), 400

    user_message = data["message"]

    # Save user input
    cur.execute("INSERT INTO messages(sender,text) VALUES (?,?)",
                ("user", user_message))

    # Get AI
    ai_reply = get_ai_reply(user_message)

    # Save AI reply
    cur.execute("INSERT INTO messages(sender,text) VALUES (?,?)",
                ("ai", ai_reply))

    conn.commit()

    return jsonify({"reply": ai_reply})
# ----------------- CLEAR CHAT DATABASE -----------------

# -----------------
app.run(debug=True)
