from flask import Flask, render_template, request, jsonify, send_file
import instaloader
import os
import tempfile
import shutil

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

        # Create a temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            loader.download_post(post, target=temp_dir)

            # Find the video file (should be the only .mp4 file)
            video_file = None
            for filename in os.listdir(temp_dir):
                if filename.endswith(".mp4"):
                    video_file = os.path.join(temp_dir, filename)
                    break

            if video_file:
                # Send the file to the user for download
                return send_file(video_file, as_attachment=True, download_name=f"{shortcode}.mp4")
            else:
                return jsonify({'error': 'Video file not found after download.'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

