from flask import Flask, render_template_string, request, jsonify
import urllib.request
import json
import uuid

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Pro AI Chat</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        :root {
            --bg-color: #343541;
            --sidebar-bg: #202123;
            --text-color: #ececf1;
            --user-msg-bg: #343541;
            --ai-msg-bg: #444654;
            --input-bg: #40414f;
            --border-color: #4d4d4f;
            --accent-color: #10a37f;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* সাইডবার */
        .sidebar {
            width: 260px;
            background-color: var(--sidebar-bg);
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease;
            border-right: 1px solid var(--border-color);
            z-index: 100;
        }

        .sidebar.closed { transform: translateX(-100%); position: absolute; height: 100%; }

        .sidebar-header { padding: 15px; }
        
        .new-chat-btn {
            width: 100%;
            padding: 12px;
            background: transparent;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            color: var(--text-color);
            text-align: left;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: 0.2s;
            font-size: 14px;
        }
        .new-chat-btn:hover { background: rgba(255,255,255,0.1); }

        .chat-history { flex: 1; overflow-y: auto; padding: 10px; }
        .history-item {
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #c5c5d2;
        }
        .history-item:hover { background: rgba(255,255,255,0.1); }
        .history-item.active { background: rgba(255,255,255,0.15); color: #fff; }

        .sidebar-footer {
            padding: 15px;
            border-top: 1px solid var(--border-color);
        }
        .footer-btn {
            width: 100%;
            padding: 10px;
            background: transparent;
            border: none;
            color: var(--text-color);
            text-align: left;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
        }
        .footer-btn:hover { background: rgba(255,255,255,0.1); border-radius: 5px; }

        /* মেইন চ্যাট এরিয়া */
        .main-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
            height: 100%;
        }

        .top-bar {
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            background: var(--bg-color);
            border-bottom: 1px solid var(--border-color);
        }

        .menu-btn {
            background: transparent;
            border: none;
            color: var(--text-color);
            font-size: 24px;
            cursor: pointer;
            display: none;
        }

        .model-selector {
            background: transparent;
            color: var(--text-color);
            border: none;
            font-size: 16px;
            font-weight: 600;
            outline: none;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            padding-bottom: 120px;
        }

        .message {
            width: 100%;
            padding: 25px 20px;
            display: flex;
            gap: 20px;
            line-height: 1.6;
            font-size: 15px;
        }

        .message.user { background: var(--user-msg-bg); }
        .message.ai { background: var(--ai-msg-bg); border-top: 1px solid rgba(0,0,0,0.1); border-bottom: 1px solid rgba(0,0,0,0.1); }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 4px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            flex-shrink: 0;
        }
        .user .avatar { background: #5436DA; color: white; }
        .ai .avatar { background: #10a37f; color: white; }

        .message-content { flex: 1; white-space: pre-wrap; word-wrap: break-word; }

        .typing-indicator {
            display: none;
            padding: 20px;
            background: var(--ai-msg-bg);
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        .typing-dots span {
            display: inline-block;
            width: 8px; height: 8px;
            background: #c5c5d2;
            border-radius: 50%;
            margin: 0 3px;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* ইনপুট এরিয়া */
        .input-container {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 20px;
            background: linear-gradient(180deg, transparent, var(--bg-color) 30%);
        }

        .input-box {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            background: var(--input-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }

        .input-box textarea {
            width: 100%;
            padding: 15px 50px 15px 15px;
            background: transparent;
            border: none;
            color: var(--text-color);
            font-size: 16px;
            resize: none;
            outline: none;
            height: 54px;
            max-height: 200px;
            font-family: 'Inter', sans-serif;
            line-height: 1.5;
        }

        .send-btn {
            position: absolute;
            right: 10px;
            bottom: 10px;
            background: var(--accent-color);
            border: none;
            width: 34px;
            height: 34px;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: 0.2s;
        }
        .send-btn:disabled { background: #555; cursor: not-allowed; }

        .footer-text {
            text-align: center;
            font-size: 12px;
            color: #888;
            margin-top: 10px;
        }

        /* মোবাইল রেসপন্সিভ */
        @media (max-width: 768px) {
            .sidebar { position: absolute; height: 100%; }
            .sidebar.closed { transform: translateX(-100%); }
            .menu-btn { display: block; }
            .message { padding: 20px 15px; }
        }
    </style>
</head>
<body>

    <!-- সাইডবার -->
    <div class="sidebar closed" id="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-btn" onclick="newChat()">
                <span>+</span> New Chat
            </button>
        </div>
        <div class="chat-history" id="chatHistory">
            <!-- চ্যাট হিস্ট্রি এখানে আসবে -->
        </div>
        <div class="sidebar-footer">
            <button class="footer-btn" onclick="toggleDarkMode()">🌙 Toggle Theme</button>
            <button class="footer-btn" onclick="clearAll()">🗑️ Clear All Chats</button>
        </div>
    </div>

    <!-- মেইন চ্যাট -->
    <div class="main-chat">
        <div class="top-bar">
            <button class="menu-btn" onclick="toggleSidebar()">☰</button>
            <select class="model-selector">
                <option>Pro AI (Pollinations)</option>
            </select>
        </div>

        <div class="chat-container" id="chatContainer">
            <!-- মেসেজ এখানে আসবে -->
        </div>

        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>

        <div class="input-container">
            <div class="input-box">
                <textarea id="userInput" placeholder="Message Pro AI..." rows="1" oninput="autoResize(this)" onkeydown="handleKeyDown(event)"></textarea>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()" disabled>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
            <div class="footer-text">Pro AI can make mistakes. Consider verifying important information.</div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let chats = JSON.parse(localStorage.getItem('pro_ai_chats')) || {};
        let isDark = localStorage.getItem('pro_ai_dark') !== 'false';

        // থিম সেট করা
        function applyTheme() {
            if (!isDark) {
                document.documentElement.style.setProperty('--bg-color', '#ffffff');
                document.documentElement.style.setProperty('--sidebar-bg', '#f7f7f8');
                document.documentElement.style.setProperty('--text-color', '#343541');
                document.documentElement.style.setProperty('--user-msg-bg', '#ffffff');
                document.documentElement.style.setProperty('--ai-msg-bg', '#f7f7f8');
                document.documentElement.style.setProperty('--input-bg', '#ffffff');
                document.documentElement.style.setProperty('--border-color', '#d9d9e3');
            } else {
                document.documentElement.style.setProperty('--bg-color', '#343541');
                document.documentElement.style.setProperty('--sidebar-bg', '#202123');
                document.documentElement.style.setProperty('--text-color', '#ececf1');
                document.documentElement.style.setProperty('--user-msg-bg', '#343541');
                document.documentElement.style.setProperty('--ai-msg-bg', '#444654');
                document.documentElement.style.setProperty('--input-bg', '#40414f');
                document.documentElement.style.setProperty('--border-color', '#4d4d4f');
            }
        }
        applyTheme();

        // সাইডবার টগল
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('closed');
        }

        // ডার্ক মোড টগল
        function toggleDarkMode() {
            isDark = !isDark;
            localStorage.setItem('pro_ai_dark', isDark);
            applyTheme();
        }

        // চ্যাট হিস্ট্রি রেন্ডার
        function renderHistory() {
            const historyContainer = document.getElementById('chatHistory');
            historyContainer.innerHTML = '';
            Object.keys(chats).reverse().forEach(id => {
                const div = document.createElement('div');
                div.className = `history-item ${id === currentChatId ? 'active' : ''}`;
                div.innerText = chats[id].title || 'New Chat';
                div.onclick = () => loadChat(id);
                historyContainer.appendChild(div);
            });
        }

        // নতুন চ্যাট
        function newChat() {
            currentChatId = 'chat_' + Date.now();
            chats[currentChatId] = { title: 'New Chat', messages: [] };
            saveChats();
            renderHistory();
            document.getElementById('chatContainer').innerHTML = '';
            toggleSidebar(); // মোবাইলে সাইডবার বন্ধ করে দেবে
        }

        // চ্যাট লোড করা
        function loadChat(id) {
            currentChatId = id;
            renderHistory();
            const container = document.getElementById('chatContainer');
            container.innerHTML = '';
            chats[id].messages.forEach(msg => {
                addMessageToUI(msg.text, msg.sender);
            });
            toggleSidebar();
        }

        // চ্যাট সেভ করা
        function saveChats() {
            localStorage.setItem('pro_ai_chats', JSON.stringify(chats));
        }

        // সব চ্যাট মুছে ফেলা
        function clearAll() {
            if(confirm("Are you sure you want to delete all chats?")) {
                chats = {};
                currentChatId = null;
                saveChats();
                renderHistory();
                document.getElementById('chatContainer').innerHTML = '';
            }
        }

        // মেসেজ পাঠানো
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;

            if (!currentChatId) newChat();

            // ইউজারের মেসেজ যোগ করা
            addMessageToUI(text, 'user');
            chats[currentChatId].messages.push({ text: text, sender: 'user' });
            
            // প্রথম মেসেজ হলে চ্যাটের টাইটেল সেট করা
            if (chats[currentChatId].messages.length === 1) {
                chats[currentChatId].title = text.substring(0, 30) + (text.length > 30 ? '...' : '');
                renderHistory();
            }
            saveChats();

            input.value = '';
            input.style.height = '54px';
            document.getElementById('sendBtn').disabled = true;

            // টাইপিং ইন্ডিকেটর দেখানো
            const typing = document.getElementById('typingIndicator');
            typing.style.display = 'block';
            scrollToBottom();

            try {
                // Pollinations AI API-তে রিকোয়েস্ট
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();
                
                typing.style.display = 'none';
                addMessageToUI(data.reply, 'ai');
                chats[currentChatId].messages.push({ text: data.reply, sender: 'ai' });
                saveChats();
            } catch (error) {
                typing.style.display = 'none';
                addMessageToUI("দুঃখিত, একটি সমস্যা হয়েছে। আবার চেষ্টা করুন।", 'ai');
            } finally {
                document.getElementById('sendBtn').disabled = false;
                scrollToBottom();
                input.focus();
            }
        }

        // UI-তে মেসেজ যোগ করা
        function addMessageToUI(text, sender) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerText = sender === 'user' ? 'U' : 'AI';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.innerText = text;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            container.appendChild(messageDiv);
            scrollToBottom();
        }

        // নিচে স্ক্রল করা
        function scrollToBottom() {
            const container = document.getElementById('chatContainer');
            container.scrollTop = container.scrollHeight;
        }

        // এন্টার কী হ্যান্ডল
        function handleKeyDown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!document.getElementById('sendBtn').disabled) {
                    sendMessage();
                }
            }
        }

        // টেক্সটএরিয়া অটো রিসাইজ
        function autoResize(textarea) {
            textarea.style.height = '54px';
            textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
            document.getElementById('sendBtn').disabled = textarea.value.trim() === '';
        }

        // শুরুতে হিস্ট্রি লোড করা
        renderHistory();

    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    try:
        api_url = "https://text.pollinations.ai/openai"
        payload = json.dumps({
            "model": "openai",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant. Always reply in the same language the user speaks (Bengali or English)."},
                {"role": "user", "content": user_message}
            ]
        }).encode('utf-8')

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )

        res = urllib.request.urlopen(req, timeout=60)
        res_data = json.loads(res.read().decode())
        
        reply = res_data['choices'][0]['message']['content']
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': f'[-] AI Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
