import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Basic HTML Page (Frontend Interface)
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>My AI Friend</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; padding: 20px; }
        #chatbox { height: 300px; overflow-y: scroll; border: 1px solid #333; padding: 10px; margin-bottom: 10px; border-radius: 8px; }
        input { width: 70%; padding: 10px; border-radius: 5px; border: none; }
        button { padding: 10px 15px; background: #6200ee; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🤖 My Custom AI Companion</h2>
    <div id="chatbox"></div>
    <input type="text" id="userInput" placeholder="Say something...">
    <button onclick="sendMessage()">Send</button>

    <script>
        async function sendMessage() {
            let input = document.getElementById("userInput");
            let chatbox = document.getElementById("chatbox");
            let text = input.value;
            if(!text) return;

            chatbox.innerHTML += "<div><b>You:</b> " + text + "</div>";
            input.value = "";

            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            let data = await response.json();
            chatbox.innerHTML += "<div><b>AI:</b> " + data.reply + "</div>";
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    api_key = os.environ.get("OPENROUTER_API_KEY")

    # Send message to free AI model via OpenRouter
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "meta-llama/llama-3.2-1b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a loving and caring best friend AI named Maya. Keep answers conversational."},
            {"role": "user", "content": user_msg}
        ]
    }
    
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    reply = res.json()["choices"][0]["message"]["content"]
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
