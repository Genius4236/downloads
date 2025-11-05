from flask import Flask, render_template, request, jsonify, send_file, url_for
import instaloader
import os
import tempfile
import shutil
import uuid

app = Flask(__name__)

loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False,
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'Please enter a valid Instagram post URL.'})

    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if not post.is_video:
            return jsonify({'error': 'This post does not contain a video.'})

        # Download directly to static folder
        target_folder = 'static'
        os.makedirs(target_folder, exist_ok=True)
        loader.download_post(post, target=target_folder)

        # Find the newly downloaded video file
        video_file = None
        for filename in os.listdir(target_folder):
            if filename.endswith(".mp4") and shortcode in filename:
                video_file = os.path.join(target_folder, filename)
                break

        if video_file:
            # Return the direct URL to the static file
            download_url = url_for('static', filename=os.path.basename(video_file), _external=True)
            return jsonify({'download_url': download_url, 'filename': os.path.basename(video_file)})
        else:
            return jsonify({'error': 'Video file not found after download.'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

