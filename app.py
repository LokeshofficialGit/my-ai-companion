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

        [data-theme="light"] {
            --bg-main: #f4f4f5;
            --bg-surface: #ffffff;
            --bg-surface-solid: #ffffff;
            --bg-input: #e4e4e7;
            --border-color: rgba(168, 85, 247, 0.2);
            --text-main: #09090b;
            --text-sub: #52525b;
            --action-text: #be185d;
            --ai-msg-bg: #ffffff;
            --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);

            --sidebar-bg: #ffffff;
            --sidebar-border: rgba(168, 85, 247, 0.15);
            --sidebar-text: #09090b;
            --sidebar-btn-bg: #f4f4f5;
            --sidebar-btn-hover: #e4e4e7;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        
        html, body { height: 100dvh; width: 100vw; background: #000000; color: var(--text-main); overflow: hidden; display: flex; justify-content: center; align-items: center; }

        .app-container { width: 100%; max-width: 440px; height: 100dvh; background: var(--bg-main); display: flex; flex-direction: column; position: relative; overflow: hidden; border: 1px solid var(--border-color); }
        @media (min-width: 500px) { .app-container { height: 94dvh; border-radius: 20px; } }

        /* Top Bar Styling */
        .top-bar { height: 56px; background: var(--bg-surface); border-bottom: 2px solid transparent; border-image: linear-gradient(90deg, #a855f7, #ec4899) 1; display: flex; align-items: center; justify-content: space-between; padding: 0 12px; z-index: 10; }
        .top-title { font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-main); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; margin-left: 4px; }

        /* Dashboard */
        .dashboard { flex: 1; padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow-y: auto; }
        .dash-logo-large { width: 120px; height: 120px; margin-bottom: 20px; filter: drop-shadow(0 0 16px rgba(236,72,153,0.6)); }
        .dash-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 6px; }
        .dash-sub { font-size: 0.85rem; color: var(--text-sub); margin-bottom: 30px; }
        .dash-card { width: 100%; background: var(--bg-surface); border: 1px solid var(--border-color); padding: 16px; border-radius: 16px; display: flex; align-items: center; gap: 14px; margin-bottom: 12px; cursor: pointer; }
        .dash-card i { font-size: 1.2rem; color: var(--accent-pink); }
        
        /* Sidebar & Others (kept for structure) */
        .sidebar { position: absolute; top:0; left:0; width: 85%; height: 100%; background: var(--sidebar-bg); z-index: 100; transform: translateX(-100%); transition: 0.3s; }
        .sidebar.open { transform: translateX(0); }
        
        .workspace { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .hidden { display: none !important; }
        
        /* Logos */
        .aura-logo-svg { width: 32px; height: 32px; }
    </style>
</head>
<body data-theme="dark">

    <svg class="hidden">
        <defs>
            <linearGradient id="auraLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#a855f7"/>
                <stop offset="100%" stop-color="#ec4899"/>
            </linearGradient>
            <g id="aura-brand-icon">
                <circle cx="50" cy="50" r="38" fill="none" stroke="url(#auraLogoGrad)" stroke-width="10"/>
                <path d="M 50 18 L 70 72 L 58 72 L 53 58 L 47 58 L 42 72 L 30 72 Z M 48 45 L 50 34 L 52 45 Z" fill="url(#auraLogoGrad)"/>
                <path d="M 59 62 L 68 76 Q 72 82 78 78 L 74 68 Z" fill="url(#auraLogoGrad)"/>
            </g>
        </defs>
    </svg>

    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar" id="sidebar">
            <div style="padding:20px; color:var(--accent-pink); font-weight:800; font-size:1.2rem; display:flex; justify-content:space-between;">
                Aura
                <button onclick="toggleSidebar()" style="background:none; border:none; color:inherit;"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <!-- Menu items placeholder -->
        </div>

        <!-- Dynamic Header (Visible only in Chat) -->
        <div class="top-bar hidden" id="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                <div class="top-title" id="top-title"></div>
            </div>
            <div style="display: flex;" id="top-actions">
                <button class="icon-btn"><i class="fa-solid fa-thumbtack"></i></button>
                <button class="icon-btn"><i class="fa-solid fa-wrench"></i></button>
                <button class="icon-btn"><i class="fa-solid fa-rotate-right"></i></button>
                <button class="icon-btn"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <!-- Workspace -->
        <div class="workspace">
            <div id="dashboard-view" class="dashboard">
                <div style="position: absolute; top: 16px; left: 16px;">
                    <button class="icon-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
                </div>
                <svg viewBox="0 0 100 100" class="dash-logo-large"><use href="#aura-brand-icon"/></svg>
                <h2 class="dash-title">Welcome to Aura</h2>
                <p class="dash-sub">Your secure personal AI companion space.</p>
                <div class="dash-card" onclick="openChat('char', '1')">
                    <i class="fa-solid fa-user-plus"></i>
                    <div><strong>Create AI Companion</strong><span>Custom backstory</span></div>
                </div>
            </div>

            <div id="chat-view" class="hidden">
                <div class="chat-messages" id="message-container"></div>
            </div>
        </div>
    </div>

    <script>
        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('open'); }
        function openChat(type, id) {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('top-bar').classList.remove('hidden');
            document.getElementById('top-title').innerHTML = `<svg viewBox="0 0 100 100" class="aura-logo-svg"><use href="#aura-brand-icon"/></svg> Kareena <span style="font-size:0.6rem; color:#ec4899; margin-left:4px;">Warm (55%)</span>`;
        }
        function goHome() {
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('top-bar').classList.add('hidden');
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
