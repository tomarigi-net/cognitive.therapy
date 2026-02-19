import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORSを全てのオリジンに対して許可
CORS(app)

# 1. プロンプト読み込み関数
def load_prompt_from_file(filename="prompt.txt"):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"DEBUG: prompt reading error: {e}")
    return "あなたは優秀なカウンセラーです。JSON形式で回答してください。"

SYSTEM_PROMPT = load_prompt_from_file()

# 2. Gemini APIの設定（最新の安定したURL）
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_thought = data.get('thought', '')
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }]
    }

    try:
        response = requests.post(
            BASE_URL, 
            params={"key": API_KEY}, 
            json=payload, 
            timeout=15
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        response_data = response.json()
        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # JSONの余計な装飾を削除
        clean_json = ai_response_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is active."

if __name__ == '__main__':
    # ローカル実行用
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)