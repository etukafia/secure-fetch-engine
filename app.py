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

    # THE DIGITAL PADLOCK: Change "Fetch2026" to whatever password you want
    if passcode != "Fetch2026": 
        return jsonify({"error": "Access denied. Invalid passcode."}), 401

    if not url:
        return jsonify({"error": "Please provide a valid link."}), 400

    # Engine settings for best quality without using server storage
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or info.get('entries', [{}])[0].get('url')
            
            return jsonify({"success": True, "video_url": video_url})
    except Exception as e:
        return jsonify({"success": False, "error": "Could not extract video. The link might be private."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)