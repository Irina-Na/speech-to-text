# Whisper Transcriber

Local audio/video transcription based on OpenAI Whisper. Works via CLI and a Streamlit UI, with models cached locally.

## Features

- Formats: MP4, MP3, WAV, M4A (anything supported by FFmpeg)
- Models: `tiny`, `base`, `small`, `medium`, `large`
- Auto GPU: uses CUDA when available, otherwise CPU
- Model cache: stored in `models/`
- Output: text + (optional) timestamps in `txt/srt/vtt/tsv`

## Quick start (local)

1. Install Python 3.12+ and FFmpeg.
2. Clone the repo and create a venv:

```bash
git clone https://github.com/Irina-Na/speech-to-text.git
cd speech-to-text
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the UI:

```bash
streamlit run app.py --server.maxUploadSize 2048
# Open http://localhost:8501
```

## CLI usage

```bash
python transcribe_video.py path_to_file.mp4 \
  -o transcript.txt \
  -m small \
  -l ru
```

### Language auto-detection by filename

In batch mode, the language is inferred from the filename (without extension):

- Name starts with `en` (case-insensitive) -> English
- Name starts with `ru` -> Russian
- Otherwise, the `-l` parameter is used (default `ru`)

Examples:
- `en_interview1.mp4` -> `en`
- `ru_sozvon.wav` -> `ru`
- `myfile.mp3` -> `ru` (default)

### Timestamps (separate file)

Add the `--timestamps` flag and choose a format:

```bash
python transcribe_video.py path_to_file.mp4 \
  -o transcript.txt \
  --timestamps srt --language en
```

Available formats:
- `txt` - lines like `[HH:MM:SS.mmm - HH:MM:SS.mmm] text`
- `srt` - standard SRT subtitles
- `vtt` - WebVTT
- `tsv` - `start<TAB>end<TAB>text`

### Timestamp-per-line text file

Use `--timestamps txt` to create a file like:

```text
[00:00:01.230 - 00:00:04.560] Hello, this is a test.
[00:00:04.560 - 00:00:08.900] Next phrase.
```

### Batch processing (batch_transcribe.py)

The script reads files from `video/` and writes results to `outputs/`.

```bash
python batch_transcribe.py \
  --input-dir video \
  --output-dir outputs \
  -m large
```

If you need timestamps for each file, add `--timestamps` and choose a format:

```bash
python batch_transcribe.py \
  --input-dir video \
  --output-dir outputs \
  -m large \
  --timestamps txt
```

Example output: `outputs/meeting.txt` + `outputs/meeting.srt`.

## Docker

```bash
docker build -t whisper-ui .
```

### Run the container (Streamlit UI)

PowerShell (Windows):

```powershell
docker run --rm -p 8501:8501 `
  -v ${PWD}\models:/models `
  -v ${PWD}\outputs:/app/outputs `
  whisper-ui
# UI available at http://localhost:8501
```

Linux/macOS:

```bash
docker run --rm -p 8501:8501 \
  -v $(pwd)/models:/models \
  -v $(pwd)/outputs:/app/outputs \
  whisper-ui
# UI available at http://localhost:8501
```

Notes:
- `/models` - Whisper model cache (so they persist between runs)
- `/app/outputs` - output text files and ZIP archives

## Project structure

```text
.
├── app.py
├── transcribe_video.py
├── batch_transcribe.py
├── requirements.txt
├── Dockerfile
├── models/        # model cache
└── outputs/       # results (if using batch scripts)
```

## Environment variables

| Variable           | Default   | Description                        |
| ------------------ | --------- | ---------------------------------- |
| `WHISPER_CACHE_DIR`| `./models`| Overrides Whisper model cache dir  |

## License

MIT.

---

# Whisper Transcriber (RU)

Локальный транскриптер аудио/видео на базе OpenAI Whisper. Работает через CLI и Streamlit-интерфейс, модели кэшируются локально.

## Возможности

