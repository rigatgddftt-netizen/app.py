from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import socket
import urllib.request
import json
import os
from PIL import Image
from PIL.ExifTags import TAGS

app = Flask(__name__)
app.secret_key = 'super_secret_hacker_key'

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

# === মূল কনসোল পেজ (Pollinations AI সহ) ===
MAIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ADVANCED HACKER CONSOLE</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #000; color: #0f0; padding: 20px; margin: 0; overflow-x: hidden; }
        #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; opacity: 0.15; }
        .container { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; }
        input, button, select, textarea { padding: 12px; margin: 5px; background: #0a0a0a; color: #0f0; border: 1px solid #0f0; font-family: 'Courier New', monospace; border-radius: 4px; }
        button { cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0f0; color: #000; box-shadow: 0 0 15px #0f0;}
        #result, #ai-result { white-space: pre-wrap; margin-top: 20px; border: 1px solid #333; padding: 15px; background: #050505; height: 250px; overflow-y: auto; line-height: 1.4; font-size: 14px; border-radius: 4px;}
        .section { margin-bottom: 20px; border-bottom: 1px dashed #333; padding-bottom: 10px; }
        h1 { text-shadow: 0 0 20px #0f0; text-align: center; letter-spacing: 2px; }
        h3 { border-left: 3px solid #0f0; padding-left: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .logout { position: absolute; top: 10px; right: 20px; color: red; text-decoration: none; border: 1px solid red; padding: 5px 10px; border-radius: 4px;}
        .logout:hover { background: red; color: #000; }
        .ai-section { border: 2px solid #0f0; padding: 20px; background: #001100; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,255,0,0.2);}
        .glitch { animation: glitch 1s linear infinite; }
        @keyframes glitch { 2%, 64% { transform: translate(2px,0) skew(0deg); } 4%, 60% { transform: translate(-2px,0) skew(0deg); } 62% { transform: translate(0,0) skew(5deg); } }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    
    <div class="container">
        <a href="/logout" class="logout">LOGOUT</a>
        <h1 class="glitch">☠️ ADVANCED HACKER CONSOLE ☠️</h1>
        <p style="text-align:center; color: #888;">Authorized Security Testing Only. Stay Ethical.</p>
        
        <!-- AI Section -->
        <div class="ai-section">
            <h3>[0] HACKER AI ASSISTANT (Keyless)</h3>
            <input type="text" id="ai_prompt" placeholder="Ask anything (e.g., How to secure WiFi?)" style="width: 70%;">
            <button onclick="askAI()">Ask AI</button>
            <div id="ai-result">[+] AI is ready. Ask a question...</div>
        </div>

        <div class="section">
            <h3>[1] IP & OSINT Tracker</h3>
            <input type="text" id="target_link" value="https://google.com" placeholder="Enter Website Link" style="width: 50%;">
            <button onclick="runCommand('track')">Track Info</button>
        </div>

        <div class="section">
            <h3>[2] Massive Port Scanner</h3>
            <input type="text" id="target_ip" value="8.8.8.8" placeholder="Target IP">
            <select id="scan_type">
                <option value="fast">Fast Scan (Top 100 Ports)</option>
                <option value="full">Full Scan (1-10000 Ports)</option>
            </select>
            <button onclick="runCommand('portscan')">Start Scan</button>
        </div>

        <div class="section">
            <h3>[3] OSINT Username Tracker</h3>
            <input type="text" id="username" value="john_doe" placeholder="Enter Username">
            <button onclick="runCommand('usertrack')">Find Profiles</button>
        </div>
        
        <div class="section">
            <h3>[4] Reverse Image Search (Google Lens Style)</h3>
            <input type="text" id="image_url" value="https://i.imgur.com/B4h4W4j.jpg" placeholder="Paste Image URL">
            <button onclick="runCommand('imgsearch')">Search Image</button>
        </div>

        <div id="result">[+] Awaiting commands... Output will appear here.</div>
    </div>

    <script>
        // Matrix Effect
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

        // Tools Logic
        async function runCommand(type) {
            const resultDiv = document.getElementById('result');
            let cmd = "";
            
            if (type === 'track') cmd = `track ${document.getElementById('target_link').value.trim()}`;
            else if (type === 'portscan') cmd = `portscan ${document.getElementById('target_ip').value.trim()} ${document.getElementById('scan_type').value}`;
            else if (type === 'usertrack') cmd = `usertrack ${document.getElementById('username').value.trim()}`;
            else if (type === 'imgsearch') cmd = `imgsearch ${document.getElementById('image_url').value.trim()}`;

            resultDiv.innerText = "[*] Executing: " + cmd + "\\n\\n[+] Please wait...\\n";
            
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({cmd: cmd})
                });
                const data = await response.json();
                resultDiv.innerText = data.output;
            } catch (error) {
                resultDiv.innerText = "[-] Error communicating with server.";
            }
        }

        // AI Logic (Pollinations - কোনো Key বা Login ছাড়াই)
        async function askAI() {
            const aiResultDiv = document.getElementById('ai-result');
            const prompt = document.getElementById('ai_prompt').value.trim();
            if(!prompt) return;
            
            aiResultDiv.innerText = "[*] AI is thinking...\\n";
            
            try {
                // Pollinations API ব্যবহার করে AI কল
                const response = await fetch('/ai', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                aiResultDiv.innerText = data.reply;
            } catch (error) {
                aiResultDiv.innerText = "[-] Error connecting to AI.";
            }
        }
    </script>
</body>
</html>
'''

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

# === AI Endpoint (Pollinations API) ===
@app.route('/ai', methods=['POST'])
def ai_chat():
    if 'logged_in' not in session:
        return jsonify({'reply': '[-] Unauthorized.'})
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    try:
        # Pollinations API - কোনো Key বা Login ছাড়াই
        api_url = "https://text.pollinations.ai/openai"
        payload = json.dumps({
            "model": "openai",
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        
        res = urllib.request.urlopen(req, timeout=30)
        res_data = json.loads(res.read().decode())
        reply = res_data['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'[-] AI Error: {str(e)}'})

# === অন্যান্য টুলস ===
@app.route('/execute', methods=['POST'])
def execute():
    if 'logged_in' not in session:
        return jsonify({'output': '[-] Unauthorized. Please login.'})
        
    data = request.get_json()
    cmd = data.get('cmd', '')
    output = ""

    if cmd.startswith('track'):
        domain = cmd.split()[1].replace('https://', '').replace('http://', '').split('/')[0]
        try:
            ip = socket.gethostbyname(domain)
            output += f"[+] Target IP: {ip}\\n"
            req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=66846719", headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=5)
            ip_data = json.loads(res.read().decode())
            if ip_data.get('status') == 'success':
                output += f"Country: {ip_data.get('country')}\\nRegion: {ip_data.get('regionName')}\\nCity: {ip_data.get('city')}\\nISP: {ip_data.get('isp')}\\n"
        except Exception as e:
            output = f"[-] Error: {e}"

    elif cmd.startswith('portscan'):
        parts = cmd.split()
        ip = parts[1]
        scan_type = parts[2]
        if scan_type == 'fast':
            ports = [21, 22, 80, 443, 3306, 8080]
            output = f"[*] Fast scanning {ip}...\\n"
        else:
            ports = range(1, 1001)
            output = f"[*] Full scanning {ip} (1-1000)...\\n"
        open_ports = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
                output += f"[+] Port {port}: OPEN\\n"
            s.close()
        if not open_ports: output += "[-] No open ports found.\\n"

    elif cmd.startswith('usertrack'):
        username = cmd.split()[1]
        output = f"[*] Searching username: {username}...\\n"
        sites = {
            "Facebook": f"https://www.facebook.com/{username}",
            "Instagram": f"https://www.instagram.com/{username}",
            "Twitter/X": f"https://twitter.com/{username}",
            "GitHub": f"https://github.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}"
        }
        for site, url in sites.items():
            try:
                req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
                res = urllib.request.urlopen(req, timeout=3)
                if res.status == 200:
                    output += f"[+] Found on {site}: {url}\\n"
            except:
                pass
        output += "\\n[+] Search complete.\\n"

    elif cmd.startswith('imgsearch'):
        img_url = cmd.split()[1]
        output = f"[*] Initiating Reverse Image Search for: {img_url}\\n"
        lens_url = f"https://lens.google.com/uploadbyurl?url={img_url}"
        output += f"\\n[+] View Results Here: {lens_url}\\n"

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
