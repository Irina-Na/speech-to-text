import tempfile
from pathlib import Path
import shutil
import zipfile
import streamlit as st
import whisper

from transcribe_video_to_russian import transcribe

st.set_page_config(page_title="Whisper Transcriber", page_icon="📝", layout="centered")
st.title("📝 Whisper Transcriber")

st.markdown(
    """
**Single file** ▶ upload one media file and get the transcript.
**Batch mode** ▶ upload several files at once; optionally download a zip archive with all transcripts.
"""
)

mode = st.radio(
    "Mode",
    ["Single file", "Batch mode"],
    horizontal=True,
    key="mode_radio",
)

model_size = st.selectbox("Model size", ["tiny", "base", "small", "medium", "large"], index=2)

# build language options from Whisper
whisper_langs = whisper.tokenizer.LANGUAGES
top_langs = [
    ("English", "en"),
    ("Ukrainian", "uk"),
    ("Russian", "ru"),
    ("auto detection", "auto"),
]
other_langs = sorted(
    [(name, code) for code, name in whisper_langs.items() if code not in {"en", "uk", "ru"}],
    key=lambda x: x[0],
)
all_langs = top_langs + other_langs

lang_choice = st.selectbox(
    "Choose language",
    options=all_langs,
    format_func=lambda x: x[0].capitalize() if x[1] == "auto" else f"{x[0].capitalize()} ({x[1]})",
    index=2,
    key="language_select",
)
language = None if lang_choice[1] == "auto" else lang_choice[1]

if mode == "Single file":
    up_file = st.file_uploader("Upload file", type=["mp4", "mp3", "wav", "m4a"], accept_multiple_files=False)
    if st.button("Transcribe"):
        if not up_file:
            st.warning("Please upload a file first.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(up_file.name).suffix) as tmp:
                tmp.write(up_file.getbuffer())
                tmp_path = Path(tmp.name)

            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            out_path = output_dir / f"{Path(up_file.name).stem}_{model_size}.txt"

            with st.spinner("Transcribing…"):
                transcribe(str(tmp_path), str(out_path), model_size=model_size, language=language)

            st.success("Done!")
            st.download_button("Download transcript", data=out_path.read_text("utf‑8"), file_name=out_path.name, mime="text/plain")

else:  # Batch mode
    up_files = st.file_uploader("Select multiple files", type=["mp4", "mp3", "wav", "m4a"], accept_multiple_files=True)
    zip_checkbox = st.checkbox("Bundle all transcripts into a zip archive")

    if st.button("Transcribe all"):
        if not up_files:
            st.warning("Add at least one file.")
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

            st.success(f"Done! Processed {len(up_files)} files.")

            if zip_checkbox:
                zip_name = output_dir / "transcripts.zip"
                with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
                    for p in transcript_paths:
                        zf.write(p, arcname=p.name)
                st.download_button("Download zip", data=zip_name.read_bytes(), file_name="transcripts.zip", mime="application/zip")
            else:
                for p in transcript_paths:
                    st.download_button(f"Download {p.name}", data=p.read_text("utf‑8"), file_name=p.name, mime="text/plain")

            # clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)
