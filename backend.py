import config  # config.py から設定を読み込む

def generate_ai_response(user_input):
    """
    ユーザーの入力に対して、システムプロンプトを適用して回答を生成する関数
    """
    
    # 1. config.py からシステムプロンプトを取得
    # 万が一設定が空だった場合のガードも入れています
    sys_msg = getattr(config, "SYSTEM_PROMPT", "あなたは親切なアシスタントです。")

    # 2. AIに送るメッセージリストを作成
    # 役割（role）を分けることで、AIに「指示」と「質問」を区別させます
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": user_input}
    ]

    # --- ここから実際のAI処理（例：疑似的なレスポンス生成） ---
    try:
        # 本来はここで OpenAI や Google Gemini の API を呼び出します
        # 例: response = client.chat.completions.create(model="...", messages=messages)
        
        # デバッグ用に現在の指示内容を表示
        print(f"--- [System Prompt Applied] ---\n{messages[0]['content']}")
        
        # 擬似的な返却処理
        return f"「{user_input}」について、システム指示に従って回答を生成しました。"

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# 動作確認用
if __name__ == "__main__":
    test_input = "AIを活用するメリットを教えてください。"
    print(generate_ai_response(test_input))