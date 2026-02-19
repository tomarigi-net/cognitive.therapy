import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 1. プロンプト読み込み関数
def load_prompt_from_file(filename="prompt.txt"):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "あなたは優秀なカウンセラーです。JSON形式で回答してください。"

SYSTEM_PROMPT = load_prompt_from_file()

# 2. Gemini APIの設定（URLからキーを切り離す）
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
# URLにはキーを含めず、ベースのURLのみを記述
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_thought = data.get('thought', '')

    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }]
    }

    try:
        # 修正ポイント: paramsを使ってURLを安全に生成する
        # これにより、URLに余計な記号やスペースが混じるのを防げます
        response = requests.post(
            BASE_URL, 
            params={"key": API_KEY}, 
            json=payload, 
            timeout=15
        )
        
        # デバッグ：URLが変になっていないかログに出す（キーは隠す）
        print(f"DEBUG: Request sent to {response.url.split('key=')[0]}...")

        response_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": response_data.get('error', {}).get('message', 'API Error')}), response.status_code

        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        clean_json = ai_response_text.strip().replace('```json', '').replace('```', '')
        
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"Serious Error Detail: {e}")
        return jsonify({"error": "サーバー内部でエラーが発生しました。"}), 500

@app.route('/')
def home():
    return "CBT Backend is active."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)