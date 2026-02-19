import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def load_prompt_from_file(filename="prompt.txt"):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"DEBUG: prompt.txt 読み込みエラー: {e}")
    return "あなたは優秀なカウンセラーです。JSON形式で回答してください。"

SYSTEM_PROMPT = load_prompt_from_file()

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
# URLのバージョンを v1beta に変えてみる（一部環境で v1 が 404 になるケースがあるため）
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.route('/analyze', methods=['POST', 'OPTIONS'], strict_slashes=False)
def analyze():
    # OPTIONS（プリフライト）リクエストへの対応
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    print(f"DEBUG: /analyze にアクセスがありました - Method: {request.method}")
    
    data = request.json
    if not data:
        print("DEBUG: リクエストボディが空です")
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
        
        # Google API からの生の応答コードをチェック
        print(f"DEBUG: Gemini API Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"DEBUG: Gemini Error Body: {response.text}")
            # Gemini側が404を出しているなら、ここで詳細がわかります
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        response_data = response.json()
        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        clean_json = ai_response_text.strip().replace('```json', '').replace('```', '')
        
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"DEBUG: 実行エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    print("DEBUG: ルートパス (/) にアクセスがありました")
    return "CBT Backend is active."

# 404エラーをキャッチしてログに出す
@app.errorhandler(404)
def not_found(e):
    print(f"DEBUG: 存在しないパスへのアクセス: {request.path}")
    return jsonify({"error": "Path Not Found", "requested_path": request.path}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)