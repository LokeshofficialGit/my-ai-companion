import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kio. - Intelligence with a heart</title>
    <style>
        :root { --accent-pink: #ec4899; --bg-surface: #12131c; --text-main: #f4f4f5; }
        body { background: #000; color: var(--text-main); font-family: sans-serif; }
        .app-container { width: 100%; max-width: 440px; margin: auto; height: 100vh; display: flex; flex-direction: column; background: #0a0b10; border: 1px solid #333; }
        .input-area { padding: 12px; border-top: 1px solid #333; display: flex; gap: 8px; align-items: center; }
        .tool-btn { background: #1a1c29; color: var(--accent-pink); border: 1px solid #333; padding: 10px; border-radius: 12px; cursor: pointer; font-weight: bold; width: 45px; }
        input { flex: 1; padding: 12px; border-radius: 20px; border: 1px solid #333; background: #1a1c29; color: white; }
        .send-btn { padding: 10px 15px; background: var(--accent-pink); border: none; border-radius: 12px; color: white; cursor: pointer; }
    </style>
</head>
<body>
    <div class="app-container">
        <div id="chat-view" style="flex:1; overflow-y:auto; padding:16px;"></div>
        <div class="input-area">
            <button class="tool-btn" id="lang-toggle" onclick="toggleLang()">H</button>
            <input type="text" id="chat-input" placeholder="Type a message...">
            <button class="send-btn" onclick="sendMsg()">➤</button>
        </div>
    </div>
    <script>
        let currentLang = 'H'; // 'H' for Hinglish, 'E' for English
        function toggleLang() {
            currentLang = (currentLang === 'H') ? 'E' : 'H';
            document.getElementById('lang-toggle').innerText = currentLang;
        }
        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let text = input.value.trim();
            if(!text) return;
            // Send to backend with currentLang
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text, lang: currentLang })
            }).then(r => r.json()).then(data => { /* Render logic */ });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    lang = data.get("lang", "H")
    
    # Prompt logic based on Lang
    if lang == 'H':
        system_prompt = "You are a cool desi friend. Use natural Hinglish (Roman Hindi mixed with English), 'yaar', 'sach mein', etc. Keep it very casual and human-like."
    else:
        system_prompt = "You are a friendly, intelligent companion. Use natural, conversational English. Keep it warm, engaging, and avoid robotic or corporate AI tone."

    # API Call to Groq (since keys are working)
    api_key = os.environ.get("GROQ_API_KEY")
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": data['text']}]
    }, headers={"Authorization": f"Bearer {api_key.strip()}"}).json()

    return jsonify({"reply": res["choices"][0]["message"]["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
