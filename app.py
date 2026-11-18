from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/info')
def get_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Link nahi mila'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Video')[:100],
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', ''),
                'video_url': info.get('url'),
                'duration': info.get('duration', 0)
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Video nahi mila. ' + str(e)[:100]}), 400

@app.route('/api/download')
def download_video():
    url = request.args.get('url')
    if not url:
        return "Link nahi mila", 400
    filename = f"{uuid.uuid4().hex}.mp4"
    filepath = f"/tmp/{filename}"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': filepath,
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name="waqas-downloader.mp4")
        else:
            return "Download fail ho gaya", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
