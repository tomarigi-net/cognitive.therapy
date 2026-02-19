import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # 全ての通信を許可

# APIキー設定
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# モデル指定（最も安定している名前に固定）
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの「自動思考」を分析し、以下のJSON形式でのみ回答してください。
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
    try:
        # JSONモードを強制する最新の設定
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}",
            generation_config={"response_mime_type": "application/json"}
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)