- Форматы: MP4, MP3, WAV, M4A (всё, что поддерживает FFmpeg)
- Модели: `tiny`, `base`, `small`, `medium`, `large`
- Авто-GPU: при наличии CUDA используется GPU, иначе CPU
- Кэш моделей: хранится в `models/`
- Вывод: текст + (опционально) таймкоды в `txt/srt/vtt/tsv`

## Быстрый старт (локально)

1. Установите Python 3.12+ и FFmpeg.
2. Клонируйте репозиторий и создайте venv:

```bash
git clone https://github.com/Irina-Na/speech-to-text.git
cd speech-to-text
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
```

3. Установите зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Запуск UI:

```bash
streamlit run app.py --server.maxUploadSize 2048
# Откройте http://localhost:8501
```

## CLI использование

```bash
python transcribe_video.py path_to_file.mp4 \
  -o transcript.txt \
  -m small \
  -l ru
```

### Автоопределение языка по имени файла

При пакетной обработке язык определяется автоматически по имени файла (без расширения):

- Имя начинается с `en` (регистр не важен) -> английский
- Имя начинается с `ru` -> русский
- Иначе используется язык из параметра `-l` (по умолчанию `ru`)

Примеры:
- `en_interview1.mp4` -> `en`
- `ru_sozvon.wav` -> `ru`
- `myfile.mp3` -> `ru` (по умолчанию)

### Таймкоды (отдельный файл)

Добавьте флаг `--timestamps` и выберите формат:

```bash
python transcribe_video.py path_to_file.mp4 \
  -o transcript.txt \
  --timestamps srt --language en
```

Доступные форматы:
- `txt` — строки вида `[HH:MM:SS.mmm - HH:MM:SS.mmm] текст`
- `srt` — стандартные субтитры SRT
- `vtt` — WebVTT
- `tsv` — `start<TAB>end<TAB>text`

### Файл, где каждая строка начинается с таймштампа + текст

Используйте `--timestamps txt`. Будет создан файл с таким видом:

```text
[00:00:01.230 - 00:00:04.560] Привет, это тест.
[00:00:04.560 - 00:00:08.900] Следующая фраза.
```

### Пакетная обработка (batch_transcribe.py)

Скрипт берёт файлы из папки `video/` и складывает результаты в `outputs/`.

```bash
python batch_transcribe.py \
  --input-dir video \
  --output-dir outputs \
  -m large
```

Если нужны таймкоды для каждого файла, добавьте `--timestamps` и выберите формат:

```bash
python batch_transcribe.py \
  --input-dir video \
  --output-dir outputs \
  -m large \
  --timestamps txt
```

Пример результата: `outputs/meeting.txt` + `outputs/meeting.srt`.

## Docker

```bash
docker build -t whisper-ui .
```

### Запуск контейнера (Streamlit UI)

PowerShell (Windows):

```powershell
docker run --rm -p 8501:8501 `
  -v ${PWD}\models:/models `
  -v ${PWD}\outputs:/app/outputs `
  whisper-ui
# UI доступен на http://localhost:8501
```

Linux/macOS:

```bash
docker run --rm -p 8501:8501 \
  -v $(pwd)/models:/models \
  -v $(pwd)/outputs:/app/outputs \
  whisper-ui
# UI доступен на http://localhost:8501
```

Пояснения:
- `/models` — кэш моделей Whisper (чтобы сохранялись между запусками)
- `/app/outputs` — готовые тексты и ZIP-архивы

## Структура проекта

```text
.
├── app.py
├── transcribe_video.py
├── batch_transcribe.py
├── requirements.txt
├── Dockerfile
├── models/        # кэш моделей
└── outputs/       # результаты (если используете пакетные скрипты)
```

## Переменные окружения

| Переменная         | По умолчанию | Назначение                         |
| ------------------ | ------------ | ---------------------------------- |
| `WHISPER_CACHE_DIR`| `./models`   | Переопределяет каталог кэша моделей|

## Лицензия

MIT.
