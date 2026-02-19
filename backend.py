import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# GitHub Pages からの通信を許可
CORS(app)

# --- prompt.txt の読み込み設定 ---
def load_system_prompt():
    # backend.py と同じフォルダにある prompt.txt の絶対パスを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompt.txt")
    
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    print(f"DEBUG: prompt.txt loaded successfully.")
                    return content
        except Exception as e:
            print(f"DEBUG: Error reading prompt.txt: {e}")
    
    # ファイルが見つからない、またはエラー時のデフォルト
    print("DEBUG: Using default fallback prompt.")
    return "あなたは優秀なCBTカウンセラーです。必ずJSON形式で回答してください。"

# サーバー起動時に一度だけ読み込む
SYSTEM_PROMPT = load_system_prompt()

@app.route('/analyze', methods=['POST', 'OPTIONS'], strict_slashes=False)
def analyze():
    # CORS プリフライト（事前確認）対応
    if request.method == 'OPTIONS':
        return '', 200

    # Render の環境変数から API キーを取得
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    # 最もエラーが起きにくい v1beta / flash の組み合わせ
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "No data received"}), 400
            
        user_thought = req_data.get('thought', '入力なし')
        
        # プロンプトとユーザー入力を組み合わせて Gemini に送る
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
            }]
        }

        # Gemini API へリクエスト送信
        response = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        data = response.json()
        ai_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # AI の回答から JSON 部分（```json ... ```）を抽出してパース
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"DEBUG: Error during analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    # 正常動作確認用
    return "CBT Backend is Online (prompt.txt mode)"

if __name__ == '__main__':
    # Render のポート設定に対応
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)