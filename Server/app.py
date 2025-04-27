from flask import Flask, render_template, request, redirect
import os
from pathlib import Path

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


@app.route('/file-upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return 'File uploaded successfully'


if __name__ == "__main__":
    app.run(debug=True)