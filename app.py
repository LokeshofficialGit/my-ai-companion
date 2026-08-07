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
        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; position: relative; }
        .notification-dot { position: absolute; top: 2px; right: 2px; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; border: 1.5px solid var(--bg-surface); }
        .sidebar { position: absolute; top: 0; left: 0; width: 85%; height: 100%; background: var(--sidebar-bg); color: var(--sidebar-text); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 100; transform: translateX(-100%); pointer-events: none; }
        .sidebar.open { transform: translateX(0); pointer-events: auto; }
        .sidebar-header { padding: 14px 16px; font-size: 1.2rem; font-weight: 800; color: var(--accent-pink); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
        .sidebar-icon-btn { background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.88rem; }
        .nav-section { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .menu-category-btn { width: 100%; padding: 12px 14px; background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); border-radius: 10px; text-align: left; cursor: pointer; display: flex; align-items: center; justify-content: space-between; font-size: 0.92rem; font-weight: 600; }
        .menu-category-btn i.cat-icon { color: var(--accent-pink); font-size: 1rem; margin-right: 10px; }
        .menu-category-btn .arrow-icon { font-size: 0.8rem; color: var(--text-sub); transition: transform 0.2s ease; }
        .menu-category-btn.active .arrow-icon { transform: rotate(180deg); }
        .submenu-container { padding: 6px 0 6px 12px; display: flex; flex-direction: column; gap: 4px; }
        .item-btn { width: 100%; padding: 9px 12px; background: transparent; border: none; color: var(--text-sub); border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 0.88rem; }
        .item-btn:hover, .item-btn.active { background: var(--sidebar-btn-hover); color: var(--sidebar-text); }
        .item-btn img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
        .sub-create-btn { width: 100%; padding: 9px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .workspace { flex: 1; display: flex; flex-direction: column; height: calc(100% - 52px); position: relative; overflow: hidden; }
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .dash-logo { width: 80px; height: 80px; margin-bottom: 12px; filter: drop-shadow(0 0 10px rgba(236,72,153,0.4)); }
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
        
        /* Chat Image Box Non-Stretched */
        .chat-img-attachment { width: 100%; max-width: 240px; aspect-ratio: 3/4; object-fit: cover; border-radius: 10px; margin-top: 6px; cursor: pointer; border: 1px solid var(--border-color); display: block; }
        
        .action-text { color: var(--action-text); font-style: italic; font-weight: 500; }
        .bubble-controls { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
        .edit-link, .continue-bubble-btn { font-size: 0.68rem; color: var(--text-sub); text-decoration: underline; cursor: pointer; opacity: 0.65; transition: opacity 0.2s; }
        .edit-link:hover, .continue-bubble-btn:hover { opacity: 1; color: var(--accent-pink); }
        .input-area { padding: 10px 12px; border-top: 1px solid var(--border-color); background: var(--bg-surface); display: flex; gap: 8px; width: 100%; align-items: center; }
        .input-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
        .input-wrapper input { width: 100%; background: var(--bg-input); border: 1px solid var(--border-color); padding: 10px 38px 10px 12px; border-radius: 20px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .wand-inbox-btn { position: absolute; right: 10px; background: transparent; border: none; color: var(--accent-pink); opacity: 0.6; font-size: 0.95rem; cursor: pointer; padding: 4px; }
        .input-area button.send-btn { height: 38px; padding: 0 14px; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; }
        .tool-btn { background: var(--bg-input) !important; color: var(--accent-pink) !important; border: 1px solid var(--border-color) !important; padding: 0 10px !important; font-size: 0.95rem; border-radius: 10px !important; height: 38px; cursor: pointer; }
        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 4px; font-size: 0.8rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .form-group textarea { height: 75px; resize: vertical; }
        .avatar-edit-trigger { display: flex; align-items: center; gap: 12px; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 12px; cursor: pointer; }
        .avatar-thumb-wrapper { width: 54px; height: 54px; border-radius: 50%; overflow: hidden; border: 2px solid var(--accent-pink); flex-shrink: 0; background: var(--border-color); display: flex; justify-content: center; align-items: center; }
        .avatar-thumb-wrapper img { width: 100%; height: 100%; object-fit: cover; }
        
        /* Lightbox Fixes */
        .lightbox-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.92); backdrop-filter: blur(10px); z-index: 300; display: flex; flex-direction: column; justify-content: space-between; padding: 16px 12px; align-items: center; }
        .lightbox-img { width: auto; max-width: 95%; max-height: 68vh; object-fit: contain; border-radius: 14px; border: 1px solid #27272a; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
        .lightbox-actions { display: flex; gap: 8px; width: 100%; max-width: 360px; margin-bottom: 10px; justify-content: space-between; }
        .lightbox-btn { flex: 1; padding: 12px 6px; background: #121215; border: 1px solid #27272a; color: #ffffff; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 0.8rem; }
        .lightbox-btn.primary { background: linear-gradient(135deg, #9333ea, #ec4899); border: none; }
        .lightbox-btn.danger { background: #ef4444; border: none; color: white; }

        .gallery-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
        .gallery-item { position: relative; border-radius: 12px; overflow: hidden; aspect-ratio: 3/4; border: 1px solid var(--border-color); cursor: pointer; }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; }
        .hidden { display: none !important; }
        .aura-logo-svg { width: 28px; height: 28px; filter: drop-shadow(0 0 6px rgba(236,72,153,0.5)); }
    </style>
</head>
<body data-theme="dark">

    <svg class="hidden">
        <defs>
            <linearGradient id="roleGradVibrant" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#a855f7"/><stop offset="50%" stop-color="#ec4899"/><stop offset="100%" stop-color="#f43f5e"/>
            </linearGradient>
            <g id="aura-brand-icon">
                <path d="M 20 6 C 50 6, 75 30, 65 70 C 55 110, 20 120, 0 80 C -15 50 -10 6 20 6 Z" fill="url(#roleGradVibrant)" stroke="#ffffff" stroke-width="3" opacity="0.95"/>
                <path d="M 45 30 C 0 30, -20 60, -5 100 C 10 135, 50 140, 70 110 C 85 70, 75 30, 45 30 Z" fill="#ec4899" stroke="#9333ea" stroke-width="2.5" opacity="0.85"/>
                <path d="M 30 -5 Q 30 15 50 15 Q 30 15 30 35 Q 30 15 10 15 Q 30 15 30 -5 Z" fill="#ffffff"/>
            </g>
        </defs>
    </svg>

    <div class="app-container">
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span style="display:flex; align-items:center; gap:8px;">
                    <svg viewBox="-40 -20 140 180" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg> Aura
                </span>
                <div class="header-actions">
                    <button class="sidebar-icon-btn" onclick="toggleAppTheme()" id="sidebar-theme-btn"><i class="fa-solid fa-moon"></i></button>
                    <button class="sidebar-icon-btn" onclick="toggleFullScreen()"><i class="fa-solid fa-expand"></i></button>
                    <button class="sidebar-icon-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
                </div>
            </div>
            <div class="nav-section">
                <button class="menu-category-btn" onclick="goHome()"><span><i class="fa-solid fa-house cat-icon"></i> Home</span></button>
                <div>
                    <button class="menu-category-btn" onclick="toggleMenuCategory('chars-sub')"><span><i class="fa-solid fa-users-viewfinder cat-icon"></i> Characters</span><i class="fa-solid fa-chevron-down arrow-icon"></i></button>
                    <div class="submenu-container hidden" id="chars-sub">
                        <button class="sub-create-btn" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> New Character</button>
                        <div id="char-list"></div>
                    </div>
                </div>
                <div>
                    <button class="menu-category-btn" onclick="toggleMenuCategory('groups-sub')"><span><i class="fa-solid fa-people-group cat-icon"></i> Groups</span><i class="fa-solid fa-chevron-down arrow-icon"></i></button>
                    <div class="submenu-container hidden" id="groups-sub">
                        <button class="sub-create-btn blue" onclick="openNewGroupForm()"><i class="fa-solid fa-plus"></i> New Group Room</button>
                        <div id="group-list"></div>
                    </div>
                </div>
                <button class="menu-category-btn" onclick="showForm('settings-form')"><span><i class="fa-solid fa-sliders cat-icon"></i> Settings & Backup</span></button>
            </div>
        </div>

        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title">
                    <svg viewBox="-40 -20 140 180" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg> Aura
                </div>
            </div>
            <div style="display: flex; gap: 6px; align-items: center;">
                <div id="top-actions" class="hidden" style="display: flex; gap: 6px;">
                    <button class="icon-btn" id="gallery-btn" onclick="openCharacterGallery()">🖼️<span id="gallery-red-dot" class="notification-dot hidden"></span></button>
                    <button class="icon-btn" id="pin-mem-btn" onclick="openPinnedMemoryModal()"><i class="fa-solid fa-thumbtack"></i></button>
                    <button class="icon-btn" onclick="handleEditClick()"><i class="fa-solid fa-wrench"></i></button>
                    <button class="icon-btn" onclick="regenerateLastResponse()"><i class="fa-solid fa-rotate-right"></i></button>
                    <button class="icon-btn" onclick="clearCurrentChat()"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
        </div>

        <div class="workspace">
            <div id="dashboard-view" class="dashboard">
                <svg viewBox="-40 -20 140 180" class="dash-logo"><use href="#aura-brand-icon"/></svg>
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your personal AI companion & roleplay platform.</p>
                <div class="dash-card" onclick="openNewCharForm()"><i class="fa-solid fa-user-plus"></i><div><strong>Create AI Companion</strong><span>Custom backstory & relationship</span></div></div>
                <div class="dash-card" onclick="openNewGroupForm()"><i class="fa-solid fa-users"></i><div><strong>Create Group Room</strong><span>Chat with multiple characters</span></div></div>
                <div class="dash-card" onclick="showForm('settings-form')"><i class="fa-solid fa-sliders"></i><div><strong>Persona & Settings</strong><span>Edit profile & backup</span></div></div>
            </div>
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="tool-btn" onclick="openManualImageModal()">🤳</button>
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="Message..." onkeypress="if(event.key==='Enter') sendMsg()">
                        <button class="wand-inbox-btn" onclick="suggestUserMessage()">🪄</button>
                    </div>
                    <button class="send-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>
            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;" id="char-form-title">Create Companion</h3>
                <input type="hidden" id="char-id">
                <div class="form-group"><label>Name</label><input type="text" id="char-name"></div>
                <div class="form-group"><label>Relationship</label><input type="text" id="char-rel"></div>
                <div class="form-group"><label>Appearance</label><input type="text" id="char-app"></div>
                <div class="form-group"><label>Backstory</label><textarea id="char-backstory"></textarea></div>
                <button class="submit-btn" onclick="saveCharacter()">Save</button>
            </div>
            <div id="gallery-view" class="form-container hidden">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 id="gallery-char-title">Gallery</h3>
                    <button class="icon-btn" onclick="openChat('char', activeContext.id)"><i class="fa-solid fa-arrow-left"></i></button>
                </div>
                <div class="gallery-grid" id="gallery-grid-container"></div>
            </div>
        </div>

        <div id="image-gen-modal" class="avatar-modal-overlay hidden">
            <div class="avatar-modal-card">
                <h4 style="font-size:1rem;">Generate Photo</h4>
                <div class="input-wrapper" style="width:100%;"><input type="text" id="manual-prompt-input" placeholder="Keywords..."><button class="wand-inbox-btn" onclick="enhancePromptWithWand()">🪄</button></div>
                <button class="submit-btn" onclick="submitManualImageGen()">Generate Image</button>
                <button class="toggle-btn" style="color:#ffffff; margin-top:10px;" onclick="document.getElementById('image-gen-modal').classList.add('hidden')">Cancel</button>
            </div>
        </div>

        <!-- Lightbox Overlay with Fixed Delete Button -->
        <div id="lightbox-modal" class="lightbox-overlay hidden">
            <div style="width:100%; display:flex; justify-content:flex-end; padding:4px;">
                <button class="toggle-btn" style="color:#ffffff; font-size:1.8rem;" onclick="document.getElementById('lightbox-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <img id="lightbox-target-img" class="lightbox-img" src="">
            <div class="lightbox-actions">
                <button class="lightbox-btn" onclick="downloadLightboxImage()"><i class="fa-solid fa-download"></i> Save</button>
                <button class="lightbox-btn primary" onclick="regenerateLightboxImage()"><i class="fa-solid fa-rotate-right"></i> Retry</button>
                <button class="lightbox-btn danger" onclick="deleteCurrentGalleryImage()"><i class="fa-solid fa-trash"></i> Delete</button>
            </div>
        </div>
    </div>
    
    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('aura_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let galleries = JSON.parse(localStorage.getItem('aura_galleries') || '{}');
        let userPersona = JSON.parse(localStorage.getItem('aura_user') || '{"name":"User", "bio":""}');
        let activeContext = null;
        let activeLightboxImgUrl = ''; let activeLightboxPrompt = '';

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function goHome() { activeContext = null; document.getElementById('sidebar').classList.remove('open'); document.getElementById('dashboard-view').classList.remove('hidden'); document.getElementById('chat-view').classList.add('hidden'); document.getElementById('char-form').classList.add('hidden'); document.getElementById('gallery-view').classList.add('hidden'); document.getElementById('top-actions').classList.add('hidden'); }
        function saveState() { localStorage.setItem('aura_chars', JSON.stringify(characters)); localStorage.setItem('aura_groups', JSON.stringify(groups)); localStorage.setItem('aura_chats', JSON.stringify(chatHistories)); localStorage.setItem('aura_galleries', JSON.stringify(galleries)); renderSidebar(); }
        
        function saveToCharacterGallery(charId, imgUrl, promptText) {
            if(!galleries[charId]) galleries[charId] = [];
            galleries[charId].unshift({ id: 'img_' + Date.now(), url: imgUrl, prompt: promptText });
            saveState();
            document.getElementById('gallery-red-dot')?.classList.remove('hidden');
        }

        function openCharacterGallery() {
            if(!activeContext || activeContext.type !== 'char') return;
            document.getElementById('gallery-red-dot')?.classList.add('hidden');
            let container = document.getElementById('gallery-grid-container');
            let list = galleries[activeContext.id] || [];
            container.innerHTML = list.length === 0 ? '<div style="grid-column:span 2; padding:20px; text-align:center;">No photos yet.</div>' : list.map(item => `<div class="gallery-item" onclick="openLightbox('${item.url}', '${item.prompt}')"><img src="${item.url}" /></div>`).join('');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('gallery-view').classList.remove('hidden');
        }

        function openLightbox(imgUrl, promptText) {
            activeLightboxImgUrl = imgUrl; activeLightboxPrompt = promptText;
            document.getElementById('lightbox-target-img').src = imgUrl;
            document.getElementById('lightbox-modal').classList.remove('hidden');
        }

        function deleteCurrentGalleryImage() {
            if(!activeContext || !activeLightboxImgUrl) return;
            let charId = activeContext.id;
            if(galleries[charId]) {
                galleries[charId] = galleries[charId].filter(item => item.url !== activeLightboxImgUrl);
                saveState();
            }
            document.getElementById('lightbox-modal').classList.add('hidden');
            openCharacterGallery();
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

        async function submitManualImageGen() {
            let promptVal = document.getElementById('manual-prompt-input').value;
            document.getElementById('image-gen-modal').classList.add('hidden');
            let c = characters.find(item => item.id === activeContext.id);
            let res = await fetch('/api/generate-image', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({charId: activeContext.id, character: c, userPrompt: promptVal})});
            let data = await res.json();
            if(data.imageUrl) { typeWriterEffect(c.name, `*Here is the photo!*`, c.avatar, data.imageUrl, data.prompt); saveToCharacterGallery(activeContext.id, data.imageUrl, data.prompt); }
        }

        async function typeWriterEffect(sender, fullText, avatar, image = null, prompt = null) {
            let msg = { sender, text: fullText, avatar };
            if(image) { msg.image = image; msg.prompt = prompt; }
            chatHistories[activeContext.id].push(msg);
            saveState(); renderMessages();
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];
            container.innerHTML = history.map((m, idx) => {
                let isUser = m.sender === 'You';
                return `<div class="message ${isUser ? 'user':'ai'}">
                    <div class="content">
                        ${m.text}
                        ${m.image ? `<img src="${m.image}" class="chat-img-attachment" onclick="openLightbox('${m.image}', '${m.prompt}')" />` : ''}
                    </div>
                </div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        function renderSidebar() {
            document.getElementById('char-list').innerHTML = characters.map(c => `<button class="item-btn" onclick="openChat('char', '${c.id}')"><span>${c.name}</span></button>`).join('');
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('gallery-view').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-actions').classList.remove('hidden');
            renderMessages();
        }

        renderSidebar();
    </script>
</body>
</html>
"""

@app.route("/")
def home(): return render_template_string(HTML_CODE)

@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    data = request.json
    c = data.get("character", {})
    user_prompt = data.get("userPrompt", "candid photo")

    # Real human prompt + 768x1024 native non-stretched 4:3 aspect ratio
    raw_prompt = f"candid photograph of {c.get('name', 'person')}, {c.get('appearance', '')}, {user_prompt}, realistic skin texture, natural lighting, 35mm film detail, unedited"
    negative = "cartoon, anime, 3d render, doll, plastic skin, airbrushed, smooth, stretched, distorted proportions"

    encoded_p = urllib.parse.quote(raw_prompt)
    encoded_n = urllib.parse.quote(negative)

    # Fixed 768x1024 Dimensions
    image_url = f"https://image.pollinations.ai/prompt/{encoded_p}?negative={encoded_n}&width=768&height=1024&nologo=true&seed={random.randint(1000, 999999)}&model=turbo"

    return jsonify({"imageUrl": image_url, "prompt": user_prompt})

if __name__ == "__main__": app.run(host="0.0.0.0", port=10000)
