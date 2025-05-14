from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
import shutil
from util import *

# Get absolute paths
from pathlib import Path
import os

# Points to Server/
BASE_DIR = Path(__file__).resolve().parent

# UI folder is sibling to Server
UI_DIR = os.path.join(BASE_DIR.parent, "UI")

# Uploads and models are inside Server
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PIC_DIR = os.path.join(UPLOAD_DIR, "pic")


app = Flask(
    __name__,
    template_folder=os.path.join(UI_DIR, "templates"),
    static_folder=os.path.join(UI_DIR, "static"),
)

# Configure upload folder
app.config["UPLOAD_FOLDER"] = PIC_DIR
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-handler", methods=["POST"])
def upload_handler():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    if file:
        # Clear the upload folder before saving the new file
        try:
            shutil.rmtree(app.config["UPLOAD_FOLDER"])
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            PIC_DIR = os.path.join(UPLOAD_DIR, "pic")
            os.makedirs(PIC_DIR, exist_ok=True)
            app.config["UPLOAD_FOLDER"] = PIC_DIR
            print(
                f"Upload folder '{app.config['UPLOAD_FOLDER']}' cleared before new upload."
            )
        except Exception as e:
            print(f"Error clearing upload folder: {e}")
            return jsonify({"success": False, "error": "Failed to clear folder"}), 500

        filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filename)
        return jsonify({"success": True, "message": "File uploaded and folder cleared"})
    return jsonify({"success": False, "error": "Invalid request method"}), 400


@app.route("/classify_image", methods=["POST"])
def classify_image():
    file = request.files["file"]
    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        print(f"Classifying image: {file.filename}")
        return classify_image(file, file_path)
    return jsonify({"success": False, "error": "Invalid request method"}), 400


if __name__ == "__main__":
    app.run(debug=True)
