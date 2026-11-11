from flask import Flask, request, jsonify, render_template_string
import subprocess
import socket

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web Hacking Console</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #000; color: #0f0; padding: 20px; }
        input, button { padding: 10px; margin: 10px 0; background: #111; color: #0f0; border: 1px solid #0f0; font-family: 'Courier New', monospace; }
        button { cursor: pointer; font-weight: bold; }
        button:hover { background: #0f0; color: #000; }
        #result { 
            white-space: pre-wrap; 
            margin-top: 20px; 
            border: 1px solid #333; 
            padding: 15px; 
            background: #050505; 
            height: 400px; 
            overflow-y: auto;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <h1>Web Hacking Console</h1>
    <label>Target IP:</label>
    <input type="text" id="target_ip" value="8.8.8.8">
    
    <label>Port(s):</label>
    <input type="text" id="port" value="53,443">
    <br>
    <button onclick="runCommand('nmap')">Run Nmap Scan</button>
    <button onclick="runCommand('nc')">Connect via Netcat</button>
    <div id="result">Output will appear here...</div>

    <script>
        async function runCommand(type) {
            const resultDiv = document.getElementById('result');
            const ip = document.getElementById('target_ip').value.trim();
            const port = document.getElementById('port').value.trim();
            
            let cmd = "";
            
            if (type === 'nmap') {
                cmd = `nmap -sV -p ${port} ${ip}`;
            } else if (type === 'nc') {
                const firstPort = port.split(',')[0].trim();
                cmd = `echo "Testing Connection to ${ip}:${firstPort}" | nc -w 3 ${ip} ${firstPort}`;
            }

            resultDiv.innerText = "Running: " + cmd + "\\n\\n[+] Please wait...";
            
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
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    cmd = data.get('cmd', '')
    
    if not cmd:
        return jsonify({'output': '[-] No command provided.'})

    if cmd.startswith('nmap'):
        parts = cmd.split()
        target_ip = parts[-1] 
        port_range = "80,443" 
        
        for p in parts:
            if p.startswith('-p'):
                if p == '-p' and parts.index(p) + 1 < len(parts):
                    port_range = parts[parts.index(p) + 1]
                else:
                    port_range = p.replace('-p', '')
        
        try:
            ports = []
            for prt in port_range.split(','):
                if '-' in prt:
                    start, end = prt.split('-')
                    ports.extend(range(int(start), int(end) + 1))
                else:
                    ports.append(int(prt))
            
            output = f"[*] Scanning {target_ip}...\\n"
            open_ports = []
            
            for port in ports:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5) 
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
                    output += f"[+] Port {port}: OPEN\\n"
                s.close()
            
            if not open_ports:
                output += "[-] No open ports found.\\n"
            else:
                output += f"\\n[+] Total {len(open_ports)} open ports found.\\n"
                
            return jsonify({'output': output})
            
        except Exception as e:
            return jsonify({'output': f"[-] Python Scanner Error: {str(e)}"})

    elif cmd.startswith('echo') and 'nc' in cmd:
        try:
            parts = cmd.split()
            ip = parts[-2]
            port = int(parts[-1])
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex((ip, port))
            if result == 0:
                output = f"[+] Success! Connected to {ip}:{port}"
            else:
                output = f"[-] Connection refused to {ip}:{port}"
            s.close()
            return jsonify({'output': output})
        except Exception as e:
            return jsonify({'output': f"[-] Netcat Python Error: {str(e)}"})
    else:
        return jsonify({'output': '[-] This command is not supported.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
