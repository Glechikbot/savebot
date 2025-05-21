import os
import re
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
app = Flask(__name__)

IG_COOKIE = os.getenv("IG_COOKIE", "")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Cookie": IG_COOKIE
}

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/download_instagram", methods=["POST"])
def download_instagram():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing url"}), 400

    resp = requests.get(url, headers=HEADERS, timeout=10)
    html = resp.text

    # 1) Search for direct video_url JSON
    m = re.search(r'"video_url":"([^"]+)"', html)
    if m:
        link = m.group(1).replace("\u0026", "&").replace("\\", "")
        return jsonify({"url": link})

    # 2) Fallback: meta og:video
    m2 = re.search(r'<meta property="og:video" content="([^"]+)"', html)
    if m2:
        return jsonify({"url": m2.group(1)})

    # 3) Debug log first 1000 chars of HTML
    print("==== HTML START ====")
    print(html[:1000])
    print("==== HTML END ====")
    return jsonify({"error": "Video not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)