import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# すべてのオリジンからのアクセスを完全に許可
CORS(app, resources={r"/*": {"origins": "*"}})

# --- prompt.txt の読み込み ---
def load_system_prompt():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompt.txt")
    
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            print(f"Error reading prompt.txt: {e}")
    return "あなたは優秀なCBTカウンセラーです。JSON形式で回答してください。"

SYSTEM_PROMPT = load_system_prompt()

# strict_slashes=False を追加して 404 を防ぐ
@app.route('/analyze', methods=['POST', 'OPTIONS'], strict_slashes=False)
def analyze():
    if request.method == 'OPTIONS':
        return '', 200

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    # 安定版の v1beta を使用
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        req_data = request.get_json()
        if not req_data:
            return jsonify({"error": "No JSON data"}), 400
            
        user_thought = req_data.get('thought', '')
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {user_thought}"}]
            }]
        }

        response = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        data = response.json()
        ai_text = data['candidates'][0]['content']['parts'][0]['text']
        
        # Markdownの除去
        clean_json = ai_text.strip().replace('```json', '').replace('```', '')
        return jsonify(json.loads(clean_json))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "CBT Backend is Online (v1.1)"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)