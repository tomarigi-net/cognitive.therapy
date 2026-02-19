import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORSをシンプルに許可
CORS(app)

# 1. プロンプト定義
SYSTEM_PROMPT = """あなたは優秀なCBT（認知行動療法）カウンセラーです。
ユーザーの悩みに対し、以下の4つの要素を必ず含むJSON形式で回答してください。
1. distortions: 見つかった認知の歪みのリスト
2. refutation: その考えに対する客観的な反論
3. benefit: 別の視点を持つことのメリット
4. actions: 具体的なネクストアクションのリスト"""

# 2. メインの分析関数（これを1つだけにします）
@app.route('/analyze', methods=['POST', 'OPTIONS'], strict_slashes=False)
def analyze():
    # プリフライト（事前確認）対応
    if request.method == 'OPTIONS':
        return '', 200

    # APIキーとURLの設定
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    # 404エラーが出にくい安定したURL
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "No data received"}), 400
            
        user_thought = req_data.get('thought', '特にありません')
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
            }]
        }

        # Gemini APIへリクエスト
        response = requests.post(url, params={"key": api_key}, json=payload, timeout=20)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        data = response.json()
        ai_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # AIの回答からJSON部分を抽出してパース
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. 動作確認用ルート
@app.route('/')
def home():
    return "CBT Backend is Online"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)