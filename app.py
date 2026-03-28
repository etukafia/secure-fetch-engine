from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import shutil

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

    # THE DIGITAL PADLOCK
    if passcode != "Fetch2026": 
        return jsonify({"error": "Access denied. Invalid passcode."}), 401

    if not url:
        return jsonify({"error": "Please provide a valid link."}), 400

    # THE FIX: Disguise the server as an Android device to bypass Javascript puzzles
    ydl_opts = {
        'format': 'best[ext=mp4]/b',
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
            
            # Safely extract the direct link
            video_url = info.get('url') or (info.get('entries', [{}])[0].get('url') if 'entries' in info else None)

            if not video_url:
                return jsonify({"success": False, "error": "YouTube blocked the mobile API request."}), 500
            
            return jsonify({"success": True, "video_url": video_url})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
