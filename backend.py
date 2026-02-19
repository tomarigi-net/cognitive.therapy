# backend.py
import os

def load_prompt_from_file(filename="prompt.txt"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "あなたは親切なアシスタントです。" # ファイルがない場合の予備

# 起動時にプロンプトを読み込む
SYSTEM_PROMPT = load_prompt_from_file()

def get_ai_response(user_message):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    # ...以下、API呼び出し処理


import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
# どんなサイトからのアクセスも、どんなデータ形式もすべて許可する設定
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
API_KEY = os.environ.get("GEMINI_API_KEY")
# v1betaではなく安定版の v1 を使用
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの思考を分析し、必ず以下のJSON形式でのみ回答してください。
解説や挨拶、```json などの装飾は一切含めず、{ } の中身だけを出力してください。

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

    # エラーの原因だった generationConfig を削除し、シンプルに
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        response_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": response_data.get('error', {}).get('message', 'API Error')}), response.status_code

        # AIの回答テキストを取得
        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # ```json などの余計な装飾を削ぎ落とす処理
        clean_json = ai_response_text.strip().replace('```json', '').replace('```', '')
        
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"Serious Error Detail: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running (Ultimate Mode)!"

if __name__ == '__main__':
    # Renderから割り当てられるポート番号を取得（デフォルトは5000）
    port = int(os.environ.get("PORT", 5000))
    
    # debug=False にすることで、本番環境での安定性を高めます
    # host="0.0.0.0" は必須です
    app.run(host="0.0.0.0", port=port, debug=False)