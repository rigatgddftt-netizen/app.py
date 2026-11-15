from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Phone Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body { font-family: 'Poppins', sans-serif; margin: 0; padding: 20px; background: #0f0c29; background: linear-gradient(to right, #24243e, #302b63, #0f0c29); color: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; }
        h1 { font-size: 2rem; background: -webkit-linear-gradient(45deg, #01cdfe, #b967ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 20px; }
        .container { width: 100%; max-width: 800px; display: flex; flex-direction: column; gap: 20px; }
        .glass-panel { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
        h3 { margin-top: 0; color: #01cdfe; border-bottom: 1px solid rgba(1, 205, 254, 0.3); padding-bottom: 10px; }
        
        /* ফাইল আপলোড বাটন */
        .file-input-wrapper { position: relative; overflow: hidden; display: inline-block; width: 100%; }
        .file-input-btn { border: 2px dashed #01cdfe; border-radius: 10px; color: #01cdfe; padding: 15px; text-align: center; cursor: pointer; transition: 0.3s; background: rgba(1, 205, 254, 0.1); font-weight: bold; }
        .file-input-btn:hover { background: rgba(1, 205, 254, 0.2); box-shadow: 0 0 15px rgba(1, 205, 254, 0.5); }
        input[type="file"] { position: absolute; left: 0; top: 0; right: 0; bottom: 0; opacity: 0; cursor: pointer; }
        
        /* ফাইল লিস্ট */
        #file-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }
        .file-item { background: #1e293b; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #334155; overflow: hidden; }
        .file-item img { width: 100%; height: 100px; object-fit: cover; border-radius: 5px; margin-bottom: 10px; }
        .file-item video { width: 100%; height: 100px; object-fit: cover; border-radius: 5px; margin-bottom: 10px; }
        .file-item .file-name { font-size: 0.8rem; color: #ccc; word-break: break-all; }
        
        /* ডিভাইস ইনফো */
        .info-item { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #01cdfe; }
        .info-item span { color: #01cdfe; font-weight: bold; }
        
        /* প্রোগ্রেস বার */
        #progress-bar { width: 100%; height: 10px; background: #1e293b; border-radius: 5px; margin-top: 10px; overflow: hidden; display: none; }
        #progress-fill { height: 100%; width: 0%; background: linear-gradient(45deg, #01cdfe, #b967ff); transition: width 0.3s; }
    </style>
</head>
<body>
    <h1>📱 My Phone Dashboard</h1>
    
    <div class="container">
        <!-- ফাইল এক্সপ্লোরার -->
        <div class="glass-panel">
            <h3>📂 Select Files from Phone</h3>
            <div class="file-input-wrapper">
                <div class="file-input-btn">Click to Select Files (Images, Videos, Audio)</div>
                <input type="file" id="fileInput" multiple accept="image/*,video/*,audio/*">
            </div>
            <div id="progress-bar"><div id="progress-fill"></div></div>
            <div id="file-list"></div>
        </div>
        
        <!-- ডিভাইস ইনফো -->
        <div class="glass-panel">
            <h3>📱 Device Information</h3>
            <div id="device-info">
                <div class="info-item"><span>Device Name:</span> <span id="dev-name">Loading...</span></div>
                <div class="info-item"><span>Operating System:</span> <span id="dev-os">Loading...</span></div>
                <div class="info-item"><span>Browser:</span> <span id="dev-browser">Loading...</span></div>
                <div class="info-item"><span>Screen Resolution:</span> <span id="dev-screen">Loading...</span></div>
                <div class="info-item"><span>Battery Status:</span> <span id="dev-battery">Loading...</span></div>
            </div>
        </div>
    </div>

    <script>
        // ডিভাইস ইনফো বের করা
        window.onload = async function() {
            // ডিভাইসের নাম (ব্রাউজার থেকে)
            const deviceName = navigator.userAgent.split('(')[0] || 'Unknown';
            document.getElementById('dev-name').innerText = deviceName;
            
            // অপারেটিং সিস্টেম
            let os = "Unknown";
            if (navigator.userAgent.indexOf("Android") !== -1) os = "Android";
            else if (navigator.userAgent.indexOf("iPhone") !== -1) os = "iOS";
            else if (navigator.userAgent.indexOf("Windows") !== -1) os = "Windows";
            document.getElementById('dev-os').innerText = os;

            // ব্রাউজার
            let browser = "Unknown";
            if (navigator.userAgent.indexOf("Chrome") !== -1) browser = "Google Chrome";
            else if (navigator.userAgent.indexOf("Firefox") !== -1) browser = "Mozilla Firefox";
            else if (navigator.userAgent.indexOf("Safari") !== -1) browser = "Safari";
            document.getElementById('dev-browser').innerText = browser;

            // স্ক্রিন রেজোলিউশন
            document.getElementById('dev-screen').innerText = window.screen.width + " x " + window.screen.height + " px";

            // ব্যাটারি স্ট্যাটাস (যদি ব্রাউজার সাপোর্ট করে)
            if (navigator.getBattery) {
                try {
                    const battery = await navigator.getBattery();
                    document.getElementById('dev-battery').innerText = Math.round(battery.level * 100) + "% " + (battery.charging ? "(Charging)" : "(Not Charging)");
                } catch (e) {
                    document.getElementById('dev-battery').innerText = "Not Available";
                }
            } else {
                document.getElementById('dev-battery').innerText = "Not Supported";
            }
        };

        // ফাইল সিলেক্ট করার লজিক
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('file-list');
        const progressBar = document.getElementById('progress-bar');
        const progressFill = document.getElementById('progress-fill');

        fileInput.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length === 0) return;
            
            fileList.innerHTML = ""; // আগের লিস্ট মুছে ফেলা
            progressBar.style.display = 'block'; // প্রোগ্রেস বার দেখানো
            
            let processed = 0;
            const total = files.length;
            
            for (let file of files) {
                const fileDiv = document.createElement('div');
                fileDiv.classList.add('file-item');
                
                const fileName = document.createElement('div');
                fileName.classList.add('file-name');
                fileName.innerText = file.name;
                
                // ফাইল টাইপ অনুযায়ী প্রিভিউ
                if (file.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    fileDiv.appendChild(img);
                } else if (file.type.startsWith('video/')) {
                    const video = document.createElement('video');
                    video.src = URL.createObjectURL(file);
                    video.controls = true;
                    fileDiv.appendChild(video);
                } else {
                    const icon = document.createElement('div');
                    icon.innerText = "📄";
                    icon.style.fontSize = "40px";
                    fileDiv.appendChild(icon);
                }
                
                fileDiv.appendChild(fileName);
                fileList.appendChild(fileDiv);
                
                processed++;
                // প্রোগ্রেস আপডেট
                const percent = Math.round((processed / total) * 100);
                progressFill.style.width = percent + "%";
            }
            
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressFill.style.width = '0%';
            }, 1000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
