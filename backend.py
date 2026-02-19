import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_prompt():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except:
        pass
    return "あなたは優秀なCBTカウンセラーです。JSON形式で回答してください。"

# あらゆるリクエストを「/」だけで受け付ける
@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_all():
    if request.method == 'OPTIONS':
        return '', 200
    
    # GET（ブラウザでの直接確認）の場合
    if request.method == 'GET':
        return "CBT Backend is Online"

    # POST（分析リクエスト）の場合
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        req_data = request.get_json()
        user_thought = req_data.get('thought', '')
        system_prompt = get_prompt()

        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n入力: {user_thought}"}]}]
        }

        response = requests.post(url, params={"key": api_key}, json=payload, timeout=25)
        
        if response.status_code != 200:
            return jsonify({"error": "API Error", "detail": response.text}), response.status_code

        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)