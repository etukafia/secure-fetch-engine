from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import shutil

app = Flask(__name__)
# This allows your UI to securely talk to this backend
CORS(app) 

# --- THE FIX: Move cookies to a writable temporary folder ---
SECRET_COOKIE_PATH = '/etc/secrets/cookies.txt'
WRITABLE_COOKIE_PATH = '/tmp/cookies.txt'

def setup_cookies():
    # If the secret vault has cookies, copy them to the writable scratchpad
    if os.path.exists(SECRET_COOKIE_PATH):
        try:
            shutil.copyfile(SECRET_COOKIE_PATH, WRITABLE_COOKIE_PATH)
        except Exception as e:
            print(f"Cookie copy failed: {e}")

# Run the setup right when the server starts
setup_cookies()
# ----------------------------------------------------------

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

    # Engine settings
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    # Only attach the VIP pass if it successfully copied to the scratchpad
    if os.path.exists(WRITABLE_COOKIE_PATH):
        ydl_opts['cookiefile'] = WRITABLE_COOKIE_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or info.get('entries', [{}])[0].get('url')
            
            return jsonify({"success": True, "video_url": video_url})
    except Exception as e:
        # Sends the exact error message to your screen if something goes wrong
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
