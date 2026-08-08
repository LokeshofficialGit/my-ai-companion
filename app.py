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
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background: #000; color: var(--text-main); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .app-container { width: 100%; max-width: 440px; height: 100vh; display: flex; flex-direction: column; background: #0a0b10; border: 1px solid #333; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .message { padding: 10px 14px; border-radius: 12px; max-width: 80%; font-size: 0.9rem; line-height: 1.4; word-break: break-word; }
        .message.user { background: #9333ea; align-self: flex-end; color: white; }
        .message.ai { background: #161824; border: 1px solid #333; align-self: flex-start; color: white; }
        .input-area { padding: 12px; border-top: 1px solid #333; display: flex; gap: 8px; align-items: center; background: #12131c; }
        .tool-btn { background: #1a1c29; color: var(--accent-pink); border: 1px solid #333; padding: 10px; border-radius: 12px; cursor: pointer; font-weight: bold; width: 45px; text-align: center; }
        input { flex: 1; padding: 11px 14px; border-radius: 20px; border: 1px solid #333; background: #1a1c29; color: white; outline: none; }
        .send-btn { padding: 0 16px; height: 42px; background: var(--accent-pink); border: none; border-radius: 12px; color: white; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="app-container">
        <div id="chat-view" class="chat-messages">
            <div class="message ai">Hey! Main ready hoon. Batao kya baat karni hai?</div>
        </div>
        <div class="input-area">
            <button class="tool-btn" id="lang-toggle" onclick="toggleLang()" title="Toggle Language">H</button>
            <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
            <button class="send-btn" onclick="sendMsg()">Send</button>
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

            let chatView = document.getElementById('chat-view');
            chatView.innerHTML += `<div class="message user">${text}</div>`;
            input.value = '';
            chatView.scrollTop = chatView.scrollHeight;

            try {
                let res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text, lang: currentLang })
                });
                let data = await res.json();
                chatView.innerHTML += `<div class="message ai">${data.reply}</div>`;
                chatView.scrollTop = chatView.scrollHeight;
            } catch(e) {
                chatView.innerHTML += `<div class="message ai">Error connecting to server.</div>`;
            }
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
    user_text = data.get("text", "")
    
    if lang == 'H':
        system_prompt = "You are a cool desi friend. Use natural casual Hinglish (Roman Hindi mixed with English), 'yaar', 'sach mein', etc. Keep it very short and human-like."
    else:
        system_prompt = "You are a friendly, intelligent companion. Use natural, conversational English. Keep it warm, engaging, and avoid robotic or corporate AI tone."

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"reply": "Groq API Key missing in environment variables!"})

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
        }, headers={"Authorization": f"Bearer {api_key.strip()}"}).json()

        reply = res["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
