from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import socket
import urllib.request
import json
import os
import hashlib

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

# === মূল টার্মিনাল পেজ (GeekTyper মোবাইল ডিজাইন) ===
MAIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GeekTyper Mobile</title>
    <style>
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body, html { margin: 0; padding: 0; height: 100%; background: #000; color: #0f0; font-family: 'Courier New', monospace; overflow: hidden; font-size: 12px; }
        
        /* টার্মিনাল কন্টেইনার */
        .terminal-container { display: flex; flex-direction: column; height: 100%; padding: 8px; }
        
        /* হেডার */
        .header { font-size: 10px; color: #0a0; text-shadow: 0 0 3px #0f0; line-height: 1.3; margin-bottom: 5px; border-bottom: 1px solid #222; padding-bottom: 5px; display: flex; justify-content: space-between; }
        
        /* মেইন আউটপুট এরিয়া */
        .output-box { flex: 1; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 11px; line-height: 1.4; padding-bottom: 10px; }
        .output-box::-webkit-scrollbar { width: 3px; }
        .output-box::-webkit-scrollbar-thumb { background: #0f0; }
        
        /* ইনপুট এরিয়া */
        .input-area { display: flex; align-items: center; border-top: 1px solid #333; padding-top: 5px; }
        .input-area span { color: #0f0; margin-right: 5px; font-size: 12px; }
        .input-area input { flex: 1; background: transparent; border: none; color: #0f0; font-family: 'Courier New', monospace; font-size: 13px; outline: none; padding: 5px 0; }
        
        /* ডান দিকের সাইডবার (একদম GeekTyper-এর মতো) */
        .sidebar { position: absolute; top: 50px; right: 10px; display: flex; flex-direction: column; gap: 8px; z-index: 10; }
        .folder { display: flex; align-items: center; cursor: pointer; font-size: 14px; color: #0f0; text-shadow: 0 0 5px #0f0; transition: 0.2s; background: rgba(0,20,0,0.8); padding: 4px; border-radius: 3px; border: 1px solid #0f0; }
        .folder:hover { background: #0f0; color: #000; }
        
        /* এনিমেশন ইফেক্ট */
        .blink { animation: blink 1s step-end infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        .glitch { animation: glitch 0.5s linear infinite; }
        @keyframes glitch { 0% { transform: translate(1px,0); } 50% { transform: translate(-1px,0); } 100% { transform: translate(1px,0); } }
    </style>
</head>
<body>
    <div class="terminal-container">
        <!-- হেডার (GeekTyper স্টাইল) -->
        <div class="header">
            <div>
                <div id="clock">00:00:00</div>
                <div>SCP Secure Systems v4.2654.2</div>
                <div style="color: #8f8;">SLEVEL 6 Security Clearance Required</div>
                <div style="color: #f00;">DATA LOCKED</div>
            </div>
        </div>

        <!-- মেইন আউটপুট -->
        <div class="output-box" id="output">
[+] SYSTEM INITIALIZED...
[+] CONNECTING TO SECURE SERVER...
[+] ACCESS GRANTED.
[+] TYPE 'help' FOR COMMANDS.

<div class="glitch">[!] WARNING: AUTHORIZED ACCESS ONLY [!]</div>
        </div>

        <!-- ইনপুট এরিয়া -->
        <div class="input-area">
            <span>C:\\HACKER></span>
            <input type="text" id="commandInput" autofocus onkeydown="handleCommand(event)">
        </div>
    </div>

    <!-- ডান দিকের সাইডবার (ফোল্ডারগুলো) -->
    <div class="sidebar">
        <div class="folder" onclick="quickCmd('nmap 8.8.8.8 53,443')">📁 nmap</div>
        <div class="folder" onclick="quickCmd('ipinfo google.com')">📁 ipinfo</div>
        <div class="folder" onclick="quickCmd('ai How to secure WiFi?')">📁 ai</div>
        <div class="folder" onclick="quickCmd('hash hello')">📁 hash</div>
        <div class="folder" onclick="quickCmd('help')">📁 help</div>
    </div>

    <script>
        // ঘড়ি আপডেট
        setInterval(() => {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString();
        }, 1000);

        // স্ক্রিনে লেখা যোগ করা
        function appendOutput(text) {
            const outputDiv = document.getElementById('output');
            outputDiv.innerText += '\\n' + text;
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }

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

        // কমান্ড প্রসেসিং
        async function processCommand(cmd) {
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

        // সাইডবার থেকে দ্রুত কমান্ড চালানো
        function quickCmd(cmd) {
            const input = document.getElementById('commandInput');
            input.value = cmd;
            input.focus();
            // অটোমেটিক এন্টার চাপার দরকার নেই, ইউজার নিজে চাপবে
        }
    </script>
</body>
</html>
'''

# === রাউটিং এবং লজিক ===
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
        if len(parts) < 3:
            output = "[-] Usage: nmap <ip> <port1,port2>"
        else:
            ip = parts[1]
            ports_str = parts[2]
            try:
                ports = [int(p) for p in ports_str.split(',')]
                output = f"[*] Nmap scan on {ip}...\\n"
                for port in ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    if s.connect_ex((ip, port)) == 0:
                        output += f"[+] Port {port}: OPEN\\n"
                    s.close()
            except:
                output = "[-] Invalid port format."

    # ২. ipinfo ট্র্যাকার
    elif cmd.startswith('ipinfo'):
        parts = cmd.split()
        if len(parts) < 2:
            output = "[-] Usage: ipinfo <domain>"
        else:
            domain = parts[1]
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

    # ৩. ai চ্যাট
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

    # ৪. হ্যাশ জেনারেটর
    elif cmd.startswith('hash '):
        text = cmd[5:].encode('utf-8')
        output = f"MD5: {hashlib.md5(text).hexdigest()}\\n"
        output += f"SHA256: {hashlib.sha256(text).hexdigest()}"

    # ৫. হেল্প
    elif cmd == 'help':
        output = """Available Commands:
nmap <ip> <port1,port2> - Scan ports
ipinfo <domain> - Get IP location
ai <question> - Ask AI anything
hash <text> - Generate MD5/SHA256"""

    else:
        output = "[-] Command not found. Type 'help' for available commands."

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
