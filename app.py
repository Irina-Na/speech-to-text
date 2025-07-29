import tempfile
from pathlib import Path
import streamlit as st

# Импортируем функцию транскрибации из вашего скрипта
from transcribe_video_to_russian import transcribe

st.set_page_config(page_title="Whisper‑RU Transcriber", page_icon="📝", layout="centered")
st.title("📝 Whisper‑RU Transcriber")

st.markdown("""
Простой веб‑интерфейс для транскрибации аудио/видео на русском языке с помощью модели OpenAI Whisper.
Загрузите файл, выберите размер модели и нажмите **«Транскрибировать»**.
""")

uploaded_file = st.file_uploader(
    "Загрузите файл (mp4 / mp3 / wav / m4a)",
    type=["mp4", "mp3", "wav", "m4a"],
)

model_size = st.selectbox(
    "Размер модели",
    ["tiny", "base", "small", "medium", "large"],
    index=2,
)

language = st.text_input("ISO‑код языка", "ru")

if st.button("Транскрибировать"):
    if not uploaded_file:
        st.warning("Сначала загрузите файл.")
    else:
        # Сохраняем загруженный файл во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{Path(uploaded_file.name).stem}_{model_size}.txt"

        with st.spinner("Транскрибируем… может занять пару минут…"):
            transcribe(tmp_path, str(output_path), model_size=model_size, language=language)

        st.success("Готово!")
        st.download_button(
            label="Скачать транскрипт",
            data=output_path.read_text(encoding="utf-8"),
            file_name=output_path.name,
            mime="text/plain",
        )
