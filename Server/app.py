from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
import shutil
import tensorflow as tf
import numpy as np
import json
import time

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = os.path.join(BASE_DIR, 'UI')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
PIC_DIR = os.path.join(DATABASE_DIR, 'pic')

app = Flask(__name__,
            template_folder=os.path.join(UI_DIR, 'templates'),
            static_folder=os.path.join(UI_DIR, 'static'))

# Load models with progress indication
def loader(model_name, model_path):
    print(f"Loading {model_name} model...")
    start_time = time.time()
    model = tf.keras.models.load_model(model_path)
    print(f"{model_name} model loaded in {time.time() - start_time:.2f} seconds.")
    return model

# Load models
model_vgg = loader('VGG', 'models/task1_vgg_model.h5')
model_mobile_net = loader('MobileNet', 'models/task1_mobile_net_model.h5')
model_cnn = loader('CNN', 'models/task1_cnn_model.h5')

# Configure upload folder
app.config['UPLOAD_FOLDER'] = PIC_DIR
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
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            print(f"File uploaded successfully: {file.filename}")
            return jsonify({'success': True, 'message': 'File uploaded successfully'})
        except Exception as e:
            print(f"Error during file upload: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/classify_image', methods=['POST'])
def classify_image():
    file = request.files['file']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(f"Classifying image: {file.filename}")

        try:
            # Make predictions using the models (assuming they handle image loading internally)
            print("Making predictions...")
            vgg_prediction = model_vgg.predict([file_path])
            mobile_net_prediction = model_mobile_net.predict([file_path])
            cnn_prediction = model_cnn.predict([file_path])

            vgg_class = int(np.argmax(vgg_prediction, axis=1)[0])
            mobile_net_class = int(np.argmax(mobile_net_prediction, axis=1)[0])
            cnn_class = int(np.argmax(cnn_prediction, axis=1)[0])

            predictions = {
                'vgg': vgg_class,
                'mobile_net': mobile_net_class,
                'cnn': cnn_class
            }

            print(f"Predictions for {file.filename}: {predictions}")

            prediction_file_path = os.path.join(DATABASE_DIR, 'predictions.json')

            # Save predictions to JSON
            if os.path.exists(prediction_file_path):
                with open(prediction_file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            data[file.filename] = predictions

            with open(prediction_file_path, 'w') as f:
                json.dump(data, f, indent=4)

            print(f"Predictions saved successfully for {file.filename}")
            return jsonify({'predictions': predictions, 'message': 'Image classified and predictions saved successfully'})
        except Exception as e:
            print(f"Error during classification: {e}")
            return jsonify({'success': False, 'error': f'Prediction failed: {e}'}), 500


if __name__ == "__main__":
    app.run(debug=True)
