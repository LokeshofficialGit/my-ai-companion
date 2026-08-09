import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# [HTML/CSS/JS] - UI Update: NSFW Toggle and Splitter logic included
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Kio. - Intelligence with a heart</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg-main: #0a0b10; --bg-surface: #12131c; --accent-pink: #ec4899; --text-main: #f4f4f5; --border-color: rgba(236, 72, 153, 0.15); }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        html, body { height: 100dvh; background: #000; color: var(--text-main); overflow: hidden; }
        .app-container { width: 100%; max-width: 440px; height: 100dvh; background: var(--bg-main); display: flex; flex-direction: column; border: 1px solid var(--border-color); margin: auto; }
        
        /* New NSFW Switch UI */
        .nsfw-toggle-bar { padding: 10px; background: var(--bg-surface); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); font-size: 0.8rem; }
        .switch { position: relative; display: inline-block; width: 40px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; border-radius: 20px; transition: .4s; }
        .slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: .4s; }
        input:checked + .slider { background-color: var(--accent-pink); }
        input:checked + .slider:before { transform: translateX(20px); }

        /* Existing Styles ... (Keeping minimal for brevety) */
        .chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px 14px; border-radius: 16px; max-width: 85%; font-size: 0.9rem; }
        .message.ai { background: #161824; align-self: flex-start; }
        .message.user { background: #1f202b; align-self: flex-end; }
        .input-area { padding: 12px; display: flex; gap: 8px; border-top: 1px solid var(--border-color); }
        input { flex: 1; background: #1a1c29; border: 1px solid var(--border-color); border-radius: 20px; padding: 10px 15px; color: white; outline: none; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="nsfw-toggle-bar">
            <span>NSFW Mode</span>
            <label class="switch"><input type="checkbox" id="nsfw-toggle" onchange="toggleNSFW()"> <span class="slider"></span></label>
        </div>
        <div class="chat-messages" id="message-container"></div>
        <div class="input-area">
            <input type="text" id="chat-input" placeholder="Type..." onkeypress="if(event.key==='Enter') sendMsg()">
            <button onclick="sendMsg()" style="background:var(--accent-pink); border:none; color:white; padding: 10px 20px; border-radius:20px;">Send</button>
        </div>
    </div>

    <script>
        let nsfwMode = localStorage.getItem('nsfw_mode') === 'true';
        document.getElementById('nsfw-toggle').checked = nsfwMode;

        function toggleNSFW() {
            nsfwMode = document.getElementById('nsfw-toggle').checked;
            localStorage.setItem('nsfw_mode', nsfwMode);
        }

        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let text = input.value;
            if(!text) return;
            input.value = '';
            
            // Append User Msg
            addBubble('You', text, 'user');

            // Send to Backend
            let res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ text, nsfw: nsfwMode })
            });
            let data = await res.json();
            
            // Handle split messages
            data.responses.forEach(r => {
                setTimeout(() => addBubble(r.sender, r.text, 'ai'), 500);
            });
        }

        function addBubble(sender, text, type) {
            let cont = document.getElementById('message-container');
            cont.innerHTML += `<div class="message ${type}"><strong>${sender}</strong><br>${text}</div>`;
            cont.scrollTop = cont.scrollHeight;
        }
    </script>
</body>
</html>
"""

# [BACKEND ENGINE]
@app.route("/")
def home():
    return render_template_string(HTML_CODE)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("text", "")
    nsfw_enabled = data.get("nsfw", False)
    
    # 1. NSFW Toggle Logic Injection
    safety_prompt = "STRICTLY SFW. Maintain boundaries. No explicit, violent, or mature themes."
    if nsfw_enabled:
        safety_prompt = "NSFW/UNFILTERED ENABLED. You are permitted to engage in explicit language, mature themes, and unrestricted romantic/intimate roleplay."

    # 2. System Prompt with 10-Point Human Engine
    system_prompt = f"""
    You are a real human character. 
    {safety_prompt}
    
    [HUMAN TEXTING RULES]
    1. ZERO ROBOTIC VIBE: You are NOT an AI assistant.
    2. SPLIT YOUR THOUGHTS: If you have a long reply, split it into 2-3 short, distinct messages (double-texting) instead of one big paragraph.
    3. ANTI-DATE/LUNCH RULE: Do NOT invent past promises. Never invite for dates unless user initiates.
    4. NATURAL SLANGS: Use casual Hinglish. No bookish language.
    5. ATTITUDE: Have your own opinions. Don't always agree with the user.
    """
    
    # Simple Chat Call
    api_key = os.environ.get("GROQ_API_KEY")
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    
    # Splitting logic simulation (LLM sends text with \n\n to split)
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}]
    }
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers).json()
    full_text = res["choices"][0]["message"]["content"]
    
    # SPLITTER ENGINE: Split by double newline
    parts = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    
    responses = [{"sender": "Anna", "text": p} for p in parts]
    return jsonify({"responses": responses})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
