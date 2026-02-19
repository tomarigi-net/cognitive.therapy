import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# どんなアクセスも許可（CORSエラーを物理的に防ぐ）
CORS(app)

# 起動確認用の超シンプルプロンプト
DEFAULT_PROMPT = "あなたは優秀なCBTカウンセラーです。JSON形式で回答してください。"

@app.route('/', methods=['GET'])
def home():
    return "Backend is running!"

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # OPTIONSリクエスト（CORS事前確認）には即座に200を返す
    if request.method == 'OPTIONS':
        return '', 200

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        req_data = request.get_json()
        user_thought = req_data.get('thought', '') if req_data else "なし"
        
        # prompt.txt読み込み（失敗しても止まらないようにtry内に入れる）
        system_prompt = DEFAULT_PROMPT
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(base_dir, "prompt.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    system_prompt = f.read().strip()
        except:
            pass

        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nユーザー思考: {user_thought}"}]}]
        }

        response = requests.post(url, params={"key": api_key}, json=payload, timeout=25)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        # Markdownの除去
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Renderのポート指定に合わせる
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)