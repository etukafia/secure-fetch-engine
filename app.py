from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import os
import shutil
import requests

app = Flask(__name__)
CORS(app) 

SECRET_COOKIE_PATH = '/etc/secrets/cookies.txt'
WRITABLE_COOKIE_PATH = '/tmp/cookies.txt'

def setup_cookies():
    if os.path.exists(SECRET_COOKIE_PATH):
        try:
            shutil.copyfile(SECRET_COOKIE_PATH, WRITABLE_COOKIE_PATH)
        except Exception as e:
            print(f"Cookie copy failed: {e}")

setup_cookies()

@app.route('/extract', methods=['POST'])
def extract_media():
    data = request.json
    url = data.get('url')
    passcode = data.get('passcode')
    # NEW: The engine now checks which quality button you clicked
    quality = data.get('quality', 'best') 

    if passcode != "Fetch2026": 
        return jsonify({"error": "Access denied. Invalid passcode."}), 401

    if not url:
        return jsonify({"error": "Please provide a valid link."}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {'player_client': ['tv', 'web']}
        }
    }

    if os.path.exists(WRITABLE_COOKIE_PATH):
        ydl_opts['cookiefile'] = WRITABLE_COOKIE_PATH

    # If the user just wants the MP3/Audio
    if quality == 'audio':
        ydl_opts['format'] = 'bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            
            # --- THE UPGRADED SMART FILTER ---
            if 'formats' in info and quality != 'audio':
                is_youtube = 'youtube' in info.get('extractor', '').lower()
                valid_formats = []
                
                for f in info['formats']:
                    if f.get('protocol') not in ['http', 'https']:
                        continue
                    if f.get('vcodec') == 'none':
                        continue
                    if is_youtube and f.get('acodec') == 'none':
                        continue
                    if f.get('ext') != 'mp4':
                        continue
                        
                    # Filter out resolutions higher than what the user requested
                    h = f.get('height', 0) or 0
                    if quality == '720p' and h > 720:
                        continue
                    if quality == '480p' and h > 480:
                        continue
                        
                    valid_formats.append(f)
                    
                if valid_formats:
                    valid_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                    video_url = valid_formats[0].get('url')
            
            # Fallbacks
            if not video_url and 'requested_formats' in info:
                video_url = info['requested_formats'][0].get('url')
            if not video_url:
                video_url = info.get('url')
            
            if not video_url:
                return jsonify({"success": False, "error": "No playable links were found."}), 500
            
            return jsonify({"success": True, "video_url": video_url})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Engine Error: {str(e)}"}), 500

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
                'Content-Disposition': 'attachment; filename="secure_fetch_media.mp4"'
            }
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
