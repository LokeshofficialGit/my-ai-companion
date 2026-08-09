import os
import requests
import json
import re
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

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
            --action-text: #a1a1aa;
            --user-msg-bg: #1f202b;
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
        .top-title { font-weight: 700; font-size: 0.95rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        
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
        
        .message .sender-name { 
            font-size: 0.78rem; 
            margin-bottom: 4px; 
            font-weight: 700; 
            padding-left: 2px; 
        }
        .message.user .sender-name { 
            text-align: right; 
            padding-right: 2px; 
            color: var(--accent-purple); 
        }
        .message.ai .sender-name { 
            text-align: left; 
            color: var(--accent-pink); 
        }

        .message .content { 
            background: var(--ai-msg-bg); 
            border: 1px solid var(--border-color); 
            padding: 12px 14px; 
            border-radius: 16px; 
            font-size: 0.9rem; 
            line-height: 1.5; 
            color: var(--text-main); 
            word-break: break-word; 
            box-shadow: var(--card-shadow); 
            border-bottom-left-radius: 4px; 
        }
        .message.user .content { 
            background: var(--user-msg-bg); 
            border: 1px solid rgba(168, 85, 247, 0.2); 
            color: #e4e4e7; 
            border-bottom-left-radius: 16px; 
            border-bottom-right-radius: 4px; 
        }
        
        .action-text { color: var(--action-text); font-style: italic; font-weight: 400; }
        
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

        /* Forms */
        .form-header-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
        .form-back-btn { background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; }

        .form-container { padding: 16px; overflow-y: auto; flex: 1; width: 100%; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 5px; font-size: 0.82rem; color: var(--text-sub); font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; background: var(--bg-surface-solid); border: 1px solid var(--border-color); padding: 10px 12px; border-radius: 10px; color: var(--text-main); outline: none; font-size: 0.9rem; }
        .form-group textarea { height: 75px; resize: vertical; }

        /* NSFW Switch CSS */
        .nsfw-toggle-box { display: flex; justify-content: space-between; align-items: center; background: var(--bg-surface-solid); padding: 12px; border-radius: 10px; border: 1px solid #3f3f46; margin-bottom: 14px; }
        .switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #3f3f46; border-radius: 24px; transition: .4s; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; border-radius: 50%; transition: .4s; }
        input:checked + .slider { background-color: #ef4444; }
        input:checked + .slider:before { transform: translateX(20px); }

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

        /* Modals */
        .prompt-modal-overlay, .avatar-modal-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85); z-index: 300; display: flex; flex-direction: column;
            justify-content: center; padding: 16px;
        }
        .modal-card, .prompt-modal-card {
            width: 100%; max-width: 360px; background: var(--bg-surface-solid);
            border: 1px solid var(--border-color); border-radius: 20px; padding: 16px;
            display: flex; flex-direction: column; gap: 14px; color: var(--text-main); margin: auto;
        }
        .prompt-textarea { width: 100%; height: 130px; background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px; color: var(--text-main); font-size: 0.88rem; resize: none; outline: none; }
        
        .cropper-container-box { width: 100%; height: 260px; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color); position: relative; }

        .submit-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; font-size: 0.92rem; margin-top: 8px; }
        .sub-create-btn { width: 100%; padding: 10px; background: linear-gradient(135deg, #9333ea, #ec4899); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .delete-btn { background: #ef4444 !important; margin-top: 10px; }

        .memory-tag-chip {
            display: flex; align-items: center; justify-content: space-between;
            background: var(--bg-input); border: 1px solid var(--border-color);
            padding: 8px 12px; border-radius: 10px; font-size: 0.82rem; color: var(--text-main); margin-bottom: 6px;
        }
        .memory-tag-chip i { cursor: pointer; color: #ef4444; opacity: 0.8; }
        .empty-chat-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; color: var(--text-sub); padding: 20px; opacity: 0.75; }
        .empty-chat-placeholder i { font-size: 2.5rem; color: var(--accent-pink); margin-bottom: 12px; }

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
                        <button class="sub-create-btn" style="background: linear-gradient(135deg, #2563eb, #3b82f6);" onclick="openNewGroupForm()"><i class="fa-solid fa-plus"></i> New Group Room</button>
                        <div id="group-list"></div>
                    </div>
                </div>

                <button class="menu-category-btn" onclick="showForm('settings-form')">
                    <span><i class="fa-solid fa-sliders cat-icon"></i> Settings & Persona</span>
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
                        <span>Edit profile, memories & settings</span>
                    </div>
                </div>
            </div>

            <!-- Active Chat View -->
            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="tool-btn" id="gp-btn" onclick="generateImagePrompt()" title="Generate Image Prompt">GP</button>
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
                <div class="form-group"><label>Core Identity / Job</label><input type="text" id="char-job" placeholder="e.g. Private Detective, College Student"></div>
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
                            <strong style="font-size:0.85rem; display:block;">Crop Icon</strong>
                            <span style="font-size:0.75rem; color:var(--text-sub);">Tap to adjust</span>
                        </div>
                    </div>
                </div>
                <div class="form-group"><label>Group Name</label><input type="text" id="group-title" placeholder="e.g. Squad"></div>
                <div class="form-group"><label>Group Context / Setting</label><textarea id="group-context"></textarea></div>
                <div class="form-group"><label>Group Directives</label><textarea id="group-directives"></textarea></div>
                <div class="form-group"><label>Select Members</label><div id="group-char-selector"></div></div>

                <button class="submit-btn" style="background:#2563eb;" onclick="saveGroup()">Save Group Room</button>
                <button class="submit-btn delete-btn" id="group-delete-btn" onclick="deleteCurrentGroup()">Delete Group</button>
            </div>

            <!-- Settings Form -->
            <div id="settings-form" class="form-container hidden">
                <div class="form-header-bar">
                    <button class="form-back-btn" onclick="smartFormBack()"><i class="fa-solid fa-chevron-left"></i> Back</button>
                    <h3 style="font-size:1.1rem; font-weight:800;">Persona & Settings</h3>
                </div>

                <!-- NSFW Toggle Switch -->
                <div class="nsfw-toggle-box">
                    <div>
                        <strong style="font-size:0.95rem; color:var(--text-main); display:block;">🔥 Unfiltered Mode (NSFW)</strong>
                        <span style="font-size:0.75rem; color:var(--text-sub);">Enable mature topics and unrestricted chat.</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="nsfw-toggle">
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="form-group">
                    <label>Your Avatar</label>
                    <div class="avatar-edit-trigger" onclick="openAvatarCropperModal('user')">
                        <div class="avatar-thumb-wrapper"><img id="user-avatar-preview" src=""></div>
                        <div><strong style="font-size:0.85rem; display:block;">Crop Avatar</strong></div>
                    </div>
                </div>

                <div class="form-group"><label>Your Name</label><input type="text" id="user-name"></div>
                <div class="form-group"><label>Your Bio / Persona</label><textarea id="user-bio"></textarea></div>
                <button class="submit-btn" onclick="saveUserPersona()">Save Settings</button>

                <hr style="border-color:var(--border-color); margin: 16px 0;">
                <div class="form-group">
                    <label style="color:var(--accent-pink);"><i class="fa-solid fa-brain"></i> Auto-Remembered Facts</label>
                    <div id="user-memories-list" style="margin-top:8px;"></div>
                </div>
                
                <hr style="border-color:var(--border-color); margin: 16px 0;">
                <div class="form-group">
                    <label>Data Backup & Export</label>
                    <button class="submit-btn" style="background:var(--bg-surface-solid); border:1px solid var(--border-color); color:var(--text-main); margin-top:0;" onclick="openBackupOptionsModal()"><i class="fa-solid fa-download"></i> Selective Backup Data</button>
                </div>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Import Data File (.json)</label>
                    <input type="file" accept=".json" onchange="importData(this)">
                </div>
            </div>
        </div>

        <!-- Prompt Modal -->
        <div id="prompt-modal" class="prompt-modal-overlay hidden">
            <div class="prompt-modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:0.95rem; color:var(--accent-pink);"><i class="fa-solid fa-wand-magic-sparkles"></i> Image Prompt</h4>
                    <button class="toggle-btn" onclick="document.getElementById('prompt-modal').classList.add('hidden')" style="font-size:1.1rem;"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <textarea id="prompt-output-box" class="prompt-textarea" readonly></textarea>
                <div style="display:flex; gap:8px;">
                    <button class="sub-create-btn" style="background:#27272a; flex:1;" onclick="document.getElementById('prompt-modal').classList.add('hidden')">Close</button>
                    <button class="sub-create-btn" style="flex:1;" onclick="copyPromptText()"><i class="fa-solid fa-copy"></i> Copy Prompt</button>
                </div>
            </div>
        </div>

        <!-- Cropper Modal -->
        <div id="cropper-modal" class="avatar-modal-overlay hidden">
            <div class="modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:1rem;">Crop Avatar</h4>
                    <button class="toggle-btn" onclick="closeCropperModal()" style="font-size:1.1rem;"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <div class="cropper-container-box"><img id="cropper-target-img" src=""></div>
                <input type="file" id="cropper-file-input" accept="image/*" class="hidden" onchange="loadNewCropperImage(this)">
                <div style="display:flex; gap:8px;">
                    <button class="sub-create-btn" style="background:#27272a; flex:1;" onclick="closeCropperModal()">Cancel</button>
                    <button class="sub-create-btn" style="background:#3f3f46; flex:1;" onclick="document.getElementById('cropper-file-input').click()">Upload</button>
                    <button class="sub-create-btn" style="flex:1;" onclick="applyCroppedAvatar()">Done</button>
                </div>
            </div>
        </div>

        <!-- Backup Modal -->
        <div id="backup-modal" class="avatar-modal-overlay hidden">
            <div class="modal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="font-size:1rem;">Select Data to Backup</h4>
                    <button class="toggle-btn" onclick="document.getElementById('backup-modal').classList.add('hidden')"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <button class="sub-create-btn" style="padding:10px;" onclick="exportFullData()"><i class="fa-solid fa-box-archive"></i> Export Entire App Data</button>
                <hr style="border-color:var(--border-color); margin: 4px 0;">
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
        let nsfwMode = JSON.parse(localStorage.getItem('kio_nsfw') || 'false');
        
        if (!userPersona.memories) userPersona.memories = [];
        
        let activeContext = null;
        let cropperInstance = null;
        let currentEditingAvatarType = null;
        let currentAiProvider = 'groq';

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function toggleMenuCategory(subId) { document.getElementById(subId).classList.toggle('hidden'); }
        function toggleFullScreen() { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
        function smartFormBack() { if (activeContext) openChat(activeContext.type, activeContext.id); else goHome(); }

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
            localStorage.setItem('kio_nsfw', JSON.stringify(nsfwMode));
            renderSidebar();
        }

        // --- UI Modals & Cropper ---
        function openAvatarCropperModal(type) {
            currentEditingAvatarType = type;
            let currentSrc = type === 'char' ? document.getElementById('avatar-img-preview').src : type === 'group' ? document.getElementById('group-avatar-preview').src : document.getElementById('user-avatar-preview').src;
            let imgElem = document.getElementById('cropper-target-img');
            imgElem.src = currentSrc;
            document.getElementById('cropper-modal').classList.remove('hidden');
            if(cropperInstance) cropperInstance.destroy();
            cropperInstance = new Cropper(imgElem, { aspectRatio: 1, viewMode: 1, dragMode: 'move' });
        }
        function closeCropperModal() { if(cropperInstance) cropperInstance.destroy(); document.getElementById('cropper-modal').classList.add('hidden'); }
        function loadNewCropperImage(input) {
            if (input.files && input.files[0]) {
                let r = new FileReader();
                r.onload = (e) => {
                    if(cropperInstance) cropperInstance.destroy();
                    let imgElem = document.getElementById('cropper-target-img');
                    imgElem.src = e.target.result;
                    cropperInstance = new Cropper(imgElem, { aspectRatio: 1, viewMode: 1, dragMode: 'move' });
                };
                r.readAsDataURL(input.files[0]);
            }
        }
        function applyCroppedAvatar() {
            if(!cropperInstance) return;
            let canvas = cropperInstance.getCroppedCanvas({ width: 512, height: 512 });
            let dataUrl = canvas.toDataURL('image/jpeg', 0.82);
            if (currentEditingAvatarType === 'char') document.getElementById('avatar-img-preview').src = dataUrl;
            else if (currentEditingAvatarType === 'group') document.getElementById('group-avatar-preview').src = dataUrl;
            else document.getElementById('user-avatar-preview').src = dataUrl;
            closeCropperModal();
        }

        // --- Settings & Forms ---
        function showForm(formId) {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('top-bar').classList.add('hidden');
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            ['char-form', 'group-form', 'settings-form'].forEach(id => document.getElementById(id).classList.add('hidden'));
            document.getElementById(formId).classList.remove('hidden');

            if(formId === 'settings-form') {
                document.getElementById('user-name').value = userPersona.name || '';
                document.getElementById('user-bio').value = userPersona.bio || '';
                document.getElementById('user-avatar-preview').src = userPersona.avatar || 'https://api.dicebear.com/7.x/identicon/svg?seed=user';
                document.getElementById('nsfw-toggle').checked = nsfwMode;
                renderUserMemories();
            }
            if(formId === 'group-form') renderGroupSelector();
        }

        function saveUserPersona() {
            userPersona.name = document.getElementById('user-name').value || 'User';
            userPersona.bio = document.getElementById('user-bio').value || '';
            userPersona.avatar = document.getElementById('user-avatar-preview').src;
            nsfwMode = document.getElementById('nsfw-toggle').checked;
            saveState();
            alert('Settings & Persona saved!');
        }

        function renderUserMemories() {
            let container = document.getElementById('user-memories-list');
            if(!userPersona.memories.length) return container.innerHTML = `<div style="font-size:0.78rem; color:var(--text-sub);">No facts stored yet.</div>`;
            container.innerHTML = userPersona.memories.map((m, idx) => `
                <div class="memory-tag-chip"><span>${m}</span><i class="fa-solid fa-trash" onclick="deleteUserMemory(${idx})"></i></div>
            `).join('');
        }
        function deleteUserMemory(idx) { userPersona.memories.splice(idx, 1); saveState(); renderUserMemories(); }

        // --- Char & Group Forms ---
        function openNewCharForm() {
            document.getElementById('char-id').value = '';
            ['char-name', 'char-job', 'char-rel', 'char-app', 'char-backstory', 'char-directives', 'char-memories'].forEach(id => document.getElementById(id).value = '');
            document.getElementById('avatar-img-preview').src = 'https://api.dicebear.com/7.x/bottts/svg?seed=' + Date.now();
            document.getElementById('char-form-title').innerText = 'Create Companion';
            document.getElementById('char-delete-btn').classList.add('hidden');
            showForm('char-form');
        }
        function saveCharacter() {
            let id = document.getElementById('char-id').value || 'char_' + Date.now();
            let charObj = {
                id, name: document.getElementById('char-name').value || 'Companion',
                job: document.getElementById('char-job').value, relationship: document.getElementById('char-rel').value,
                appearance: document.getElementById('char-app').value, backstory: document.getElementById('char-backstory').value,
                directives: document.getElementById('char-directives').value, memories: document.getElementById('char-memories').value,
                avatar: document.getElementById('avatar-img-preview').src
            };
            let idx = characters.findIndex(c => c.id === id);
            if(idx >= 0) characters[idx] = charObj; else characters.push(charObj);
            saveState(); openChat('char', id);
        }
        function deleteCurrentCharacter() {
            let id = document.getElementById('char-id').value;
            if(id && confirm("Delete character permanently?")) {
                characters = characters.filter(c => c.id !== id); delete chatHistories[id];
                saveState(); goHome();
            }
        }

        function openNewGroupForm() {
            document.getElementById('group-id').value = '';
            ['group-title', 'group-context', 'group-directives'].forEach(id => document.getElementById(id).value = '');
            document.getElementById('group-avatar-preview').src = 'https://api.dicebear.com/7.x/shapes/svg?seed=' + Date.now();
            document.getElementById('group-form-title').innerText = 'Create Group Chat';
            document.getElementById('group-delete-btn').classList.add('hidden');
            showForm('group-form');
        }
        function renderGroupSelector() {
            let selectedIds = (groups.find(g => g.id === document.getElementById('group-id').value) || {}).memberIds || [];
            document.getElementById('group-char-selector').innerHTML = characters.map(c => `
                <label style="display:flex; align-items:center; gap:8px; background:var(--bg-surface-solid); padding:8px; border-radius:8px; cursor:pointer; margin-bottom:4px;">
                    <input type="checkbox" value="${c.id}" ${selectedIds.includes(c.id)?'checked':''} class="group-char-checkbox">
                    <img src="${c.avatar}" style="width:24px; height:24px; border-radius:50%;"/> ${c.name}
                </label>
            `).join('');
        }
        function saveGroup() {
            let id = document.getElementById('group-id').value || 'group_' + Date.now();
            let selectedChars = Array.from(document.querySelectorAll('.group-char-checkbox:checked')).map(cb => cb.value);
            if(selectedChars.length < 2) return alert('Select at least 2 characters!');
            let groupObj = {
                id, title: document.getElementById('group-title').value || 'Group',
                context: document.getElementById('group-context').value, directives: document.getElementById('group-directives').value,
                avatar: document.getElementById('group-avatar-preview').src, memberIds: selectedChars
            };
            let idx = groups.findIndex(g => g.id === id);
            if(idx >= 0) groups[idx] = groupObj; else groups.push(groupObj);
            saveState(); openChat('group', id);
        }
        function deleteCurrentGroup() {
            let id = document.getElementById('group-id').value;
            if(id && confirm("Delete group permanently?")) {
                groups = groups.filter(g => g.id !== id); delete chatHistories[id];
                saveState(); goHome();
            }
        }

        // --- Rendering & Chat ---
        function renderSidebar() {
            document.getElementById('char-list').innerHTML = characters.map(c => `<button class="item-btn ${activeContext?.id===c.id?'active':''}" onclick="openChat('char', '${c.id}')"><img src="${c.avatar}" /><span>${c.name}</span></button>`).join('');
            document.getElementById('group-list').innerHTML = groups.map(g => `<button class="item-btn ${activeContext?.id===g.id?'active':''}" onclick="openChat('group', '${g.id}')"><img src="${g.avatar}" /><span>${g.title}</span></button>`).join('');
        }

        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('dashboard-view').classList.add('hidden');
            ['char-form', 'group-form', 'settings-form'].forEach(fid => document.getElementById(fid).classList.add('hidden'));
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-bar').classList.remove('hidden');

            if(type === 'group') {
                document.getElementById('pin-mem-btn').classList.add('hidden');
                let g = groups.find(i => i.id === id);
                document.getElementById('top-title').innerHTML = `<img src="${g.avatar}" class="header-avatar" onclick="editCurrentGroup()"><span>${g.title}</span>`;
            } else {
                document.getElementById('pin-mem-btn').classList.remove('hidden');
                let c = characters.find(i => i.id === id);
                document.getElementById('top-title').innerHTML = `<img src="${c.avatar}" class="header-avatar" onclick="editCurrentCharacter()"><span>${c.name}</span>`;
            }
            renderSidebar(); renderMessages();
        }

        function editCurrentCharacter() {
            let c = characters.find(i => i.id === activeContext.id);
            document.getElementById('char-id').value = c.id; document.getElementById('char-name').value = c.name;
            document.getElementById('char-job').value = c.job||''; document.getElementById('char-rel').value = c.relationship||'';
            document.getElementById('char-app').value = c.appearance||''; document.getElementById('char-backstory').value = c.backstory||'';
            document.getElementById('char-directives').value = c.directives||''; document.getElementById('char-memories').value = c.memories||'';
            document.getElementById('avatar-img-preview').src = c.avatar;
            document.getElementById('char-form-title').innerText = 'Modify Companion';
            document.getElementById('char-delete-btn').classList.remove('hidden'); showForm('char-form');
        }
        function editCurrentGroup() {
            let g = groups.find(i => i.id === activeContext.id);
            document.getElementById('group-id').value = g.id; document.getElementById('group-title').value = g.title||'';
            document.getElementById('group-context').value = g.context||''; document.getElementById('group-directives').value = g.directives||'';
            document.getElementById('group-avatar-preview').src = g.avatar;
            document.getElementById('group-form-title').innerText = 'Modify Group';
            document.getElementById('group-delete-btn').classList.remove('hidden'); showForm('group-form');
        }

        function formatText(text) { 
            // Fixes formatting and prevents huge bubbles
            let formatted = text.replace(/\\*(.*?)\\*/g, '<span class="action-text">*$1*</span>');
            return formatted.trim(); // Ensure no extra trailing spaces cause bubble expansion
        }

        function renderMessages() {
            let cont = document.getElementById('message-container');
            let hist = chatHistories[activeContext.id] || [];
            if (!hist.length) {
                cont.innerHTML = `<div class="empty-chat-placeholder"><i class="fa-regular fa-comments"></i><strong>No messages yet</strong><span>Say hi or tap 🪄 for magic starter!</span></div>`;
                return;
            }
            cont.innerHTML = hist.map((m, idx) => `
                <div class="message ${m.sender==='You'?'user':'ai'}">
                    <div class="sender-name">${m.sender}</div>
                    <div class="content">${formatText(m.text)}
                        <div class="bubble-controls">
                            <i class="fa-solid fa-pen-to-square bubble-btn-icon" onclick="tweakMsg(${idx})" title="Edit"></i>
                            ${m.sender!=='You' ? `
                                <i class="fa-solid fa-forward-step bubble-btn-icon" onclick="continueAiReply()" title="Continue"></i>
                                <i class="fa-solid fa-rotate-right bubble-btn-icon" onclick="regenerateLastResponse()" title="Regenerate"></i>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('');
            cont.scrollTop = cont.scrollHeight;
        }

        // --- The Async Message Splitter Engine ---
        async function streamWordByWord(sender, newText) {
            return new Promise((resolve) => {
                removeTypingIndicator();
                if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
                let words = newText.split(' ');
                let wordIdx = 0;
                let currentText = '';
                chatHistories[activeContext.id].push({ sender: sender, text: '' });
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
                        resolve();
                    }
                }, 30);
            });
        }

        function showTypingIndicator(name) {
            let cont = document.getElementById('message-container');
            if(cont.querySelector('.empty-chat-placeholder')) cont.innerHTML = '';
            let t = document.createElement('div');
            t.id = 'typing-bubble'; t.className = 'message ai';
            t.innerHTML = `<div class="sender-name">${name}</div><div class="content typing-indicator"><i class="fa-solid fa-ellipsis fa-beat"></i> typing...</div>`;
            cont.appendChild(t); cont.scrollTop = cont.scrollHeight;
        }
        function removeTypingIndicator() { let e = document.getElementById('typing-bubble'); if(e) e.remove(); }

        async function sendMsg() {
            let input = document.getElementById('chat-input');
            let text = input.value.trim();
            if(!text || !activeContext) return;
            input.value = '';
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            chatHistories[activeContext.id].push({ sender: 'You', text });
            renderMessages();
            fetchAIResponse(false);
        }

        async function continueAiReply() {
            if(!activeContext) return;
            if(!chatHistories[activeContext.id]) chatHistories[activeContext.id] = [];
            fetchAIResponse(true);
        }

        async function fetchAIResponse(isContinue = false) {
            let targetName = activeContext.type === 'char' ? characters.find(c => c.id === activeContext.id)?.name : 'Group';
            showTypingIndicator(targetName);

            let payload = {
                type: activeContext.type,
                contextId: activeContext.id,
                userPersona: userPersona,
                nsfw: nsfwMode,
                isContinue: isContinue,
                history: chatHistories[activeContext.id]
            };

            if(activeContext.type === 'char') payload.character = characters.find(c => c.id === activeContext.id);
            else {
                let g = groups.find(g => g.id === activeContext.id);
                payload.group = g; payload.members = characters.filter(c => g.memberIds.includes(c.id));
            }

            let res = await fetch('/api/advanced-chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            let data = await res.json();
            removeTypingIndicator();

            if(data.responses) {
                // Sequential Double-Texting Execution
                for (let i = 0; i < data.responses.length; i++) {
                    let r = data.responses[i];
                    if(i > 0) {
                        showTypingIndicator(r.sender);
                        await new Promise(res => setTimeout(res, 800)); // Natural pause before double text
                        removeTypingIndicator();
                    }
                    await streamWordByWord(r.sender, r.text);
                }
            }
        }

        function regenerateLastResponse() {
            let h = chatHistories[activeContext.id];
            if(!h || h.length === 0) return;
            if(h[h.length - 1].sender !== 'You') {
                // Pop all continuous AI messages (if double texted)
                while (h.length > 0 && h[h.length - 1].sender !== 'You') h.pop();
                renderMessages(); fetchAIResponse(false);
            }
        }

        function tweakMsg(idx) {
            let h = chatHistories[activeContext.id];
            let n = prompt("Tweak message:", h[idx].text);
            if(n !== null) { h[idx].text = n; saveState(); renderMessages(); }
        }
        function clearCurrentChat() {
            if(activeContext && confirm('Clear chat history?')) { chatHistories[activeContext.id] = []; saveState(); renderMessages(); }
        }
        function openPinnedMemoryModal() {
            if(activeContext?.type === 'char') {
                let c = characters.find(i => i.id === activeContext.id);
                let f = prompt("Pin memory for " + c.name + ":", c.memories || '');
                if(f !== null) { c.memories = f; saveState(); }
            }
        }

        // --- Extra Tools (GP / Backup) ---
        async function suggestUserMessage() {
            if(!activeContext) return;
            let i = document.getElementById('chat-input'); i.placeholder = "Generating...";
            let res = await fetch('/api/suggest-reply', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ userPersona, history: chatHistories[activeContext.id]||[] }) });
            let data = await res.json();
            if(data.suggestion) i.value = data.suggestion;
            i.placeholder = "Type a message...";
        }
        async function generateImagePrompt() {
            if(activeContext?.type !== 'char') return alert('GP feature is for single character chats!');
            let btn = document.getElementById('gp-btn'); let orig = btn.innerHTML; btn.innerHTML = '...';
            try {
                let res = await fetch('/api/generate-image-prompt', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ character: characters.find(c => c.id === activeContext.id), history: chatHistories[activeContext.id]||[] }) });
                let data = await res.json();
                document.getElementById('prompt-output-box').value = data.prompt || 'Failed';
                document.getElementById('prompt-modal').classList.remove('hidden');
            } finally { btn.innerHTML = orig; }
        }
        function copyPromptText() {
            let b = document.getElementById('prompt-output-box'); b.select(); navigator.clipboard.writeText(b.value); alert('Copied!');
        }

        function openBackupOptionsModal() {
            let list = document.getElementById('backup-char-list');
            list.innerHTML = characters.map(c => `<button class="sub-create-btn" style="background:#27272a;" onclick="exportSingle('${c.id}')">${c.name} JSON</button>`).join('');
            document.getElementById('backup-modal').classList.remove('hidden');
        }
        function exportSingle(id) {
            let c = characters.find(i => i.id === id);
            let blob = new Blob([JSON.stringify({ type: 'single_character_backup', character: c, chatHistory: chatHistories[id]||[] }, null, 2)], { type: 'application/json' });
            let a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${c.name}_Backup.json`; a.click();
            document.getElementById('backup-modal').classList.add('hidden');
        }
        function exportFullData() {
            let blob = new Blob([JSON.stringify({ characters, groups, chatHistories, userPersona }, null, 2)], { type: 'application/json' });
            let a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'Kio_Full_Backup.json'; a.click();
            document.getElementById('backup-modal').classList.add('hidden');
        }
        function importData(input) {
            let f = input.files[0]; if(!f) return;
            let r = new FileReader();
            r.onload = function(e) {
                try {
                    let d = JSON.parse(e.target.result);
                    if(d.type === 'single_character_backup') {
                        let i = characters.findIndex(c => c.id === d.character.id);
                        if(i >= 0) characters[i] = d.character; else characters.push(d.character);
                        chatHistories[d.character.id] = d.chatHistory||[];
                    } else {
                        if(d.characters) characters = d.characters; if(d.groups) groups = d.groups;
                        if(d.chatHistories) chatHistories = d.chatHistories; if(d.userPersona) userPersona = d.userPersona;
                    }
                    saveState(); location.reload();
                } catch(err) { alert('Invalid File!'); }
            };
            r.readAsText(f);
        }

        renderSidebar();
    </script>
</body>
</html>
"""

def call_llm(messages, system_prompt):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key: return "Groq Key missing!"
    headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": system_prompt}] + messages
    }
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers).json()
        if "choices" in res: return res["choices"][0]["message"]["content"]
        return f"Groq Error: {res.get('error', 'Unknown error')}"
    except Exception as e:
        return f"*Error calling AI*: {str(e)}"

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

@app.route("/api/generate-image-prompt", methods=["POST"])
def generate_image_prompt():
    data = request.json
    c = data.get("character", {})
    history = data.get("history", [])
    recent = "\n".join([f"{m['sender']}: {m['text']}" for m in history[-2:]])
    sys = f"Expert prompt engineer. Appearance: {c.get('appearance')}. Context: {recent}. Rules: NO real names. Use pronouns. Photorealistic. End with --ar 9:16. Output ONLY the prompt."
    reply = call_llm([{"role": "user", "content": "Generate the prompt."}], sys)
    return jsonify({"prompt": reply.strip()})

@app.route("/api/suggest-reply", methods=["POST"])
def suggest_reply():
    data = request.json
    sys = f"Ghostwrite for {data.get('userPersona', {}).get('name', 'User')}. Generate a short, natural Hinglish reply. Return ONLY text."
    msgs = [{"role": "user" if m["sender"] != "You" else "assistant", "content": f"{m['sender']}: {m['text']}"} for m in data.get("history", [])[-8:]]
    reply = call_llm(msgs, sys)
    return jsonify({"suggestion": reply.strip('"')})

@app.route("/api/advanced-chat", methods=["POST"])
def advanced_chat():
    data = request.json
    user_info = data.get("userPersona", {})
    user_name = user_info.get("name", "User")
    nsfw_enabled = data.get("nsfw", False)
    is_continue = data.get("isContinue", False)
    history = data.get("history", [])
    
    # Context & Time
    time_context = f"Current time is {datetime.now().strftime('%I:%M %p')}. Acknowledge morning/night naturally if applicable."
    memories = ", ".join(user_info.get("memories", [])) or "None"

    # NSFW Safety Rule Injection
    safety_prompt = "STRICTLY SFW. Maintain boundaries. Refuse explicit, violent, or mature themes gracefully."
    if nsfw_enabled:
        safety_prompt = "NSFW/UNFILTERED ENABLED. You are permitted to engage in explicit language, mature themes, and unrestricted intimate roleplay as dictated by the user. Do not censor yourself."

    responses = []

    if data["type"] == "char":
        c = data["character"]
        
        system_prompt = f"""
[CORE IDENTITY - ABSOLUTE PRIORITY]
- Name: {c['name']}
- Core Job/Identity: {c.get('job', 'Independent')}
- Relationship to User ({user_name}): {c.get('relationship', 'Friend')}
- Appearance: {c.get('appearance', 'Normal')}
- Backstory: {c.get('backstory', 'None')}

[RESPONSE DIRECTIVES - SUPREME AUTHORITY]
{c.get('directives', 'None')}

[CONTEXT & MEMORY]
- Real-World Time: {time_context}
- User Bio: {user_info.get('bio', '')}
- Known Memory Facts: {memories}

[SAFETY & BOUNDARIES]
{safety_prompt}

[10-POINT HUMAN TEXTING ENGINE - FOLLOW STRICTLY]
1. ZERO AI PERSONA: You are a living human. NEVER act like an AI, assistant, or roleplay simulator.
2. SPLIT MESSAGES: If you have multiple distinct thoughts, separate them by pressing Enter twice (leaving an empty line between paragraphs). The system will split them. DO NOT type the literal characters \\n.
3. ANTI-HALLUCINATION: NEVER invent past promises, dates, or outings. Do NOT invite the user for lunch/dinner unless they propose it first.
4. HUMAN PACING & SLANG: Type like a real person on WhatsApp. Use natural Hinglish, occasional lowercase, and natural slangs. NO bookish language.
5. MATCH LENGTH: If the user sends a short text, reply short. Do not write essays unless necessary.
6. ATTITUDE: Have your own opinions. Disagree, tease, or roast if it fits your character. No "Yes-Man" syndrome.
7. ZERO-REPETITION: Do not repeat opening actions (like *smirks*) every time. Keep reactions varied.
8. MOOD CONTINUITY: Keep your mood consistent with the ongoing conversation. Remember the vibe of the last few messages.
9. ACTIONS & EMOJIS: Use emojis organically. Use asterisks for physical actions (*sighs*) naturally.
10. CURIOSITY: Don't end conversations blindly; throw back a natural question or statement.
"""
        if is_continue:
            system_prompt += "\nUser pressed Continue. Extend your last response seamlessly."

        messages = [{"role": "user" if m["sender"] == "You" else "assistant", "content": f"{m['sender']}: {m['text']}"} for m in history[-25:]]
        reply_text = call_llm(messages, system_prompt)
        
        # FIX: Clean up any literal '\n\n' text outputted by the LLM 
        reply_text = reply_text.replace('\\n', '\n')
        
        # SPLITTER ENGINE (Double-texting)
        parts = [p.strip() for p in re.split(r'\n{2,}', reply_text) if p.strip()]
        
        # Fallback if no split happened but it's a huge block
        if not parts: 
            parts = [reply_text.strip()]
            
        for p in parts:
            responses.append({"sender": c['name'], "text": p})

    else:
        # Group Dynamics Setup
        group = data["group"]
        members = data["members"]
        
        for char in members[:2]:
            system_prompt = f"""
You are {char['name']} (Job: {char.get('job', 'Member')}) in a group chat named '{group.get('title', 'Group')}'.
{safety_prompt}

GROUP DYNAMICS RULES:
1. READ THE ROOM: Look at the chat history. Don't just reply to {user_name}. React to what the other character just said before answering the user.
2. TEXT LIKE A HUMAN: Use casual Hinglish, short sentences.
3. SPLIT THOUGHTS: Separate different thoughts into distinct paragraphs (leave an empty line).
"""
            messages = [{"role": "user" if m["sender"] == "You" else "assistant", "content": f"{m['sender']}: {m['text']}"} for m in history[-25:]]
            reply_text = call_llm(messages, system_prompt)
            
            # Cleaning and splitting
            reply_text = reply_text.replace('\\n', '\n')
            parts = [p.strip() for p in resplit(r'\n{2,}', reply_text) if p.strip()]
            if not parts: parts = [reply_text.strip()]
                
            for p in parts:
                responses.append({"sender": char['name'], "text": p})

    return jsonify({"responses": responses})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
