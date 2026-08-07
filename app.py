import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Complete Chat Interface (Frontend)
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My AI Friend</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #18181b; color: #fff; display: flex; flex-direction: column; height: 100vh; justify-content: center; align-items: center; }
        .chat-container { width: 100%; max-width: 500px; height: 90vh; background: #27272a; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        .header { background: #3f3f46; padding: 15px; text-align: center; font-weight: bold; font-size: 1.1rem; border-bottom: 1px solid #52525b; }
        #chatbox { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; line-height: 1.4; word-wrap: break-word; }
        .user-msg { background: #6366f1; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai-msg { background: #3f3f46; align-self: flex-start; border-bottom-left-radius: 2px; }
        .error-msg { background: #ef4444; color: white; align-self: center; font-size: 0.85rem; }
        .input-area { display: flex; padding: 10px; background: #18181b; border-top: 1px solid #3f3f46; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #3f3f46; background: #27272a; color: white; outline: none; }
        button { margin-left: 8px; padding: 12px 18px; background: #6366f1; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        button:hover { background: #4f46e5; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">💖 Maya - AI Best Friend</div>
        <div id="chatbox">
            <div class="msg ai-msg">Hey there! I'm Maya. What's on your mind today? 😊</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            let input = document.getElementById("userInput");
            let chatbox = document.getElementById("chatbox");
            let text = input.value.trim();
            if(!text) return;

            // Display User Message
            chatbox.innerHTML += `<div class="msg user-msg">${text}</div>`;
            input.value = "";
            chatbox.scrollTop = chatbox.scrollHeight;

            try {
                let response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });
                let data = await response.json();
                
                if (data.reply.startsWith("Error:") || data.reply.startsWith("API Error:")) {
                    chatbox.innerHTML += `<div class="msg error-msg">${data.reply}</div>`;
                } else {
                    chatbox.innerHTML += `<div class="msg ai-msg">${data.reply}</div>`;
                }
            } catch (err) {
                chatbox.innerHTML += `<div class="msg error-msg">Network error. Please try again.</div>`;
            }
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

    if not api_key:
        return jsonify({"reply": "Error: OPENROUTER_API_KEY missing in Render environment variables!"})

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "HTTP-Referer": "https://render.com",
        "Content-Type": "application/json"
    }
    
    # 100% Free Google Gemma Model
    payload = {
        "model": "google/gemma-2-9b-it:free",
        "messages": [
            {
                "role": "system", 
                "content": "You are a loving, supportive, and natural conversational AI companion named Maya. Keep responses friendly, short, and engaging."
            },
            {"role": "user", "content": user_msg}
        ]
    }
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=20)
        data = res.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
        elif "error" in data:
            reply = f"API Error: {data['error'].get('message', 'Check OpenRouter Settings')}"
        else:
            reply = "API Error: Unexpected response from OpenRouter."
            
    except Exception as e:
        reply = f"Error: Server connection failed ({str(e)})"
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
