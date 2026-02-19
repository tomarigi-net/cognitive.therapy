import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS設定：フロントエンドからのアクセスを許可
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- 1. 外部ファイルからプロンプトを読み込む関数 ---
def load_prompt_from_file(filename="prompt.txt"):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    # ファイルがない、または読み込めない場合のデフォルト
    return "あなたは親切なアシスタントです。JSON形式で回答してください。"

# 起動時に一度だけプロンプトを読み込む
SYSTEM_PROMPT = load_prompt_from_file()

# --- 2. Gemini APIの設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY")
# 安定版 v1 を使用
GEMINI_URL = f"[https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=){API_KEY}"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_thought = data.get('thought', '')

    # プロンプトとユーザー入力を合体させる
    # ここで load_prompt_from_file() で読み込んだ内容が使われます
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
        }]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=10)
        response_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": response_data.get('error', {}).get('message', 'API Error')}), response.status_code

        # AIの回答テキストを取得
        ai_response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # ```json などの余計な装飾を削ぎ落とす処理
        clean_json = ai_response_text.strip().replace('```json', '').replace('```', '')
        
        # JSONとして解析して返却
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"Serious Error Detail: {e}")
        return jsonify({"error": "解析中にエラーが発生しました。"}), 500

@app.route('/')
def home():
    return "CBT Backend is running (Prompt from File Mode)!"

if __name__ == '__main__':
    # ポート番号の設定（Renderなどの環境に対応）
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" は外部からのアクセスを受けるために必須
    app.run(host="0.0.0.0", port=port, debug=False)