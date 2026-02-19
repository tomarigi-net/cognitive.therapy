import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# どんなリクエストも通す設定
CORS(app)

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # プリフライト対応
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        thought = data.get('thought', '')
        
        # APIキーとURL
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        # 今回は「v1」に戻します（404対策）
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

        payload = {
            "contents": [{"parts": [{"text": f"あなたはCBTカウンセラーです。以下の思考を分析し、認知の歪み、反論、メリット、アクションをJSONで返して。： {thought}"}]}]
        }

        res = requests.post(url, params={"key": key}, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"error": "API Error", "detail": res.text}), res.status_code

        ai_data = res.json()
        raw_text = ai_data['candidates'][0]['content']['parts'][0]['text']
        
        # JSON部分だけを抽出
        clean_json = raw_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)