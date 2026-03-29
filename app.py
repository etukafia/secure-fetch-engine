from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import os
import shutil
import requests

app = Flask(__name__)
CORS(app) 

# --- Cookie Scratchpad Setup ---
SECRET_COOKIE_PATH = '/etc/secrets/cookies.txt'
WRITABLE_COOKIE_PATH = '/tmp/cookies.txt'

def setup_cookies():
    if os.path.exists(SECRET_COOKIE_PATH):
        try:
            shutil.copyfile(SECRET_COOKIE_PATH, WRITABLE_COOKIE_PATH)
        except Exception as e:
            print(f"Cookie copy failed: {e}")

setup_cookies()
# -------------------------------

@app.route('/extract', methods=['POST'])
def extract_media():
    data = request.json
    url = data.get('url')
    passcode = data.get('passcode')

    if passcode != "Fetch2026": 
        return jsonify({"error": "Access denied. Invalid passcode."}), 401

    if not url:
        return jsonify({"error": "Please provide a valid link."}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }

    if os.path.exists(WRITABLE_COOKIE_PATH):
        ydl_opts['cookiefile'] = WRITABLE_COOKIE_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # THE FIX: Ultra-forgiving extraction.
            # 1. Try to grab the default link it found
            video_url = info.get('url')
            
            # 2. Check if it's hiding in a different folder
            if not video_url and 'requested_formats' in info:
                video_url = info['requested_formats'][0].get('url')

            # 3. If all else fails, just grab the biggest MP4 we can find
            if not video_url and 'formats' in info:
                mp4s = [f for f in info['formats'] if f.get('ext') == 'mp4' and f.get('url')]
                if mp4s:
                    mp4s.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                    video_url = mp4s[0].get('url')
            
            if not video_url:
                return jsonify({"success": False, "error": "No playable links were found."}), 500
            
            return jsonify({"success": True, "video_url": video_url})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

# --- THE PROXY DOWNLOADER ---
@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL provided", 400
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://twitter.com/'
        }
        r = requests.get(video_url, stream=True, headers=headers)
        
        return Response(
            stream_with_context(r.iter_content(chunk_size=8192)),
            content_type=r.headers.get('content-type', 'video/mp4'),
            headers={
                'Content-Disposition': 'attachment; filename="secure_fetch_video.mp4"'
            }
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
