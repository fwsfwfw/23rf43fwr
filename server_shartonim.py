from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import yt_dlp
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)

VIDEO_DIR = os.path.join(os.getcwd(), "videos")
LOG_FILE = os.path.join(os.getcwd(), "save_video_log.txt")
COOKIES_FILE = os.path.join(os.getcwd(), "www.youtube.com_cookies.txt")  # ✅ נוספה שורת קובץ קוקיז

os.makedirs(VIDEO_DIR, exist_ok=True)

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response

@app.route("/save-video", methods=["POST", "OPTIONS"])
def save_video():
    if request.method == "OPTIONS":
        return '', 200

    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            log("❌ שגיאה: URL לא נשלח")
            return jsonify({"status": "שגיאה", "error": "URL חסר"}), 400

        ydl_opts = {
            'outtmpl': os.path.join(VIDEO_DIR, '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'merge_output_format': 'mp4',
            'cookies': COOKIES_FILE  # ✅ שימוש בקובץ העוגיות
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            short_name = os.path.basename(filename)

        log(f"✅ אושר: הורדה בוצעה ל־URL: {url}")
        return jsonify({
            "status": "אושר",
            "url": url,
            "file": f"/video-file/{short_name}"
        })

    except Exception as e:
        log(f"❌ שגיאה: {str(e)}")
        return jsonify({"status": "שגיאה", "error": str(e)}), 500

@app.route('/video-file/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
