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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aura - AI Companions</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        
        /* Fixed Dynamic Viewport Height for Mobile Browsers */
        html, body { 
            height: 100dvh; 
            width: 100vw; 
            background: #000000; 
            color: #f4f4f5; 
            overflow: hidden; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
        }

        .app-container {
            width: 100%; 
            max-width: 440px; 
            height: 100dvh;
            background: #09090b; 
            display: flex; 
            flex-direction: column; 
            position: relative;
            overflow: hidden; 
            border: 1px solid #27272a;
        }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }

        /* Top Bar */
        .top-bar { height: 52px; min-height: 52px; background: #121215; border-bottom: 1px solid #27272a; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 10; }
        .toggle-btn { background: transparent; border: none; color: #f4f4f5; font-size: 1.2rem; cursor: pointer; }
        .top-title { font-weight: 700; font-size: 1rem; color: #ffffff; display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: #27272a; border: none; color: #f4f4f5; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }

        /* Sidebar Overlay */
        .sidebar { position: absolute; top: 0; left: 0; width: 85%; height: 100%; background: #121215; border-right: 1px solid #27272a; display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 100; transform: translateX(-100%); pointer-events: none; }
        .sidebar.open { transform: translateX(0); pointer-events: auto; }
        .sidebar-header { padding: 16px; font-size: 1.2rem; font-weight: 800; color: #a855f7; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #18181b; }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; }
        .section-title { font-size: 0.7rem; text-transform: uppercase; color: #71717a; padding: 6px 8px; font-weight: 700; }
        
        .item-btn { width: 100%; padding: 10px; background: transparent; border: none; color: #a1a1aa; border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; font-size: 0.9rem; }
        .item-btn:hover, .item-btn.active { background: #27272a; color: #fff; }
        .item-btn img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }

        /* Workspace & Pages */
        .workspace { flex: 1; display: flex; flex-direction: column; height: calc(100% - 52px); position: relative; overflow: hidden; }

        /* Dashboard */
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .dash-logo { font-size: 2.8rem; color: #a855f7; margin-bottom: 12px; }
        .dash-title { font-size: 1.5rem; font-weight: 800; color: #ffffff; margin-bottom: 6px; }
        .dash-sub { font-size: 0.85rem; color: #a1a1aa; text-align: center; margin-bottom: 24px; }
        
        .dash-card { width: 100%; background: #121215; border: 1px solid #27272a; padding: 14px 16px; border-radius: 12px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; }
        .dash-card i { font-size: 1.2rem; color: #a855f7; }
        .dash-card strong { display: block; color: #ffffff; font-size: 0.92rem; }
        .dash-card span { font-size: 0.75rem; color: #a1a1aa; }

        /* Chat Room */
        #chat-view { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; -webkit-overflow-scrolling: touch; }
        .message { display: flex; gap: 10px; max-width: 88%; position: relative; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; background: #27272a; flex-shrink: 0; }
        .message .content { background: #121215; border: 1px solid #27272a; padding: 10px 14px; border-radius: 14px; font-size: 0.9rem; line-height: 1.45; color: #ffffff; word-break: break-word; }
        .message.user .content { background: #9333ea; border: none; color: #ffffff; border-bottom-right-radius: 2px; }
        .message.ai .content { border-bottom-left-radius: 2px; }
        .message .sender-name { font-size: 0.7rem; color: #a1a1aa; margin-bottom: 3px; font-weight: 600; }
        
        /* Actions Text Changed from Purple to Soft Silver/Gray */
        .action-text { color: #a1a1aa; font-style: italic; }

        .edit-link { font-size: 0.68rem; color: #71717a; text-decoration: underline; cursor: pointer; display: inline-block; margin-top: 4px; }
        .edit-link:hover { color: #c084fc; }

        /* Typing Dots */
        .typing-dots { display: flex; gap: 4px; align-items: center; padding: 4px 0; }
        .typing-dots span { width: 5px; height: 5px; background: #a855f7; border-radius: 50%; animation: pulse 1.2s infinite ease-in-out; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }

        /* Input Controls Bar */
        .input-area { padding: 10px 12px; border-top: 1px solid #1c1c21; background: #121215; display: flex; gap: 6px; width: 100%; align-items: center; }
        .input-area input { flex: 1; background: #09090b; border: 1px solid #27272a; padding: 10px 12px; border-radius: 10px; color: #ffffff; outline: none; font-size: 0.88rem; }
        .input-area button { height: 38px; padding: 0 12px; background: #9333ea; color: #ffffff; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .tool-btn { background: #27272a !important; color: #a855f7 !important; border: 1px solid #3f3f46 !important; padding: 0 10px !important; font-size: 0.85rem; }

        /* Forms */
        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 4px; font-size: 0.8rem; color: #a1a1aa; font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: #121215; border: 1px solid #27272a; padding: 10px; border-radius: 8px; color: #ffffff; outline: none; font-size: 0.88rem; }
        .form-group textarea { height: 75px; resize: vertical; }

        .submit-btn { width: 100%; padding: 11px; background: #9333ea; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.9rem; margin-top: 8px; }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Sidebar Overlay Navigation -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span>✨ Aura</span>
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <button class="submit-btn" style="margin: 12px; width: calc(100% - 24px);" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> New Character</button>

            <div class="nav-section">
                <div class="section-title">Characters</div>
                <div id="char-list"></div>

                <div class="section-title" style="margin-top: 10px;">Group Chats</div>
                <div id="group-list"></div>
            </div>
        </div>

        <!-- Top Navigation Bar -->
        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title">✨ Aura</div>
            </div>
            <!-- Header Icons (Shown ONLY Inside Active Chat) -->
            <div id="top-actions" class="hidden" style="display: flex; gap: 6px;">
                <button class="icon-btn" onclick="openPinnedMemoryModal()" title="Pin Memory"><i class="fa-solid fa-thumbtack"></i></button>
                <button class="icon-btn" onclick="editCurrentCharacter()" title="Edit Companion"><i class="fa-solid fa-wrench"></i></button>
                <button class="icon-btn" onclick="regenerateLastResponse()" title="Regenerate"><i class="fa-solid fa-rotate-right"></i></button>
                <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <!-- Main Workspace Area -->
        <div class="workspace">
            <!-- Dashboard View -->
            <div id="dashboard-view" class="dashboard">
                <div class="dash-logo"><i class="fa-solid fa-sparkles"></i></div>
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your personal AI companion platform.</p>
                
                <div class="dash-card" onclick="openNewCharForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    <div>
                        <strong>Create AI Companion</strong>
                        <span>Custom backstory & relationship</span>
                    </div>
                </div>

                <div class="dash-card" onclick="showForm('group-form')">
                    <i class="fa-solid fa-users"></i>
                    <div>
                        <strong>Create Group Room</strong>
                        <span>Chat with multiple characters</span>
                    </div>
                </div>

                <div class="dash-card" onclick="showForm('settings-form')">
                    <i class="fa-solid fa-sliders"></i>
                    <div>
                        <strong>Persona & Settings</strong>
                        <span>Edit your profile, backup & restore</span>
                    </div>
                </div>

                <div class="dash-card" onclick="toggleFullScreen()">
                    <i class="fa-solid fa-expand"></i>
                    <div>
                        <strong>📱 Enter Fullscreen Mode</strong>
                        <span>Best experience on mobile devices</span>
                    </div>
                </div>
            </div>

            <!-- Active Chat View -->
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="tool-btn" onclick="suggestUserMessage()" title="Magic Auto-Suggest">🪄</button>
                    <button class="tool-btn" onclick="continueAiReply()" title="Continue AI Reply">&gt;&gt;</button>
                    <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    <button onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <!-- Character Creation Form -->
            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px; color: #ffffff;" id="char-form-title">Create Companion</h3>
                <input type="hidden" id="char-id">
                
                <div class="form-group">
                    <label>Avatar Picture</label>
                    <input type="file" id="char-avatar-file" accept="image/*" onchange="previewImage(this)">
                    <img id="avatar-img-preview" src="https://api.dicebear.com/7.x/bottts/svg?seed=default" style="width:60px; height:60px; border-radius:50%; margin-top:6px; object-fit:cover;">
                </div>

                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="char-name" placeholder="e.g. Maya">
                </div>

                <div class="form-group">
                    <label>Relationship with You</label>
                    <input type="text" id="char-rel" placeholder="e.g. Best Friend, Partner, Boss">
                </div>

                <div class="form-group">
                    <label>Appearance Description</label>
                    <input type="text" id="char-app" placeholder="e.g. Tall, blue eyes">
                </div>

                <div class="form-group">
                    <label>Backstory</label>
                    <textarea id="char-backstory" placeholder="Describe backstory..."></textarea>
                </div>

                <div class="form-group">
                    <label>Response Directives</label>
                    <textarea id="char-directives" placeholder="Behavior rules..."></textarea>
                </div>

                <div class="form-group">
                    <label>Key Memories / Core Facts</label>
                    <textarea id="char-memories" placeholder="Pinned facts..."></textarea>
                </div>

                <button class="submit-btn" onclick="saveCharacter()">Save Character</button>
            </div>

            <!-- Group Chat Form -->
            <div id="group-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px; color: #ffffff;">Create Group Chat</h3>
                <div class="form-group">
                    <label>Group Title</label>
                    <input type="text" id="group-title" placeholder="e.g. Squad Chat">
                </div>
                <div class="form-group">
                    <label>Select Characters</label>
                    <div id="group-char-selector" style="display:flex; flex-direction:column; gap:6px;"></div>
                </div>
                <button class="submit-btn" style="background:#2563eb;" onclick="saveGroup()">Launch Group Chat</button>
            </div>

            <!-- Persona & Settings Form -->
            <div id="settings-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px; color: #ffffff;">User Persona & Settings</h3>
                
                <div class="form-group">
                    <label>Your Name</label>
                    <input type="text" id="user-name" placeholder="Your name">
                </div>

                <div class="form-group">
                    <label>Your Bio / Persona</label>
                    <textarea id="user-bio" placeholder="Describe yourself..."></textarea>
                </div>

                <button class="submit-btn" onclick="saveUserPersona()">Save Persona</button>

                <hr style="border-color:#27272a; margin: 16px 0;">

                <div class="form-group">
                    <label>Export Data Backup (.json)</label>
                    <button class="submit-btn" style="background:#27272a; margin-top:0;" onclick="exportData()"><i class="fa-solid fa-download"></i> Backup Data</button>
                </div>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Import Data</label>
                    <input type="file" id="import-file" accept=".json" onchange="importData(this)">
                </div>
            </div>
        </div>
    </div>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('aura_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let userPersona = JSON.parse(localStorage.getItem('aura_user') || '{"name":"User", "bio":""}');
        let activeContext = null;

        function toggleSidebar() { 
            let sb = document.getElementById('sidebar');
            sb.classList.toggle('open'); 
        }

        function toggleFullScreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => alert("Fullscreen blocked by browser!"));
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
            }
        }

        function saveState() {
            localStorage.setItem('aura_chars', JSON.stringify(characters));
            localStorage.setItem('aura_groups', JSON.stringify(groups));
            localStorage.setItem('aura_chats', JSON.stringify(chatHistories));
            localStorage.setItem('aura_user', JSON.stringify(userPersona));
            renderSidebar();
        }

        function previewImage(input) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = (e) => document.getElementById('avatar-img-preview').src = e.target.result;
                reader.readAsDataURL(input.files[0]);
            }
        }

        function openNewCharForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('char-id').value = '';
            document.getElementById('char-name').value = '';
            document.getElementById('char-rel').value = '';
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
            document.getElementById('char-rel').value = c.relationship || '';
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
            let fact = prompt("Pin memory for " + c.name + ":", c.memories || '');
            if(fact !== null) {
                c.memories = fact;
                saveState();
            }
        }

        function saveUserPersona() {
            userPersona.name = document.getElementById('user-name').value || 'User';
            userPersona.bio = document.getElementById('user-bio').value || '';
            saveState();
            alert('Persona saved!');
        }

        function showForm(formId) {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('top-actions').classList.add('hidden');
            document.getElementById(formId).classList.remove('hidden');

            document.getElementById('top-title').innerText = "✨ Aura";

            if(formId === 'settings-form') {
                document.getElementById('user-name').value = userPersona.name || '';
                document.getElementById('user-bio').value = userPersona.bio || '';
            }
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
                    <i class="fa-solid fa-users"></i>
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
                relationship: document.getElementById('char-rel').value,
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

        function renderGroupSelector() {
            let container = document.getElementById('group-char-selector');
            container.innerHTML = characters.map(c => `
                <label style="display:flex; align-items:center; gap:8px; background:#121215; padding:8px; border-radius:6px;">
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
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-actions').classList.remove('hidden');

            renderSidebar();
            
            let name = type === 'char' ? characters.find(c => c.id === id)?.name : groups.find(g => g.id === id)?.title;
            document.getElementById('top-title').innerText = name || 'Chat';

            renderMessages();
            document.getElementById('chat-input').focus();
        }

        function formatText(text) {
            return text.replace(/\*(.*?)\*/g, '<span class="action-text">*$1*</span>');
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];

            container.innerHTML = history.map((m, idx) => {
                let isUser = m.sender === 'You';
                let avatar = isUser ? 'https://api.dicebear.com/7.x/identicon/svg?seed=user' : m.avatar;
                return `
                    <div class="message ${isUser ? 'user':'ai'}">
                        <img class="avatar" src="${avatar}" />
                        <div>
                            <div class="sender-name">${m.sender}</div>
                            <div class="content">
                                ${formatText(m.text)}
                                <div><span class="edit-link" onclick="tweakMsg(${idx})">edit</span></div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        function tweakMsg(idx) {
            let history = chatHistories[activeContext.id];
            let newText = prompt("Tweak message:", history[idx].text);
            if(newText !== null) {
                history[idx].text = newText;
                saveState();
                renderMessages();
            }
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

            await new Promise(resolve => setTimeout(resolve, 800));

            let contentDiv = typingDiv.querySelector('.content');
            contentDiv.innerHTML = '';
            let words = fullText.split(' ');
            
            for (let i = 0; i < words.length; i++) {
                let currentSubText = words.slice(0, i + 1).join(' ');
                contentDiv.innerHTML = formatText(currentSubText) + `<div><span class="edit-link" onclick="tweakMsg(${chatHistories[activeContext.id].length})">edit</span></div>`;
                container.scrollTop = container.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 30));
            }

            chatHistories[activeContext.id].push({ sender, text: fullText, avatar });
            saveState();
            renderMessages();
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

        async function suggestUserMessage() {
            if(!activeContext) return;
            let input = document.getElementById('chat-input');
            input.placeholder = "Generating magic reply...";

            let payload = {
                contextId: activeContext.id,
                userPersona: userPersona,
                history: chatHistories[activeContext.id] || []
            };

            let res = await fetch('/api/suggest-reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let data = await res.json();
            if(data.suggestion) {
                input.value = data.suggestion;
            }
            input.placeholder = "Type a message...";
        }

        async function continueAiReply() {
            if(!activeContext) return;
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            fetchAIResponse(true);
        }

        async function fetchAIResponse(isContinue = false) {
            let payload = {
                type: activeContext.type,
                contextId: activeContext.id,
                userPersona: userPersona,
                isContinue: isContinue,
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

            if(history[history.length - 1].sender !== 'You') {
                history.pop();
                renderMessages();
                fetchAIResponse();
            }
        }

        function clearCurrentChat() {
            if(!activeContext || !confirm('Clear chat history?')) return;
            chatHistories[activeContext.id] = [];
            saveState();
            renderMessages();
        }

        function exportData() {
            let backupData = { characters, groups, chatHistories, userPersona };
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
                    if(imported.userPersona) userPersona = imported.userPersona;
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

@app.route("/api/suggest-reply", methods=["POST"])
def suggest_reply():
    data = request.json
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return jsonify({"suggestion": ""})

    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    user_info = data.get("userPersona", {})
    
    system_prompt = f"""
You are a ghostwriter for the user ({user_info.get('name', 'User')}).
User Bio: {user_info.get('bio', '')}
Based on the chat history, write a short, natural, in-character next message that the User would say.
Return ONLY the text/action response. Do not add quotes or explanations.
    """

    messages = [{"role": "system", "content": system_prompt}]
    for m in data.get("history", [])[-6:]:
        messages.append({"role": "user" if m["sender"] != "You" else "assistant", "content": f"{m['sender']}: {m['text']}"})

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }, headers=headers).json()
        
        suggestion = res["choices"][0]["message"]["content"]
        return jsonify({"suggestion": suggestion.strip('"')})
    except:
        return jsonify({"suggestion": "Hey! What's on your mind?"})

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

    user_info = data.get("userPersona", {})
    user_name = user_info.get("name", "User")
    user_bio = user_info.get("bio", "")

    responses = []

    if data["type"] == "char":
        c = data["character"]
        system_prompt = f"""
Name: {c['name']}
Relationship with User: {c.get('relationship', 'Friend')}
Appearance: {c.get('appearance', '')}
Backstory: {c.get('backstory', '')}
Directives: {c.get('directives', '')}
Key Memories / Current Context: {c.get('memories', '')}

User Profile:
Name: {user_name}
Bio: {user_bio}

Roleplay naturally as {c['name']}. Stay in character. Use asterisks for actions like *smiles and looks at you*.
        """
        if data.get("isContinue"):
            system_prompt += "\nUser pressed Continue. Extend your previous reply seamlessly."

        messages = [{"role": "system", "content": system_prompt}]
        for m in data["history"][-8:]:
            role = "user" if m["sender"] == "You" or m["sender"] == user_name else "assistant"
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
User: {user_name} ({user_bio})
Relationship: {char.get('relationship', 'Friend')}
Backstory: {char.get('backstory', '')}

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
