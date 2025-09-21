from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import numpy as np
import os
import tensorflow as tf

app = FastAPI(title='AgriSathi Model Server')

MODEL_PATH = os.getenv('MODEL_PATH', '/models/plant-disease-model.h5')

# Load model lazily
model = None
class_names = None

def load_model_and_metadata():
    global model, class_names
    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
        # load class_names if available as json
        meta_path = MODEL_PATH.replace('.h5', '.json')
        if os.path.exists(meta_path):
            import json
            with open(meta_path, 'r') as f:
                class_names = json.load(f)
        else:
            # fallback: create dummy labels
            class_names = [f'class_{i}' for i in range(model.output_shape[-1])]

def preprocess_image_bytes(content, target_size=(224, 224)):
    img = Image.open(io.BytesIO(content)).convert('RGB').resize(target_size)
    arr = np.array(img) / 255.0
    arr = np.expand_dims(arr, axis=0).astype(np.float32)
    return arr

@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    try:
        content = await file.read()
        load_model_and_metadata()
        inp = preprocess_image_bytes(content)
        preds = model.predict(inp).flatten()
        idx = int(np.argmax(preds))
        conf = float(preds[idx])
        label = class_names[idx] if class_names else f'label_{idx}'
        return JSONResponse({'label': label, 'confidence': conf})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

if __name__ == '__main__':
    uvicorn.run('model_server:app', host='0.0.0.0', port=8000, reload=True)