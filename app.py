import tempfile
from pathlib import Path
import shutil
import zipfile
import streamlit as st
import whisper

from transcribe_video_to_russian import transcribe

st.set_page_config(page_title="Whisper‑RU Transcriber", page_icon="📝", layout="centered")
st.title("📝 Whisper‑RU Transcriber")

st.markdown(
    """
**Single file** ▶ загрузите один медиа‑файл и получите текст.  
**Batch mode** ▶ загрузите сразу несколько файлов; для удобства можно скачать
zip‑архив со всеми транскриптами.
"""
)

mode = st.radio(
    "Режим работы",
    ["Single file", "Batch mode"],
    horizontal=True,
    key="mode_radio",
)

model_size = st.selectbox("Размер модели", ["tiny", "base", "small", "medium", "large"], index=2)

# build language options from Whisper
whisper_langs = whisper.tokenizer.LANGUAGES
top_langs = [
    ("английский", "en"),
    ("украинский", "uk"),
    ("русский", "ru"),
    ("language autodetection", "auto"),
]
other_langs = sorted(
    [(name, code) for code, name in whisper_langs.items() if code not in {"en", "uk", "ru"}],
    key=lambda x: x[0],
)
all_langs = top_langs + other_langs

lang_choice = st.selectbox(
    "Выберите язык",
    options=all_langs,
    format_func=lambda x: x[0].capitalize() if x[1] == "auto" else f"{x[0].capitalize()} ({x[1]})",
    index=2,
    key="language_select",
)
language = None if lang_choice[1] == "auto" else lang_choice[1]

if mode == "Single file":
    up_file = st.file_uploader("Загрузите файл", type=["mp4", "mp3", "wav", "m4a"], accept_multiple_files=False)
    if st.button("Транскрибировать"):
        if not up_file:
            st.warning("Сначала загрузите файл.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(up_file.name).suffix) as tmp:
                tmp.write(up_file.getbuffer())
                tmp_path = Path(tmp.name)

            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            out_path = output_dir / f"{Path(up_file.name).stem}_{model_size}.txt"

            with st.spinner("Транскрибируем…"):
                transcribe(str(tmp_path), str(out_path), model_size=model_size, language=language)

            st.success("Готово!")
            st.download_button("Скачать транскрипт", data=out_path.read_text("utf‑8"), file_name=out_path.name, mime="text/plain")

else:  # Batch mode
    up_files = st.file_uploader("Выберите несколько файлов", type=["mp4", "mp3", "wav", "m4a"], accept_multiple_files=True)
    zip_checkbox = st.checkbox("Собрать все транскрипты в zip‑архив")

    if st.button("Транскрибировать все"):
        if not up_files:
            st.warning("Добавьте хотя бы один файл.")
        else:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            temp_dir = Path(tempfile.mkdtemp())
            transcript_paths = []

            progress = st.progress(0)
            for idx, file in enumerate(up_files, start=1):
                with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix=Path(file.name).suffix) as tmp:
                    tmp.write(file.getbuffer())
                    tmp_path = Path(tmp.name)

                out_path = output_dir / f"{Path(file.name).stem}_{model_size}.txt"
                transcribe(str(tmp_path), str(out_path), model_size=model_size, language=language)
                transcript_paths.append(out_path)
                progress.progress(idx / len(up_files))

            st.success(f"Готово! Обработано {len(up_files)} файлов.")

            if zip_checkbox:
                zip_name = output_dir / "transcripts.zip"
                with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
                    for p in transcript_paths:
                        zf.write(p, arcname=p.name)
                st.download_button("Скачать zip", data=zip_name.read_bytes(), file_name="transcripts.zip", mime="application/zip")
            else:
                for p in transcript_paths:
                    st.download_button(f"Скачать {p.name}", data=p.read_text("utf‑8"), file_name=p.name, mime="text/plain")

            # очистка временных файлов
            shutil.rmtree(temp_dir, ignore_errors=True)
