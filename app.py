from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import shutil

app = Flask(__name__)
# This allows your UI to securely talk to this backend
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

    # THE DIGITAL PADLOCK
    if passcode != "Fetch2026": 
        return jsonify({"error": "Access denied. Invalid passcode."}), 401

    if not url:
        return jsonify({"error": "Please provide a valid link."}), 400

    # THE FIX: We removed the strict 'format' rule so yt-dlp NEVER crashes here.
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    if os.path.exists(WRITABLE_COOKIE_PATH):
        ydl_opts['cookiefile'] = WRITABLE_COOKIE_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # yt-dlp fetches the giant dictionary of every possible file version
            info = ydl.extract_info(url, download=False)
            
            video_url = None
            
            # 1. We manually hunt for a file that contains BOTH video and audio codecs
            formats = info.get('formats', [])
            merged_formats = [
                f for f in formats 
                if f.get('vcodec') and f.get('vcodec') != 'none' 
                and f.get('acodec') and f.get('acodec') != 'none'
            ]
            
            if merged_formats:
                # Sort them by resolution height (biggest first)
                best_merged = sorted(merged_formats, key=lambda x: x.get('height', 0) or 0, reverse=True)[0]
                video_url = best_merged.get('url')
            
            # 2. Fallback: If YouTube stripped all merged files, grab the default URL
            if not video_url:
                video_url = info.get('url')
                
            # 3. Final Fallback: Grab the first requested format available
            if not video_url and 'requested_formats' in info:
                video_url = info['requested_formats'][0].get('url')

            if not video_url:
                return jsonify({"success": False, "error": "YouTube did not provide any playable links."}), 500
            
            return jsonify({"success": True, "video_url": video_url})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
