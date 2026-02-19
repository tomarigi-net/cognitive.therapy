import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 修正箇所: office を削除し、正しく全ドメインを許可
CORS(app, resources={r"/*": {"origins": "*"}}) 

# 1. APIキーの設定
# Renderの環境変数 GEMINI_API_KEY から読み込みます
# 第2引数は削除し、キーを直接書き込まないようにします
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Warning: API key not found. Please set GEMINI_API_KEY environment variable.")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

# 2. システム指示文 (プロンプト)
SYSTEM_PROMPT = """
あなたは優秀な認知行動療法（CBT）のカウンセラーです。
ユーザーの「自動思考」を分析し、以下のJSON形式でのみ回答してください。
必ず有効なJSONオブジェクトを返し、マークダウンの装飾（```jsonなど）は含めないでください。

{
  "distortions": ["歪み1", "歪み2"], 
  "refutation": "優しい語り口での反論...",
  "benefit": "考えを変えた時のメリット...",
  "actions": ["行動1", "行動2", "行動3"]
}
"""

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_thought = data.get('thought', '')

    if not user_thought:
        return jsonify({"error": "思考が入力されていません"}), 400

    try:
        # Geminiにリクエスト
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}")
        
        # JSON部分のクレンジング
        res_text = response.text
        clean_json = res_text.replace('```json', '').replace('```', '').strip()
        
        return jsonify(json.loads(clean_json))
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return jsonify({"error": "分析中にエラーが発生しました"}), 500

if __name__ == '__main__':
    # Render等の環境では PORT 環境変数を使うため設定
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

@app.route('/')
def home():
    return "CBT Backend is running!"