<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Media Fetch</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white font-sans min-h-screen flex items-center justify-center p-4">

    <div class="bg-gray-800 rounded-2xl shadow-2xl p-6 md:p-8 w-full max-w-md mx-auto border border-gray-700">
        
        <div class="text-center mb-8">
            <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500 mb-2">
                Secure Fetch
            </h1>
            <p class="text-sm text-gray-400">Personal Downloader Node</p>
        </div>

        <div class="flex flex-col gap-4 mb-6">
            <input type="password" id="passcode-input" placeholder="Enter secret passcode..."
                   class="w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/50 text-gray-100 placeholder-gray-500 transition-all">
            
            <input type="url" id="link-input" placeholder="Paste video link here..."
                   class="w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/50 text-gray-100 placeholder-gray-500 transition-all">
            
            <button id="extract-btn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-indigo-500/30 transition-all duration-200 active:scale-95">
                Extract Media
            </button>
        </div>

        <div id="video-container" class="w-full min-h-[300px] bg-gray-900 rounded-xl border-2 border-dashed border-gray-600 flex flex-col items-center justify-center mb-6 overflow-hidden transition-all">
            <div class="text-center p-4" id="placeholder-content">
                <svg class="w-10 h-10 mx-auto text-gray-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                <span class="text-gray-500 text-sm font-medium">Video preview will appear here</span>
            </div>
        </div>

        <button id="download-btn" style="display: none;" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-emerald-500/30 transition-all duration-200 active:scale-95">
            Save to Device
        </button>

    </div>

    <script>
        // ==========================================
        // IMPORTANT: PASTE YOUR RENDER URL RIGHT HERE (Do not put a slash at the end)
        const RENDER_URL = 'YOUR_RENDER_URL_HERE'; 
        // ==========================================

        const input = document.getElementById('link-input');
        const passcodeInput = document.getElementById('passcode-input');
        const extractBtn = document.getElementById('extract-btn');
        const downloadBtn = document.getElementById('download-btn');
        const videoContainer = document.getElementById('video-container');

        extractBtn.addEventListener('click', async () => {
            const url = input.value;
            const secretCode = passcodeInput.value;

            if (!secretCode) return alert('Please enter the passcode!');
            if (!url) return alert('Please paste a link first!');

            extractBtn.innerText = 'Extracting...';
            extractBtn.disabled = true;

            try {
                const response = await fetch(`${RENDER_URL}/extract`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, passcode: secretCode }) 
                });

                const data = await response.json();

                if (data.success) {
                    videoContainer.className = "w-full bg-gray-900 rounded-xl border border-gray-600 mb-6 overflow-hidden shadow-inner";
                    videoContainer.innerHTML = `
                        <video src="${data.video_url}" controls autoplay loop muted 
                               class="w-full h-auto block rounded-xl">
                        </video>
                    `;
                    
                    downloadBtn.style.display = 'block';
                    // THE FIX: Routes the download request through your Render server
                    downloadBtn.onclick = () => {
                        window.location.href = `${RENDER_URL}/download?url=${encodeURIComponent(data.video_url)}`;
                    };
                } else {
                    alert(data.error); 
                }
            } catch (error) {
                alert('Server error or waking up. Try again in a moment!');
            } finally {
                extractBtn.innerText = 'Extract Media';
                extractBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
