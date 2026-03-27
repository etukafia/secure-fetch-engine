from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# This allows your UI to securely talk to this backend
CORS(app) 

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

    # Engine settings - Now equipped with the VIP Pass (Cookies)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': '/etc/secrets/cookies.txt' # Looks for the secret file in Render
    }

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
