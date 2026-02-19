import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# CORS設定をさらに広げます
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

@app.route('/analyze', methods=['POST'])
def analyze():
    # (中身のロジックは以前と同じでOKです)
    data = request.json
    user_thought = data.get('thought', '')
    payload = {"contents": [{"parts": [{"text": f"JSONで分析して: {user_thought}"}]}]}
    try:
        response = requests.post(GEMINI_URL, json=payload)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running!"

# Render用のポート起動設定
if __name__ == '__main__':
    # 0.0.0.0 と PORT の組み合わせが必須です
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)