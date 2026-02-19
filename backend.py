import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS設定を「全てのパスとメソッド」に対して完全に開放します
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/analyze', methods=['POST', 'OPTIONS'], strict_slashes=False)
def analyze():
    # プリフライト（OPTIONS）リクエストが来たら、即座に200 OKを返す
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    user_thought = data.get('thought', '')
    
    # --- Gemini APIの設定 ---
    API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    # 成功率が最も高い「v1」かつ「gemini-1.5-flash」の組み合わせ
    BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

    payload = {
        "contents": [{"parts": [{"text": f"あなたはCBTカウンセラーです。JSON形式で回答して。入力: {user_thought}"}]}]
    }

    try:
        response = requests.post(BASE_URL, params={"key": API_KEY}, json=payload, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        res_json = response.json()
        ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend Online"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)