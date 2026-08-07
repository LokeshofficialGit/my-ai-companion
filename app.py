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
    <title>Aura</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; width: 100vw; overflow: hidden; }
        
        /* Mobile Frame */
        .app-container { width: 100%; max-width: 440px; height: 100vh; background: #09090b; display: flex; flex-direction: column; position: relative; overflow: hidden; }
        @media (min-width: 500px) { .app-container { height: 92vh; border-radius: 24px; border: 1px solid #27272a; } }

        .top-bar { height: 50px; background: #121215; border-bottom: 1px solid #27272a; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; }
        .main-workspace { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
        
        /* Sidebar */
        .sidebar { position: absolute; left: 0; top: 0; width: 80%; height: 100%; background: #121215; z-index: 100; transform: translateX(-100%); transition: 0.3s; padding: 20px; border-right: 1px solid #27272a; }
        .sidebar.open { transform: translateX(0); }

        /* Dashboard */
        .welcome-dashboard { padding: 40px 20px; display: flex; flex-direction: column; align-items: center; }
        .quick-card { width: 100%; background: #121215; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer; display: flex; align-items: center; gap: 15px; border: 1px solid #27272a; }
        
        /* Chat UI */
        .chat-messages { flex: 1; padding: 15px; display: flex; flex-direction: column; gap: 15px; }
        .message { display: flex; gap: 10px; max-width: 90%; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .content { background: #121215; padding: 10px 14px; border-radius: 12px; font-size: 0.9rem; position: relative; }
        .message.user .content { background: #9333ea; color: white; }
        .edit-link { font-size: 0.7rem; color: #71717a; text-decoration: underline; cursor: pointer; margin-top: 5px; display: block; }
        
        .input-area { padding: 10px; background: #121215; display: flex; gap: 5px; }
        .input-area input { flex: 1; background: #09090b; border: 1px solid #27272a; padding: 10px; border-radius: 8px; color: white; }
        .icon-btn { background: #27272a; border: none; color: #fff; width: 35px; border-radius: 8px; cursor: pointer; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar" id="sidebar">
            <button onclick="toggleSidebar()" style="background:none; border:none; color:white; font-size:1.2rem;"><i class="fa-solid fa-xmark"></i></button>
            <div style="margin-top: 20px;" id="nav-list"></div>
        </div>

        <div class="top-bar">
            <button class="toggle-btn" onclick="toggleSidebar()" style="background:none; border:none; color:white;"><i class="fa-solid fa-bars"></i></button>
            <div id="top-title" style="font-weight:bold;">Aura</div>
            <div id="top-actions" class="hidden" style="display:flex; gap:8px;">
                <button class="icon-btn" onclick="editCurrentCharacter()"><i class="fa-solid fa-wrench"></i></button>
                <button class="icon-btn" onclick="clearCurrentChat()"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <div class="main-workspace" id="main-content">
            <!-- Initial Dashboard -->
            <div id="welcome-view" class="welcome-dashboard">
                <i class="fa-solid fa-sparkles" style="font-size:3rem; color:#a855f7;"></i>
                <h2 style="margin:15px 0;">Welcome back!</h2>
                <div class="quick-card" onclick="openNewCharForm()"><i class="fa-solid fa-plus"></i> <strong>New Character</strong></div>
                <div class="quick-card" onclick="showForm('settings-form')"><i class="fa-solid fa-gear"></i> <strong>Backup & Settings</strong></div>
            </div>
            
            <!-- Chat & Forms go here -->
            <div id="chat-view" class="hidden" style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                <div class="chat-messages" id="message-container"></div>
                <div class="input-area">
                    <button class="icon-btn" onclick="continueAiReply()">>></button>
                    <input type="text" id="chat-input" placeholder="Type...">
                    <button class="icon-btn" onclick="sendMsg()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>
            <div id="forms-area"></div>
        </div>
    </div>

    <script>
        // CORE FUNCTIONS
        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        
        function openChat(type, id) {
            activeContext = { type, id };
            document.getElementById('welcome-view').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-actions').classList.remove('hidden'); // SHOW HEADER ACTIONS
            renderMessages();
        }

        function showForm(formId) {
            document.getElementById('welcome-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('top-actions').classList.add('hidden'); // HIDE HEADER ACTIONS
            // logic to show settings/char form...
        }

        // Render with clean Edit link instead of Pencil Icon
        function renderMessages() {
            // ... inside message loop ...
            // html += `<span class="edit-link" onclick="tweakMsg(${idx})">Edit</span>`;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_CODE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
