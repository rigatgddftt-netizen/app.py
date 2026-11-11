from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import socket
import urllib.request
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'geektyper_secret_key'

# === লগইন পেজ ===
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>System Login</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #000; color: #0f0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; flex-direction: column; }
        input { padding: 10px; margin: 5px; background: #111; color: #0f0; border: 1px solid #0f0; font-family: 'Courier New', monospace; }
        button { padding: 10px 20px; background: #0f0; color: #000; border: none; cursor: pointer; font-weight: bold; margin-top: 10px;}
        .error { color: red; }
        h1 { text-shadow: 0 0 10px #0f0; }
    </style>
</head>
<body>
    <h1>☠️ SECURE ACCESS ☠️</h1>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">LOGIN</button>
    </form>
</body>
</html>
'''

# === মূল কনসোল পেজ (GeekTyper ডিজাইন) ===
MAIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>GeekTyper Terminal</title>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; background: #000; color: #0f0; font-family: 'Courier New', monospace; overflow: hidden; }
        
        /* ম্যাট্রিক্স ইফেক্ট */
        #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; opacity: 0.1; }
        
        /* মূল টার্মিনাল */
        .terminal { position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 10px; box-sizing: border-box; z-index: 1; display: flex; flex-direction: column; }
        
        /* হেডার (উপরে বাম দিকে) */
        .header { font-size: 10px; color: #0a0; text-shadow: 0 0 5px #0f0; line-height: 1.2; margin-bottom: 10px; }
        
        /* ডান দিকের ফোল্ডার/মেনু আইকন */
        .sidebar { position: absolute; top: 10px; right: 10px; display: flex; flex-direction: column; gap: 5px; z-index: 2; }
        .folder { display: flex; align-items: center; justify-content: flex-end; cursor: pointer; font-size: 12px; color: #0f0; text-shadow: 0 0 5px #0f0; transition: 0.2s; }
        .folder:hover { color: #fff; text-shadow: 0 0 10px #fff; }
        .folder span { margin-left: 5px; }
        
        /* মেইন আউটপুট এরিয়া */
        .output { flex: 1; overflow-y: auto; font-size: 12px; white-space: pre-wrap; padding-bottom: 50px; }
        
        /* ইনপুট এরিয়া */
        .input-area { display: flex; align-items: center; background: #000; border-top: 1px solid #333; padding: 5px; }
        .input-area span { color: #0f0; margin-right: 5px; }
        .input-area input { flex: 1; background: transparent; border: none; color: #0f0; font-family: 'Courier New', monospace; font-size: 14px; outline: none; }
        
        /* গ্লিচ ইফেক্ট */
        .glitch { animation: glitch 1s linear infinite; }
        @keyframes glitch { 2%, 64% { transform: translate(2px,0) skew(0deg); } 4%, 60% { transform: translate(-2px,0) skew(0deg); } 62% { transform: translate(0,0) skew(5deg); } }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>

    <div class="terminal">
        <!-- হেডার -->
        <div class="header">
            <div id="clock">00:00:00</div>
            <div>SCP Secure Systems v4.2654.2</div>
            <div style="color: #8f8;">SLEVEL 6 Security Clearance Required</div>
            <div>DATA LOCKED</div>
        </div>

        <!-- মেইন আউটপুট -->
        <div class="output" id="output">
            <div class="glitch">☠️ GEEKTYPER SYSTEM INITIALIZED ☠️</div>
            <div>=========================================</div>
            <div>Welcome, Hacker. Type a command or click a folder.</div>
            <div>Type 'help' to see available commands.</div>
            <br>
            <div>[+] Ready for input...</div>
        </div>

        <!-- ইনপুট এরিয়া -->
        <div class="input-area">
            <span>C:\\HACKER></span>
            <input type="text" id="commandInput" autofocus onkeydown="handleCommand(event)">
        </div>
    </div>

    <!-- ডান দিকের সাইডবার -->
    <div class="sidebar">
        <div class="folder" onclick="runTool('nmap')"><span>📁 nmap_scan</span></div>
        <div class="folder" onclick="runTool('ipinfo')"><span>📁 ip_tracker</span></div>
        <div class="folder" onclick="runTool('ai')"><span>📁 hacker_ai</span></div>
        <div class="folder" onclick="runTool('hash')"><span>📁 hash_cracker</span></div>
    </div>

    <script>
        // ম্যাট্রিক্স ইফেক্ট
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        const fontSize = 16; const columns = canvas.width / fontSize;
        const drops = []; for (let x = 0; x < columns; x++) drops[x] = 1;
        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = letters.charAt(Math.floor(Math.random() * letters.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(draw, 33);

        // ঘড়ি আপডেট
        setInterval(() => {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString();
        }, 1000);

        // কমান্ড হ্যান্ডলার
        async function handleCommand(event) {
            if (event.key === 'Enter') {
                const input = document.getElementById('commandInput');
                const command = input.value.trim();
                if (command) {
                    appendOutput(`C:\\\\HACKER> ${command}`);
                    await processCommand(command);
                }
                input.value = '';
            }
        }

        // আউটপুটে লেখা যোগ করা
        function appendOutput(text) {
            const outputDiv = document.getElementById('output');
            outputDiv.innerText += '\\n' + text;
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }

        // কমান্ড প্রসেসিং
        async function processCommand(cmd) {
            appendOutput("[*] Executing: " + cmd);
            
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({cmd: cmd})
                });
                const data = await response.json();
                appendOutput(data.output);
            } catch (error) {
                appendOutput("[-] Error: " + error);
            }
        }

        // সাইডবার থেকে টুল চালানো
        function runTool(tool) {
            const input = document.getElementById('commandInput');
            if (tool === 'nmap') {
                input.value = 'nmap 8.8.8.8 53,443';
            } else if (tool === 'ipinfo') {
                input.value = 'ipinfo google.com';
            } else if (tool === 'ai') {
                input.value = 'ai How to secure a server?';
            } else if (tool === 'hash') {
                input.value = 'hash hello';
            }
            input.focus();
        }
    </script>
</body>
</html>
'''

# === বাকি সব লজিক (একই থাকবে, শুধু টার্মিনাল কমান্ডের জন্য আপডেট) ===
@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template_string(MAIN_PAGE)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'hacker123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Access Denied.'
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# === টার্মিনাল কমান্ড এক্সিকিউটর ===
@app.route('/execute', methods=['POST'])
def execute():
    if 'logged_in' not in session:
        return jsonify({'output': '[-] Unauthorized.'})
        
    data = request.get_json()
    cmd = data.get('cmd', '')
    output = ""

    # ১. nmap স্ক্যান
    if cmd.startswith('nmap'):
        parts = cmd.split()
        ip = parts[1]
        ports_str = parts[2]
        ports = [int(p) for p in ports_str.split(',')]
        output = f"[*] Starting Nmap scan on {ip}...\\n"
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                output += f"[+] Port {port}: OPEN\\n"
            s.close()

    # ২. আইপি ট্র্যাকার
    elif cmd.startswith('ipinfo'):
        domain = cmd.split()[1]
        try:
            ip = socket.gethostbyname(domain)
            output = f"[+] Target IP: {ip}\\n"
            req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=66846719", headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=5)
            ip_data = json.loads(res.read().decode())
            if ip_data.get('status') == 'success':
                output += f"Country: {ip_data.get('country')}\\nRegion: {ip_data.get('regionName')}\\nCity: {ip_data.get('city')}\\nISP: {ip_data.get('isp')}\\n"
        except Exception as e:
            output = f"[-] Error: {e}"

    # ৩. AI চ্যাট
    elif cmd.startswith('ai '):
        prompt = cmd[3:]
        try:
            api_url = "https://text.pollinations.ai/openai"
            payload = json.dumps({
                "model": "openai",
                "messages": [{"role": "user", "content": prompt}]
            }).encode('utf-8')
            req = urllib.request.Request(api_url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=50)
            res_data = json.loads(res.read().decode())
            output = res_data['choices'][0]['message']['content']
        except Exception as e:
            output = f"[-] AI Error: {e}"

    # ৪. হেল্প কমান্ড
    elif cmd == 'help':
        output = """Available Commands:
nmap <ip> <port1,port2> - Scan ports
ipinfo <domain> - Get IP location
ai <question> - Ask AI anything
hash <text> - Generate MD5/SHA256
clear - Clear screen"""

    else:
        output = "[-] Command not found. Type 'help' for available commands."

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
