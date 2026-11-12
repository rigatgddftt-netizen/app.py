from flask import Flask, render_template_string

app = Flask(__name__)

EDITOR_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Spider-Verse Neon Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        body {
            margin: 0; padding: 0;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff; min-height: 100vh; overflow-x: hidden;
        }

        /* মায়াবী নিয়ন ব্যাকগ্রাউন্ড গ্লো */
        .glow-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(255, 0, 204, 0.3) 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(1, 205, 254, 0.3) 0%, transparent 50%);
            z-index: -1; filter: blur(40px); animation: pulse 6s infinite alternate;
        }

        @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(1.2); opacity: 1; } }

        .container { max-width: 900px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }

        h1 {
            text-align: center; font-weight: 600; font-size: 2rem;
            background: -webkit-linear-gradient(45deg, #ff00cc, #01cdfe, #b967ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(255, 0, 204, 0.5); margin-bottom: 30px;
        }

        .glass-panel {
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px;
            padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        .file-upload-wrapper { position: relative; overflow: hidden; display: inline-block; width: 100%; margin-bottom: 20px; }

        .file-upload-btn {
            border: 2px dashed #01cdfe; border-radius: 10px; color: #01cdfe;
            padding: 15px; text-align: center; cursor: pointer; transition: 0.3s;
            background: rgba(1, 205, 254, 0.1); font-weight: bold;
        }

        .file-upload-btn:hover { background: rgba(1, 205, 254, 0.2); box-shadow: 0 0 15px rgba(1, 205, 254, 0.5); }

        .file-upload-wrapper input[type=file] {
            position: absolute; left: 0; top: 0; right: 0; bottom: 0; opacity: 0; cursor: pointer;
        }

        .preview-area {
            display: flex; justify-content: center; align-items: center;
            background: #000; border-radius: 15px; overflow: hidden;
            min-height: 250px; position: relative;
        }

        .preview-area img, .preview-area video {
            max-width: 100%; max-height: 350px; border-radius: 10px;
            object-fit: contain; transition: filter 1s ease; /* ফিল্টার স্মুথলি আসবে */
        }

        .btn-container { text-align: center; margin-top: 20px; }

        .magic-btn {
            padding: 15px 30px; border-radius: 30px; border: none;
            background: linear-gradient(45deg, #ff00cc, #01cdfe);
            color: white; font-weight: bold; font-size: 1.1rem;
            cursor: pointer; box-shadow: 0 0 20px rgba(255, 0, 204, 0.6);
            transition: 0.3s;
        }

        .magic-btn:hover { transform: scale(1.05); box-shadow: 0 0 30px rgba(1, 205, 254, 0.8); }

        /* লোডিং স্পিনার */
        .loader {
            display: none; border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #01cdfe; border-radius: 50%;
            width: 40px; height: 40px; animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    </style>
</head>
<body>
    <div class="glow-bg"></div>

    <div class="container">
        <h1>Spider-Verse Magic Editor</h1>
        
        <div class="glass-panel">
            <div class="file-upload-wrapper">
                <div class="file-upload-btn">Select Image or Video</div>
                <input type="file" id="mediaUpload" accept="image/*,video/*">
            </div>

            <div class="preview-area" id="previewContainer">
                <!-- ডিফল্ট ইমেজ -->
                <img id="previewImg" src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop" alt="Preview">
                <video id="previewVideo" style="display:none;" controls autoplay loop muted></video>
                <div id="overlay" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; mix-blend-mode: screen; opacity:0; transition: opacity 1s;"></div>
            </div>
            
            <div class="loader" id="loader"></div>

            <div class="btn-container">
                <button class="magic-btn" onclick="applyMagic()">✨ Apply Spider-Verse Magic ✨</button>
            </div>
        </div>
    </div>

    <script>
        const previewImg = document.getElementById('previewImg');
        const previewVideo = document.getElementById('previewVideo');
        const overlay = document.getElementById('overlay');
        const loader = document.getElementById('loader');
        let activeMedia = previewImg;

        // ভিডিও বা ছবি আপলোড
        document.getElementById('mediaUpload').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileType = file.type;
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    // ফিল্টার রিসেট
                    previewImg.style.filter = 'none';
                    previewVideo.style.filter = 'none';
                    overlay.style.opacity = '0';

                    if (fileType.startsWith('image/')) {
                        previewImg.src = event.target.result;
                        previewImg.style.display = 'block';
                        previewVideo.style.display = 'none';
                        activeMedia = previewImg;
                    } else if (fileType.startsWith('video/')) {
                        previewVideo.src = event.target.result;
                        previewVideo.style.display = 'block';
                        previewImg.style.display = 'none';
                        activeMedia = previewVideo;
                    }
                }
                reader.readAsDataURL(file);
            }
        });

        // ম্যাজিক বাটন ফাংশন
        function applyMagic() {
            // লোডার দেখাও
            loader.style.display = 'block';
            
            // ১ সেকেন্ড পর ম্যাজিক Apply হবে (দেখতে ভালো লাগবে)
            setTimeout(() => {
                loader.style.display = 'none';
                
                // ১. মেইন ফিল্টার (কনট্রাস্ট, কালার বুস্ট)
                // এখানে আমরা ছবির রঙকে স্পাইডারম্যানের মত নীল-বেগুনির দিকে নিচ্ছি
                activeMedia.style.filter = 'contrast(1.4) saturate(2) hue-rotate(220deg) brightness(0.9)';

                // ২. নিয়ন ওভারলে (Screen Blend Mode দিয়ে পুরো স্ক্রিনে ম্যাজেন্টা-সায়ান গ্লো)
                // আমরা CSS গ্রেডিয়েন্ট ব্যবহার করে একটি কালারফুল লেয়ার তৈরি করছি
                overlay.style.background = 'linear-gradient(45deg, rgba(255,0,204,0.3) 0%, rgba(1,205,254,0.3) 100%)';
                overlay.style.opacity = '0.8'; // ওভারলে ওপাসিটি
                overlay.style.boxShadow = 'inset 0 0 100px rgba(255,0,204,0.5)'; // ভেতরে গ্লো

            }, 1000); // ১ সেকেন্ড ওয়েট
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(EDITOR_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
