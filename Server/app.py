from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
import shutil
import tensorflow as tf
from keras.preprocessing import image
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
            static_folder=os.path.join(UI_DIR, 'static'))  # Corrected typo here

# Load models with progress indication
def load_model_with_progress(model_name, model_path):
    print(f"Loading {model_name} model...")
    start_time = time.time()
    model = tf.keras.models.load_model(model_path)
    print(f"{model_name} model loaded in {time.time() - start_time:.2f} seconds.")
    return model

# Load models
model_vgg = load_model_with_progress('VGG', 'models/task1_vgg_model.h5')
model_mobile_net = load_model_with_progress('MobileNet', 'models/task1_mobile_net_model.h5')
model_cnn = load_model_with_progress('CNN', 'models/task1_cnn_model.h5')

# Configure upload folder
app.config['UPLOAD_FOLDER'] = PIC_DIR
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def prepare_image(file_path):
    """Preprocess the image for prediction"""
    print(f"Preparing image: {file_path}")
    img = image.load_img(file_path, target_size=(224, 224))  # Assuming models take 224x224 images
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize the image
    return img_array


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
        # Save the file in the pic directory
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

        # Prepare the image
        img_array = prepare_image(file_path)

        # Make predictions using the models (models handle preprocessing)
        print("Making predictions...")
        vgg_prediction = model_vgg.predict(img_array)
        mobile_net_prediction = model_mobile_net.predict(img_array)
        cnn_prediction = model_cnn.predict(img_array)

        # Get the class with highest probability from each model
        vgg_class = np.argmax(vgg_prediction, axis=1)[0]
        mobile_net_class = np.argmax(mobile_net_prediction, axis=1)[0]
        cnn_class = np.argmax(cnn_prediction, axis=1)[0]

        # Prepare the predictions data
        predictions = {
            'vgg': vgg_class,
            'mobile_net': mobile_net_class,
            'cnn': cnn_class
        }

        print(f"Predictions for {file.filename}: {predictions}")

        # Save predictions to a file
        prediction_file_path = os.path.join(DATABASE_DIR, 'predictions.json')

        try:
            # Check if the predictions file already exists
            if os.path.exists(prediction_file_path):
                with open(prediction_file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            # Append the image name and predictions to the file
            data[file.filename] = predictions

            # Save the updated data back to the file
            with open(prediction_file_path, 'w') as f:
                json.dump(data, f, indent=4)

            print(f"Predictions saved successfully for {file.filename}")
        except Exception as e:
            print(f"Error saving predictions: {e}")
            return jsonify({'success': False, 'error': f'Failed to save predictions: {e}'}), 500

        return jsonify({'predictions': predictions, 'message': 'Image classified and predictions saved successfully'})


if __name__ == "__main__":
    app.run(debug=True)
