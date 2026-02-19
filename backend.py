import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# どんなアクセスも許可
CORS(app, resources={r"/*": {"origins": "*"}})

def load_system_prompt():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompt.txt")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return "あなたは優秀なCBTカウンセラーです。JSONで回答してください。"

SYSTEM_PROMPT = load_system_prompt()

# あらゆるパス (/) を受け入れるように設定
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def catch_all(path):
    # CORS対応
    if request.method == 'OPTIONS':
        return '', 200

    # POSTリクエスト かつ パスが analyze の場合のみ実行
    if request.method == 'POST' and 'analyze' in path:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

        try:
            req_data = request.get_json()
            user_thought = req_data.get('thought', '')
            
            payload = {
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザー思考: {user_thought}"}]}]
            }

            response = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
            
            if response.status_code != 200:
                return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

            ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            clean_json = ai_text.strip().replace('```json', '').replace('```', '')
            return jsonify(json.loads(clean_json))

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # それ以外（トップページなど）へのアクセス
    return "CBT Backend is Online"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)