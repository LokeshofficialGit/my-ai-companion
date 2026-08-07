import os
import requests
import json
import base64
import threading
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Background Task Storage for Asynchronous Photo Generation
task_storage = {}

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aura - AI Companions</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-main: #050508; --bg-surface: #121215; --bg-input: #09090b;
            --border-color: #27272a; --text-main: #f4f4f5; --text-sub: #a1a1aa;
            --accent-purple: #a855f7; --accent-pink: #ec4899; --action-text: #f472b6;
            --user-msg-bg: linear-gradient(135deg, #9333ea, #ec4899);
            --ai-msg-bg: #121215; --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            --sidebar-bg: #09090b; --sidebar-border: #27272a; --sidebar-text: #f4f4f5;
            --sidebar-btn-bg: #121215; --sidebar-btn-hover: #27272a;
        }
        [data-theme="light"] {
            --bg-main: #f4f4f5; --bg-surface: #ffffff; --bg-input: #ffffff;
            --border-color: #e4e4e7; --text-main: #09090b; --text-sub: #52525b;
            --action-text: #be185d; --ai-msg-bg: #ffffff; --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            --sidebar-bg: #ffffff; --sidebar-border: #e4e4e7; --sidebar-text: #09090b;
            --sidebar-btn-bg: #f4f4f5; --sidebar-btn-hover: #e4e4e7;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        html, body { height: 100dvh; width: 100vw; background: #000000; color: var(--text-main); overflow: hidden; display: flex; justify-content: center; align-items: center; transition: background 0.3s, color 0.3s; }
        .app-container { width: 100%; max-width: 440px; height: 100dvh; background: var(--bg-main); display: flex; flex-direction: column; position: relative; overflow: hidden; border: 1px solid var(--border-color); }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }

        .top-bar { height: 52px; min-height: 52px; background: var(--bg-surface); border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 10; }
        .toggle-btn { background: transparent; border: none; color: var(--text-main); font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .top-title { font-weight: 700; font-size: 1rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }

        .sidebar { position: absolute; top: 0; left: 0; width: 85%; height: 100%; background: var(--sidebar-bg); color: var(--sidebar-text); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 100; transform: translateX(-100%); pointer-events: none; }
        .sidebar.open { transform: translateX(0); pointer-events: auto; }
        .sidebar-header { padding: 14px 16px; font-size: 1.2rem; font-weight: 800; color: var(--accent-pink); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
        .header-actions { display: flex; align-items: center; gap: 6px; }
        .sidebar-icon-btn { background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.88rem; }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }

        .menu-category-btn { width: 100%; padding: 12px 14px; background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); border-radius: 10px; text-align: left; cursor: pointer; display: flex; align-items: center; justify-content: space-between; font-size: 0.92rem; font-weight: 600; }
        .menu-category-btn i.cat-icon { color: var(--accent-pink); font-size: 1rem; margin-right: 10px; }
        .submenu-container { padding: 6px 0 6px 12px; display: flex; flex-direction: column; gap: 4px; }
        .item-btn { width: 100%; padding: 9px 12px; background: transparent; border: none; color: var(--text-sub); border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 0.88rem; }
        .item-btn img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
        .sub-create-btn { width: 100%; padding: 9px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 4px; }

        .workspace { flex: 1; display: flex; flex-direction: column; height: calc(100% - 52px); position: relative; overflow: hidden; }
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .dash-title { font-size: 1.5rem; font-weight: 800; color: var(--text-main); margin-bottom: 6px; }
        .dash-sub { font-size: 0.85rem; color: var(--text-sub); text-align: center; margin-bottom: 24px; }
        .dash-card { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 14px 16px; border-radius: 14px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; box-shadow: var(--card-shadow); }
        .dash-card i { font-size: 1.3rem; color: var(--accent-pink); }
        .dash-card strong { display: block; color: var(--text-main); font-size: 0.92rem; }
        .dash-card span { font-size: 0.75rem; color: var(--text-sub); }

        #chat-view { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { display: flex; gap: 10px; max-width: 88%; position: relative; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; background: var(--border-color); flex-shrink: 0; }
        .message .content { background: var(--ai-msg-bg); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 14px; font-size: 0.9rem; line-height: 1.45; color: var(--text-main); word-break: break-word; box-shadow: var(--card-shadow); }
        .message.user .content { background: var(--user-msg-bg); border: none; color: #ffffff; border-bottom-right-radius: 2px; }
        .message.ai .content { border-bottom-left-radius: 2px; }
        .message .sender-name { font-size: 0.7rem; color: var(--text-sub); margin-bottom: 3px; font-weight: 600; }
        .action-text { color: var(--action-text); font-style: italic; font-weight: 500; }
        
        .chat-img-bubble { width: 100%; max-width: 220px; border-radius: 10px; margin-top: 6px; border: 1px solid var(--border-color); display: block; }
        .loading-bubble { display: flex; align-items: center; gap: 8px; color: var(--text-sub); font-style: italic; font-size: 0.85rem; padding: 6px 0; }
        .spinner { width: 16px; height: 16px; border: 2px solid var(--accent-pink); border-top: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .input-area { padding: 10px 12px; border-top: 1px solid var(--border-color); background: var(--bg-surface); display: flex; gap: 8px; width: 100%; align-items: center; }
        .input-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; background: var(--bg-input); border: 1px solid var(--border-color); padding: 10px 12px; border-radius: 20px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .tool-btn { background: var(--bg-input) !important; color: var(--accent-pink) !important; border: 1px solid var(--border-color) !important; padding: 0 10px !important; font-size: 0.95rem; border-radius: 10px !important; height: 38px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .send-btn { height: 38px; padding: 0 14px; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 4px; font-size: 0.8rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .form-group textarea { height: 75px; resize: vertical; }
        .submit-btn { width: 100%; padding: 11px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.9rem; margin-top: 8px; }
        .hidden { display: none !important; }
    </style>
</head>
<body data-theme="dark">
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span>Aura</span>
                <button class="sidebar-icon-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="nav-section">
                <button class="menu-category-btn" onclick="goHome()"><i class="fa-solid fa-house cat-icon"></i> Home</button>
                <div>
                    <button class="menu-category-btn" onclick="let s=document.getElementById('chars-sub'); s.classList.toggle('hidden');">
                        <span><i class="fa-solid fa-users cat-icon"></i> Characters</span>
                        <i class="fa-solid fa-chevron-down"></i>
                    </button>
                    <div class="submenu-container hidden" id="chars-sub">
                        <button class="sub-create-btn" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> New Companion</button>
                        <div id="char-list"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Top Bar -->
        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title">Aura</div>
            </div>
            <button class="icon-btn hidden" id="clear-chat-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-trash"></i></button>
        </div>

        <!-- Workspace -->
        <div class="workspace">
            <div id="dashboard-view" class="dashboard">
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your personal AI companion platform.</p>
                <div class="dash-card" onclick="openNewCharForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    <div>
                        <strong>Create AI Companion</strong>
                        <span>Custom backstory & relationship</span>
                    </div>
                </div>
            </div>

            <!-- Chat View -->
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="tool-btn" onclick="triggerPhotoRequest()" title="Generate Photo">🤳</button>
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="Message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    </div>
                    <button class="send-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <!-- Character Form -->
            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;">Create Companion</h3>
                <input type="hidden" id="char-id">
                <div class="form-group"><label>Name</label><input type="text" id="char-name"></div>
                <div class="form-group"><label>Appearance</label><input type="text" id="char-app"></div>
                <div class="form-group"><label>Backstory</label><textarea id="char-backstory"></textarea></div>
                <button class="submit-btn" onclick="saveCharacter()">Save</button>
            </div>
        </div>
    </div>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let activeContext = null;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function goHome() { 
            activeContext = null; 
            document.getElementById('sidebar').classList.remove('open'); 
            document.getElementById('dashboard-view').classList.remove('hidden'); 
            document.getElementById('chat-view').classList.add('hidden'); 
            document.getElementById('char-form').classList.add('hidden'); 
            document.getElementById('clear-chat-btn').classList.add('hidden'); 
        }

        function saveState() {
            localStorage.setItem('aura_chars', JSON.stringify(characters));
            localStorage.setItem('aura_chats', JSON.stringify(chatHistories));
            renderSidebar();
        }

        function appendMsg(sender, text, image = null, isLoading = false) {
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            let msg = { sender, text, image, isLoading };
            chatHistories[activeContext.id].push(msg);
            saveState();
            renderMessages();
            return chatHistories[activeContext.id].length - 1;
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];
            container.innerHTML = history.map((m, idx) => {
                let isUser = m.sender === 'You';
                return `<div class="message ${isUser ? 'user':'ai'}">
                    <div class="content">
                        ${m.text}
                        ${m.isLoading ? `<div class="loading-bubble"><div class="spinner"></div> Generating photo...</div>` : ''}
                        ${m.image ? `<img src="${m.image}" class="chat-img-bubble" />` : ''}
                    </div>
                </div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let val = input.value.trim();
            if(!val) return;
            input.value = '';

            appendMsg('You', val);

            let lower = val.toLowerCase();
            let autoPhoto = lower.includes('pic') || lower.includes('photo') || lower.includes('selfie') || lower.includes('bhejo');

            let res = await fetch('/api/advanced-chat', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                    contextId: activeContext.id,
                    history: chatHistories[activeContext.id],
                    character: characters.find(c => c.id === activeContext.id),
                    autoPhoto: autoPhoto
                })
            });
            let data = await res.json();
            if(data.reply) appendMsg(data.sender, data.reply);
            if(data.taskId) pollBackgroundPhoto(activeContext.id, data.taskId);
        }

        async function triggerPhotoRequest() {
            let res = await fetch('/api/start-image-task', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ character: characters.find(c => c.id === activeContext.id), prompt: "casual selfie" })
            });
            let data = await res.json();
            if(data.taskId) {
                let msgIdx = appendMsg(activeContext.name || 'AI', "Here is your photo:", null, true);
                pollBackgroundPhoto(activeContext.id, data.taskId, msgIdx);
            }
        }

        async function pollBackgroundPhoto(charId, taskId, msgIndex = null) {
            let interval = setInterval(async () => {
                let res = await fetch(`/api/check-task/${taskId}`);
                let data = await res.json();

                if(data.status === 'completed') {
                    clearInterval(interval);
                    if(activeContext && activeContext.id === charId) {
                        let history = chatHistories[charId];
                        let targetMsg = msgIndex !== null ? history[msgIndex] : history[history.length - 1];
                        if(targetMsg) {
                            targetMsg.isLoading = false;
                            targetMsg.image = data.imageUrl;
                            saveState();
                            renderMessages();
                        }
                    }
                } else if(data.status === 'failed') {
                    clearInterval(interval);
                    if(msgIndex !== null && chatHistories[charId][msgIndex]) {
                        chatHistories[charId][msgIndex].isLoading = false;
                        chatHistories[charId][msgIndex].text += " (Generation failed)";
                        saveState();
                        renderMessages();
                    }
                }
            }, 4000);
        }

        function openNewCharForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('char-id').value = 'char_' + Date.now();
            document.getElementById('char-name').value = '';
            document.getElementById('char-app').value = '';
            document.getElementById('char-backstory').value = '';
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.remove('hidden');
            document.getElementById('clear-chat-btn').classList.add('hidden');
        }

        function saveCharacter() {
            let id = document.getElementById('char-id').value;
            let c = {
                id,
                name: document.getElementById('char-name').value || 'Companion',
                appearance: document.getElementById('char-app').value,
                backstory: document.getElementById('char-backstory').value
            };
            characters.push(c);
            saveState();
            openChat(id);
        }

        function renderSidebar() {
            document.getElementById('char-list').innerHTML = characters.map(c => `<button class="item-btn" onclick="openChat('${c.id}')"><i class="fa-solid fa-user" style="margin-right:8px; color:var(--accent-pink);"></i>${c.name}</button>`).join('');
        }

        function openChat(id) {
            activeContext = { id, name: characters.find(c => c.id === id)?.name };
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('clear-chat-btn').classList.remove('hidden');
            renderMessages();
        }

        function clearCurrentChat() {
            if(confirm("Clear chat?")) {
                chatHistories[activeContext.id] = [];
                saveState();
                renderMessages();
            }
        }

        renderSidebar();
    </script>
</body>
</html>
"""

@app.route("/")
def home(): 
    return render_template_string(HTML_CODE)

def run_hf_image_task(task_id, character):
    hf_token = os.environ.get("HF_TOKEN")
    raw_prompt = f"candid raw photo of {character.get('name', 'woman')}, {character.get('appearance', 'natural beauty')}, realistic skin texture, 35mm film, sharp focus, natural lighting"
    
    try:
        img_res = requests.post(
            "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
            headers={"Authorization": f"Bearer {hf_token.strip()}"},
            json={"inputs": raw_prompt},
            timeout=60
        )
        if img_res.status_code == 200:
            encoded_img = base64.b64encode(img_res.content).decode('utf-8')
            task_storage[task_id] = {"status": "completed", "imageUrl": f"data:image/jpeg;base64,{encoded_img}"}
            return
    except Exception as e:
        print("HF Error:", e)
    
    task_storage[task_id] = {"status": "failed"}

@app.route("/api/start-image-task", methods=["POST"])
def start_image_task():
    data = request.json
    c = data.get("character", {})
    task_id = "task_" + str(random.randint(100000, 999999))
    
    task_storage[task_id] = {"status": "processing"}
    threading.Thread(target=run_hf_image_task, args=(task_id, c)).start()
    
    return jsonify({"taskId": task_id})

@app.route("/api/check-task/<task_id>", methods=["GET"])
def check_task(task_id):
    return jsonify(task_storage.get(task_id, {"status": "processing"}))

@app.route("/api/advanced-chat", methods=["POST"])
def advanced_chat():
    data = request.json
    groq_api_key = os.environ.get("GROQ_API_KEY")
    c = data.get("character", {})
    history = data.get("history", [])
    auto_photo = data.get("autoPhoto", False)

    if not groq_api_key:
        return jsonify({"reply": "Groq Key missing!"})

    system_prompt = f"Roleplay as {c.get('name', 'Companion')}. Backstory: {c.get('backstory', '')}. Stay in character."
    messages = [{"role": "system", "content": system_prompt}]
    for m in history[-25:]:
        messages.append({"role": "user" if m["sender"] == "You" else "assistant", "content": m["text"]})

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }, headers={"Authorization": f"Bearer {groq_api_key.strip()}", "Content-Type": "application/json"}).json()
        reply = res["choices"][0]["message"]["content"]
    except:
        reply = "*Smiles* Hey there!"

    resp = {"sender": c.get('name', 'Companion'), "reply": reply}

    if auto_photo:
        task_id = "task_" + str(random.randint(100000, 999999))
        task_storage[task_id] = {"status": "processing"}
        threading.Thread(target=run_hf_image_task, args=(task_id, c)).start()
        resp["taskId"] = task_id

    return jsonify(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
