from flask import Flask, render_template_string, Response
import io

app = Flask(__name__)

EDITOR_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HD Magic Editor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body { margin: 0; padding: 0; font-family: 'Poppins', sans-serif; background: linear-gradient(to right, #24243e, #302b63, #0f0c29); color: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; }
        .container { width: 95%; max-width: 800px; padding: 20px 0; display: flex; flex-direction: column; align-items: center; }
        h1 { font-weight: 600; font-size: 1.8rem; background: -webkit-linear-gradient(45deg, #ff00cc, #01cdfe, #b967ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 15px; text-align: center; }
        .open-gallery-btn { background: linear-gradient(45deg, #01cdfe, #b967ff); padding: 12px 30px; border: none; border-radius: 30px; color: white; font-size: 1rem; font-weight: bold; cursor: pointer; box-shadow: 0 0 15px rgba(1, 205, 254, 0.5); }
        input[type="file"] { display: none; }
        .preview-area { width: 100%; display: none; justify-content: center; align-items: center; background: #000; border-radius: 15px; overflow: hidden; min-height: 200px; max-height: 400px; position: relative; margin: 15px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .preview-area img, .preview-area video { width: 100%; max-height: 400px; object-fit: contain; transition: filter 0.5s ease; }
        #overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; mix-blend-mode: screen; opacity: 0; transition: opacity 0.5s; }
        .controls { display: none; width: 100%; flex-direction: column; gap: 10px; margin-top: 10px; }
        .section-title { font-size: 0.9rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; margin-bottom: 5px; }
        .btn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; width: 100%; }
        .magic-btn { padding: 12px; border-radius: 10px; border: none; color: white; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: 0.2s; text-align: center; }
        .magic-btn:active { transform: scale(0.95); }
        .btn-hd { background: linear-gradient(135deg, #00b09b, #96c93d); }
        .btn-spider { background: linear-gradient(135deg, #ff00cc, #01cdfe); }
        .btn-hdr { background: linear-gradient(135deg, #ffb347, #00b09b); }
        .btn-reset { background: #444; }
        .btn-lut { background: #2196F3; grid-column: 1 / -1; margin-top: 10px; }
        .btn-download-img { background: #ff9800; grid-column: 1 / -1; }
        .loader { display: none; border: 4px solid rgba(255, 255, 255, 0.1); border-top: 4px solid #01cdfe; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 10px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
                <button class="magic-btn btn-hd" onclick="applyEffect('hd')">✨ Auto HD</button>
                <button class="magic-btn btn-spider" onclick="applyEffect('spider')">Spider-Verse</button>
                <button class="magic-btn btn-hdr" onclick="applyEffect('hdr')">HDR Nature</button>
                <button class="magic-btn btn-reset" onclick="applyEffect('reset')">Reset</button>
            </div>
            <div class="btn-grid" style="margin-top: 15px;">
                <button class="magic-btn btn-download-img" onclick="downloadImage()">⬇️ Download High Quality Image</button>
                <button class="magic-btn btn-lut" onclick="downloadLUT()">⬇️ Download LUT for CapCut/Premiere</button>
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
        let activeMedia = null;
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
                let filter = '';
                let overlayBg = '';
                switch(effect) {
                    case 'hd': filter = 'contrast(1.1) saturate(1.2) brightness(1.05)'; break;
                    case 'spider': filter = 'contrast(1.4) saturate(2) hue-rotate(220deg) brightness(0.9)'; overlayBg = 'linear-gradient(45deg, rgba(255,0,204,0.3) 0%, rgba(1,205,254,0.3) 100%)'; break;
                    case 'hdr': filter = 'contrast(1.3) saturate(2.5) sepia(0.3) hue-rotate(10deg) brightness(1.05)'; overlayBg = 'linear-gradient(45deg, rgba(255,179,71,0.2) 0%, rgba(0,176,155,0.2) 100%)'; break;
                    default: filter = 'none'; overlayBg = 'none';
                }
                activeMedia.style.filter = filter;
                if(overlayBg !== 'none') {
                    overlay.style.background = overlayBg;
                    overlay.style.opacity = '0.6';
                }
            }, 800);
        }

        function downloadImage() {
            if(!activeMedia || previewVideo.style.display === 'block') {
                alert("Please select an Image to download, or use the LUT option for Videos.");
                return;
            }
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = previewImg.naturalWidth;
            canvas.height = previewImg.naturalHeight;
            ctx.filter = activeMedia.style.filter;
            ctx.drawImage(previewImg, 0, 0);
            const link = document.createElement('a');
            link.download = 'hd_magic_image.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }

        function downloadLUT() {
            if(!activeMedia) {
                alert("Please select a Video or Image first to generate a LUT.");
                return;
            }
            window.location.href = '/download_lut?effect=' + currentEffect;
        }
    </script>
</body>
</html>
'''

# LUT ফাইল জেনারেট করার জন্য একটি ছোট ফাংশন
def generate_lut(effect):
    # একটি সাধারণ ৩৩x৩৩x৩৩ সাইজের LUT ফাইলের হেডার
    content = "TITLE \"Magic_LUT\"\nLUT_3D_SIZE 33\n"
    # এখানে আসল কালার ম্যাথ না করে একটি ডেমো LUT জেনারেট করা হচ্ছে
    # বাস্তবে একটি সঠিক LUT ফাইল তৈরি করতে হলে কালার সায়েন্সের জটিল হিসাব করতে হয়
    for b in range(33):
        for g in range(33):
            for r in range(33):
                # সাধারণ মান (০ থেকে ১ এর মধ্যে)
                r_val = r / 32.0
                g_val = g / 32.0
                b_val = b / 32.0
                
                # ইফেক্ট অনুযায়ী কিছুটা রঙ পরিবর্তন (ডেমো)
                if effect == 'spider':
                    r_val = min(1.0, r_val * 1.2)
                    g_val = min(1.0, g_val * 0.8)
                    b_val = min(1.0, b_val * 1.5)
                elif effect == 'hdr':
                    r_val = min(1.0, r_val * 1.1)
                    g_val = min(1.0, g_val * 1.3)
                    b_val = min(1.0, b_val * 0.9)
                
                content += f"{r_val:.6f} {g_val:.6f} {b_val:.6f}\n"
    return content

@app.route('/')
def index():
    return render_template_string(EDITOR_PAGE)

@app.route('/download_lut')
def download_lut():
    effect = request.args.get('effect', 'reset')
    lut_content = generate_lut(effect)
    # ফাইলটি ডাউনলোড হিসেবে পাঠানো
    return Response(
        lut_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment;filename=magic_{effect}.cube'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
