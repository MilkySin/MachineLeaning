from flask import Flask, render_template, request, redirect, jsonify
import os
from pathlib import Path
import shutil

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = os.path.join(BASE_DIR, 'UI')

app = Flask(__name__,
            # Point to UI folder for templates
            template_folder=os.path.join(UI_DIR, 'templates'),
            # Point to UI/static for static files
            static_folder=os.path.join(UI_DIR, 'static'))

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'Server/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload-handler', methods=['POST'])
def upload_handler():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    if file:
        # Clear the upload folder before saving the new file
        try:
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            print(
                f"Upload folder '{app.config['UPLOAD_FOLDER']}' cleared before new upload.")
        except Exception as e:
            print(f"Error clearing upload folder: {e}")
            return jsonify({'success': False, 'error': 'Failed to clear folder'}), 500

        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return jsonify({'success': True, 'message': 'File uploaded and folder cleared'})
    return jsonify({'success': False, 'error': 'Invalid request method'}), 400


@app.route('/classify_image', methods=['GET'])
def classify_image():
    image_data = request.form['image_data']

    response = jsonify(util.classify_image(image_data))

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == "__main__":
    app.run(debug=True)