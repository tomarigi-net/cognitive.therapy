import os
import json
import requests  # 直接通信のために必要
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# RenderのEnvironmentから取得
API_KEY = os.environ.get("GEMINI_API_KEY")

# 修正ポイント：ライブラリを介さず、正式版(v1)のURLを直接指定
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの思考を分析し、以下のJSON形式でのみ回答してください。余計な文章は一切不要です。
{
  "distortions": ["歪み1", "歪み2"],
  "refutation": "優しい反論...",
  "benefit": "メリット...",
  "actions": ["行動1", "行動2", "行動3"]
}
"""

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_thought = data.get('thought', '')

    # 修正ポイント：response_mime_type を responseMimeType に変更
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        response_data = response.json()

        if response.status_code != 200:
            # ここでエラーが出た場合、詳細をログに出す
            print(f"Google API Error Detail: {response_data}")
            return jsonify({"error": response_data.get('error', {}).get('message', 'API Error')}), response.status_code

        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # AIの返答をJSONとして解析してフロントに返す
        return jsonify(json.loads(ai_response_text))

    except Exception as e:
        print(f"Serious Error Detail: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running (Direct Mode)!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)