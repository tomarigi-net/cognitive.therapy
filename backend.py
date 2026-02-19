import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# APIキー設定
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 修正ポイント：モデル名を最も標準的なものに固定
# これにより API v1beta ではなく v1 が使われるようになります
model = genai.GenerativeModel('gemini-pro')

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
    
    if not user_thought:
        return jsonify({"error": "No thought provided"}), 400

    try:
        # 修正ポイント：generation_configを使わず、よりシンプルな呼び出しにする
        # ライブラリのバージョンが古い場合でも動くようにします
        prompt = f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"
        response = model.generate_content(prompt)
        
        # 文字列の中からJSON部分だけを抽出する（念のため）
        res_text = response.text
        start_idx = res_text.find('{')
        end_idx = res_text.rfind('}') + 1
        json_str = res_text[start_idx:end_idx]
        
        return jsonify(json.loads(json_str))
        
    except Exception as e:
        # エラーが出た場合、詳細をRenderのLogsに出力
        print(f"Serious Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)