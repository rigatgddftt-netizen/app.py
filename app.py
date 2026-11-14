from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json

app = Flask(__name__)

# আপনার গুগল API Key এখানে বসান
GEMINI_API_KEY = "AQ.Ab8RN6LoCELPDU69d-WPkHx1EIEUB7gP5CnJRMhhSxyose2Pyw"

# === নিখুঁত AI চ্যাট ইন্টারফেস ===
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Assistant (Gemini)</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            border-bottom: 1px solid #1e293b;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 10;
        }

        .header .status {
            width: 10px; height: 10px;
            background: #22c55e;
            border-radius: 50%;
            box-shadow: 0 0 10px #22c55e;
        }

        .header h1 { font-size: 1.1rem; font-weight: 600; color: #f8fafc; }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scroll-behavior: smooth;
        }

        .chat-container::-webkit-scrollbar { width: 6px; }
        .chat-container::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.95rem;
            line-height: 1.5;
            animation: fadeIn 0.3s ease-out;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            background: #3b82f6;
            color: white;
            border-bottom-right-radius: 2px;
        }

        .message.ai {
            align-self: flex-start;
            background: #1e293b;
            color: #e2e8f0;
            border-bottom-left-radius: 2px;
            border: 1px solid #334155;
        }

        .typing {
            display: none;
            align-self: flex-start;
            background: #1e293b;
            padding: 12px 18px;
            border-radius: 12px;
            border-bottom-left-radius: 2px;
            border: 1px solid #334155;
        }

        .typing span {
            display: inline-block;
            width: 8px; height: 8px;
            background: #64748b;
            border-radius: 50%;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .input-area {
            padding: 15px 20px;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            border-top: 1px solid #1e293b;
            display: flex;
            gap: 10px;
            z-index: 10;
        }

        .input-area input {
            flex: 1;
            padding: 14px 20px;
            border-radius: 25px;
            border: 1px solid #334155;
            background: #1e293b;
            color: #f8fafc;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }

        .input-area input:focus { border-color: #3b82f6; }

        .input-area button {
            width: 50px; height: 50px;
            border-radius: 50%;
            border: none;
            background: #3b82f6;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: 0.3s;
        }

        .input-area button:hover { background: #2563eb; transform: scale(1.05); }
        .input-area button:disabled { background: #475569; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header">
        <div class="status"></div>
        <h1>AI Assistant (Gemini)</h1>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="message ai">হ্যালো! আমি গুগলের জেমিনি এআই। বাংলা বা ইংরেজিতে যেকোনো প্রশ্ন করতে পারো।</div>
    </div>

    <div class="typing" id="typingIndicator">
        <span></span><span></span><span></span>
    </div>

    <div class="input-area">
        <input type="text" id="userInput" placeholder="মেসেজ লিখুন..." autocomplete="off">
        <button id="sendBtn" onclick="sendMessage()">➤</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const typingIndicator = document.getElementById('typingIndicator');

        userInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            userInput.value = '';
            
            sendBtn.disabled = true;
            typingIndicator.style.display = 'block';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                typingIndicator.style.display = 'none';
                addMessage(data.reply, 'ai');
            } catch (error) {
                typingIndicator.style.display = 'none';
                addMessage("দুঃখিত, একটি সমস্যা হয়েছে। আবার চেষ্টা করুন।", 'ai');
            } finally {
                sendBtn.disabled = false;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                userInput.focus();
            }
        }

        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', sender);
            messageDiv.innerText = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
'''

# === সার্ভার সাইড এআই লজিক (Gemini API) ===
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    try:
        # গুগলের Gemini 1.5 Flash API
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = json.dumps({
            "contents": [{
                "parts": [{"text": user_message}]
            }]
        }).encode('utf-8')

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )

        res = urllib.request.urlopen(req, timeout=30)
        res_data = json.loads(res.read().decode())
        
        # Gemini-এর রেসপন্স থেকে টেক্সট বের করা
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': f'[-] AI Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
