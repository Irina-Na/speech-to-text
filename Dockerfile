# --- Dockerfile для запуска Streamlit‑UI + Whisper ---
FROM python:3.12-slim

# 1. Устанавливаем FFmpeg (для декодирования mp4/mp3/wav)
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Копируем зависимости и устанавливаем
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем исходники проекта (скрипт, UI, модели не включаем)
COPY . .

# 4. Экспонируем порт Streamlit
EXPOSE 8501

# 5. Запуск UI
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.maxUploadSize", "2048"]
