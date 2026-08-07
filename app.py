import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Modern Minimal Dark UI (Kindroid Inspired)
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Companion Hub</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f0f12; color: #e4e4e7; display: flex; height: 100vh; overflow: hidden; }

        /* Sidebar Navigation */
        .sidebar { width: 260px; background: #18181b; border-right: 1px solid #27272a; display: flex; flex-direction: column; }
        .sidebar-header { padding: 20px; font-size: 1.2rem; font-weight: 700; color: #a855f7; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #27272a; }
        .nav-section { padding: 10px; flex: 1; overflow-y: auto; }
        .section-title { font-size: 0.75rem; text-transform: uppercase; color: #71717a; padding: 10px; letter-spacing: 0.05em; font-weight: 600; }
        
        .item-btn { width: 100%; padding: 10px 12px; background: transparent; border: none; color: #a1a1aa; border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; font-size: 0.9rem; transition: 0.2s; }
        .item-btn:hover, .item-btn.active { background: #27272a; color: #fff; }
        .item-btn img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }

        .create-btn { width: calc(100% - 20px); margin: 10px; padding: 10px; background: #9333ea; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .create-btn:hover { background: #7e22ce; }

        /* Main Workspace */
        .main-content { flex: 1; display: flex; flex-direction: column; background: #0f0f12; }
        .top-bar { height: 60px; border-bottom: 1px solid #27272a; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: #18181b; }
        .chat-title { font-weight: 600; font-size: 1.1rem; display: flex; align-items: center; gap: 10px; }

        /* Chat View */
        #chat-view { flex: 1; display: flex; flex-direction: column; height: calc(100vh - 60px); }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { display: flex; gap: 12px; max-width: 80%; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #3f3f46; flex-shrink: 0; }
        .message .content { background: #18181b; border: 1px solid #27272a; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.5; }
        .message.user .content { background: #9333ea; border: none; color: white; }
        .message .sender-name { font-size: 0.75rem; color: #a1a1aa; margin-bottom: 4px; font-weight: 600; }

        .input-area { padding: 16px; border-top: 1px solid #27272a; background: #18181b; display: flex; gap: 10px; }
        .input-area input { flex: 1; background: #0f0f12; border: 1px solid #27272a; padding: 12px 16px; border-radius: 8px; color: white; outline: none; font-size: 0.95rem; }
        .input-area button { padding: 12px 20px; background: #9333ea; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }

        /* Modal / Forms */
        .form-container { padding: 30px; overflow-y: auto; flex: 1; max-width: 700px; margin: 0 auto; width: 100%; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 0.85rem; color: #a1a1aa; font-weight: 600; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; background: #18181b; border: 1px solid #27272a; padding: 12px; border-radius: 8px; color: white; outline: none; font-size: 0.9rem; }
        .form-group textarea { height: 100px; resize: vertical; }
        .toggle-group { display: flex; align-items: center; justify-content: space-between; background: #18181b; padding: 12px; border-radius: 8px; border: 1px solid #27272a; }

        .hidden { display: none !important; }
        .avatar-preview { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-top: 10px; background: #27272a; }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <i class="fa-solid fa-brain"></i> Kindroid Studio
        </div>

        <button class="create-btn" onclick="showForm('char-form')"><i class="fa-solid fa-plus"></i> New Character</button>
        <button class="create-btn" style="background: #2563eb;" onclick="showForm('group-form')"><i class="fa-solid fa-users"></i> New Group Chat</button>

        <div class="nav-section">
            <div class="section-title">Characters</div>
            <div id="char-list"></div>

            <div class="section-title" style="margin-top: 15px;">Group Chats</div>
            <div id="group-list"></div>
        </div>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
        <div class="top-bar">
            <div class="chat-title" id="current-title">Select or Create a Companion</div>
            <button class="item-btn" id="edit-btn" style="width: auto;" onclick="editCurrentItem()"><i class="fa-solid fa-gear"></i> Settings</button>
        </div>

        <!-- Chat View -->
        <div id="chat-view">
            <div class="chat-messages" id="message-container"></div>
            <div class="input-area">
                <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                <button onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>

        <!-- Create/Edit Character Form -->
        <div id="char-form" class="form-container hidden">
            <h2 style="margin-bottom: 20px;">Character Details</h2>
            <input type="hidden" id="char-id">
            
            <div class="form-group">
                <label>Avatar Picture</label>
                <input type="file" id="char-avatar-file" accept="image/*" onchange="previewImage(this, 'avatar-img-preview')">
                <img id="avatar-img-preview" class="avatar-preview" src="">
            </div>

            <div class="form-group">
                <label>Name</label>
                <input type="text" id="char-name" placeholder="e.g. Maya">
            </div>

            <div class="form-group">
                <label>Appearance Description</label>
                <input type="text" id="char-app" placeholder="e.g. Tall, blue eyes, long black hair, wears leather jacket">
            </div>

            <div class="form-group">
                <label>Backstory</label>
                <textarea id="char-backstory" placeholder="Describe personality, history, dynamic with you..."></textarea>
            </div>

            <div class="form-group">
                <label>Response Directives</label>
                <textarea id="char-directives" placeholder="e.g. Talk casually using slang, short sentences, playful tone"></textarea>
            </div>

            <div class="form-group">
                <label>Key Memories / Core Facts</label>
                <textarea id="char-memories" placeholder="Important facts the AI must always remember (e.g., We met in Paris)"></textarea>
            </div>

            <div class="form-group">
                <div class="toggle-group">
                    <span>Enable Unfiltered / NSFW Mode</span>
                    <input type="checkbox" id="char-nsfw" style="width: auto;">
                </div>
            </div>

            <button class="create-btn" onclick="saveCharacter()">Save Character</button>
        </div>

        <!-- Create Group Chat Form -->
        <div id="group-form" class="form-container hidden">
            <h2 style="margin-bottom: 20px;">Create Group Chat</h2>
            
            <div class="form-group">
                <label>Group Title</label>
                <input type="text" id="group-title" placeholder="e.g. Late Night Squad">
            </div>

            <div class="form-group">
                <label>Select Characters for Group</label>
                <div id="group-char-selector" style="display:flex; flex-direction:column; gap:10px;"></div>
            </div>

            <button class="create-btn" style="background:#2563eb;" onclick="saveGroup()">Launch Group Chat</button>
        </div>
    </div>

    <script>
        let characters = JSON.parse(localStorage.getItem('kindroid_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('kindroid_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('kindroid_chats') || '{}');
        let activeContext = null; // { type: 'char'|'group', id: string }

        function saveState() {
            localStorage.setItem('kindroid_chars', JSON.stringify(characters));
            localStorage.setItem('kindroid_groups', JSON.stringify(groups));
            localStorage.setItem('kindroid_chats', JSON.stringify(chatHistories));
            renderSidebar();
        }

        function previewImage(input, previewId) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById(previewId).src = e.target.result;
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function showForm(formId) {
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById(formId).classList.remove('hidden');

            if(formId === 'group-form') renderGroupSelector();
        }

        function renderSidebar() {
            let charList = document.getElementById('char-list');
            let groupList = document.getElementById('group-list');
            
            charList.innerHTML = characters.map(c => `
                <button class="item-btn ${activeContext?.id === c.id ? 'active':''}" onclick="openChat('char', '${c.id}')">
                    <img src="${c.avatar || 'https://via.placeholder.com/40'}" />
                    <span>${c.name}</span>
                </button>
            `).join('');

            groupList.innerHTML = groups.map(g => `
                <button class="item-btn ${activeContext?.id === g.id ? 'active':''}" onclick="openChat('group', '${g.id}')">
                    <i class="fa-solid fa-users" style="margin-left: 5px; margin-right: 5px;"></i>
                    <span>${g.title}</span>
                </button>
            `).join('');
        }

        function saveCharacter() {
            let id = document.getElementById('char-id').value || 'char_' + Date.now();
            let avatarImg = document.getElementById('avatar-img-preview').src;
            
            let charObj = {
                id,
                name: document.getElementById('char-name').value || 'Companion',
                appearance: document.getElementById('char-app').value,
                backstory: document.getElementById('char-backstory').value,
                directives: document.getElementById('char-directives').value,
                memories: document.getElementById('char-memories').value,
                nsfw: document.getElementById('char-nsfw').checked,
                avatar: avatarImg.length > 100 ? avatarImg : 'https://api.dicebear.com/7.x/bottts/svg?seed=' + id
            };

            let existingIdx = characters.findIndex(c => c.id === id);
            if(existingIdx >= 0) characters[existingIdx] = charObj;
            else characters.push(charObj);

            saveState();
            openChat('char', id);
        }

        function renderGroupSelector() {
            let container = document.getElementById('group-char-selector');
            container.innerHTML = characters.map(c => `
                <label style="display:flex; align-items:center; gap:10px; background:#18181b; padding:10px; border-radius:8px;">
                    <input type="checkbox" value="${c.id}" class="group-char-checkbox" style="width:auto;">
                    <img src="${c.avatar}" style="width:24px; height:24px; border-radius:50%;"/>
                    ${c.name}
                </label>
            `).join('');
        }

        function saveGroup() {
            let title = document.getElementById('group-title').value || 'Group Chat';
            let selectedChars = Array.from(document.querySelectorAll('.group-char-checkbox:checked')).map(cb => cb.value);
            
            if(selectedChars.length < 2) return alert('Select at least 2 characters!');

            let groupId = 'group_' + Date.now();
            groups.push({ id: groupId, title, memberIds: selectedChars });
            
            saveState();
            openChat('group', groupId);
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');

            renderSidebar();
            
            let name = type === 'char' ? characters.find(c => c.id === id)?.name : groups.find(g => g.id === id)?.title;
            document.getElementById('current-title').innerText = name || 'Chat';

            renderMessages();
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];

            container.innerHTML = history.map(m => {
                let isUser = m.sender === 'You';
                let avatar = isUser ? 'https://api.dicebear.com/7.x/identicon/svg?seed=user' : m.avatar;
                return `
                    <div class="message ${isUser ? 'user':''}">
                        <img class="avatar" src="${avatar}" />
                        <div>
                            <div class="sender-name">${m.sender}</div>
                            <div class="content">${m.text}</div>
                        </div>
                    </div>
                `;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let text = input.value.trim();
            if(!text || !activeContext) return;

            input.value = '';
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            
            chatHistories[activeContext.id].push({ sender: 'You', text });
            renderMessages();

            let payload = {
                type: activeContext.type,
                contextId: activeContext.id,
                message: text,
                history: chatHistories[activeContext.id]
            };

            if(activeContext.type === 'char') {
                payload.character = characters.find(c => c.id === activeContext.id);
            } else {
                let group = groups.find(g => g.id === activeContext.id);
                payload.members = characters.filter(c => group.memberIds.includes(c.id));
            }

            let res = await fetch('/api/advanced-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let data = await res.json();
            
            if(data.responses) {
                data.responses.forEach(r => {
                    chatHistories[activeContext.id].push({ sender: r.sender, text: r.text, avatar: r.avatar });
                });
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
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return jsonify({"responses": [{"sender": "System", "text": "Groq Key missing in Render Environment!"}]})

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    responses = []

    # 1. Single Character Chat
    if data["type"] == "char":
        c = data["character"]
        system_prompt = f"""
Name: {c['name']}
Appearance: {c.get('appearance', '')}
Backstory: {c.get('backstory', '')}
Response Directives: {c.get('directives', '')}
Key Memories: {c.get('memories', '')}
Unfiltered/NSFW Allowed: {c.get('nsfw', False)}

Roleplay naturally as {c['name']}. Stay in character. Keep responses human-like and immersive.
        """
        
        # Build prompt history
        messages = [{"role": "system", "content": system_prompt}]
        for m in data["history"][-6:]:
            role = "user" if m["sender"] == "You" else "assistant"
            messages.append({"role": role, "content": m["text"]})

        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }, headers=headers).json()

        reply_text = res["choices"][0]["message"]["content"]
        responses.append({"sender": c['name'], "text": reply_text, "avatar": c['avatar']})

    # 2. Group Chat Logic (Multiple characters talk)
    else:
        members = data["members"]
        # Allow 2 characters to respond sequentially in group
        for char in members[:2]:
            system_prompt = f"""
You are participating in a group chat as {char['name']}.
Backstory: {char.get('backstory', '')}
Directives: {char.get('directives', '')}
Other Members in Room: {', '.join([m['name'] for m in members if m['name'] != char['name']])}

Respond briefly to the recent conversation from {char['name']}'s perspective.
            """

            messages = [{"role": "system", "content": system_prompt}]
            for m in data["history"][-6:]:
                messages.append({"role": "user", "content": f"{m['sender']}: {m['text']}"})

            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                "model": "llama-3.1-8b-instant",
                "messages": messages
            }, headers=headers).json()

            reply_text = res["choices"][0]["message"]["content"]
            responses.append({"sender": char['name'], "text": reply_text, "avatar": char['avatar']})

    return jsonify({"responses": responses})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
