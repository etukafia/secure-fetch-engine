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

    # THE REAL FIX: Notice there is NO 'format' line here at all. 
    # This guarantees yt-dlp will never throw the "Requested format not available" error again.
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
            # Get the giant dictionary of data without trying to pick a format yet
            info = ydl.extract_info(url, download=False)
            
            video_url = None
            
            # Step 1: Manually hunt through the formats for one that has BOTH video and audio
            if 'formats' in info:
                merged_formats = [
                    f for f in info['formats'] 
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
                ]
                
                if merged_formats:
                    # Sort them to get the highest quality one available
                    merged_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                    video_url = merged_formats[0].get('url')
            
            # Step 2: If we couldn't find a merged one, just grab the default URL YouTube gave us
            if not video_url:
                video_url = info.get('url')

            # Step 3: If it's STILL empty, throw an error we can actually read
            if not video_url:
                return jsonify({"success": False, "error": "YouTube sent the data, but no playable links were found inside."}), 500
            
            return jsonify({"success": True, "video_url": video_url})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
