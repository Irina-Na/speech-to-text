# --- Dockerfile for running the Streamlit UI with Whisper ---
FROM python:3.12-slim

# 1. Install system deps (FFmpeg + libgomp for PyTorch CPU wheels)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies and install them
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy project sources (models are not included)
COPY . .

# 4. Prepare cache/output dirs
RUN mkdir -p /models /app/outputs

# 5. Expose Streamlit port
EXPOSE 8501

# 6. Launch the UI
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.maxUploadSize", "2048"]
