from flask import Flask, render_template_string, request, jsonify
import urllib.parse

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Voice Image Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body { font-family: 'Poppins', sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #333; display: flex; flex-direction: column; align-items: center; }
        h1 { color: #4a90e2; text-align: center; margin-bottom: 20px; }
        .container { width: 100%; max-width: 600px; background: #fff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 20px; }
        
        .mic-btn {
            width: 80px; height: 80px; border-radius: 50%; border: none;
            background: #4a90e2; color: white; font-size: 30px;
            cursor: pointer; display: block; margin: 0 auto 20px auto;
            box-shadow: 0 4px 10px rgba(74, 144, 226, 0.4); transition: 0.3s;
        }
        .mic-btn.recording { background: #e74c3c; animation: pulse 1s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); } 70% { box-shadow: 0 0 0 20px rgba(231, 76, 60, 0); } 100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); } }

        .text-input-area { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; }
        .gen-btn { padding: 12px 20px; background: #4a90e2; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        
        .image-area { width: 100%; min-height: 300px; background: #f9f9f9; border: 2px dashed #ccc; border-radius: 10px; display: flex; justify-content: center; align-items: center; margin-bottom: 20px; overflow: hidden; }
        .image-area img { width: 100%; height: auto; border-radius: 10px; display: none; }
        .loading { display: none; font-weight: bold; color: #4a90e2; }
        
        .download-btn { width: 100%; padding: 15px; background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ AI Voice Image Editor</h1>
        
        <!-- ভয়েস ইনপুট -->
        <button class="mic-btn" id="micBtn">🎤</button>
        <p style="text-align:center; font-size: 14px; color: #888;" id="statusText">Tap mic and speak...</p>
        
        <!-- টেক্সট ইনপুট -->
        <div class="text-input-area">
            <input type="text" id="promptText" placeholder="Describe your image...">
            <button class="gen-btn" onclick="generateImage()">Generate</button>
        </div>

        <!-- ইমেজ প্রিভিউ -->
        <div class="image-area" id="imageContainer">
            <span style="color: #aaa;">Your image will appear here</span>
            <img id="resultImage" src="" alt="AI Image">
            <div class="loading" id="loadingSpinner">Generating Magic... ⏳</div>
        </div>

        <!-- ডাউনলোড বাটন -->
        <button class="download-btn" id="downloadBtn" onclick="downloadImage()">⬇️ Download Image</button>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const statusText = document.getElementById('statusText');
        const promptText = document.getElementById('promptText');
        const resultImage = document.getElementById('resultImage');
        const imageContainer = document.getElementById('imageContainer');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const downloadBtn = document.getElementById('downloadBtn');

        // ভয়েস রিকগনিশন সেটআপ
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.lang = 'bn-BD'; // বাংলা ভাষা সাপোর্ট (ইংরেজির জন্য 'en-US' করতে পারেন)
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            micBtn.addEventListener('click', () => {
                if (micBtn.classList.contains('recording')) {
                    recognition.stop();
                    micBtn.classList.remove('recording');
                    statusText.innerText = "Stopped listening.";
                } else {
                    recognition.start();
                    micBtn.classList.add('recording');
                    statusText.innerText = "Listening... Speak now!";
                }
            });

            recognition.onresult = (event) => {
                const speechResult = event.results[0][0].transcript;
                promptText.value = speechResult;
                statusText.innerText = "Recognized: " + speechResult;
                micBtn.classList.remove('recording');
                // ভয়েস রিকগনিশন শেষে অটোমেটিক ইমেজ জেনারেট করবে
                generateImage(); 
            };

            recognition.onspeechend = () => {
                recognition.stop();
                micBtn.classList.remove('recording');
            };

            recognition.onerror = (event) => {
                statusText.innerText = "Error: " + event.error;
                micBtn.classList.remove('recording');
            };
        } else {
            statusText.innerText = "Voice recognition not supported in this browser.";
            micBtn.style.display = 'none';
        }

        // ইমেজ জেনারেশন ফাংশন
        async function generateImage() {
            const prompt = promptText.value.trim();
            if (!prompt) {
                alert("Please enter a description or speak first!");
                return;
            }

            // UI আপডেট
            imageContainer.querySelector('span').style.display = 'none';
            resultImage.style.display = 'none';
            downloadBtn.style.display = 'none';
            loadingSpinner.style.display = 'block';
            statusText.innerText = "Generating image...";

            try {
                // Pollinations AI API-তে রিকোয়েস্ট পাঠানো (কোনো API Key ছাড়াই)
                const encodedPrompt = encodeURIComponent(prompt + ", high quality, detailed, 4k");
                const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&nologo=true`;
                
                // ইমেজ লোড হওয়া পর্যন্ত অপেক্ষা
                const img = new Image();
                img.onload = function() {
                    resultImage.src = imageUrl;
                    resultImage.style.display = 'block';
                    loadingSpinner.style.display = 'none';
                    downloadBtn.style.display = 'block';
                    statusText.innerText = "Image generated successfully!";
                };
                img.onerror = function() {
                    loadingSpinner.style.display = 'none';
                    statusText.innerText = "Error generating image. Try again.";
                };
                img.src = imageUrl;

            } catch (error) {
                console.error(error);
                loadingSpinner.style.display = 'none';
                statusText.innerText = "Error connecting to AI.";
            }
        }

        // ইমেজ ডাউনলোড ফাংশন
        function downloadImage() {
            const imgUrl = resultImage.src;
            if (!imgUrl) return;

            // একটি নতুন ট্যাবে ইমেজটি ওপেন করবে যাতে ইউজার সেভ করতে পারে
            const link = document.createElement('a');
            link.href = imgUrl;
            link.download = 'ai_generated_image.jpg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
