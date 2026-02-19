import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 最もシンプルなCORS設定
CORS(app)

# 1. プロンプト（ファイルがなければデフォルトを使用）
def load_prompt():
    path = "prompt.txt"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return "あなたは優秀なCBTカウンセラーです。必ずJSON形式で回答してください。"

SYSTEM_PROMPT = load_prompt()

# 2. Gemini APIの設定（v1 安定版に固定）
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_thought = data.get('thought', '')
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }]
    }

    try:
        # API呼び出し
        response = requests.post(
            BASE_URL, 
            params={"key": API_KEY}, 
            json=payload, 
            timeout=15
        )
        
        # Googleからのエラーをチェック
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return jsonify({"error": "API Error", "detail": response.text}), response.status_code

        res_json = response.json()
        ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
        
        # 不要な文字を削ってJSONとして返す
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/')
def home():
    return "CBT Backend Status: Online"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)