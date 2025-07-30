# --- Dockerfile for running the Streamlit UI with Whisper ---
FROM python:3.12-slim

# 1. Install FFmpeg (for decoding mp4/mp3/wav)
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies and install them
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy project sources (models are not included)
COPY . .

# 4. Expose Streamlit port
EXPOSE 8501

# 5. Launch the UI
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.maxUploadSize", "2048"]
