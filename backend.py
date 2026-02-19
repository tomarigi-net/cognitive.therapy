import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. APIキーの設定
api_key = os.environ.get("GEMINI_API_KEY")

# 2. 通信の設定（APIバージョンを正式版 v1 に固定する）
# これにより、エラーの原因である v1beta を回避します
genai.configure(api_key=api_key, transport='rest') 

# モデル名を最新の 'gemini-1.5-flash' に戻します
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの「自動思考」を分析し、以下のJSON形式でのみ回答してください。
余計な挨拶や解説は一切不要です。
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
    
    if not user_thought:
        return jsonify({"error": "入力が空です"}), 400

    try:
        # 確実にJSONだけを返させる最新の呼び出し方
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}",
            generation_config={"response_mime_type": "application/json"}
        )
        
        # もしresponse.textが空っぽだった場合のガード
        if not response.text:
            raise ValueError("AIからの返答が空でした")

        return jsonify(json.loads(response.text))
        
    except Exception as e:
        print(f"Serious Error Detail: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)