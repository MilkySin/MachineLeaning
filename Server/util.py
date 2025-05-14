from PIL import Image  # Import Pillow for image processing
import numpy as np
from flask import jsonify
import json
import time
import tensorflow as tf

# Get absolute paths
from pathlib import Path
import os


class_labels = [
    "bacterial_leaf_blight",
    "bacterial_leaf_streak",
    "bacterial_panicle_blight",
    "blast",
    "brown_spot",
    "dead_heart",
    "downy_mildew",
    "hispa",
    "normal",
    "tungro",
]

BASE_DIR = Path(__file__).resolve().parent

# UI folder is sibling to Server
UI_DIR = os.path.join(BASE_DIR.parent, "UI")

# Uploads and models are inside Server
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PIC_DIR = os.path.join(UPLOAD_DIR, "pic")


def loader(model_name, model_path):
    print(f"Loading {model_name} model...")
    start_time = time.time()
    model = tf.keras.models.load_model(model_path)
    print(f"{model_name} model loaded in {time.time() - start_time:.2f} seconds.")
    return model


# Load models
model_vgg = loader("VGG", "models/task1_vgg_model.h5")
model_mobile_net = loader("MobileNet", "models/task1_mobile_net_model.h5")
model_cnn = loader("CNN", "models/task1_cnn_model.h5")

# normalize the image


def preprocess_image(img_path):
    img = Image.open(img_path)
    img = img.resize((224, 224))  # Resize to the target size
    img_array = np.array(img) / 255.0  # Normalize to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


def classify_image(file, file_path):
    # Predict with all models
    img_array = preprocess_image(file_path)

    try:
        vgg_prediction = model_vgg.predict(img_array)
        mobile_net_prediction = model_mobile_net.predict(img_array)
        cnn_prediction = model_cnn.predict(img_array)

        vgg_index = int(np.argmax(vgg_prediction, axis=1)[0])
        vgg_confidence = float(np.max(vgg_prediction, axis=1)[0])
        vgg_label = class_labels[vgg_index]

        mobile_index = int(np.argmax(mobile_net_prediction, axis=1)[0])
        mobile_confidence = float(np.max(mobile_net_prediction, axis=1)[0])
        mobile_label = class_labels[mobile_index]

        cnn_index = int(np.argmax(cnn_prediction, axis=1)[0])
        cnn_confidence = float(np.max(cnn_prediction, axis=1)[0])
        cnn_label = class_labels[cnn_index]

        predictions = {
            "vgg": {
                "label": vgg_label,
                "confidence": f"{vgg_confidence * 100:.2f}%",
            },
            "mobile_net": {
                "label": mobile_label,
                "confidence": f"{mobile_confidence * 100:.2f}%",
            },
            "cnn": {
                "label": cnn_label,
                "confidence": f"{cnn_confidence * 100:.2f}%",
            },
        }

        # Save to predictions.json
        prediction_file_path = os.path.join(UPLOAD_DIR, "predictions.json")
        data = {file.filename: predictions}

        with open(prediction_file_path, "w") as f:
            json.dump(data, f, indent=4)

        return jsonify(
            {
                "predictions": predictions,
                "message": "Image classified and predictions saved successfully",
            }
        )
    except Exception as e:
        print(f"Error during classification: {e}")
        return jsonify({"success": False, "error": f"Prediction failed"}), 500
