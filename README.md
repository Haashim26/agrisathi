README - AgriSathi


Quick start (local):
1. Create Python venv and install requirements.txt
python -m venv venv; source venv/bin/activate; pip install -r requirements.txt
2. Place trained model at models/plant-disease-model.h5
3. Run model server:
export MODEL_PATH=./models/plant-disease-model.h5
uvicorn app.model_server:app --host 0.0.0.0 --port 8000 --reload
4. Run Streamlit app:
export MODEL_SERVER_URL=http://localhost:8000/predict
streamlit run app/streamlit_app.py


Production notes:
- Use Dockerfiles to build images and deploy on Kubernetes or cloud VMs.
- Use GPU instance for model server for faster inference.
- Use managed TTS (AWS Polly) and SMS (MSG91/Twilio) providers.
- Secure endpoints with API keys and rate limiting. Use HTTPS.