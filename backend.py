from flask import Flask, request, jsonify
import config  # 先ほど作成した config.py を読み込む

# --- Gunicornが探している 'app' インスタンスを定義 ---
app = Flask(__name__)

# config.py からシステムプロンプトを取得
# 万が一設定がない場合はデフォルトの文言を使用
SYSTEM_PROMPT = getattr(config, "SYSTEM_PROMPT", "あなたは親切なアシスタントです。")

@app.route('/chat', methods=['POST'])
def chat():
    """
    フロントエンドからの質問を受け取るエンドポイント
    """
    data = request.json
    user_message = data.get("message", "")

    # メッセージリストの構築
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    try:
        # ここに実際のAI API (OpenAIやGemini) の呼び出し処理を書きます
        # 現時点では、正しくプロンプトが組み込まれたことを確認するレスポンスを返します
        response_text = f"システムプロンプト「{SYSTEM_PROMPT[:20]}...」を適用して、回答を生成しました。"
        
        return jsonify({
            "status": "success",
            "reply": response_text
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 開発環境で直接実行する場合（python backend.py）
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)