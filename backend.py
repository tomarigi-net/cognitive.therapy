import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # フロントエンドからの通信を許可

# 1. APIキーの設定
# ローカルでテストする際は "YOUR_KEY" に書き換えるか、環境変数に設定してください
api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. システム指示文 (プロンプト)
SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの「自動思考」を分析し、以下のJSON形式でのみ回答してください。

{
  "distortions": ["歪み1", "歪み2"], // 最大3つ
  "refutation": "優しい語り口での反論...",
  "benefit": "考えを変えた時のメリット...",
  "actions": ["行動1", "行動2", "行動3"] // 具体的なアクション
}
"""

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_thought = data.get('thought', '')

    try:
        # Geminiにリクエスト
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}")
        
        # JSON部分のクレンジング
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return jsonify(json.loads(clean_json))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "分析中にエラーが発生しました"}), 500

if __name__ == '__main__':
    # ポート5000でサーバーを起動
    app.run(host='0.0.0.0', port=5000, debug=True)