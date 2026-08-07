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
        body { background: #000000; color: #f4f4f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; width: 100vw; overflow: hidden; }

        /* App Mobile Wrapper Frame */
        .app-wrapper {
            width: 100%; max-width: 440px; height: 100vh; max-height: 920px;
            background: #09090b; display: flex; flex-direction: column; position: relative;
            overflow: hidden; box-shadow: 0 0 50px rgba(147, 51, 234, 0.15); border: 1px solid #27272a;
        }
        @media (min-width: 500px) { .app-wrapper { height: 94vh; border-radius: 24px; } }

        /* Sidebar Navigation Overlay */
        .sidebar {
            position: absolute; top: 0; left: 0; width: 85%; height: 100%;
            background: #121215; border-right: 1px solid #27272a; display: flex; flex-direction: column;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 100; transform: translateX(-100%);
        }
        .sidebar.open { transform: translateX(0); }
        .sidebar-header { padding: 18px; font-size: 1.3rem; font-weight: 800; color: #a855f7; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #18181b; }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch; }
        .section-title { font-size: 0.7rem; text-transform: uppercase; color: #71717a; padding: 8px; font-weight: 700; letter-spacing: 0.05em; }
        
        .item-btn { width: 100%; padding: 10px 12px; background: transparent; border: none; color: #a1a1aa; border-radius: 10px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 4px; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; }
        .item-btn:hover, .item-btn.active { background: #27272a; color: #fff; }
        .item-btn img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }

        .create-btn { width: calc(100% - 24px); margin: 6px 12px; padding: 11px; background: #9333ea; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.88rem; }
        .create-btn:hover { background: #7e22ce; }
        .sidebar-footer { padding: 14px; border-top: 1px solid #18181b; background: #121215; }

        /* Main Workspace Container */
        .main-content { flex: 1; display: flex; flex-direction: column; background: #09090b; height: 100%; width: 100%; overflow: hidden; position: relative; }
        .top-bar { height: 56px; min-height: 56px; border-bottom: 1px solid #1c1c21; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; background: #121215; z-index: 10; }
        .toggle-sidebar-btn { background: transparent; border: none; color: #f4f4f5; font-size: 1.2rem; cursor: pointer; padding: 6px; }
        .chat-title { font-weight: 700; font-size: 1.05rem; color: #ffffff; display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: #27272a; border: none; color: #e4e4e7; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
        .icon-btn:hover { background: #3f3f46; color: #fff; }

        /* High Visibility Welcome Screen Dashboard */
        .welcome-dashboard { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px; text-align: center; overflow-y: auto; }
        .welcome-logo { font-size: 3.5rem; color: #c084fc; margin-bottom: 12px; filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.4)); }
        .welcome-title { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-bottom: 8px; }
        .welcome-subtitle { font-size: 0.9rem; color: #a1a1aa; max-width: 280px; margin-bottom: 28px; line-height: 1.5; }
        .quick-card { width: 100%; max-width: 320px; background: #121215; border: 1px solid #27272a; padding: 14px 18px; border-radius: 14px; display: flex; align-items: center; gap: 14px; margin-bottom: 10px; cursor: pointer; text-align: left; transition: border 0.2s; }
        .quick-card:hover { border-color: #a855f7; }
        .quick-card i { font-size: 1.2rem; color: #a855f7; }
        .quick-card div strong { display: block; color: #f4f4f5; font-size: 0.95rem; }
        .quick-card div span { font-size: 0.78rem; color: #71717a; }

        /* Chat View Box */
        #chat-view { flex: 1; display: flex; flex-direction: column; height: calc(100% - 56px); overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 18px; -webkit-overflow-scrolling: touch; }
        .message { display: flex; gap: 10px; max-width: 90%; position: relative; group; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #27272a; flex-shrink: 0; }
        .message .content { background: #121215; border: 1px solid #27272a; padding: 12px 16px; border-radius: 16px; font-size: 0.92rem; line-height: 1.5; color: #f4f4f5; word-break: break-word; position: relative; }
        .message.user .content { background: #9333ea; border: none; color: white; border-bottom-right-radius: 4px; }
        .message.ai .content { border-bottom-left-radius: 4px; }
        .message .sender-name { font-size: 0.72rem; color: #a1a1aa; margin-bottom: 4px; font-weight: 600; }
        
        .action-text { color: #d8b4fe; font-style: italic; }
        .chat-break-line { width: 100%; border-bottom: 1px dashed #3f3f46; text-align: center; margin: 12px 0; font-size: 0.7rem; color: #71717a; }

        /* Message Options Button (...) */
        .msg-menu-btn { position: absolute; top: -8px; right: -8px; background: #27272a; border: 1px solid #3f3f46; color: #a1a1aa; width: 22px; height: 22px; border-radius: 50%; font-size: 0.65rem; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .message.user .msg-menu-btn { left: -8px; right: auto; }

        /* Typing Dots */
        .typing-dots { display: flex; gap: 5px; align-items: center; padding: 6px 0; }
        .typing-dots span { width: 6px; height: 6px; background: #c084fc; border-radius: 50%; animation: pulse 1.2s infinite ease-in-out; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }

        /* Input Area with Continue (>>) Button */
        .input-area { padding: 12px 16px; border-top: 1px solid #1c1c21; background: #121215; display: flex; gap: 8px; width: 100%; box-sizing: border-box; align-items: center; }
        .input-area input { flex: 1; background: #09090b; border: 1px solid #27272a; padding: 12px 14px; border-radius: 12px; color: white; outline: none; font-size: 0.9rem; }
        .input-area input:focus { border-color: #a855f7; }
        .input-area button { height: 42px; padding: 0 16px; background: #9333ea; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .continue-btn { background: #27272a !important; color: #a855f7 !important; border: 1px solid #3f3f46 !important; padding: 0 12px !important; font-size: 1rem; }

        /* Scrollable Form Containers */
        .form-container { padding: 20px; overflow-y: auto; flex: 1; width: 100%; -webkit-overflow-scrolling: touch; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 0.82rem; color: #a1a1aa; font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: #121215; border: 1px solid #27272a; padding: 12px; border-radius: 10px; color: white; outline: none; font-size: 0.9rem; }
        .form-group textarea { height: 80px; resize: vertical; }

        /* Avatar Upload Box with Scale Slider */
        .avatar-upload-box { display: flex; flex-direction: column; align-items: center; gap: 10px; background: #121215; padding: 16px; border-radius: 14px; border: 1px solid #27272a; }
        .avatar-preview-container { width: 90px; height: 90px; border-radius: 50%; overflow: hidden; border: 2px solid #a855f7; display: flex; justify-content: center; align-items: center; background: #27272a; }
        .avatar-preview-container img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.1s ease; }
        .avatar-controls { display: flex; gap: 10px; align-items: center; width: 100%; }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="app-wrapper">
        <!-- Sidebar Navigation -->
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

                <div class="section-title" style="margin-top: 14px;">Group Chats</div>
                <div id="group-list"></div>
            </div>

            <div class="sidebar-footer">
                <button class="item-btn" onclick="showForm('settings-form')"><i class="fa-solid fa-sliders"></i> User Persona & Settings</button>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="main-content">
            <!-- Top Navigation Bar -->
            <div class="top-bar">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="toggle-sidebar-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                    <div class="chat-title" id="current-title">Aura Workspace</div>
                </div>
                <!-- Chat Actions (Only Shown inside Chat) -->
                <div id="top-actions" class="hidden" style="display: flex; gap: 6px;">
                    <button class="icon-btn" onclick="openPinnedMemoryModal()" title="Pin Memory"><i class="fa-solid fa-thumbtack"></i></button>
                    <button class="icon-btn" onclick="editCurrentCharacter()" title="Edit Character"><i class="fa-solid fa-wrench"></i></button>
                    <button class="icon-btn" onclick="regenerateLastResponse()" title="Regenerate"><i class="fa-solid fa-rotate-right"></i></button>
                    <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>

            <!-- Welcome Screen Dashboard -->
            <div id="welcome-view" class="welcome-dashboard">
                <div class="welcome-logo"><i class="fa-solid fa-sparkles"></i></div>
                <h2 class="welcome-title">Welcome to Aura</h2>
                <p class="welcome-subtitle">Your personal AI companion platform. Pick a companion or create a new story.</p>
                
                <div class="quick-card" onclick="openNewCharForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    <div>
                        <strong>Create AI Companion</strong>
                        <span>Custom backstory, persona & avatar</span>
                    </div>
                </div>

                <div class="quick-card" onclick="showForm('group-form')">
                    <i class="fa-solid fa-people-group"></i>
                    <div>
                        <strong>Create Group Room</strong>
                        <span>Chat with multiple characters at once</span>
                    </div>
                </div>
            </div>

            <!-- Active Chat View -->
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="continue-btn" onclick="continueAiReply()" title="Continue AI Reply"><strong>&gt;&gt;</strong></button>
                    <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    <button onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <!-- Create / Edit Character Form -->
            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 18px; font-weight: 700; color: #ffffff;" id="char-form-title">Create Companion</h3>
                <input type="hidden" id="char-id">
                
                <div class="form-group">
                    <label>Avatar Picture</label>
                    <div class="avatar-upload-box">
                        <div class="avatar-preview-container">
                            <img id="avatar-img-preview" src="https://api.dicebear.com/7.x/bottts/svg?seed=default">
                        </div>
                        <input type="file" id="char-avatar-file" accept="image/*" onchange="previewImage(this)">
                        <div class="avatar-controls">
                            <label style="font-size:0.75rem;">Scale:</label>
                            <input type="range" id="avatar-scale" min="1" max="2" step="0.05" value="1" oninput="scaleAvatar(this.value)">
                            <button type="button" onclick="removeAvatar()" style="padding: 4px 10px; background: #ef4444; border:none; color:white; border-radius:6px; font-size:0.75rem; cursor:pointer;">Remove</button>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="char-name" placeholder="e.g. Maya">
                </div>

                <div class="form-group">
                    <label>Relationship with You (Persona Connection)</label>
                    <input type="text" id="char-rel" placeholder="e.g. Best Friend, Girlfriend, Rival, Mentor">
                </div>

                <div class="form-group">
                    <label>Appearance Description</label>
                    <input type="text" id="char-app" placeholder="e.g. Tall, blue eyes, wears leather jacket">
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

            <!-- Create Group Chat Form -->
            <div id="group-form" class="form-container hidden">
                <h3 style="margin-bottom: 18px; font-weight: 700; color: #ffffff;">Create Group Chat</h3>
                <div class="form-group">
                    <label>Group Title</label>
                    <input type="text" id="group-title" placeholder="e.g. Squad Chat">
                </div>
                <div class="form-group">
                    <label>Select Characters for Group</label>
                    <div id="group-char-selector" style="display:flex; flex-direction:column; gap:8px;"></div>
                </div>
                <button class="create-btn" style="background:#2563eb; margin:0; width:100%;" onclick="saveGroup()">Launch Group Chat</button>
            </div>

            <!-- User Persona & Backup Settings Form -->
            <div id="settings-form" class="form-container hidden">
                <h3 style="margin-bottom: 18px; color: #ffffff;">User Persona & Backup</h3>
                
                <div class="form-group">
                    <label>Your Name</label>
                    <input type="text" id="user-name" placeholder="Your name (e.g. Alex)">
                </div>

                <div class="form-group">
                    <label>Your Bio / Persona</label>
                    <textarea id="user-bio" placeholder="Describe yourself (e.g. 24 year old artist, cheerful personality)"></textarea>
                </div>

                <button class="create-btn" style="margin-bottom: 24px; width: 100%;" onclick="saveUserPersona()">Save Persona</button>

                <hr style="border-color: #27272a; margin-bottom: 20px;">

                <div class="form-group">
                    <label>Export Companion Data (.json)</label>
                    <button class="create-btn" style="margin:0; width:100%; background: #27272a;" onclick="exportData()"><i class="fa-solid fa-download"></i> Download Backup</button>
                </div>
                <div class="form-group" style="margin-top: 16px;">
                    <label>Import Companion Data</label>
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

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }

        function saveState() {
            localStorage.setItem('aura_chars', JSON.stringify(characters));
            localStorage.setItem('aura_groups', JSON.stringify(groups));
            localStorage.setItem('aura_chats', JSON.stringify(chatHistories));
            localStorage.setItem('aura_user', JSON.stringify(userPersona));
            renderSidebar();
        }

        // Avatar Image Controls
        function previewImage(input) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = (e) => document.getElementById('avatar-img-preview').src = e.target.result;
                reader.readAsDataURL(input.files[0]);
            }
        }
        function scaleAvatar(val) {
            document.getElementById('avatar-img-preview').style.transform = `scale(${val})`;
        }
        function removeAvatar() {
            document.getElementById('avatar-img-preview').src = 'https://api.dicebear.com/7.x/bottts/svg?seed=' + Date.now();
            document.getElementById('avatar-scale').value = 1;
            document.getElementById('avatar-img-preview').style.transform = 'scale(1)';
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
            removeAvatar();
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
            let fact = prompt("Pin temporary memory context for " + c.name + ":", c.memories || '');
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
            document.getElementById('welcome-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('top-actions').classList.add('hidden');
            document.getElementById(formId).classList.remove('hidden');

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
                    <i class="fa-solid fa-users" style="margin-left: 2px;"></i>
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
                <label style="display:flex; align-items:center; gap:8px; background:#121215; padding:10px; border-radius:8px;">
                    <input type="checkbox" value="${c.id}" class="group-char-checkbox" style="width:auto;">
                    <img src="${c.avatar}" style="width:26px; height:26px; border-radius:50%;"/>
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
            document.getElementById('welcome-view').classList.add('hidden');
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
                                <button class="msg-menu-btn" onclick="tweakMsg(${idx})" title="Edit Message"><i class="fa-solid fa-pen"></i></button>
                                ${formatText(m.text)}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        function tweakMsg(idx) {
            let history = chatHistories[activeContext.id];
            let newText = prompt("Tweak/Edit message:", history[idx].text);
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

            await new Promise(resolve => setTimeout(resolve, 1000));

            let contentDiv = typingDiv.querySelector('.content');
            contentDiv.innerHTML = '';
            let words = fullText.split(' ');
            
            for (let i = 0; i < words.length; i++) {
                let currentSubText = words.slice(0, i + 1).join(' ');
                contentDiv.innerHTML = formatText(currentSubText);
                container.scrollTop = container.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 40));
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
            system_prompt += "\nUser pressed Continue. Extend your previous reply seamlessly without repeating yourself."

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
Other Members in Room: {', '.join([m['name'] for m in members if m['name'] != char['name']])}

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
