import os
import requests
import json
import urllib.parse
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aura - AI Companions</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-main: #050508; --bg-surface: #121215; --bg-input: #09090b;
            --border-color: #27272a; --text-main: #f4f4f5; --text-sub: #a1a1aa;
            --accent-purple: #a855f7; --accent-pink: #ec4899; --action-text: #f472b6;
            --user-msg-bg: linear-gradient(135deg, #9333ea, #ec4899);
            --ai-msg-bg: #121215; --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            --sidebar-bg: #09090b; --sidebar-border: #27272a; --sidebar-text: #f4f4f5;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        html, body { height: 100dvh; width: 100vw; background: #000000; color: var(--text-main); overflow: hidden; display: flex; justify-content: center; align-items: center; }
        .app-container { width: 100%; max-width: 440px; height: 100dvh; background: var(--bg-main); display: flex; flex-direction: column; position: relative; overflow: hidden; border: 1px solid var(--border-color); }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }
        
        .top-bar { height: 52px; min-height: 52px; background: var(--bg-surface); border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 10; }
        .toggle-btn { background: transparent; border: none; color: var(--text-main); font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .top-title { font-weight: 700; font-size: 1rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
        
        .sidebar { position: absolute; top: 0; left: 0; width: 85%; height: 100%; background: var(--sidebar-bg); color: var(--sidebar-text); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 100; transform: translateX(-100%); }
        .sidebar.open { transform: translateX(0); }
        .sidebar-header { padding: 14px 16px; font-size: 1.2rem; font-weight: 800; color: var(--accent-pink); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .menu-category-btn { width: 100%; padding: 12px 14px; background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 10px; text-align: left; cursor: pointer; font-size: 0.92rem; font-weight: 600; display: flex; align-items: center; gap: 10px; }
        .item-btn { width: 100%; padding: 9px 12px; background: transparent; border: none; color: var(--text-sub); border-radius: 8px; text-align: left; cursor: pointer; font-size: 0.88rem; }
        
        .workspace { flex: 1; display: flex; flex-direction: column; height: calc(100% - 52px); position: relative; overflow: hidden; }
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .dash-title { font-size: 1.5rem; font-weight: 800; color: var(--text-main); margin-bottom: 6px; }
        .dash-sub { font-size: 0.85rem; color: var(--text-sub); text-align: center; margin-bottom: 24px; }
        .dash-card { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 14px 16px; border-radius: 14px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; box-shadow: var(--card-shadow); }
        .dash-card i { font-size: 1.3rem; color: var(--accent-pink); }
        
        #chat-view { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { display: flex; gap: 10px; max-width: 88%; position: relative; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .content { background: var(--ai-msg-bg); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 14px; font-size: 0.9rem; line-height: 1.45; color: var(--text-main); word-break: break-word; box-shadow: var(--card-shadow); }
        .message.user .content { background: var(--user-msg-bg); border: none; color: #ffffff; }
        .chat-img-attachment { width: 100%; max-width: 240px; border-radius: 10px; margin-top: 6px; cursor: pointer; border: 1px solid var(--border-color); display: block; }
        
        .input-area { padding: 10px 12px; border-top: 1px solid var(--border-color); background: var(--bg-surface); display: flex; gap: 8px; width: 100%; align-items: center; }
        .input-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; background: var(--bg-input); border: 1px solid var(--border-color); padding: 10px 12px; border-radius: 20px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .send-btn { height: 38px; padding: 0 14px; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; }
        
        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 4px; font-size: 0.8rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .form-group textarea { height: 75px; resize: vertical; }
        .submit-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; margin-top: 6px; }
        
        .lightbox-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.92); backdrop-filter: blur(10px); z-index: 300; display: flex; flex-direction: column; justify-content: space-between; padding: 16px 12px; align-items: center; }
        .lightbox-img { max-width: 95%; max-height: 75vh; border-radius: 16px; object-fit: contain; border: 1px solid #27272a; }
        .lightbox-actions { display: flex; gap: 12px; width: 100%; max-width: 340px; margin-bottom: 20px; }
        .lightbox-btn { flex: 1; padding: 12px; background: #121215; border: 1px solid #27272a; color: #ffffff; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.88rem; }
        .lightbox-btn.primary { background: linear-gradient(135deg, #9333ea, #ec4899); border: none; }
        
        .gallery-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
        .gallery-item { position: relative; border-radius: 12px; overflow: hidden; height: 160px; border: 1px solid var(--border-color); cursor: pointer; }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span>Aura v1.2</span>
                <button class="icon-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="nav-section">
                <button class="menu-category-btn" onclick="goHome()"><i class="fa-solid fa-house" style="color:var(--accent-pink);"></i> Home</button>
                <button class="menu-category-btn" onclick="openNewCharForm()"><i class="fa-solid fa-user-plus" style="color:var(--accent-pink);"></i> New Character</button>
                <div id="char-list" style="margin-top: 8px; display:flex; flex-direction:column; gap:4px;"></div>
            </div>
        </div>

        <div class="top-bar">
            <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
            <div class="top-title">Aura</div>
            <div id="top-actions" class="hidden" style="display: flex; gap: 6px;">
                <button class="icon-btn" onclick="openCharacterGallery()" title="Gallery">🖼️</button>
                <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <div class="workspace">
            <div id="dashboard-view" class="dashboard">
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your personal AI companion platform.</p>
                <div class="dash-card" onclick="openNewCharForm()"><i class="fa-solid fa-user-plus"></i><div><strong>Create AI Companion</strong><span>Custom backstory & relationship</span></div></div>
            </div>

            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    </div>
                    <button class="send-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;">Create Companion</h3>
                <input type="hidden" id="char-id">
                <div class="form-group"><label>Name</label><input type="text" id="char-name"></div>
                <div class="form-group"><label>Appearance</label><input type="text" id="char-app"></div>
                <div class="form-group"><label>Backstory</label><textarea id="char-backstory"></textarea></div>
                <button class="submit-btn" onclick="saveCharacter()">Save</button>
            </div>

            <div id="gallery-view" class="form-container hidden">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3>Gallery</h3>
                    <button class="icon-btn" onclick="openChat('char', activeContext.id)"><i class="fa-solid fa-arrow-left"></i></button>
                </div>
                <div class="gallery-grid" id="gallery-grid-container"></div>
            </div>
        </div>

        <div id="lightbox-modal" class="lightbox-overlay hidden">
            <div style="width:100%; display:flex; justify-content:flex-end;">
                <button class="toggle-btn" style="color:#ffffff; font-size:1.8rem;" onclick="document.getElementById('lightbox-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <img id="lightbox-target-img" class="lightbox-img" src="">
            <div class="lightbox-actions">
                <button class="lightbox-btn" onclick="downloadLightboxImage()"><i class="fa-solid fa-download"></i> Save</button>
                <button class="lightbox-btn primary" onclick="document.getElementById('lightbox-modal').classList.add('hidden')">Close</button>
            </div>
        </div>
    </div>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let galleries = JSON.parse(localStorage.getItem('aura_galleries') || '{}');
        let activeContext = null;
        let activeLightboxImgUrl = '';

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function goHome() { activeContext = null; document.getElementById('sidebar').classList.remove('open'); document.getElementById('dashboard-view').classList.remove('hidden'); document.getElementById('chat-view').classList.add('hidden'); document.getElementById('char-form').classList.add('hidden'); document.getElementById('gallery-view').classList.add('hidden'); document.getElementById('top-actions').classList.add('hidden'); }
        function saveState() { localStorage.setItem('aura_chars', JSON.stringify(characters)); localStorage.setItem('aura_chats', JSON.stringify(chatHistories)); localStorage.setItem('aura_galleries', JSON.stringify(galleries)); renderSidebar(); }

        function saveToGallery(charId, imgUrl) {
            if(!galleries[charId]) galleries[charId] = [];
            galleries[charId].unshift({ id: 'img_' + Date.now(), url: imgUrl });
            saveState();
        }

        function openCharacterGallery() {
            if(!activeContext) return;
            document.getElementById('sidebar').classList.remove('open');
            let container = document.getElementById('gallery-grid-container');
            let list = galleries[activeContext.id] || [];
            container.innerHTML = list.length === 0 ? '<div style="grid-column:span 2; text-align:center; color:var(--text-sub);">No photos yet.</div>' : list.map(item => `<div class="gallery-item" onclick="openLightbox('${item.url}')"><img src="${item.url}" /></div>`).join('');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('gallery-view').classList.remove('hidden');
        }

        function openLightbox(imgUrl) {
            activeLightboxImgUrl = imgUrl;
            document.getElementById('lightbox-target-img').src = imgUrl;
            document.getElementById('lightbox-modal').classList.remove('hidden');
        }

        async function downloadLightboxImage() {
            if(!activeLightboxImgUrl) return;
            try {
                const res = await fetch(activeLightboxImgUrl);
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a'); a.href = url; a.download = `Photo_${Date.now()}.jpg`;
                document.body.appendChild(a); a.click();
                window.URL.revokeObjectURL(url); document.body.removeChild(a);
            } catch(e) { alert("Download failed"); }
        }

        function appendMsg(sender, text, image = null) {
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            let msg = { sender, text };
            if(image) msg.image = image;
            chatHistories[activeContext.id].push(msg);
            saveState();
            renderMessages();
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];
            container.innerHTML = history.map((m) => {
                let isUser = m.sender === 'You';
                return `<div class="message ${isUser ? 'user':'ai'}">
                    <div class="content">
                        ${m.text}
                        ${m.image ? `<img src="${m.image}" class="chat-img-attachment" onclick="openLightbox('${m.image}')" />` : ''}
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

            let res = await fetch('/api/advanced-chat', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                    contextId: activeContext.id,
                    history: chatHistories[activeContext.id],
                    character: characters.find(c => c.id === activeContext.id)
                })
            });
            let data = await res.json();
            if(data.responses) {
                data.responses.forEach(r => {
                    appendMsg(r.sender, r.text, r.image);
                    if(r.image) saveToGallery(activeContext.id, r.image);
                });
            }
        }

        function openNewCharForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('char-id').value = 'char_' + Date.now();
            document.getElementById('char-name').value = '';
            document.getElementById('char-app').value = '';
            document.getElementById('char-backstory').value = '';
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('gallery-view').classList.add('hidden');
            document.getElementById('char-form').classList.remove('hidden');
            document.getElementById('top-actions').classList.add('hidden');
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
            openChat('char', id);
        }

        function renderSidebar() {
            document.getElementById('char-list').innerHTML = characters.map(c => `<button class="item-btn" onclick="openChat('char', '${c.id}')"><i class="fa-solid fa-user" style="margin-right:8px; color:var(--accent-pink);"></i>${c.name}</button>`).join('');
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('gallery-view').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-actions').classList.remove('hidden');
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

@app.route("/api/advanced-chat", methods=["POST"])
def advanced_chat():
    data = request.json
    groq_api_key = os.environ.get("GROQ_API_KEY")
    c = data.get("character", {})
    history = data.get("history", [])

    if not groq_api_key:
        return jsonify({"responses": [{"sender": c.get('name', 'AI'), "text": "Groq API Key missing!"}]})

    last_user_msg = history[-1]["text"].lower() if history else ""
    photo_requested = any(kw in last_user_msg for kw in ["photo", "pic", "picture", "selfie", "bhejo", "vejo", "dikhao", "send"])

    system_prompt = f"You are roleplaying as {c.get('name', 'Companion')}. Backstory: {c.get('backstory', '')}. Stay in character."
    if photo_requested:
        system_prompt += " The user requested a photo. Agree naturally in text."

    messages = [{"role": "system", "content": system_prompt}]
    for m in history[-20:]:
        messages.append({"role": "user" if m["sender"] == "You" else "assistant", "content": m["text"]})

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }, headers={"Authorization": f"Bearer {groq_api_key.strip()}", "Content-Type": "application/json"}).json()

        reply = res["choices"][0]["message"]["content"]
    except Exception as e:
        reply = "*Smile* Hey there!"

    resp = {"sender": c.get('name', 'Companion'), "text": reply}

    if photo_requested:
        raw_prompt = f"photorealistic portrait of {c.get('name', 'woman')}, {c.get('appearance', '')}, natural lighting, high quality"
        negative = "cartoon, anime, doll, plastic"
        encoded_p = urllib.parse.quote(raw_prompt)
        encoded_n = urllib.parse.quote(negative)
        resp["image"] = f"https://image.pollinations.ai/prompt/{encoded_p}?negative={encoded_n}&width=768&height=1024&nologo=true&seed={random.randint(1000, 999999)}&model=flux"

    return jsonify({"responses": [resp]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
