from flask import Flask, request, render_template_string

app = Flask(__name__)

EDITOR_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Cinematic Color Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        body {
            margin: 0; padding: 0;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff; min-height: 100vh; overflow-x: hidden;
        }

        .glow-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(255, 0, 204, 0.2) 0%, transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(1, 205, 254, 0.2) 0%, transparent 40%);
            z-index: -1; filter: blur(50px); animation: pulse 8s infinite alternate;
        }

        @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(1.1); opacity: 1; } }

        .container { max-width: 1000px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }

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

        .editor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .editor-grid { grid-template-columns: 1fr; } }

        .preview-area {
            display: flex; justify-content: center; align-items: center;
            background: #000; border-radius: 15px; overflow: hidden;
            min-height: 300px; position: relative;
        }

        .preview-area img, .preview-area video {
            max-width: 100%; max-height: 400px; border-radius: 10px;
            transition: filter 0.5s ease; object-fit: contain;
        }

        .controls-area h3 {
            margin-top: 0; color: #b967ff; font-weight: 400;
            border-bottom: 1px solid rgba(185, 103, 255, 0.3); padding-bottom: 10px;
        }

        .file-upload-wrapper { position: relative; overflow: hidden; display: inline-block; width: 100%; margin-bottom: 20px; }

        .file-upload-btn {
            border: 2px dashed #01cdfe; border-radius: 10px; color: #01cdfe;
            padding: 15px; text-align: center; cursor: pointer; transition: 0.3s;
            background: rgba(1, 205, 254, 0.1);
        }

        .file-upload-btn:hover { background: rgba(1, 205, 254, 0.2); box-shadow: 0 0 15px rgba(1, 205, 254, 0.5); }

        .file-upload-wrapper input[type=file] {
            position: absolute; left: 0; top: 0; right: 0; bottom: 0; opacity: 0; cursor: pointer;
        }

        .presets { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }

        .preset-btn {
            padding: 10px 15px; border-radius: 30px; border: none;
            font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 0.8rem;
            color: #fff; text-shadow: 1px 1px 2px #000;
        }

        .preset-btn:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.5); }

        .preset-cyber { background: linear-gradient(45deg, #ff00cc, #333399); }
        .preset-magic { background: linear-gradient(45deg, #01cdfe, #b967ff); }
        .preset-vapor { background: linear-gradient(45deg, #ff71ce, #01cdfe); }
        .preset-sunset { background: linear-gradient(45deg, #ff512f, #dd2476); }
        .preset-reset { background: #555; }

        .slider-group { margin-bottom: 15px; }
        .slider-group label { display: block; margin-bottom: 5px; font-size: 0.9rem; color: #ddd; }

        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none; height: 20px; width: 20px; border-radius: 50%;
            background: #fff; cursor: pointer; margin-top: -8px; box-shadow: 0 0 10px #ff00cc;
        }
        input[type=range]::-webkit-slider-runnable-track {
            width: 100%; height: 4px; cursor: pointer;
            background: linear-gradient(90deg, #ff00cc, #01cdfe); border-radius: 2px;
        }
    </style>
</head>
<body>
    <div class="glow-bg"></div>

    <div class="container">
        <h1>Cinematic Color Editor</h1>
        
        <div class="glass-panel">
            <!-- আপলোড সেকশন -->
            <div class="file-upload-wrapper">
                <div class="file-upload-btn">Click to Upload Image or Video</div>
                <input type="file" id="mediaUpload" accept="image/*,video/*">
            </div>

            <div class="editor-grid">
                <!-- প্রিভিউ এরিয়া -->
                <div class="preview-area" id="previewContainer">
                    <img id="previewImg" src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop" alt="Preview">
                    <video id="previewVideo" style="display:none;" controls autoplay loop muted></video>
                </div>

                <!-- কন্ট্রোল এরিয়া -->
                <div class="controls-area">
                    <h3>Magic Presets</h3>
                    <div class="presets">
                        <button class="preset-btn preset-cyber" onclick="applyPreset('cyber')">Cyberpunk</button>
                        <button class="preset-btn preset-magic" onclick="applyPreset('magic')">Magic</button>
                        <button class="preset-btn preset-vapor" onclick="applyPreset('vapor')">Vaporwave</button>
                        <button class="preset-btn preset-sunset" onclick="applyPreset('sunset')">Sunset</button>
                        <button class="preset-btn preset-reset" onclick="applyPreset('none')">Reset</button>
                    </div>

                    <h3>Manual Adjustments</h3>
                    <div class="slider-group"><label>Brightness</label><input type="range" id="brightness" min="0" max="200" value="100" oninput="updateManual()"></div>
                    <div class="slider-group"><label>Contrast</label><input type="range" id="contrast" min="0" max="200" value="100" oninput="updateManual()"></div>
                    <div class="slider-group"><label>Saturation</label><input type="range" id="saturation" min="0" max="200" value="100" oninput="updateManual()"></div>
                    <div class="slider-group"><label>Hue Shift</label><input type="range" id="hue" min="0" max="360" value="0" oninput="updateManual()"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const previewImg = document.getElementById('previewImg');
        const previewVideo = document.getElementById('previewVideo');
        let activeMedia = previewImg; // ডিফল্টভাবে ছবি অ্যাক্টিভ থাকবে

        // মিডিয়া আপলোড (ছবি বা ভিডিও)
        document.getElementById('mediaUpload').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileType = file.type;
                const reader = new FileReader();
                
                reader.onload = function(event) {
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
                    resetFilters();
                }
                reader.readAsDataURL(file);
            }
        });

        // প্রিসেট ফিল্টার
        function applyPreset(type) {
            resetSliders();
            let filter = '';
            switch(type) {
                case 'cyber': filter = 'contrast(1.3) saturate(1.8) hue-rotate(240deg) brightness(0.9)'; break;
                case 'magic': filter = 'contrast(1.1) saturate(2) hue-rotate(300deg) brightness(1.1)'; break;
                case 'vapor': filter = 'contrast(1.2) saturate(1.5) hue-rotate(150deg) sepia(0.2)'; break;
                case 'sunset': filter = 'contrast(1.1) saturate(1.4) sepia(0.4) hue-rotate(330deg)'; break;
                default: filter = 'none';
            }
            activeMedia.style.filter = filter;
        }

        // ম্যানুয়াল ফিল্টার
        function updateManual() {
            const b = document.getElementById('brightness').value;
            const c = document.getElementById('contrast').value;
            const s = document.getElementById('saturation').value;
            const h = document.getElementById('hue').value;
            activeMedia.style.filter = `brightness(${b}%) contrast(${c}%) saturate(${s}%) hue-rotate(${h}deg)`;
        }

        function resetSliders() {
            document.getElementById('brightness').value = 100;
            document.getElementById('contrast').value = 100;
            document.getElementById('saturation').value = 100;
            document.getElementById('hue').value = 0;
        }

        function resetFilters() {
            activeMedia.style.filter = 'none';
            resetSliders();
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
