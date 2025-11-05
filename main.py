from flask import Flask, render_template, request, jsonify
import instaloader
import os

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

        target_folder = "static"
        loader.download_post(post, target=target_folder)

        # Remove any .txt files in the target folder
        for filename in os.listdir(target_folder):
            if filename.endswith(".txt"):
                os.remove(os.path.join(target_folder, filename))

        return jsonify({'success': 'Video downloaded successfully!'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

