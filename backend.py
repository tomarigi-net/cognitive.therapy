import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_prompt():
    try:
        path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except:
        pass
    return "あなたは優秀なCBTカウンセラーです。JSON形式で回答してください。"

SYSTEM_PROMPT = get_prompt()

# スラッシュあり・なしの両方を定義して404を物理的に防ぐ
@app.route('/', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
@app.route('', methods=['POST', 'OPTIONS'], strict_slashes=False)
def home():
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        return "CBT Backend is Online"

    # POST処理
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        data = request.get_json()
        thought = data.get('thought', '入力なし')

        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {thought}"}]}]
        }

        response = requests.post(url, params={"key": api_key}, json=payload, timeout=25)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error"}), response.status_code

        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # JSONのクリーニング
        clean_json = ai_text.replace('```json', '').replace('```', '').strip()
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)