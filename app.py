import os
from flask import Flask, request, send_file, render_template, jsonify
import yt_dlp
import uuid
from threading import Timer

app = Flask(__name__)
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_file(path):
    try:
        os.remove(path)
    except:
        pass

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def download():
    url = request.json.get("url", "")

    if "facebook.com/reel/" not in url and "fb.watch" not in url:
        return jsonify({"error": "Please provide a valid Facebook Reel URL"}), 400

    file_id = str(uuid.uuid4())
    filepath = os.path.join(TEMP_DIR, f"{file_id}.mp4")

    ydl_opts = {
        'outtmpl': filepath,
        'format': 'best[ext=mp4]/best[height<=1080]/best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YtDlp(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'facebook_reel')

        Timer(600, cleanup_file, [filepath]).start()

        return jsonify({
            "success": True,
            "file_id": file_id,
            "title": title
        })
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@app.route("/api/file/<file_id>")
def serve_file(file_id):
    filepath = os.path.join(TEMP_DIR, f"{file_id}.mp4")
    if not os.path.exists(filepath):
        return "File expired or not found", 404
    return send_file(filepath, as_attachment=True, download_name="reel.mp4")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)