import io
import os

import mlflow
import numpy as np
from fastapi import FastAPI, File, UploadFile
from PIL import Image


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_URI = "models:/food11@champion"

# Load once at startup
model = mlflow.pyfunc.load_model(MODEL_URI)

app = FastAPI()


CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = image.resize((128, 128))

    # Convert to numpy in HWC format and scale to [0, 1]
    image_array = np.asarray(image).astype("float32") / 255.0

    # Apply the same ImageNet normalization used during training
    mean = np.array([0.485, 0.456, 0.406], dtype="float32")
    std = np.array([0.229, 0.224, 0.225], dtype="float32")

    image_array = (image_array - mean) / std

    # HWC -> CHW
    image_array = np.transpose(image_array, (2, 0, 1))

    # Add batch dimension: CHW -> NCHW
    image_array = np.expand_dims(image_array, axis=0)

    # MLflow PyTorch expects numpy.ndarray, not a list
    prediction = model.predict(image_array)

    # prediction should be shape (1, 11)
    logits = np.asarray(prediction)[0]

    # Softmax for confidence
    exp_logits = np.exp(logits - np.max(logits))
    probabilities = exp_logits / exp_logits.sum()

    class_index = int(np.argmax(probabilities))
    confidence = float(probabilities[class_index])

    return {
        "category": CLASS_NAMES[class_index],
        "confidence": confidence,
    }