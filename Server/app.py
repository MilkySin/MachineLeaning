from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
import shutil
import tensorflow as tf
import numpy as np
import json
import time
from tensorflow.keras.preprocessing import image

# Get absolute paths
from pathlib import Path
import os

# Points to Server/
BASE_DIR = Path(__file__).resolve().parent

# UI folder is sibling to Server
UI_DIR = os.path.join(BASE_DIR.parent, 'UI')

# Uploads and models are inside Server
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
PIC_DIR = os.path.join(UPLOAD_DIR, 'pic')


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
        # Clear the upload folder before saving the new file
        try:
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            PIC_DIR = os.path.join(UPLOAD_DIR, 'pic')
            os.makedirs(PIC_DIR, exist_ok=True)
            app.config['UPLOAD_FOLDER'] = PIC_DIR
            print(
                f"Upload folder '{app.config['UPLOAD_FOLDER']}' cleared before new upload.")
        except Exception as e:
            print(f"Error clearing upload folder: {e}")
            return jsonify({'success': False, 'error': 'Failed to clear folder'}), 500

        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return jsonify({'success': True, 'message': 'File uploaded and folder cleared'})
    return jsonify({'success': False, 'error': 'Invalid request method'}), 400

#normalize the image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))  
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  
    img_array = img_array / 255.0  
    return img_array


@app.route('/classify_image', methods=['POST'])
def classify_image():
    file = request.files['file']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(f"Classifying image: {file.filename}")

        try:
            # Preprocess image for prediction
            img_array = preprocess_image(file_path)

            # Predict with all models
            vgg_prediction = model_vgg.predict(img_array)
            mobile_net_prediction = model_mobile_net.predict(img_array)
            cnn_prediction = model_cnn.predict(img_array)

            # Get the predicted class index
            vgg_class = int(np.argmax(vgg_prediction, axis=1)[0])
            mobile_net_class = int(np.argmax(mobile_net_prediction, axis=1)[0])
            cnn_class = int(np.argmax(cnn_prediction, axis=1)[0])

            predictions = {
                'vgg': vgg_class,
                'mobile_net': mobile_net_class,
                'cnn': cnn_class
            }

            # Save to predictions.json
            prediction_file_path = os.path.join(UPLOAD_DIR, 'predictions.json')
            if os.path.exists(prediction_file_path):
                with open(prediction_file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            data[file.filename] = predictions

            with open(prediction_file_path, 'w') as f:
                json.dump(data, f, indent=4)

            return jsonify({'predictions': predictions, 'message': 'Image classified and predictions saved successfully'})
        except Exception as e:
            print(f"Error during classification: {e}")
            return jsonify({'success': False, 'error': f'Prediction failed: {e}'}), 500



if __name__ == "__main__":
    app.run(debug=True)
