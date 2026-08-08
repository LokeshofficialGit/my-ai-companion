import os
import requests
import json
import base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Kio. - Intelligence with a heart</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0a0b10;
            --bg-surface: #12131c;
            --bg-surface-solid: #161824;
            --bg-input: #1a1c29;
            --border-color: rgba(236, 72, 153, 0.15);
            --text-main: #f4f4f5;
            --text-sub: #a1a1aa;
            --accent-purple: #a855f7;
            --accent-pink: #ec4899;
            --action-text: #f472b6;
            --user-msg-bg: linear-gradient(135deg, #9333ea, #ec4899);
            --ai-msg-bg: #161824;
            --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            
            --sidebar-bg: #0a0b10;
            --sidebar-border: rgba(236, 72, 153, 0.12);
            --sidebar-text: #f4f4f5;
            --sidebar-btn-bg: #12131c;
            --sidebar-btn-hover: #1c1e2d;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        
        html, body { 
            height: 100dvh; 
            width: 100vw; 
            background: #000000; 
            color: var(--text-main); 
            overflow: hidden; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
        }

        .app-container {
            width: 100%; 
            max-width: 440px; 
            height: 100dvh;
            background: var(--bg-main); 
            display: flex; 
            flex-direction: column; 
            position: relative;
            overflow: hidden; 
            border: 1px solid var(--border-color);
            box-shadow: 0 0 40px rgba(168, 85, 247, 0.08);
        }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }

        button, .dash-card, .menu-category-btn, .item-btn, .avatar-edit-trigger {
            transition: transform 0.15s ease, background 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
        }
        button:active, .dash-card:active, .menu-category-btn:active, .item-btn:active, .avatar-edit-trigger:active {
            transform: scale(0.96) !important;
        }

        /* Top Bar */
        .top-bar { 
            height: 56px; 
            min-height: 56px; 
            background: var(--bg-surface); 
            border-bottom: none;
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 0 12px; 
            z-index: 10; 
            box-shadow: 0 4px 20px rgba(168, 85, 247, 0.12);
        }
        
        .toggle-btn { background: transparent; border: none; color: var(--text-main); font-size: 1.25rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .top-title { font-weight: 700; font-size: 0.9rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        
        .header-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--accent-pink);
            cursor: pointer;
            flex-shrink: 0;
            background: var(--border-color);
        }
        .header-avatar:hover { opacity: 0.85; }

        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; flex-shrink: 0; margin-left: 3px; }

        /* Sidebar Drawer */
        .sidebar { 
            position: absolute; top: 0; left: 0; width: 85%; height: 100%; 
            background: var(--sidebar-bg); 
            color: var(--sidebar-text);
            border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; 
            transition: transform 0.3s ease; z-index: 100; transform: translateX(-100%); pointer-events: none; 
        }
        .sidebar.open { transform: translateX(0); pointer-events: auto; }
        .sidebar-header { padding: 16px; font-size: 1.3rem; font-weight: 900; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
        .header-actions { display: flex; align-items: center; gap: 6px; }
        .sidebar-icon-btn { background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.88rem; }

        .nav-section { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }

        .menu-category-btn { width: 100%; padding: 12px 14px; background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); border-radius: 12px; text-align: left; cursor: pointer; display: flex; align-items: center; justify-content: space-between; font-size: 0.92rem; font-weight: 600; }
        .menu-category-btn i.cat-icon { color: var(--accent-pink); font-size: 1rem; margin-right: 10px; }
        .menu-category-btn .arrow-icon { font-size: 0.8rem; color: var(--text-sub); transition: transform 0.2s ease; }
        .menu-category-btn.active .arrow-icon { transform: rotate(180deg); }

        .submenu-container { padding: 6px 0 6px 12px; display: flex; flex-direction: column; gap: 4px; }
        
        .item-btn { width: 100%; padding: 9px 12px; background: transparent; border: none; color: var(--text-sub); border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 0.88rem; }
        .item-btn:hover, .item-btn.active { background: var(--sidebar-btn-hover); color: var(--sidebar-text); }
        .item-btn img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }

        .sub-create-btn { width: 100%; padding: 10px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 4px; }
        .sub-create-btn.blue { background: linear-gradient(135deg, #2563eb, #3b82f6); }

        .workspace { flex: 1; display: flex; flex-direction: column; height: 100%; position: relative; overflow: hidden; }

        /* Dashboard Layout */
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
        
        .brand-name {
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #a855f7, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
            filter: drop-shadow(0 0 16px rgba(236,72,153,0.4));
        }

        .dash-title { font-size: 1.3rem; font-weight: 800; color: var(--text-main); margin-bottom: 4px; }
        .dash-sub { font-size: 0.82rem; color: var(--text-sub); text-align: center; margin-bottom: 24px; font-style: italic; letter-spacing: 0.3px; }
        
        .dash-card { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 16px; border-radius: 16px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; box-shadow: var(--card-shadow); }
        .dash-card i { font-size: 1.3rem; color: var(--accent-pink); }
        .dash-card strong { display: block; color: var(--text-main); font-size: 0.95rem; }
        .dash-card span { font-size: 0.78rem; color: var(--text-sub); }

        #chat-view { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; -webkit-overflow-scrolling: touch; }
        
        /* Message Bubbles */
        .message { display: flex; flex-direction: column; max-width: 88%; position: relative; will-change: transform; align-self: flex-start; }
        .message.user { align-self: flex-end; }
        .message .content { background: var(--ai-msg-bg); border: 1px solid var(--border-color); padding: 12px 14px; border-radius: 16px; font-size: 0.9rem; line-height: 1.45; color: var(--text-main); word-break: break-word; box-shadow: var(--card-shadow); border-bottom-left-radius: 4px; }
        .message.user .content { background: var(--user-msg-bg); border: none; color: #ffffff; border-bottom-left-radius: 16px; border-bottom-right-radius: 4px; }
        .message .sender-name { font-size: 0.72rem; color: var(--text-sub); margin-bottom: 3px; font-weight: 600; padding-left: 2px; }
        .message.user .sender-name { text-align: right; padding-right: 2px; }
        
        .action-text { color: var(--action-text); font-style: italic; font-weight: 500; }
        
        .bubble-controls { display: flex; align-items: center; gap: 12px; margin-top: 6px; }
        .bubble-btn-icon { font-size: 0.75rem; color: var(--text-sub); opacity: 0.45; cursor: pointer; transition: opacity 0.2s, color 0.2s; }
        .bubble-btn-icon:hover { opacity: 1; color: var(--accent-pink); }

        .typing-indicator { display: flex; align-items: center; gap: 4px; padding: 4px 8px; font-style: italic; font-size: 0.78rem; color: var(--accent-pink); }

        /* Input Area */
        .input-area { 
            padding: 12px; 
            border-top: 1px solid var(--border-color); 
            background: var(--bg-surface); 
            display: flex; 
            gap: 8px; 
            width: 100%; 
            align-items: center; 
        }
        .input-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
        .input-wrapper input { 
            width: 100%; 
            background: var(--bg-input); 
            border: 1px solid var(--border-color); 
            padding: 11px 40px 11px 14px; 
            border-radius: 24px; 
            color: var(--text-main); 
            outline: none; 
            font-size: 0.9rem; 
        }
        .input-wrapper input:focus {
            border-color: var(--accent-pink);
            box-shadow: 0 0 10px rgba(236, 72, 153, 0.2);
        }

        .wand-inbox-btn { 
            position: absolute; right: 12px; background: transparent; border: none; 
            color: var(--accent-pink); opacity: 0.7; font-size: 1rem; cursor: pointer; 
            display: flex; align-items: center; justify-content: center; 
        }
        .wand-inbox-btn:hover { opacity: 1; }

        .input-area button.send-btn { height: 42px; padding: 0 16px; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; border: none; border-radius: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .tool-btn { background: var(--bg-input) !important; color: var(--accent-pink) !important; border: 1px solid var(--border-color) !important; padding: 0 10px !important; font-size: 0.75rem; font-weight: 700; border-radius: 12px !important; height: 42px; cursor: pointer; display: flex; align-items: center; justify-content: center; min-width: 45px; }

        /* Prompt Popup Modal */
        .prompt-modal-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.8); z-index: 300; display: flex; flex-direction: column;
            justify-content: flex-end; padding: 0; animation: fadeIn 0.2s ease;
        }
        .prompt-modal-card {
            width: 100%; background: var(--bg-surface-solid); border-top: 1px solid var(--border-color);
            border-top-left-radius: 24px; border-top-right-radius: 24px; padding: 20px;
            display: flex; flex-direction: column; gap: 14px; color: var(--text-main);
            box-shadow: 0 -10px 30px rgba(0,0,0,0.5); max-height: 70vh;
        }
        .prompt-textarea {
            width: 100%; height: 130px; background: var(--bg-input); border: 1px solid var(--border-color);
            border-radius: 12px; padding: 12px; color: var(--text-main); font-size: 0.88rem; resize: none; outline: none;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .empty-chat-placeholder {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100%; text-align: center; color: var(--text-sub); padding: 20px; opacity: 0.75;
        }
        .empty-chat-placeholder i { font-size: 2.5rem; color: var(--accent-pink); margin-bottom: 12px; }

        .form-header-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
        .form-back-btn { background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; }

        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 0.82rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface-solid); border: 1px solid var(--border-color); padding: 10px 12px; border-radius: 10px; color: var(--text-main); outline: none; font-size: 0.9rem; }
        .form-group textarea { height: 75px; resize: vertical; }

        .avatar-edit-trigger {
            display: flex; align-items: center; gap: 12px; background: var(--bg-surface-solid);
            border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 14px; cursor: pointer;
        }
        .avatar-thumb-wrapper {
            width: 52px; height: 52px; border-radius: 50%; overflow: hidden;
            border: 2px solid var(--accent-pink); flex-shrink: 0; background: var(--border-color);
            display: flex; justify-content: center; align-items: center;
        }
        .avatar-thumb-wrapper img { width: 100%; height: 100%; object-fit: cover; }

        .avatar-modal-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85); z-index: 200; display: flex; flex-direction: column;
            align-items: center; justify-content: center; padding: 16px;
        }
        .avatar-modal-card {
            width: 100%; max-width: 360px; background: var(--bg-surface-solid);
            border: 1px solid var(--border-color); border-radius: 20px; padding: 16px;
            display: flex; flex-direction: column; align-items: center; gap: 14px; color: var(--text-main);
        }
        .cropper-container-box {
            width: 100%; height: 260px; background: #000; border-radius: 12px;
            overflow: hidden; border: 1px solid var(--border-color); position: relative;
        }

        .modal-card {
            width: 100%; max-width: 340px; background: var(--bg-surface-solid);
            border: 1px solid var(--border-color); border-radius: 20px; padding: 20px;
            display: flex; flex-direction: column; gap: 12px; max-height: 80vh; overflow-y: auto; color: var(--text-main);
        }

        .submit-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; font-size: 0.92rem; margin-top: 8px; }
        .delete-btn { background: #ef4444 !important; margin-top: 10px; }

        .memory-tag-chip {
            display: flex; align-items: center; justify-content: space-between;
            background: var(--bg-input); border: 1px solid var(--border-color);
            padding: 8px 12px; border-radius: 10px; font-size: 0.82rem; color: var(--text-main); margin-bottom: 6px;
        }
        .memory-tag-chip i { cursor: pointer; color: #ef4444; opacity: 0.8; }

        .hidden { display: none !important; }
    </style>
</head>
<body data-theme="dark">

    <div class="app-container">
        <!-- Sidebar Navigation -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span class="brand-name" style="font-size: 1.2rem; margin:0;">Kio.</span>
                <div class="header-actions">
                    <button class="sidebar-icon-btn" onclick="toggleFullScreen()"><i class="fa-solid fa-expand"></i></button>
                    <button class="sidebar-icon-btn" onclick="toggleSidebar()"><i class="fa-solid fa-xmark"></i></button>
                </div>
            </div>

            <div class="nav-section">
                <button class="menu-category-btn" onclick="goHome()">
                    <span><i class="fa-solid fa-house cat-icon"></i> Home</span>
                </button>

                <div>
                    <button class="menu-category-btn" onclick="toggleMenuCategory('chars-sub')">
                        <span><i class="fa-solid fa-users-viewfinder cat-icon"></i> Characters</span>
                        <i class="fa-solid fa-chevron-down arrow-icon"></i>
                    </button>
                    <div class="submenu-container hidden" id="chars-sub">
                        <button class="sub-create-btn" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> New Character</button>
                        <div id="char-list"></div>
                    </div>
                </div>

                <div>
                    <button class="menu-category-btn" onclick="toggleMenuCategory('groups-sub')">
                        <span><i class="fa-solid fa-people-group cat-icon"></i> Groups</span>
                        <i class="fa-solid fa-chevron-down arrow-icon"></i>
                    </button>
                    <div class="submenu-container hidden" id="groups-sub">
                        <button class="sub-create-btn blue" onclick="openNewGroupForm()"><i class="fa-solid fa-plus"></i> New Group Room</button>
                        <div id="group-list"></div>
                    </div>
                </div>

                <button class="menu-category-btn" onclick="showForm('settings-form')">
                    <span><i class="fa-solid fa-sliders cat-icon"></i> Settings & Backup</span>
                </button>
            </div>
        </div>

        <!-- Top Bar -->
        <div class="top-bar hidden" id="top-bar">
            <div style="display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title"></div>
            </div>
            
            <div style="display: flex; gap: 3px; align-items: center; flex-shrink: 0;" id="top-actions">
                <button class="icon-btn" id="pin-mem-btn" onclick="openPinnedMemoryModal()" title="Pin Memory"><i class="fa-solid fa-location-dot"></i></button>
                <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-comment-slash"></i></button>
            </div>
        </div>

        <!-- Workspace -->
        <div class="workspace">
            <!-- Dashboard View -->
            <div id="dashboard-view" class="dashboard">
                <div style="position: absolute; top: 16px; left: 16px;">
                    <button class="icon-btn" onclick="toggleSidebar()" style="width:38px; height:38px; font-size:1rem;"><i class="fa-solid fa-bars"></i></button>
                </div>
                
                <div class="brand-name">Kio.</div>
                
                <h2 class="dash-title">Welcome to Kio.</h2>
                <p class="dash-sub">Intelligence with a heart.</p>
                
                <div class="dash-card" onclick="openNewCharForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    <div>
                        <strong>Create AI Companion</strong>
                        <span>Custom backstory & bonded persona</span>
                    </div>
                </div>

                <div class="dash-card" onclick="openNewGroupForm()">
                    <i class="fa-solid fa-users"></i>
                    <div>
                        <strong>Create Group Room</strong>
                        <span>Chat with multi-characters</span>
                    </div>
                </div>

                <div class="dash-card" onclick="showForm('settings-form')">
                    <i class="fa-solid fa-sliders"></i>
                    <div>
                        <strong>Persona & Settings</strong>
                        <span>Edit profile, memories & data backup</span>
                    </div>
                </div>
            </div>

            <!-- Active Chat View -->
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="tool-btn" id="gp-btn" onclick="generateImagePrompt()" title="Generate 9:16 Image Prompt">GP</button>
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                        <button class="wand-inbox-btn" onclick="suggestUserMessage()" title="Magic Reply">🪄</button>
                    </div>
                    <button class="send-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <!-- Character Form -->
            <div id="char-form" class="form-container hidden">
                <div class="form-header-bar">
                    <button class="form-back-btn" onclick="smartFormBack()"><i class="fa-solid fa-chevron-left"></i> Back</button>
                    <h3 style="font-size:1.1rem; font-weight:800;" id="char-form-title">Create Companion</h3>
                </div>
                <input type="hidden" id="char-id">
                
                <div class="form-group">
                    <label>Avatar Picture</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('char')">
                        <div class="avatar-thumb-wrapper">
                            <img id="avatar-img-preview" src="https://api.dicebear.com/7.x/bottts/svg?seed=default">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Pinch & Drag Crop Avatar</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to configure</span>
                        </div>
                    </div>
                </div>

                <div class="form-group"><label>Name</label><input type="text" id="char-name" placeholder="e.g. Maya"></div>
                <div class="form-group"><label>Relationship with You</label><input type="text" id="char-rel" placeholder="e.g. Best Friend"></div>
                <div class="form-group"><label>Appearance</label><input type="text" id="char-app" placeholder="e.g. Cute, brown eyes"></div>
                <div class="form-group"><label>Backstory</label><textarea id="char-backstory"></textarea></div>
                <div class="form-group"><label>Response Directives</label><textarea id="char-directives"></textarea></div>
                <div class="form-group"><label>Key Memories</label><textarea id="char-memories"></textarea></div>

                <button class="submit-btn" onclick="saveCharacter()">Save Character</button>
                <button class="submit-btn delete-btn" id="char-delete-btn" onclick="deleteCurrentCharacter()">Delete Companion</button>
            </div>

            <!-- Group Form -->
            <div id="group-form" class="form-container hidden">
                <div class="form-header-bar">
                    <button class="form-back-btn" onclick="smartFormBack()"><i class="fa-solid fa-chevron-left"></i> Back</button>
                    <h3 style="font-size:1.1rem; font-weight:800;" id="group-form-title">Create Group Chat</h3>
                </div>
                <input type="hidden" id="group-id">

                <div class="form-group">
                    <label>Group Icon</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('group')">
                        <div class="avatar-thumb-wrapper">
                            <img id="group-avatar-preview" src="https://api.dicebear.com/7.x/shapes/svg?seed=group">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Pinch & Drag Crop Icon</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to crop</span>
                        </div>
                    </div>
                </div>

                <div class="form-group"><label>Group Name</label><input type="text" id="group-title" placeholder="e.g. Squad"></div>
                <div class="form-group"><label>Group Context / Setting</label><textarea id="group-context"></textarea></div>
                <div class="form-group"><label>Group Directives</label><textarea id="group-directives"></textarea></div>
                <div class="form-group"><label>Group Members</label><div id="group-char-selector"></div></div>

                <button class="submit-btn" style="background:#2563eb;" onclick="saveGroup()">Save Group Room</button>
                <button class="submit-btn delete-btn" id="group-delete-btn" onclick="deleteCurrentGroup()">Delete Group</button>
            </div>

            <!-- Settings Form -->
            <div id="settings-form" class="form-container hidden">
                <div class="form-header-bar">
                    <button class="form-back-btn" onclick="smartFormBack()"><i class="fa-solid fa-chevron-left"></i> Back</button>
                    <h3 style="font-size:1.1rem; font-weight:800;">Persona & Settings</h3>
                </div>

                <div class="form-group">
                    <label>Your Avatar Picture</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('user')">
                        <div class="avatar-thumb-wrapper">
                            <img id="user-avatar-preview" src="https://api.dicebear.com/7.x/identicon/svg?seed=user">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Crop Your Avatar</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to adjust photo</span>
                        </div>
                    </div>
                </div>

                <div class="form-group"><label>Your Name</label><input type="text" id="user-name"></div>
                <div class="form-group"><label>Your Bio / Persona</label><textarea id="user-bio"></textarea></div>
                <button class="submit-btn" onclick="saveUserPersona()">Save Persona</button>

                <hr style="border-color:var(--border-color); margin: 16px 0;">

                <div class="form-group">
                    <label style="color:var(--accent-pink); display:flex; align-items:center; gap:6px;">
                        <i class="fa-solid fa-brain"></i> AI Auto-Remembered Facts
                    </label>
                    <div id="user-memories-list" style="margin-top:8px;"></div>
                </div>

                <hr style="border-color:var(--border-color); margin: 16px 0;">

                <div class="form-group">
                    <label>Data Backup & Export</label>
                    <button class="submit-btn" style="background:var(--bg-surface-solid); border:1px solid var(--border-color); color:var(--text-main); margin-top:0;" onclick="openBackupOptionsModal()"><i class="fa-solid fa-download"></i> Selective Backup Data</button>
                </div>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Import Data File (.json)</label>
                    <input type="file" id="import-file" accept=".json" onchange="importData(this)">
                </div>
            </div>
        </div>

        <!-- Prompt Modal -->
        <div id="prompt-modal" class="prompt-modal-overlay hidden">
            <div class="prompt-modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:0.95rem; color:var(--accent-pink);"><i class="fa-solid fa-wand-magic-sparkles"></i> 9:16 Image Generation Prompt</h4>
                    <button class="toggle-btn" onclick="document.getElementById('prompt-modal').classList.add('hidden')" style="font-size:1.1rem;"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <textarea id="prompt-output-box" class="prompt-textarea" readonly></textarea>
                <div style="display:flex; gap:8px; width:100%;">
                    <button class="sub-create-btn" style="background:#27272a; flex:1;" onclick="document.getElementById('prompt-modal').classList.add('hidden')">Close</button>
                    <button class="sub-create-btn" style="flex:1;" onclick="copyPromptText()"><i class="fa-solid fa-copy"></i> Copy Prompt</button>
                </div>
            </div>
        </div>

        <!-- Cropper Modal -->
        <div id="cropper-modal" class="avatar-modal-overlay hidden" style="justify-content:center;">
            <div class="avatar-modal-card" style="border-top-left-radius:20px; border-top-right-radius:20px;">
                <div style="width:100%; display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:1rem;">Crop Avatar</h4>
                    <button class="toggle-btn" onclick="closeCropperModal()" style="font-size:1.1rem;"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="cropper-container-box"><img id="cropper-target-img" src="" style="max-width:100%;"></div>
                <input type="file" id="cropper-file-input" accept="image/*" class="hidden" onchange="loadNewCropperImage(this)">
                <div style="display:flex; gap:8px; width:100%;">
                    <button class="sub-create-btn" style="background:#27272a; flex:1;" onclick="closeCropperModal()">Cancel</button>
                    <button class="sub-create-btn" style="background:#3f3f46; flex:1;" onclick="document.getElementById('cropper-file-input').click()">Upload</button>
                    <button class="sub-create-btn" style="flex:1;" onclick="applyCroppedAvatar()">Done</button>
                </div>
            </div>
        </div>

        <!-- Backup Modal -->
        <div id="backup-modal" class="avatar-modal-overlay hidden" style="justify-content:center;">
            <div class="modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:1rem;">Select Data to Backup</h4>
                    <button class="toggle-btn" onclick="document.getElementById('backup-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <button class="sub-create-btn" style="padding:10px;" onclick="exportFullData()"><i class="fa-solid fa-box-archive"></i> Export Entire App Data</button>
                <hr style="border-color:var(--border-color); margin: 4px 0;">
                <div style="font-size:0.75rem; color:var(--text-sub); font-weight:700;">INDIVIDUAL COMPANIONS</div>
                <div id="backup-char-list" style="display:flex; flex-direction:column; gap:6px;"></div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('aura_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let userPersona = JSON.parse(localStorage.getItem('aura_user') || '{"name":"User", "bio":"", "avatar":"https://api.dicebear.com/7.x/identicon/svg?seed=user", "memories":[]}');
        if (!userPersona.memories) userPersona.memories = [];
        
        let activeContext = null;
        let cropperInstance = null;
        let currentEditingAvatarType = null;
        let currentAiProvider = 'groq';

        async function generateImagePrompt() {
            if(!activeContext || activeContext.type !== 'char') {
                alert('GP feature is currently available for single character chats!');
                return;
            }

            let btn = document.getElementById('gp-btn');
            let origText = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

            let history = chatHistories[activeContext.id] || [];
            let character = characters.find(c => c.id === activeContext.id);

            try {
                let res = await fetch('/api/generate-image-prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ character, history })
                });
                let data = await res.json();
                
                document.getElementById('prompt-output-box').value = data.prompt || 'Failed to generate prompt.';
                document.getElementById('prompt-modal').classList.remove('hidden');
            } catch(e) {
                alert('Error generating prompt.');
            } finally {
                btn.innerHTML = origText;
            }
        }

        function copyPromptText() {
            let box = document.getElementById('prompt-output-box');
            box.select();
            navigator.clipboard.writeText(box.value);
            alert('Prompt copied to clipboard!');
        }

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function toggleMenuCategory(subId) { document.getElementById(subId).classList.toggle('hidden'); }
        function toggleFullScreen() { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }

        function smartFormBack() {
            if (activeContext) openChat(activeContext.type, activeContext.id);
            else goHome();
        }

        function goHome() {
            activeContext = null;
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
        }

        function saveState() {
            localStorage.setItem('aura_chars', JSON.stringify(characters));
            localStorage.setItem('aura_groups', JSON.stringify(groups));
            localStorage.setItem('aura_chats', JSON.stringify(chatHistories));
            localStorage.setItem('aura_user', JSON.stringify(userPersona));
            renderSidebar();
        }

        function openAvatarCropperModal(type) {
            currentEditingAvatarType = type;
            let currentSrc = type === 'char' ? document.getElementById('avatar-img-preview').src :
                             type === 'group' ? document.getElementById('group-avatar-preview').src :
                             document.getElementById('user-avatar-preview').src;

            let imgElem = document.getElementById('cropper-target-img');
            imgElem.src = currentSrc;
            document.getElementById('cropper-modal').classList.remove('hidden');

            if(cropperInstance) cropperInstance.destroy();
            cropperInstance = new Cropper(imgElem, { aspectRatio: 1, viewMode: 1, dragMode: 'move' });
        }

        function closeCropperModal() {
            if(cropperInstance) { cropperInstance.destroy(); cropperInstance = null; }
            document.getElementById('cropper-modal').classList.add('hidden');
        }

        function loadNewCropperImage(input) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = (e) => {
                    if(cropperInstance) cropperInstance.destroy();
                    let imgElem = document.getElementById('cropper-target-img');
                    imgElem.src = e.target.result;
                    cropperInstance = new Cropper(imgElem, { aspectRatio: 1, viewMode: 1, dragMode: 'move' });
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function applyCroppedAvatar() {
            if(!cropperInstance) return;
            let canvas = cropperInstance.getCroppedCanvas({ width: 512, height: 512 });
            let finalDataUrl = canvas.toDataURL('image/jpeg', 0.82);

            if (currentEditingAvatarType === 'char') document.getElementById('avatar-img-preview').src = finalDataUrl;
            else if (currentEditingAvatarType === 'group') document.getElementById('group-avatar-preview').src = finalDataUrl;
            else if (currentEditingAvatarType === 'user') document.getElementById('user-avatar-preview').src = finalDataUrl;

            closeCropperModal();
        }

        function renderUserMemories() {
            let container = document.getElementById('user-memories-list');
            if(!userPersona.memories || userPersona.memories.length === 0) {
                container.innerHTML = `<div style="font-size:0.78rem; color:var(--text-sub);">No facts stored yet.</div>`;
                return;
            }
            container.innerHTML = userPersona.memories.map((m, idx) => `
                <div class="memory-tag-chip">
                    <span>${m}</span>
                    <i class="fa-solid fa-trash" onclick="deleteUserMemory(${idx})"></i>
                </div>
            `).join('');
        }

        function deleteUserMemory(idx) {
            userPersona.memories.splice(idx, 1);
            saveState();
            renderUserMemories();
        }

        function openBackupOptionsModal() {
            let container = document.getElementById('backup-char-list');
            if(characters.length === 0) container.innerHTML = `<div style="font-size:0.8rem; color:var(--text-sub);">No characters created yet.</div>`;
            else {
                container.innerHTML = characters.map(c => `
                    <button class="item-btn" style="background:var(--bg-input); border:1px solid var(--border-color);" onclick="exportSingleCharacterData('${c.id}')">
                        <img src="${c.avatar}" style="width:28px; height:28px; border-radius:50%;" />
                        <span>${c.name} (Export JSON)</span>
                    </button>
                `).join('');
            }
            document.getElementById('backup-modal').classList.remove('hidden');
        }

        function exportSingleCharacterData(charId) {
            let c = characters.find(item => item.id === charId);
            if(!c) return;
            let charBackup = { type: 'single_character_backup', character: c, chatHistory: chatHistories[charId] || [] };
            let blob = new Blob([JSON.stringify(charBackup, null, 2)], { type: 'application/json' });
            let a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `${c.name}_Backup_${Date.now()}.json`;
            a.click();
            document.getElementById('backup-modal').classList.add('hidden');
        }

        function exportFullData() {
            let backupData = { characters, groups, chatHistories, userPersona };
            let blob = new Blob([JSON.stringify(backupData, null, 2)], { type: 'application/json' });
            let a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'Kio_Full_Backup_' + Date.now() + '.json';
            a.click();
            document.getElementById('backup-modal').classList.add('hidden');
        }

        function importData(input) {
            let file = input.files[0];
            if(!file) return;
            let reader = new FileReader();
            reader.onload = function(e) {
                try {
                    let imported = JSON.parse(e.target.result);
                    if(imported.type === 'single_character_backup') {
                        let c = imported.character;
                        let existingIdx = characters.findIndex(item => item.id === c.id);
                        if(existingIdx >= 0) characters[existingIdx] = c;
                        else characters.push(c);
                        chatHistories[c.id] = imported.chatHistory || [];
                        saveState();
                        alert(`Character "${c.name}" imported!`);
                    } else {
                        if(imported.characters) characters = imported.characters;
                        if(imported.groups) groups = imported.groups;
                        if(imported.chatHistories) chatHistories = imported.chatHistories;
                        if(imported.userPersona) userPersona = imported.userPersona;
                        saveState();
                        alert('Full app data imported!');
                    }
                    location.reload();
                } catch(err) { alert('Invalid JSON File!'); }
            };
            reader.readAsText(file);
        }

        function openNewCharForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('char-id').value = '';
            document.getElementById('char-name').value = '';
            document.getElementById('char-rel').value = '';
            document.getElementById('char-app').value = '';
            document.getElementById('char-backstory').value = '';
            document.getElementById('char-directives').value = '';
            document.getElementById('char-memories').value = '';
            document.getElementById('avatar-img-preview').src = 'https://api.dicebear.com/7.x/bottts/svg?seed=' + Date.now();
            document.getElementById('char-form-title').innerText = 'Create Companion';
            document.getElementById('char-delete-btn').classList.add('hidden');
            showForm('char-form');
        }

        function openNewGroupForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('group-id').value = '';
            document.getElementById('group-title').value = '';
            document.getElementById('group-context').value = '';
            document.getElementById('group-directives').value = '';
            document.getElementById('group-avatar-preview').src = 'https://api.dicebear.com/7.x/shapes/svg?seed=' + Date.now();
            document.getElementById('group-form-title').innerText = 'Create Group Chat';
            document.getElementById('group-delete-btn').classList.add('hidden');
            showForm('group-form');
        }

        function handleHeaderAvatarClick() {
            if(!activeContext) return;
            if(activeContext.type === 'char') editCurrentCharacter();
            else if(activeContext.type === 'group') editCurrentGroup();
        }

        function editCurrentCharacter() {
            let c = characters.find(item => item.id === activeContext.id);
            if(!c) return;
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('char-id').value = c.id;
            document.getElementById('char-name').value = c.name;
            document.getElementById('char-rel').value = c.relationship || '';
            document.getElementById('char-app').value = c.appearance || '';
            document.getElementById('char-backstory').value = c.backstory || '';
            document.getElementById('char-directives').value = c.directives || '';
            document.getElementById('char-memories').value = c.memories || '';
            document.getElementById('avatar-img-preview').src = c.avatar;
            document.getElementById('char-form-title').innerText = 'Modify Companion';
            document.getElementById('char-delete-btn').classList.remove('hidden');
            showForm('char-form');
        }

        function editCurrentGroup() {
            let g = groups.find(item => item.id === activeContext.id);
            if(!g) return;
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('group-id').value = g.id;
            document.getElementById('group-title').value = g.title || '';
            document.getElementById('group-context').value = g.context || '';
            document.getElementById('group-directives').value = g.directives || '';
            document.getElementById('group-avatar-preview').src = g.avatar || 'https://api.dicebear.com/7.x/shapes/svg?seed=' + g.id;
            document.getElementById('group-form-title').innerText = 'Modify Group Settings';
            document.getElementById('group-delete-btn').classList.remove('hidden');
            showForm('group-form');
        }

        function deleteCurrentCharacter() {
            let id = document.getElementById('char-id').value;
            if(!id) return;
            if(confirm("Delete character permanently?")) {
                characters = characters.filter(c => c.id !== id);
                delete chatHistories[id];
                saveState();
                goHome();
            }
        }

        function deleteCurrentGroup() {
            let id = document.getElementById('group-id').value;
            if(!id) return;
            if(confirm("Delete group room permanently?")) {
                groups = groups.filter(g => g.id !== id);
                delete chatHistories[id];
                saveState();
                goHome();
            }
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

        function showForm(formId) {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById(formId).classList.remove('hidden');

            if(formId === 'settings-form') {
                document.getElementById('user-name').value = userPersona.name || '';
                document.getElementById('user-bio').value = userPersona.bio || '';
                document.getElementById('user-avatar-preview').src = userPersona.avatar || 'https://api.dicebear.com/7.x/identicon/svg?seed=user';
                renderUserMemories();
            }
            if(formId === 'group-form') renderGroupSelector();
        }

        function renderGroupSelector() {
            let container = document.getElementById('group-char-selector');
            let currentGroup = groups.find(g => g.id === document.getElementById('group-id').value);
            let selectedIds = currentGroup ? currentGroup.memberIds : [];

            container.innerHTML = characters.map(c => `
                <label style="display:flex; align-items:center; gap:8px; background:var(--bg-surface-solid); padding:8px; border-radius:8px; cursor:pointer; margin-bottom:4px;">
                    <input type="checkbox" value="${c.id}" ${selectedIds.includes(c.id) ? 'checked':''} class="group-char-checkbox" style="width:auto;">
                    <img src="${c.avatar}" style="width:24px; height:24px; border-radius:50%;"/>
                    ${c.name}
                </label>
            `).join('');
        }

        function saveCharacter() {
            let id = document.getElementById('char-id').value || 'char_' + Date.now();
            let charObj = {
                id,
                name: document.getElementById('char-name').value || 'Companion',
                relationship: document.getElementById('char-rel').value,
                appearance: document.getElementById('char-app').value,
                backstory: document.getElementById('char-backstory').value,
                directives: document.getElementById('char-directives').value,
                memories: document.getElementById('char-memories').value,
                avatar: document.getElementById('avatar-img-preview').src,
                affinity: 50
            };

            let existingIdx = characters.findIndex(c => c.id === id);
            if(existingIdx >= 0) characters[existingIdx] = charObj;
            else characters.push(charObj);

            saveState();
            openChat('char', id);
        }

        function saveGroup() {
            let groupId = document.getElementById('group-id').value || 'group_' + Date.now();
            let title = document.getElementById('group-title').value || 'Group Chat';
            let context = document.getElementById('group-context').value || '';
            let directives = document.getElementById('group-directives').value || '';
            let avatar = document.getElementById('group-avatar-preview').src;
            let selectedChars = Array.from(document.querySelectorAll('.group-char-checkbox:checked')).map(cb => cb.value);

            if(selectedChars.length < 2) return alert('Select at least 2 characters!');

            let groupObj = { id: groupId, title, context, directives, avatar, memberIds: selectedChars };
            let existingIdx = groups.findIndex(g => g.id === groupId);
            if(existingIdx >= 0) groups[existingIdx] = groupObj;
            else groups.push(groupObj);

            saveState();
            openChat('group', groupId);
        }

        function saveUserPersona() {
            userPersona.name = document.getElementById('user-name').value || 'User';
            userPersona.bio = document.getElementById('user-bio').value || '';
            userPersona.avatar = document.getElementById('user-avatar-preview').src;
            saveState();
            alert('Persona saved!');
        }

        function renderSidebar() {
            let charList = document.getElementById('char-list');
            let groupList = document.getElementById('group-list');

            charList.innerHTML = characters.map(c => `
                <button class="item-btn ${activeContext?.id === c.id ? 'active':''}" onclick="openChat('char', '${c.id}')">
                    <img src="${c.avatar}" />
                    <span>${c.name}</span>
                </button>
            `).join('');

            groupList.innerHTML = groups.map(g => `
                <button class="item-btn ${activeContext?.id === g.id ? 'active':''}" onclick="openChat('group', '${g.id}')">
                    <img src="${g.avatar || 'https://api.dicebear.com/7.x/shapes/svg?seed=' + g.id}" />
                    <span>${g.title}</span>
                </button>
            `).join('');
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-bar').classList.remove('hidden');

            if(type === 'group') {
                document.getElementById('pin-mem-btn').classList.add('hidden');
                let g = groups.find(item => item.id === id);
                let avatarSrc = g ? (g.avatar || 'https://api.dicebear.com/7.x/shapes/svg?seed=' + g.id) : 'https://api.dicebear.com/7.x/shapes/svg?seed=group';
                let titleText = g ? g.title : 'Group Chat';
                document.getElementById('top-title').innerHTML = `
                    <img src="${avatarSrc}" class="header-avatar" onclick="handleHeaderAvatarClick()" title="Edit Group">
                    <span>${titleText}</span>
                `;
            } else {
                document.getElementById('pin-mem-btn').classList.remove('hidden');
                let c = characters.find(item => item.id === id);
                let aff = c ? (c.affinity || 50) : 50;
                let label = aff >= 80 ? 'Deep Bond ❤️' : (aff >= 50 ? 'Warm 😊' : 'Distant 💔');
                let avatarSrc = c ? c.avatar : 'https://api.dicebear.com/7.x/bottts/svg?seed=default';
                let nameText = c ? c.name : 'Chat';
                document.getElementById('top-title').innerHTML = `
                    <img src="${avatarSrc}" class="header-avatar" onclick="handleHeaderAvatarClick()" title="Edit Companion">
                    <span>${nameText}</span>
                    <span style="font-size:0.6rem; padding:2px 5px; background:rgba(236,72,153,0.15); border:1px solid var(--accent-pink); color:var(--accent-pink); border-radius:8px; margin-left:4px; flex-shrink:0;">${label} (${aff}%)</span>
                `;
            }

            renderSidebar();
            renderMessages();
        }

        function formatText(text) {
            return text.replace(/\\*(.*?)\\*/g, '<span class="action-text">*$1*</span>');
        }

        function renderMessages() {
            let container = document.getElementById('message-container');
            let history = chatHistories[activeContext.id] || [];

            if (history.length === 0) {
                container.innerHTML = `
                    <div class="empty-chat-placeholder">
                        <i class="fa-regular fa-comments"></i>
                        <strong style="font-size:0.95rem; color:var(--text-main);">No messages yet</strong>
                        <span style="font-size:0.78rem;">Say hi or tap 🪄 for magic conversation starter!</span>
                    </div>
                `;
                return;
            }

            container.innerHTML = history.map((m, idx) => {
                let isUser = m.sender === 'You';
                return `
                    <div class="message ${isUser ? 'user':'ai'}">
                        <div class="sender-name">${m.sender}</div>
                        <div class="content">
                            ${formatText(m.text)}
                            <div class="bubble-controls">
                                <i class="fa-solid fa-pen-to-square bubble-btn-icon" onclick="tweakMsg(${idx})" title="Edit"></i>
                                ${!isUser ? `
                                    <i class="fa-solid fa-forward-step bubble-btn-icon" onclick="continueAiReply()" title="Continue"></i>
                                    <i class="fa-solid fa-rotate-right bubble-btn-icon" onclick="regenerateLastResponse()" title="Reload Response"></i>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        function showTypingIndicator(senderName) {
            let container = document.getElementById('message-container');
            let emptyState = container.querySelector('.empty-chat-placeholder');
            if (emptyState) emptyState.remove();

            let typingElem = document.createElement('div');
            typingElem.id = 'typing-bubble';
            typingElem.className = 'message ai';
            typingElem.innerHTML = `
                <div class="sender-name">${senderName}</div>
                <div class="content typing-indicator">
                    <i class="fa-solid fa-ellipsis fa-beat"></i> typing...
                </div>
            `;
            container.appendChild(typingElem);
            container.scrollTop = container.scrollHeight;
        }

        function removeTypingIndicator() {
            let elem = document.getElementById('typing-bubble');
            if(elem) elem.remove();
        }

        function streamWordByWord(sender, newText, isAppend = false) {
            removeTypingIndicator();
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];

            let words = newText.split(' ');
            let wordIdx = 0;

            if (isAppend && chatHistories[activeContext.id].length > 0) {
                let lastMsgIdx = chatHistories[activeContext.id].length - 1;
                let existingText = chatHistories[activeContext.id][lastMsgIdx].text;
                
                let timer = setInterval(() => {
                    if (wordIdx < words.length) {
                        existingText += (existingText && wordIdx === 0 ? ' ' : (wordIdx === 0 ? '' : ' ')) + words[wordIdx];
                        chatHistories[activeContext.id][lastMsgIdx].text = existingText;
                        renderMessages();
                        wordIdx++;
                    } else {
                        clearInterval(timer);
                        saveState();
                    }
                }, 30);
            } else {
                let currentText = '';
                let msgObj = { sender: sender, text: '' };
                chatHistories[activeContext.id].push(msgObj);
                let msgIndex = chatHistories[activeContext.id].length - 1;

                let timer = setInterval(() => {
                    if (wordIdx < words.length) {
                        currentText += (wordIdx === 0 ? '' : ' ') + words[wordIdx];
                        chatHistories[activeContext.id][msgIndex].text = currentText;
                        renderMessages();
                        wordIdx++;
                    } else {
                        clearInterval(timer);
                        saveState();
                    }
                }, 30);
            }
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
                provider: currentAiProvider,
                history: chatHistories[activeContext.id] || []
            };

            let res = await fetch('/api/suggest-reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let data = await res.json();
            if(data.suggestion) input.value = data.suggestion;
            input.placeholder = "Type a message...";
        }

        async function continueAiReply() {
            if(!activeContext) return;
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            fetchAIResponse(true);
        }

        async function fetchAIResponse(isContinue = false) {
            let targetName = 'Companion';
            
            if(activeContext.type === 'char') {
                let c = characters.find(item => item.id === activeContext.id);
                if(c) { targetName = c.name; }
            }
            
            showTypingIndicator(targetName);

            let payload = {
                type: activeContext.type,
                contextId: activeContext.id,
                userPersona: userPersona,
                isContinue: isContinue,
                provider: currentAiProvider,
                history: chatHistories[activeContext.id]
            };

            if(activeContext.type === 'char') {
                payload.character = characters.find(c => c.id === activeContext.id);
            } else {
                let group = groups.find(g => g.id === activeContext.id);
                payload.group = group;
                payload.members = characters.filter(c => group.memberIds.includes(c.id));
            }

            let res = await fetch('/api/advanced-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let data = await res.json();
            removeTypingIndicator();

            if(data.extractedMemory) {
                if(!userPersona.memories.includes(data.extractedMemory)) {
                    userPersona.memories.push(data.extractedMemory);
                    saveState();
                }
            }

            if(data.responses) {
                for (let r of data.responses) {
                    if(r.newAffinity !== undefined && activeContext.type === 'char') {
                        let charObj = characters.find(c => c.id === activeContext.id);
                        if(charObj) {
                            charObj.affinity = r.newAffinity;
                            let avatarSrc = charObj.avatar;
                            document.getElementById('top-title').innerHTML = `
                                <img src="${avatarSrc}" class="header-avatar" onclick="handleHeaderAvatarClick()" title="Edit Companion">
                                <span>${charObj.name}</span>
                                <span style="font-size:0.6rem; padding:2px 5px; background:rgba(236,72,153,0.15); border:1px solid var(--accent-pink); color:var(--accent-pink); border-radius:8px; margin-left:4px; flex-shrink:0;">${r.affinityLabel} (${r.newAffinity}%)</span>
                            `;
                        }
                    }
                    streamWordByWord(r.sender, r.text, isContinue);
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

        renderSidebar();
    </script>
</body>
</html>
"""

def call_llm(provider, messages, system_prompt):
    try:
        if provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key: return "OpenRouter Key missing!"
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "gryphe/mythomax-l2-13b",
                "messages": [{"role": "system", "content": system_prompt}] + messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers).json()
            if "choices" in res and len(res["choices"]) > 0:
                return res["choices"][0]["message"]["content"]
            return f"OpenRouter Error: {res.get('error', 'Unknown error')}"

        else:  # Default Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key: return "Groq Key missing!"
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": system_prompt}] + messages
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers).json()
            if "choices" in res and len(res["choices"]) > 0:
                return res["choices"][0]["message"]["content"]
            return f"Groq Error: {res.get('error', 'Unknown error')}"
    except Exception as e:
        return f"*Smiles* Error: {str(e)}"

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

@app.route("/api/generate-image-prompt", methods=["POST"])
def generate_image_prompt():
    data = request.json
    character = data.get("character", {})
    history = data.get("history", [])

    recent_context = "\n".join([f"{m['sender']}: {m['text']}" for m in history[-2:]])
    char_appearance = character.get("appearance", "A person with attractive features")
    char_name = character.get("name", "")

    system_prompt = f"""
You are an expert prompt engineer for AI image generators.
Your task is to create a high-quality, cinematic image generation prompt.

Details:
- Appearance details: {char_appearance}
- Recent Chat Context (Scenario, Dress, Location, Action): {recent_context}

Rules for the Image Prompt:
1. CRITICAL: NEVER use the character's name or any real person's name. Use pronouns like 'She' or 'He' exclusively.
2. Maintain all physical attributes, outfit/dress, location, and style provided in the context.
3. Keep it photorealistic, highly detailed, cinematic lighting, and professional.
4. End the prompt with aspect ratio tag `--ar 9:16`.
5. Output ONLY the final image prompt text, no extra conversation.
"""

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"prompt": "Error: Groq API Key missing!"})

    try:
        headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Generate the 9:16 image prompt now."}]
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers).json()
        prompt_text = res["choices"][0]["message"]["content"].strip()
        
        if char_name:
            prompt_text = prompt_text.replace(char_name, "the subject")

        return jsonify({"prompt": prompt_text})
    except Exception as e:
        return jsonify({"prompt": f"Error generating prompt: {str(e)}"})

@app.route("/api/suggest-reply", methods=["POST"])
def suggest_reply():
    data = request.json
    provider = data.get("provider", "groq")
    user_info = data.get("userPersona", {})
    history = data.get("history", [])

    system_prompt = f"Ghostwrite for {user_info.get('name', 'User')}. Bio: {user_info.get('bio', '')}. Generate next short natural Hinglish text reply. Return ONLY text."
    messages = [{"role": "user" if m["sender"] != "You" else "assistant", "content": f"{m['sender']}: {m['text']}"} for m in history[-10:]]
    
    reply = call_llm(provider, messages, system_prompt)
    return jsonify({"suggestion": reply.strip('"')})

@app.route("/api/advanced-chat", methods=["POST"])
def advanced_chat():
    data = request.json
    provider = data.get("provider", "groq")
    user_info = data.get("userPersona", {})
    user_name = user_info.get("name", "User")
    user_bio = user_info.get("bio", "")
    user_memories = user_info.get("memories", [])
    history = data.get("history", [])

    extracted_memory = None
    last_user_msg = history[-1]["text"] if history else ""
    responses = []

    if data["type"] == "char":
        c = data["character"]
        current_affinity = c.get("affinity", 50)

        delta = 1
        positive_words = ["love", "pyar", "achha", "sweet", "thanks", "dost", "like", "cute", "care", "pyaar"]
        negative_words = ["hate", "chup", "bad", "rude", "pagal", "shut up", "irritating"]

        if any(w in last_user_msg.lower() for w in positive_words): delta = 3
        elif any(w in last_user_msg.lower() for w in negative_words): delta = -4

        new_affinity = max(0, min(100, current_affinity + delta))
        mood_str = "Deep Bond ❤️" if new_affinity >= 80 else ("Warm 😊" if new_affinity >= 50 else "Distant 💔")
        behavior_note = "Be deeply affectionate, playful, and expressive." if new_affinity >= 80 else "Be friendly and comfortable like a close buddy."

        memories_formatted = ", ".join(user_memories) if user_memories else "None"

        system_prompt = f"""
You are {c['name']}, talking to {user_name}.
Relationship: {c.get('relationship', 'Friend')}
Appearance: {c.get('appearance', '')}
Backstory: {c.get('backstory', '')}
Bond: {new_affinity}/100 ({mood_str}). {behavior_note}
User Bio: {user_bio}
Known Memory Facts: {memories_formatted}

CRITICAL DESI HINGLISH INSTRUCTIONS:
- Talk strictly in natural, casual Hinglish (Roman Hindi mixed with simple English like WhatsApp texting).
- Use everyday words like "yaar", "sach mein", "batao", "sahi hai", "pakka".
- Keep it human-like and expressive. Use asterisks for actions like *smiles*.
"""
        if data.get("isContinue"):
            system_prompt += "\nUser pressed Continue. Extend your last response seamlessly."

        messages = []
        for m in history[-25:]:
            role = "user" if m["sender"] == "You" or m["sender"] == user_name else "assistant"
            messages.append({"role": role, "content": f"{m['sender']}: {m['text']}"})

        reply_text = call_llm(provider, messages, system_prompt)

        responses.append({
            "sender": c['name'], 
            "text": reply_text, 
            "newAffinity": new_affinity,
            "affinityLabel": mood_str
        })

    else:
        group = data["group"]
        members = data["members"]
        for char in members[:2]:
            system_prompt = f"You are {char['name']} in group '{group.get('title', 'Group')}'. Talk briefly in casual Hinglish using asterisks for actions."
            messages = [{"role": "user", "content": f"{m['sender']}: {m['text']}"} for m in history[-25:]]
            reply_text = call_llm(provider, messages, system_prompt)
            responses.append({"sender": char['name'], "text": reply_text})

    return jsonify({"responses": responses, "extractedMemory": extracted_memory})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
