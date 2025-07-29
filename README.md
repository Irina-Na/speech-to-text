# Whisper‑RU Transcriber

A lightweight solution powered by **OpenAI Whisper** that automatically transcribes Russian‑language audio or video.

* 📝 **CLI script:** `transcribe_video_to_russian.py`
* 🌐 **Web UI:** Streamlit app `app.py`
* 📦 **Container:** Dockerfile (Python 3.12 + FFmpeg)
* 🚀 **Model cache:** models are downloaded once to `./models` and reused on subsequent runs

## Features

| Feature            | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| Supported formats  | MP4, MP3, WAV, M4A (any container decodable by FFmpeg)       |
| Model sizes        | `tiny`, `base`, `small`, `medium`, `large`                   |
| Auto‑GPU detection | Automatically uses CUDA (if available) or falls back to CPU  |
| Local cache        | Downloads each model once and stores it in `models/`         |
| Output             | UTF‑8 text file; Streamlit UI provides a **Download** button |

## Quick start (local — Windows / Linux / macOS)

1. **Install** Python ≥ 3.12 **and FFmpeg**:

   * **Windows** – easiest via [Chocolatey](https://chocolatey.org/install):

     ```powershell
     choco install ffmpeg -y
     ```
   * **macOS** – via [Homebrew](https://brew.sh/):

     ```bash
     brew install ffmpeg
     ```
   * **Ubuntu/Debian**:

     ```bash
     sudo apt update && sudo apt install ffmpeg -y
     ```

   Verify with `ffmpeg -version` – you should see build information in the console.
2. Clone the repo:

   ```bash
   git clone https://github.com/Irina-Na/speech-to-text.git
   cd speech-to-text
   ```
3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Linux/macOS
   source venv/bin/activate
   ```
4. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Launch the web interface:

   ```bash
   streamlit run app.py --server.maxUploadSize 2048
   # Open http://localhost:8501 in your browser
   ```

### CLI usage

```bash
python transcribe_video_to_russian.py path_to_file.mp4 \
       -o transcript.txt \
       -m small \
       -l ru
```

## Quick start with Docker

```bash
# Build the image
docker build -t whisper-ru-ui .

# Run the container
docker run -p 8501:8501 whisper-ru-ui
# UI available at http://localhost:8501
```

## Project structure

```text
.
├── app.py                  # Streamlit UI
├── transcribe_video_to_russian.py
├── requirements.txt
├── Dockerfile
├── models/                 # Cached Whisper models (auto‑created)
└── outputs/                # Generated transcripts (auto‑created)
```

## Environment variables

| Variable            | Default    | Purpose                            |
| ------------------- | ---------- | ---------------------------------- |
| `WHISPER_CACHE_DIR` | `./models` | Override the model cache directory |

## Updating a model

Need a different model size? Pass `-m medium` (or another size) to the CLI or pick it in the UI; the script downloads the new weights into the same cache directory.

## License

MIT.


# Whisper‑RU Transcriber

Простое решение на основе **OpenAI Whisper** для автоматической транскрибации аудио/видео на русском языке.

- 📝 CLI‑скрипт: `transcribe_video_to_russian.py`
- 🌐 Web‑интерфейс: Streamlit‑приложение `app.py`
- 📦 Контейнер: Dockerfile (Python 3.12 + FFmpeg)
- 🚀 Кэш моделей: первая загрузка — скачивание в каталог `./models`, далее — локальное использование

## Возможности

| Функция                | Описание                                                 |
| ---------------------- | -------------------------------------------------------- |
| Поддерживаемые форматы | MP4, MP3, WAV, M4A (другие, поддерживаемые FFmpeg)       |
| Размеры модели         | `tiny`, `base`, `small`, `medium`, `large`               |
| Авто‑GPU               | Автоматический выбор CUDA‑устройства (при наличии)       |
| Кэш                    | Модели загружаются один раз и сохраняются в `models/`    |
| Вывод                  | UTF‑8 текстовый файл; через UI доступна кнопка «Скачать» |

## Быстрый старт (локально, Windows / Linux / macOS)

1. **Установите** Python ≥ 3.12 и FFmpeg.
2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Irina-Na/speech-to-text.git
   cd speech-to-text
   ```
3. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Linux/macOS
   source venv/bin/activate
   ```
4. Установите зависимости:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Запустите веб‑интерфейс:
   ```bash
   streamlit run app.py --server.maxUploadSize 2048
   # Откройте http://localhost:8501
   ```

### Использование CLI

```bash
python transcribe_video_to_russian.py путь_к_файлу.mp4 \
       -o transcript.txt \
       -m small \
       -l ru
```

## Быстрый старт в Docker

```bash
# Cборка образа
docker build -t whisper-ru-ui .

# Запуск контейнера
docker run -p 8501:8501 whisper-ru-ui
# UI будет доступен на http://localhost:8501
```

## Структура проекта

```
.
├── app.py                  # Streamlit‑UI
├── transcribe_video_to_russian.py
├── requirements.txt
├── Dockerfile
├── models/                 # Кэш скачанных моделей (создаётся автоматически)
└── outputs/                # Автоматически создаётся для транскриптов
```

## Переменные окружения

| Переменная          | По умолчанию | Назначение                          |
| ------------------- | ------------ | ----------------------------------- |
| `WHISPER_CACHE_DIR` | `./models`   | Переопределяет каталог кэша моделей |

## Обновление модели

Для смены размера модели достаточно указать флаг `-m medium` в CLI или выбрать размер в UI. Скрипт скачает новую модель и сохранит её рядом с текущими.

## Лицензия

MIT.

