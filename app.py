import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aura - AI Companions</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #09090b; color: #f4f4f5; display: flex; height: 100vh; width: 100vw; overflow: hidden; }

        /* Sidebar Navigation */
        .sidebar { width: 280px; min-width: 280px; background: #121215; border-right: 1px solid #27272a; display: flex; flex-direction: column; transition: all 0.3s ease; z-index: 10; height: 100vh; }
        .sidebar.collapsed { margin-left: -280px; min-width: 0; width: 0; overflow: hidden; border: none; }
        .sidebar-header { padding: 20px; font-size: 1.3rem; font-weight: 800; color: #a855f7; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #18181b; }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; }
        .section-title { font-size: 0.7rem; text-transform: uppercase; color: #71717a; padding: 8px; font-weight: 700; }
        
        .item-btn { width: 100%; padding: 10px 12px; background: transparent; border: none; color: #a1a1aa; border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 4px; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; }
        .item-btn:hover, .item-btn.active { background: #27272a; color: #fff; }
        .item-btn img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }

        .create-btn { width: calc(100% - 24px); margin: 6px 12px; padding: 11px; background: #9333ea; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.88rem; }
        .create-btn:hover { background: #7e22ce; }

        .sidebar-footer { padding: 12px; border-top: 1px solid #18181b; }

        /* Main Workspace */
        .main-content { flex: 1; display: flex; flex-direction: column; background: #09090b; height: 100vh; width: 100%; overflow: hidden; position: relative; }
        .top-bar { height: 60px; min-height: 60px; border-bottom: 1px solid #1c1c21; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: #121215; }
        .toggle-sidebar-btn { background: transparent; border: none; color: #a1a1aa; font-size: 1.2rem; cursor: pointer; padding: 8px; border-radius: 6px; }
        .toggle-sidebar-btn:hover { color: #fff; background: #27272a; }
        .chat-title { font-weight: 600; font-size: 1.05rem; display: flex; align-items: center; gap: 10px; }
        .icon-btn { background: #27272a; border: none; color: #e4e4e7; width: 36px; height: 36px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }
        .icon-btn:hover { background: #3f3f46; color: #fff; }

        /* Placeholder Screen */
        .placeholder-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #71717a; text-align: center; padding: 20px; }
        .placeholder-screen i { font-size: 3rem; margin-bottom: 16px; color: #3f3f46; }

        /* Chat View */
        #chat-view { flex: 1; display: flex; flex-direction: column; height: calc(100vh - 60px); overflow: hidden; }
        .chat-messages { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }
        .message { display: flex; gap: 12px; max-width: 82%; position: relative; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; background: #27272a; flex-shrink: 0; }
        .message .content { background: #121215; border: 1px solid #27272a; padding: 12px 16px; border-radius: 14px; font-size: 0.95rem; line-height: 1.5; color: #e4e4e7; }
        .message.user .content { background: #9333ea; border: none; color: white; border-bottom-right-radius: 4px; }
        .message.ai .content { border-bottom-left-radius: 4px; }
        .message .sender-name { font-size: 0.75rem; color: #71717a; margin-bottom: 4px; font-weight: 600; }
        
        /* Action Formatting (*Italics*) */
        .action-text { color: #c084fc; font-style: italic; }

        /* Typing Dots */
        .typing-dots { display: flex; gap: 4px; align-items: center; padding: 6px 0; }
        .typing-dots span { width: 6px; height: 6px; background: #a1a1aa; border-radius: 50%; animation: pulse 1.2s infinite ease-in-out; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }

        /* Input Area */
        .input-area { padding: 16px 24px; border-top: 1px solid #1c1c21; background: #121215; display: flex; gap: 12px; width: 100%; box-sizing: border-box; }
        .input-area input { flex: 1; background: #09090b; border: 1px solid #27272a; padding: 12px 16px; border-radius: 10px; color: white; outline: none; font-size: 0.95rem; }
        .input-area button { padding: 12px 20px; background: #9333ea; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }

        /* Modal Forms */
        .form-container { padding: 32px; overflow-y: auto; flex: 1; max-width: 650px; margin: 0 auto; width: 100%; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 0.85rem; color: #a1a1aa; font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: #121215; border: 1px solid #27272a; padding: 12px; border-radius: 10px; color: white; outline: none; font-size: 0.9rem; }
        .form-group textarea { height: 90px; resize: vertical; }

        .hidden { display: none !important; }
        .avatar-preview { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-top: 10px; background: #27272a; border: 2px solid #3f3f46; }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span>✨ Aura</span>
            <button class="toggle-sidebar-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
        </div>

        <button class="create-btn" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> New Character</button>
        <button class="create-btn" style="background: #2563eb;" onclick="showForm('group-form')"><i class="fa-solid fa-users"></i> New Group Chat</button>

        <div class="nav-section">
            <div class="section-title">Characters</div>
            <div id="char-list"></div>

            <div class="section-title" style="margin-top: 15px;">Group Chats</div>
            <div id="group-list"></div>
        </div>

        <div class="sidebar-footer">
            <button class="item-btn" onclick="showForm('settings-form')"><i class="fa-solid fa-gear"></i> Backup & Settings</button>
        </div>
    </div>

    <!-- Main Workspace -->
    <div class="main-content">
        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 12px;">
                <button class="toggle-sidebar-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="chat-title" id="current-title">Aura Workspace</div>
            </div>
            <div id="top-actions" class="hidden" style="display: flex; gap: 8px;">
                <button class="icon-btn" onclick="openPinnedMemoryModal()" title="Pin Memory"><i class="fa-solid fa-thumbtack"></i></button>
                <button class="icon-btn" onclick="editCurrentCharacter()" title="Edit Character"><i class="fa-solid fa-wrench"></i></button>
                <button class="icon-btn" onclick="regenerateLastResponse()" title="Regenerate Response"><i class="fa-solid fa-rotate-right"></i></button>
                <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat History"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <!-- Placeholder view -->
        <div id="placeholder-view" class="placeholder-screen">
            <i class="fa-solid fa-comments"></i>
            <h3>Select a Companion or Create a New One</h3>
        </div>

        <!-- Chat View -->
        <div id="chat-view" class="hidden">
            <div class="chat-messages" id="message-container"></div>
            <div class="input-area">
                <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                <button onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>

        <!-- Character Form -->
        <div id="char-form" class="form-container hidden">
            <h2 style="margin-bottom: 24px; font-weight: 700;" id="char-form-title">Create Companion</h2>
            <input type="hidden" id="char-id">
            
            <div class="form-group">
                <label>Avatar Picture</label>
                <input type="file" id="char-avatar-file" accept="image/*" onchange="previewImage(this, 'avatar-img-preview')">
                <img id="avatar-img-preview" class="avatar-preview" src="https://api.dicebear.com/7.x/bottts/svg?seed=default">
            </div>

            <div class="form-group">
                <label>Name</label>
                <input type="text" id="char-name" placeholder="e.g. Maya">
            </div>

            <div class="form-group">
                <label>Appearance Description</label>
                <input type="text" id="char-app" placeholder="e.g. Tall, blue eyes, long black hair">
            </div>

            <div class="form-group">
                <label>Backstory</label>
                <textarea id="char-backstory" placeholder="Describe personality, history, dynamic..."></textarea>
            </div>

            <div class="form-group">
                <label>Response Directives</label>
                <textarea id="char-directives" placeholder="e.g. Talk casually using slang, short sentences"></textarea>
            </div>

            <div class="form-group">
                <label>Key Memories / Core Facts</label>
                <textarea id="char-memories" placeholder="Important facts the AI must always remember"></textarea>
            </div>

            <button class="create-btn" style="margin: 0; width: 100%;" onclick="saveCharacter()">Save Character</button>
        </div>

        <!-- Group Chat Form -->
        <div id="group-form" class="form-container hidden">
            <h2 style="margin-bottom: 24px; font-weight: 700;">Create Group Chat</h2>
            <div class="form-group">
                <label>Group Title</label>
                <input type="text" id="group-title" placeholder="e.g. Squad Chat">
            </div>
            <div class="form-group">
                <label>Select Characters</label>
                <div id="group-char-selector" style="display:flex; flex-direction:column; gap:10px;"></div>
            </div>
            <button class="create-btn" style="background:#2563eb; margin:0; width:100%;" onclick="saveGroup()">Launch Group Chat</button>
        </div>

        <!-- Settings / Backup Form -->
        <div id="settings-form" class="form-container hidden">
            <h2 style="margin-bottom: 20px;">Backup & Restore Data</h2>
            <div class="form-group">
                <label>Export Companion Data</label>
                <button class="create-btn" style="margin:0; width:100%;" onclick="exportData()"><i class="fa-solid fa-download"></i> Export All Companions & Chats (.json)</button>
            </div>
            <div class="form-group" style="margin-top: 30px;">
                <label>Import Companion Data</label>
                <input type="file" id="import-file" accept=".json" onchange="importData(this)">
            </div>
        </div>
    </div>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('aura_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let activeContext = null;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('collapsed'); }

        function saveState() {
            localStorage.setItem('aura_chars', JSON.stringify(characters));
            localStorage.setItem('aura_groups', JSON.stringify(groups));
            localStorage.setItem('aura_chats', JSON.stringify(chatHistories));
            renderSidebar();
        }

        function previewImage(input, previewId) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = function(e) { document.getElementById(previewId).src = e.target.result; }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function openNewCharForm() {
            document.getElementById('char-id').value = '';
            document.getElementById('char-name').value = '';
            document.getElementById('char-app').value = '';
            document.getElementById('char-backstory').value = '';
            document.getElementById('char-directives').value = '';
            document.getElementById('char-memories').value = '';
            document.getElementById('avatar-img-preview').src = 'https://api.dicebear.com/7.x/bottts/svg?seed=' + Date.now();
            document.getElementById('char-form-title').innerText = 'Create New Companion';
            showForm('char-form');
        }

        function editCurrentCharacter() {
            if(!activeContext || activeContext.type !== 'char') return;
            let c = characters.find(item => item.id === activeContext.id);
            if(!c) return;

            document.getElementById('char-id').value = c.id;
            document.getElementById('char-name').value = c.name;
            document.getElementById('char-app').value = c.appearance || '';
            document.getElementById('char-backstory').value = c.backstory || '';
            document.getElementById('char-directives').value = c.directives || '';
            document.getElementById('char-memories').value = c.memories || '';
            document.getElementById('avatar-img-preview').src = c.avatar;
            document.getElementById('char-form-title').innerText = 'Modify Companion';
            showForm('char-form');
        }

        function openPinnedMemoryModal() {
            if(!activeContext || activeContext.type !== 'char') return;
            let c = characters.find(item => item.id === activeContext.id);
            let fact = prompt("Add a temporary pinned memory for " + c.name + " (e.g., We are currently sitting in a cafe):", c.memories || '');
            if(fact !== null) {
                c.memories = fact;
                saveState();
                alert("Memory updated!");
            }
        }

        function showForm(formId) {
            document.getElementById('placeholder-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('top-actions').classList.add('hidden');
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
                    <i class="fa-solid fa-users" style="margin-left: 4px; margin-right: 4px;"></i>
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
                avatar: avatarImg
            };

            let existingIdx = characters.findIndex(c => c.id === id);
            if(existingIdx >= 0) characters[existingIdx] = charObj;
            else characters.push(charObj);

            saveState();
            openChat('char', id);
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('placeholder-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-actions').classList.remove('hidden');

            renderSidebar();
            
            let name = type === 'char' ? characters.find(c => c.id === id)?.name : groups.find(g => g.id === id)?.title;
            document.getElementById('current-title').innerText = name || 'Chat';

            renderMessages();
            document.getElementById('chat-input').focus();
        }

        function formatText(text) {
            // Converts *actions* into purple italic text
            return text.replace(/\*(.*?)\*/g, '<span class="action-text">*$1*</span>');
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];

            container.innerHTML = history.map(m => {
                let isUser = m.sender === 'You';
                let avatar = isUser ? 'https://api.dicebear.com/7.x/identicon/svg?seed=user' : m.avatar;
                return `
                    <div class="message ${isUser ? 'user':'ai'}">
                        <img class="avatar" src="${avatar}" />
                        <div>
                            <div class="sender-name">${m.sender}</div>
                            <div class="content">${formatText(m.text)}</div>
                        </div>
                    </div>
                `;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        async function typeWriterEffect(sender, fullText, avatar) {
            let container = document.getElementById('message-container');
            
            let typingDiv = document.createElement('div');
            typingDiv.className = 'message ai';
            typingDiv.innerHTML = `
                <img class="avatar" src="${avatar}" />
                <div>
                    <div class="sender-name">${sender}</div>
                    <div class="content"><div class="typing-dots"><span></span><span></span><span></span></div></div>
                </div>
            `;
            container.appendChild(typingDiv);
            container.scrollTop = container.scrollHeight;

            await new Promise(resolve => setTimeout(resolve, 1000));

            let contentDiv = typingDiv.querySelector('.content');
            contentDiv.innerHTML = '';
            let words = fullText.split(' ');
            
            for (let i = 0; i < words.length; i++) {
                let currentSubText = words.slice(0, i + 1).join(' ');
                contentDiv.innerHTML = formatText(currentSubText);
                container.scrollTop = container.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 50));
            }

            chatHistories[activeContext.id].push({ sender, text: fullText, avatar });
            saveState();
        }

        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let text = input.value.trim();
            if(!text || !activeContext) return;

            input.value = '';
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            
            chatHistories[activeContext.id].push({ sender: 'You', text });
            renderMessages();

            fetchAIResponse();
        }

        async function fetchAIResponse() {
            let payload = {
                type: activeContext.type,
                contextId: activeContext.id,
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
                for (let r of data.responses) {
                    await typeWriterEffect(r.sender, r.text, r.avatar);
                }
            }
        }

        function regenerateLastResponse() {
            if(!activeContext || !chatHistories[activeContext.id]) return;
            let history = chatHistories[activeContext.id];
            if(history.length === 0) return;

            // Remove last AI message
            if(history[history.length - 1].sender !== 'You') {
                history.pop();
                renderMessages();
                fetchAIResponse();
            }
        }

        function clearCurrentChat() {
            if(!activeContext || !confirm('Clear all conversation history with this character?')) return;
            chatHistories[activeContext.id] = [];
            saveState();
            renderMessages();
        }

        // Import & Export Logic
        function exportData() {
            let backupData = { characters, groups, chatHistories };
            let blob = new Blob([JSON.stringify(backupData, null, 2)], { type: 'application/json' });
            let a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'Aura_Backup_' + Date.now() + '.json';
            a.click();
        }

        function importData(input) {
            let file = input.files[0];
            if(!file) return;

            let reader = new FileReader();
            reader.onload = function(e) {
                try {
                    let imported = JSON.parse(e.target.result);
                    if(imported.characters) characters = imported.characters;
                    if(imported.groups) groups = imported.groups;
                    if(imported.chatHistories) chatHistories = imported.chatHistories;
                    saveState();
                    alert('Data imported successfully!');
                    location.reload();
                } catch(err) {
                    alert('Invalid JSON File!');
                }
            };
            reader.readAsText(file);
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

    if data["type"] == "char":
        c = data["character"]
        system_prompt = f"""
Name: {c['name']}
Appearance: {c.get('appearance', '')}
Backstory: {c.get('backstory', '')}
Response Directives: {c.get('directives', '')}
Key Memories / Current Context: {c.get('memories', '')}

Roleplay naturally as {c['name']}. Stay in character. Use asterisks for actions like *smiles and looks at you*.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for m in data["history"][-8:]:
            role = "user" if m["sender"] == "You" else "assistant"
            messages.append({"role": role, "content": m["text"]})

        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }, headers=headers).json()

        reply_text = res["choices"][0]["message"]["content"]
        responses.append({"sender": c['name'], "text": reply_text, "avatar": c['avatar']})

    else:
        members = data["members"]
        for char in members[:2]:
            system_prompt = f"""
You are in a group chat as {char['name']}.
Backstory: {char.get('backstory', '')}
Directives: {char.get('directives', '')}
Other Members: {', '.join([m['name'] for m in members if m['name'] != char['name']])}

Respond briefly from {char['name']}'s perspective. Use asterisks for actions like *laughs*.
            """

            messages = [{"role": "system", "content": system_prompt}]
            for m in data["history"][-8:]:
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
