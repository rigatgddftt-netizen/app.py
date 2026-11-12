from flask import Flask, render_template_string, Response, request
import io

app = Flask(__name__)

EDITOR_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HD Magic Video Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        body {
            margin: 0; padding: 0;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(to right, #24243e, #302b63, #0f0c29);
            color: #fff; min-height: 100vh; overflow-x: hidden;
            display: flex; flex-direction: column; align-items: center;
        }

        .container { width: 95%; max-width: 800px; padding: 20px 0; display: flex; flex-direction: column; align-items: center; }

        h1 {
            font-weight: 600; font-size: 1.8rem;
            background: -webkit-linear-gradient(45deg, #ff00cc, #01cdfe, #b967ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 15px; text-align: center;
        }

        .open-gallery-btn {
            background: linear-gradient(45deg, #01cdfe, #b967ff);
            padding: 12px 30px; border: none; border-radius: 30px;
            color: white; font-size: 1rem; font-weight: bold; cursor: pointer;
            box-shadow: 0 0 15px rgba(1, 205, 254, 0.5);
            transition: 0.3s;
        }
        .open-gallery-btn:hover { transform: scale(1.05); }
        
        input[type="file"] { display: none; }

        .preview-area {
            width: 100%; display: none; justify-content: center; align-items: center;
            background: #000; border-radius: 15px; overflow: hidden;
            min-height: 200px; max-height: 400px; position: relative; margin: 15px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }

        .preview-area img, .preview-area video {
            width: 100%; max-height: 400px; object-fit: contain;
            transition: filter 0.5s ease, transform 0.5s ease;
        }

        #overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; mix-blend-mode: screen; opacity: 0; transition: opacity 0.5s;
        }

        .controls { display: none; width: 100%; flex-direction: column; gap: 10px; margin-top: 10px; }
        
        .section-title { font-size: 0.9rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; margin-bottom: 5px; }

        .btn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; width: 100%; }

        .magic-btn {
            padding: 12px; border-radius: 10px; border: none;
            color: white; font-weight: 600; font-size: 0.85rem;
            cursor: pointer; transition: 0.2s; text-align: center;
        }

        .magic-btn:active { transform: scale(0.95); }

        .btn-hd { background: linear-gradient(135deg, #00b09b, #96c93d); box-shadow: 0 0 10px rgba(150, 201, 61, 0.4); }
        .btn-spider { background: linear-gradient(135deg, #ff00cc, #01cdfe); box-shadow: 0 0 10px rgba(255, 0, 204, 0.4); }
        .btn-hdr { background: linear-gradient(135deg, #ffb347, #00b09b); box-shadow: 0 0 10px rgba(255, 179, 71, 0.4); }
        .btn-sunset { background: linear-gradient(135deg, #ff512f, #dd2476); }
        .btn-cinematic { background: linear-gradient(135deg, #141E30, #243B55); border: 1px solid #444; }
        .btn-reset { background: #444; }

        .slider-group { display: flex; flex-direction: column; margin-bottom: 10px; width: 100%; }
        .slider-group label { font-size: 0.8rem; color: #ccc; margin-bottom: 5px; display: flex; justify-content: space-between;}
        
        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; margin: 5px 0; }
        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none; height: 18px; width: 18px; border-radius: 50%;
            background: #01cdfe; cursor: pointer; margin-top: -7px; box-shadow: 0 0 10px #01cdfe;
        }
        input[type=range]::-webkit-slider-runnable-track {
            width: 100%; height: 4px; cursor: pointer;
            background: linear-gradient(90deg, #ff00cc, #01cdfe); border-radius: 2px;
        }

        .loader {
            display: none; border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #01cdfe; border-radius: 50%;
            width: 30px; height: 30px; animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .download-section { display: none; width: 100%; margin-top: 20px; border-top: 1px solid #333; padding-top: 15px; }

    </style>
</head>
<body>
    <div class="container">
        <h1>HD Magic Editor</h1>
        
        <button class="open-gallery-btn" id="openGalleryBtn">📂 Select Video/Photo</button>
        <input type="file" id="mediaUpload" accept="image/*,video/*">

        <div class="preview-area" id="previewContainer">
            <img id="previewImg" alt="Preview">
            <video id="previewVideo" style="display:none;" controls autoplay loop muted playsinline></video>
            <div id="overlay"></div>
            <div class="loader" id="loader"></div>
        </div>
        
        <div class="controls" id="controls">
            <div class="section-title">Filters & Quality</div>
            <div class="btn-grid">
                <button class="magic-btn btn-hd" onclick="applyEffect('hd')">✨ Auto HD Enhance</button>
                <button class="magic-btn btn-spider" onclick="applyEffect('spider')">Spider-Verse Neon</button>
                <button class="magic-btn btn-hdr" onclick="applyEffect('hdr')">HDR Nature</button>
                <button class="magic-btn btn-sunset" onclick="applyEffect('sunset')">Sunset Glow</button>
                <button class="magic-btn btn-cinematic" onclick="applyEffect('cinematic')">Cinematic Blue</button>
                <button class="magic-btn btn-reset" onclick="applyEffect('reset')">Reset</button>
            </div>

            <div class="section-title">Manual Adjustments</div>
            <div class="slider-group">
                <label>Sharpness (HD) <span id="valShapr">0</span></label>
                <input type="range" id="sharpness" min="0" max="100" value="0" oninput="updateManual()">
            </div>
            <div class="slider-group">
                <label>Brightness <span id="valBright">100</span></label>
                <input type="range" id="brightness" min="0" max="200" value="100" oninput="updateManual()">
            </div>
            <div class="slider-group">
                <label>Saturation <span id="valSat">100</span></label>
                <input type="range" id="saturation" min="0" max="200" value="100" oninput="updateManual()">
            </div>
        </div>

        <!-- ডাউনলোড সেকশন -->
        <div class="download-section" id="downloadSection">
            <div class="section-title">Download</div>
            <div class="btn-grid">
                <button class="magic-btn" style="background: #ff9800; grid-column: 1 / -1;" onclick="downloadImage()">⬇️ Download High Quality Image</button>
                <button class="magic-btn" style="background: #2196F3; grid-column: 1 / -1;" onclick="downloadLUT()">⬇️ Download LUT for CapCut/Premiere</button>
            </div>
        </div>
    </div>

    <script>
        const previewImg = document.getElementById('previewImg');
        const previewVideo = document.getElementById('previewVideo');
        const overlay = document.getElementById('overlay');
        const loader = document.getElementById('loader');
        const previewContainer = document.getElementById('previewContainer');
        const controls = document.getElementById('controls');
        const openGalleryBtn = document.getElementById('openGalleryBtn');
        const mediaUpload = document.getElementById('mediaUpload');
        const downloadSection = document.getElementById('downloadSection');
        let activeMedia = null;
        let isVideo = false;
        let currentEffect = 'reset';

        openGalleryBtn.addEventListener('click', () => mediaUpload.click());

        mediaUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileType = file.type;
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    openGalleryBtn.style.display = 'none';
                    previewContainer.style.display = 'flex';
                    controls.style.display = 'flex';
                    downloadSection.style.display = 'flex';
                    
                    if (fileType.startsWith('image/')) {
                        previewImg.src = event.target.result;
                        previewImg.style.display = 'block';
                        previewVideo.style.display = 'none';
                        activeMedia = previewImg;
                        isVideo = false;
                    } else if (fileType.startsWith('video/')) {
                        previewVideo.src = event.target.result;
                        previewVideo.style.display = 'block';
                        previewImg.style.display = 'none';
                        activeMedia = previewVideo;
                        isVideo = true;
                    }
                    applyEffect('reset');
                }
                reader.readAsDataURL(file);
            }
        });

        function applyEffect(effect) {
            if(!activeMedia) return;
            currentEffect = effect;
            
            loader.style.display = 'block';
            overlay.style.opacity = '0';
            
            setTimeout(() => {
                loader.style.display = 'none';
                
                document.getElementById('sharpness').value = 0;
                document.getElementById('brightness').value = 100;
                document.getElementById('saturation').value = 100;

                let filter = '';
                let overlayBg = '';
                
                switch(effect) {
                    case 'hd': filter = 'contrast(1.1) saturate(1.2) brightness(1.05)'; break;
                    case 'spider': filter = 'contrast(1.4) saturate(2) hue-rotate(220deg) brightness(0.9)'; overlayBg = 'linear-gradient(45deg, rgba(255,0,204,0.3) 0%, rgba(1,205,254,0.3) 100%)'; break;
                    case 'hdr': filter = 'contrast(1.3) saturate(2.5) sepia(0.3) hue-rotate(10deg) brightness(1.05)'; overlayBg = 'linear-gradient(45deg, rgba(255,179,71,0.2) 0%, rgba(0,176,155,0.2) 100%)'; break;
                    case 'sunset': filter = 'contrast(1.2) saturate(1.8) hue-rotate(330deg) brightness(1.1)'; overlayBg = 'linear-gradient(45deg, rgba(255,81,47,0.3) 0%, rgba(221,36,118,0.3) 100%)'; break;
                    case 'cinematic': filter = 'contrast(1.3) saturate(1.2) hue-rotate(200deg) brightness(0.9)'; overlayBg = 'linear-gradient(45deg, rgba(20,30,48,0.5) 0%, rgba(36,59,85,0.5) 100%)'; break;
                    default: filter = 'none'; overlayBg = 'none';
                }
                
                activeMedia.style.filter = filter;
                if(overlayBg !== 'none') {
                    overlay.style.background = overlayBg;
                    overlay.style.opacity = '0.6';
                }
                updateManual();
            }, 800);
        }

        function updateManual() {
            if(!activeMedia) return;
            const sharp = document.getElementById('sharpness').value;
            const bright = document.getElementById('brightness').value;
            const sat = document.getElementById('saturation').value;
            
            document.getElementById('valShapr').innerText = sharp;
            document.getElementById('valBright').innerText = bright;
            document.getElementById('valSat').innerText = sat;

            let filterParts = [];
            if (currentEffect === 'hd') filterParts.push('contrast(1.1) saturate(1.2)');
            if (currentEffect === 'spider') filterParts.push('contrast(1.4) saturate(2) hue-rotate(220deg)');
            if (currentEffect === 'hdr') filterParts.push('contrast(1.3) saturate(2.5) sepia(0.3) hue-rotate(10deg)');
            if (currentEffect === 'sunset') filterParts.push('contrast(1.2) saturate(1.8) hue-rotate(330deg)');
            if (currentEffect === 'cinematic') filterParts.push('contrast(1.3) saturate(1.2) hue-rotate(200deg)');

            if (sharp > 0) filterParts.push(`contrast(${100 + (sharp/2)}%)`);
            filterParts.push(`brightness(${bright}%)`);
            filterParts.push(`saturate(${sat}%)`);

            activeMedia.style.filter = filterParts.join(' ');
        }

        function downloadImage() {
            if(isVideo) {
                alert("You selected a Video. Please use the 'Download LUT' button for videos.");
                return;
            }
            if(!activeMedia || !previewImg.src) {
                alert("Please select an Image first.");
                return;
            }
            
            // ফিল্টার অ্যাপ্লাই করে ক্যানভাসে ছবি আঁকা
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = previewImg.naturalWidth;
            canvas.height = previewImg.naturalHeight;
            
            // ওভারলে (নিয়ন লেয়ার) সহ ছবি ডাউনলোড করা
            ctx.filter = activeMedia.style.filter;
            ctx.drawImage(previewImg, 0, 0);
            
            // ওভারলে রঙ যোগ করা
            if (overlay.style.opacity > 0) {
                ctx.globalCompositeOperation = 'screen';
                ctx.fillStyle = overlay.style.background;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
            
            const link = document.createElement('a');
            link.download = 'hd_magic_image.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }

        function downloadLUT() {
            if(!activeMedia) {
                alert("Please select a Video or Image first.");
                return;
            }
            // LUT ফাইল ডাউনলোডের জন্য সার্ভারে রিকোয়েস্ট
            window.location.href = '/download_lut?effect=' + currentEffect;
        }
    </script>
</body>
</html>
'''

# LUT ফাইল জেনারেট করার ফাংশন
def generate_lut(effect):
    content = "TITLE \"Magic_LUT\"\nLUT_3D_SIZE 33\n"
    for b in range(33):
        for g in range(33):
            for r in range(33):
                r_val = r / 32.0
                g_val = g / 32.0
                b_val = b / 32.0
                
                if effect == 'spider':
                    r_val = min(1.0, r_val * 1.3)
                    g_val = min(1.0, g_val * 0.7)
                    b_val = min(1.0, b_val * 1.6)
                elif effect == 'hdr':
                    r_val = min(1.0, r_val * 1.1)
                    g_val = min(1.0, g_val * 1.3)
                    b_val = min(1.0, b_val * 0.9)
                elif effect == 'sunset':
                    r_val = min(1.0, r_val * 1.5)
                    g_val = min(1.0, g_val * 0.6)
                    b_val = min(1.0, b_val * 0.4)
                elif effect == 'cinematic':
                    r_val = min(1.0, r_val * 0.8)
                    g_val = min(1.0, g_val * 0.9)
                    b_val = min(1.0, b_val * 1.4)
                
                content += f"{r_val:.6f} {g_val:.6f} {b_val:.6f}\n"
    return content

@app.route('/')
def index():
    return render_template_string(EDITOR_PAGE)

@app.route('/download_lut')
def download_lut():
    effect = request.args.get('effect', 'reset')
    lut_content = generate_lut(effect)
    return Response(
        lut_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment;filename=magic_{effect}.cube'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
