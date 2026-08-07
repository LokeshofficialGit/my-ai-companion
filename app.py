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
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">
    <style>
        :root {
            /* Default Dark Theme Colors */
            --bg-main: #050508;
            --bg-surface: #121215;
            --bg-input: #09090b;
            --border-color: #27272a;
            --text-main: #f4f4f5;
            --text-sub: #a1a1aa;
            --accent-purple: #a855f7;
            --accent-pink: #ec4899;
            --action-text: #f472b6;
            --user-msg-bg: linear-gradient(135deg, #9333ea, #ec4899);
            --ai-msg-bg: #121215;
            --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            
            /* Sidebar Theme Variables (Dynamic) */
            --sidebar-bg: #09090b;
            --sidebar-border: #27272a;
            --sidebar-text: #f4f4f5;
            --sidebar-btn-bg: #121215;
            --sidebar-btn-hover: #27272a;
        }

        [data-theme="light"] {
            /* Light Theme Colors */
            --bg-main: #f4f4f5;
            --bg-surface: #ffffff;
            --bg-input: #ffffff;
            --border-color: #e4e4e7;
            --text-main: #09090b;
            --text-sub: #52525b;
            --action-text: #be185d;
            --ai-msg-bg: #ffffff;
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);

            /* Sidebar Light Theme Overrides */
            --sidebar-bg: #ffffff;
            --sidebar-border: #e4e4e7;
            --sidebar-text: #09090b;
            --sidebar-btn-bg: #f4f4f5;
            --sidebar-btn-hover: #e4e4e7;
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
            transition: background 0.3s, color 0.3s;
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
            transition: background 0.3s;
        }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }

        /* Top Bar */
        .top-bar { height: 52px; min-height: 52px; background: var(--bg-surface); border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 10; transition: background 0.3s; }
        .toggle-btn { background: transparent; border: none; color: var(--text-main); font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .top-title { font-weight: 700; font-size: 1rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }

        /* DYNAMIC SIDEBAR (Adapts to Light / Dark Mode) */
        .sidebar { 
            position: absolute; top: 0; left: 0; width: 85%; height: 100%; 
            background: var(--sidebar-bg); 
            color: var(--sidebar-text);
            border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; 
            transition: transform 0.3s ease, background 0.3s; z-index: 100; transform: translateX(-100%); pointer-events: none; 
        }
        .sidebar.open { transform: translateX(0); pointer-events: auto; }
        .sidebar-header { padding: 14px 16px; font-size: 1.2rem; font-weight: 800; color: var(--accent-pink); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
        .header-actions { display: flex; align-items: center; gap: 6px; }
        .sidebar-icon-btn { background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.88rem; }

        .nav-section { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }

        /* Accordion Menu */
        .menu-category-btn { width: 100%; padding: 12px 14px; background: var(--sidebar-btn-bg); border: 1px solid var(--sidebar-border); color: var(--sidebar-text); border-radius: 10px; text-align: left; cursor: pointer; display: flex; align-items: center; justify-content: space-between; font-size: 0.92rem; font-weight: 600; }
        .menu-category-btn i.cat-icon { color: var(--accent-pink); font-size: 1rem; margin-right: 10px; }
        .menu-category-btn .arrow-icon { font-size: 0.8rem; color: var(--text-sub); transition: transform 0.2s ease; }
        .menu-category-btn.active .arrow-icon { transform: rotate(180deg); }

        .submenu-container { padding: 6px 0 6px 12px; display: flex; flex-direction: column; gap: 4px; }
        
        .item-btn { width: 100%; padding: 9px 12px; background: transparent; border: none; color: var(--text-sub); border-radius: 8px; text-align: left; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 0.88rem; }
        .item-btn:hover, .item-btn.active { background: var(--sidebar-btn-hover); color: var(--sidebar-text); }
        .item-btn img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }

        .sub-create-btn { width: 100%; padding: 9px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.82rem; display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 4px; }
        .sub-create-btn.blue { background: #2563eb; }

        /* Workspace */
        .workspace { flex: 1; display: flex; flex-direction: column; height: calc(100% - 52px); position: relative; overflow: hidden; }

        /* Dashboard */
        .dashboard { flex: 1; padding: 24px 16px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .dash-logo { width: 80px; height: 80px; margin-bottom: 12px; filter: drop-shadow(0 0 10px rgba(236,72,153,0.4)); }
        .dash-title { font-size: 1.5rem; font-weight: 800; color: var(--text-main); margin-bottom: 6px; }
        .dash-sub { font-size: 0.85rem; color: var(--text-sub); text-align: center; margin-bottom: 24px; }
        
        .dash-card { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 14px 16px; border-radius: 14px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; box-shadow: var(--card-shadow); transition: transform 0.2s; }
        .dash-card:active { transform: scale(0.98); }
        .dash-card i { font-size: 1.3rem; color: var(--accent-pink); }
        .dash-card strong { display: block; color: var(--text-main); font-size: 0.92rem; }
        .dash-card span { font-size: 0.75rem; color: var(--text-sub); }

        /* Chat Room */
        #chat-view { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; -webkit-overflow-scrolling: touch; }
        .message { display: flex; gap: 10px; max-width: 88%; position: relative; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .message .avatar { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; background: var(--border-color); flex-shrink: 0; }
        .message .content { background: var(--ai-msg-bg); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 14px; font-size: 0.9rem; line-height: 1.45; color: var(--text-main); word-break: break-word; box-shadow: var(--card-shadow); }
        .message.user .content { background: var(--user-msg-bg); border: none; color: #ffffff; border-bottom-right-radius: 2px; }
        .message.ai .content { border-bottom-left-radius: 2px; }
        .message .sender-name { font-size: 0.7rem; color: var(--text-sub); margin-bottom: 3px; font-weight: 600; }
        
        .action-text { color: var(--action-text); font-style: italic; font-weight: 500; }
        
        /* Subtle Link Container inside Bubble */
        .bubble-controls { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
        .edit-link, .continue-bubble-btn { font-size: 0.68rem; color: var(--text-sub); text-decoration: underline; cursor: pointer; opacity: 0.65; transition: opacity 0.2s; }
        .edit-link:hover, .continue-bubble-btn:hover { opacity: 1; color: var(--accent-pink); }

        /* Typing Dots */
        .typing-dots { display: flex; gap: 4px; align-items: center; padding: 4px 0; }
        .typing-dots span { width: 5px; height: 5px; background: var(--accent-pink); border-radius: 50%; animation: pulse 1.2s infinite ease-in-out; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }

        /* Input Area & Transparent In-Box Magic Wand */
        .input-area { padding: 10px 12px; border-top: 1px solid var(--border-color); background: var(--bg-surface); display: flex; gap: 8px; width: 100%; align-items: center; }
        .input-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
        .input-wrapper input { 
            width: 100%; 
            background: var(--bg-input); 
            border: 1px solid var(--border-color); 
            padding: 10px 38px 10px 12px; 
            border-radius: 20px; 
            color: var(--text-main); 
            outline: none; 
            font-size: 0.88rem; 
        }

        .wand-inbox-btn { 
            position: absolute; 
            right: 10px; 
            background: transparent; 
            border: none; 
            color: var(--accent-pink); 
            opacity: 0.6; 
            font-size: 0.95rem; 
            cursor: pointer; 
            transition: opacity 0.2s, transform 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
        }
        .wand-inbox-btn:hover, .wand-inbox-btn:active { opacity: 1; transform: scale(1.15); }

        .input-area button.send-btn { height: 38px; padding: 0 14px; background: linear-gradient(135deg, #9333ea, #ec4899); color: #ffffff; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        
        /* Camera Button for Future Img2Img */
        .tool-btn { background: var(--bg-input) !important; color: var(--accent-pink) !important; border: 1px solid var(--border-color) !important; padding: 0 10px !important; font-size: 0.95rem; border-radius: 10px !important; height: 38px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        /* Form Styles */
        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 4px; font-size: 0.8rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; color: var(--text-main); outline: none; font-size: 0.88rem; }
        .form-group textarea { height: 75px; resize: vertical; }

        /* Interactive Avatar Clickable Component */
        .avatar-edit-trigger {
            display: flex;
            align-items: center;
            gap: 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            padding: 10px 14px;
            border-radius: 12px;
            cursor: pointer;
        }
        .avatar-thumb-wrapper {
            width: 54px; height: 54px; border-radius: 50%; overflow: hidden;
            border: 2px solid var(--accent-pink); flex-shrink: 0; background: var(--border-color);
            display: flex; justify-content: center; align-items: center;
        }
        .avatar-thumb-wrapper img { width: 100%; height: 100%; object-fit: cover; }

        /* Interactive Cropper.js Avatar Modal */
        .avatar-modal-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.88); backdrop-filter: blur(8px);
            z-index: 200; display: flex; flex-direction: column;
            align-items: center; justify-content: center; padding: 16px;
        }
        .avatar-modal-card {
            width: 100%; max-width: 360px; background: #121215;
            border: 1px solid #27272a; border-radius: 20px; padding: 16px;
            display: flex; flex-direction: column; align-items: center; gap: 14px; color: #ffffff;
        }
        .cropper-container-box {
            width: 100%; height: 260px; background: #000; border-radius: 12px;
            overflow: hidden; border: 1px solid #27272a; position: relative;
        }

        /* Generic Backup Options Modal */
        .modal-card {
            width: 100%; max-width: 340px; background: var(--bg-surface);
            border: 1px solid var(--border-color); border-radius: 20px; padding: 20px;
            display: flex; flex-direction: column; gap: 12px; max-height: 80vh; overflow-y: auto; color: var(--text-main);
        }

        .submit-btn { width: 100%; padding: 11px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.9rem; margin-top: 8px; }
        .delete-btn { background: #ef4444 !important; margin-top: 10px; }

        .hidden { display: none !important; }

        /* Highly Saturated & Crisp SVG Logo Component Styling */
        .aura-logo-svg { width: 28px; height: 28px; filter: drop-shadow(0 0 6px rgba(236,72,153,0.5)); }
    </style>
</head>
<body data-theme="dark">

    <!-- Inline High-Contrast Saturated SVG Logo Template -->
    <svg class="hidden">
        <defs>
            <linearGradient id="roleGradVibrant" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#a855f7"/>
                <stop offset="50%" stop-color="#ec4899"/>
                <stop offset="100%" stop-color="#f43f5e"/>
            </linearGradient>
            <g id="aura-brand-icon">
                <!-- Base Glow Contour -->
                <path d="M 20 6 C 50 6, 75 30, 65 70 C 55 110, 20 120, 0 80 C -15 50 -10 6 20 6 Z" fill="url(#roleGradVibrant)" stroke="#ffffff" stroke-width="3" opacity="0.95"/>
                <path d="M 45 30 C 0 30, -20 60, -5 100 C 10 135, 50 140, 70 110 C 85 70, 75 30, 45 30 Z" fill="#ec4899" stroke="#9333ea" stroke-width="2.5" opacity="0.85"/>
                <!-- Central Bright Sparkle -->
                <path d="M 30 -5 Q 30 15 50 15 Q 30 15 30 35 Q 30 15 10 15 Q 30 15 30 -5 Z" fill="#ffffff"/>
            </g>
        </defs>
    </svg>

    <div class="app-container">
        <!-- Sidebar Navigation (DYNAMIC LIGHT / DARK THEME) -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span style="display:flex; align-items:center; gap:8px;">
                    <svg viewBox="-40 -20 140 180" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg>
                    Aura
                </span>
                <div class="header-actions">
                    <button class="sidebar-icon-btn" onclick="toggleAppTheme()" id="sidebar-theme-btn" title="Toggle Light/Dark Mode"><i class="fa-solid fa-moon"></i></button>
                    <button class="sidebar-icon-btn" onclick="toggleFullScreen()" title="Fullscreen Mode"><i class="fa-solid fa-expand"></i></button>
                    <button class="sidebar-icon-btn" onclick="toggleSidebar()" title="Close Sidebar"><i class="fa-solid fa-xmark"></i></button>
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

        <!-- Top Navigation Bar -->
        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title">
                    <svg viewBox="-40 -20 140 180" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg>
                    Aura
                </div>
            </div>
            
            <!-- Header Action Controls -->
            <div style="display: flex; gap: 6px; align-items: center;">
                <div id="top-actions" class="hidden" style="display: flex; gap: 6px;">
                    <button class="icon-btn" id="pin-mem-btn" onclick="openPinnedMemoryModal()" title="Pin Memory"><i class="fa-solid fa-thumbtack"></i></button>
                    <button class="icon-btn" onclick="handleEditClick()" title="Edit Companion / Group"><i class="fa-solid fa-wrench"></i></button>
                    <button class="icon-btn" onclick="regenerateLastResponse()" title="Regenerate"><i class="fa-solid fa-rotate-right"></i></button>
                    <button class="icon-btn" onclick="clearCurrentChat()" title="Clear Chat"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
        </div>

        <!-- Main Workspace Area -->
        <div class="workspace">
            <!-- Dashboard View -->
            <div id="dashboard-view" class="dashboard">
                <svg viewBox="-40 -20 140 180" class="dash-logo"><use href="#aura-brand-icon"/></svg>
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your personal AI companion & roleplay platform.</p>
                
                <div class="dash-card" onclick="openNewCharForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    <div>
                        <strong>Create AI Companion</strong>
                        <span>Custom backstory & relationship</span>
                    </div>
                </div>

                <div class="dash-card" onclick="openNewGroupForm()">
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
                    <!-- Photo Generation Button Placeholder for Future Img2Img -->
                    <button class="tool-btn" onclick="alert('Image Generation Feature coming up next!')" title="Generate AI Image">🤳</button>
                    
                    <div class="input-wrapper">
                        <input type="text" id="chat-input" placeholder="Message..." onkeypress="if(event.key==='Enter') sendMsg()">
                        <button class="wand-inbox-btn" onclick="suggestUserMessage()" title="Magic Auto-Suggest">🪄</button>
                    </div>
                    
                    <button class="send-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

            <!-- Character Creation / Edit Form -->
            <div id="char-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;" id="char-form-title">Create Companion</h3>
                <input type="hidden" id="char-id">
                
                <div class="form-group">
                    <label>Avatar Picture (Pinch & Drag Cropper)</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('char')">
                        <div class="avatar-thumb-wrapper">
                            <img id="avatar-img-preview" src="https://api.dicebear.com/7.x/bottts/svg?seed=default">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Pinch & Drag Crop Avatar</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Set high-res 512px reference image</span>
                        </div>
                    </div>
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
                <button class="submit-btn delete-btn" id="char-delete-btn" onclick="deleteCurrentCharacter()">Delete Companion</button>
            </div>

            <!-- Group Chat Creation & Editing Form -->
            <div id="group-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;" id="group-form-title">Create Group Chat</h3>
                <input type="hidden" id="group-id">

                <div class="form-group">
                    <label>Group Icon (Pinch & Drag Cropper)</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('group')">
                        <div class="avatar-thumb-wrapper">
                            <img id="group-avatar-preview" src="https://api.dicebear.com/7.x/shapes/svg?seed=group">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Pinch & Drag Crop Group Icon</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to crop or upload icon</span>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Group Name</label>
                    <input type="text" id="group-title" placeholder="e.g. Late Night Squad">
                </div>

                <div class="form-group">
                    <label>Group Context / Setting</label>
                    <textarea id="group-context" placeholder="Describe the current scene..."></textarea>
                </div>

                <div class="form-group">
                    <label>Group Directives</label>
                    <textarea id="group-directives" placeholder="Instructions for group behavior..."></textarea>
                </div>

                <div class="form-group">
                    <label>Group Members</label>
                    <div id="group-char-selector" style="display:flex; flex-direction:column; gap:6px;"></div>
                </div>

                <button class="submit-btn" style="background:#2563eb;" onclick="saveGroup()">Save Group Room</button>
                <button class="submit-btn delete-btn" id="group-delete-btn" onclick="deleteCurrentGroup()">Delete Group Room</button>
            </div>

            <!-- User Persona & Backup Form -->
            <div id="settings-form" class="form-container hidden">
                <h3 style="margin-bottom: 14px;">User Persona & Settings</h3>
                
                <div class="form-group">
                    <label>Your Avatar Picture (Pinch & Drag Cropper)</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('user')">
                        <div class="avatar-thumb-wrapper">
                            <img id="user-avatar-preview" src="https://api.dicebear.com/7.x/identicon/svg?seed=user">
                        </div>
                        <div>
                            <strong style="font-size:0.85rem; display:block;">Pinch & Drag Crop Your Avatar</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to adjust or upload photo</span>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Your Name</label>
                    <input type="text" id="user-name" placeholder="Your name">
                </div>

                <div class="form-group">
                    <label>Your Bio / Persona</label>
                    <textarea id="user-bio" placeholder="Describe yourself..."></textarea>
                </div>

                <button class="submit-btn" onclick="saveUserPersona()">Save Persona</button>

                <hr style="border-color:var(--border-color); margin: 16px 0;">

                <div class="form-group">
                    <label>Data Backup & Export</label>
                    <button class="submit-btn" style="background:var(--bg-surface); border:1px solid var(--border-color); color:var(--text-main); margin-top:0;" onclick="openBackupOptionsModal()"><i class="fa-solid fa-download"></i> Selective Backup Data</button>
                </div>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Import Data</label>
                    <input type="file" id="import-file" accept=".json" onchange="importData(this)">
                </div>
            </div>
        </div>

        <!-- Pinch & Drag Cropper.js Modal Overlay -->
        <div id="cropper-modal" class="avatar-modal-overlay hidden">
            <div class="avatar-modal-card">
                <h4 style="font-size:1rem;">Crop & Adjust Avatar (512x512)</h4>
                
                <div class="cropper-container-box">
                    <img id="cropper-target-img" src="" style="max-width:100%;">
                </div>

                <input type="file" id="cropper-file-input" accept="image/*" class="hidden" onchange="loadNewCropperImage(this)">

                <div style="display:flex; gap:8px; width:100%;">
                    <button class="sub-create-btn" style="flex:1; background:#27272a;" onclick="document.getElementById('cropper-file-input').click()"><i class="fa-solid fa-image"></i> Upload</button>
                    <button class="sub-create-btn" style="flex:1; background:#9333ea;" onclick="applyCroppedAvatar()">Done</button>
                </div>
            </div>
        </div>

        <!-- Selective Backup Chooser Modal -->
        <div id="backup-modal" class="avatar-modal-overlay hidden">
            <div class="modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:1rem;">Select Data to Backup</h4>
                    <button class="toggle-btn" style="color:var(--text-main);" onclick="document.getElementById('backup-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p style="font-size:0.78rem; color:var(--text-sub);">Choose full app backup or export a specific character's bio & chat history.</p>

                <button class="sub-create-btn" style="padding:10px; font-size:0.88rem;" onclick="exportFullData()"><i class="fa-solid fa-box-archive"></i> Export Entire App Data</button>

                <hr style="border-color:var(--border-color); margin: 4px 0;">

                <div style="font-size:0.75rem; color:var(--text-sub); font-weight:700; text-transform:uppercase;">Individual Characters</div>
                <div id="backup-char-list" style="display:flex; flex-direction:column; gap:6px;"></div>
            </div>
        </div>

    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>

    <script>
        let characters = JSON.parse(localStorage.getItem('aura_chars') || '[]');
        let groups = JSON.parse(localStorage.getItem('aura_groups') || '[]');
        let chatHistories = JSON.parse(localStorage.getItem('aura_chats') || '{}');
        let userPersona = JSON.parse(localStorage.getItem('aura_user') || '{"name":"User", "bio":"", "avatar":"https://api.dicebear.com/7.x/identicon/svg?seed=user"}');
        let currentTheme = localStorage.getItem('aura_theme') || 'dark';
        let activeContext = null;

        let cropperInstance = null;
        let currentEditingAvatarType = null;

        // Apply Theme on Initial Load
        document.body.setAttribute('data-theme', currentTheme);
        updateThemeToggleIcon();

        function toggleAppTheme() {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', currentTheme);
            localStorage.setItem('aura_theme', currentTheme);
            updateThemeToggleIcon();
        }

        function updateThemeToggleIcon() {
            let btn = document.getElementById('sidebar-theme-btn');
            if(btn) {
                if(currentTheme === 'dark') {
                    btn.innerHTML = '<i class="fa-solid fa-moon"></i>';
                } else {
                    btn.innerHTML = '<i class="fa-solid fa-sun" style="color:#eab308;"></i>';
                }
            }
        }

        function toggleSidebar() { 
            document.getElementById('sidebar').classList.toggle('open'); 
        }

        function toggleMenuCategory(subId) {
            let sub = document.getElementById(subId);
            let btn = sub.previousElementSibling;
            sub.classList.toggle('hidden');
            btn.classList.toggle('active');
        }

        function goHome() {
            activeContext = null;
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('char-form').classList.add('hidden');
            document.getElementById('group-form').classList.add('hidden');
            document.getElementById('settings-form').classList.add('hidden');
            document.getElementById('top-actions').classList.add('hidden');
            document.getElementById('top-title').innerHTML = `<svg viewBox="-40 -20 140 180" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg> Aura`;
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

        function openAvatarCropperModal(type) {
            currentEditingAvatarType = type;
            let currentSrc = '';
            
            if(type === 'char') currentSrc = document.getElementById('avatar-img-preview').src;
            else if(type === 'group') currentSrc = document.getElementById('group-avatar-preview').src;
            else if(type === 'user') currentSrc = document.getElementById('user-avatar-preview').src;

            let imgElem = document.getElementById('cropper-target-img');
            imgElem.src = currentSrc;

            document.getElementById('cropper-modal').classList.remove('hidden');

            if(cropperInstance) cropperInstance.destroy();
            
            cropperInstance = new Cropper(imgElem, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 0.9,
                restore: false,
                guides: false,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false
            });
        }

        function loadNewCropperImage(input) {
            if (input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = (e) => {
                    if(cropperInstance) cropperInstance.destroy();
                    let imgElem = document.getElementById('cropper-target-img');
                    imgElem.src = e.target.result;
                    cropperInstance = new Cropper(imgElem, {
                        aspectRatio: 1,
                        viewMode: 1,
                        dragMode: 'move',
                        autoCropArea: 0.9,
                        restore: false,
                        guides: false,
                        center: true,
                        highlight: false
                    });
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function applyCroppedAvatar() {
            if(!cropperInstance) return;

            let canvas = cropperInstance.getCroppedCanvas({ width: 512, height: 512 });
            let finalDataUrl = canvas.toDataURL('image/jpeg', 0.82);

            if (currentEditingAvatarType === 'char') {
                document.getElementById('avatar-img-preview').src = finalDataUrl;
            } else if (currentEditingAvatarType === 'group') {
                document.getElementById('group-avatar-preview').src = finalDataUrl;
            } else if (currentEditingAvatarType === 'user') {
                document.getElementById('user-avatar-preview').src = finalDataUrl;
            }

            cropperInstance.destroy();
            cropperInstance = null;
            document.getElementById('cropper-modal').classList.add('hidden');
        }

        function openBackupOptionsModal() {
            let container = document.getElementById('backup-char-list');
            if(characters.length === 0) {
                container.innerHTML = `<div style="font-size:0.8rem; color:var(--text-sub); padding:6px;">No characters created yet.</div>`;
            } else {
                container.innerHTML = characters.map(c => `
                    <button class="item-btn" style="background:var(--bg-input); border:1px solid var(--border-color); color:var(--text-main); padding:8px 10px;" onclick="exportSingleCharacterData('${c.id}')">
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

            let charBackup = {
                type: 'single_character_backup',
                character: c,
                chatHistory: chatHistories[charId] || []
            };

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
            a.download = 'Aura_Full_Backup_' + Date.now() + '.json';
            a.click();
            document.getElementById('backup-modal').classList.add('hidden');
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
            document.getElementById('char-delete-btn').classList.add('hidden');
            showForm('char-form');
        }

        function openNewGroupForm() {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('group-id').valu