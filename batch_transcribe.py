from pathlib import Path
import argparse
from tqdm.auto import tqdm
from transcribe_video import transcribe, _probe_duration_seconds

SUPPORTED_EXTS = {".mp4", ".m4a", ".mp3", ".wav"}


def _detect_language_from_name(name: str, default: str = "ru") -> str:
    """
    Very simple heuristic:

    - If the file name (without extension) starts with 'en' (any case) -> English.
    - If it starts with 'ru' -> Russian.
    - Otherwise return `default`.
    """
    lowered = name.lower()
    if lowered.startswith("en"):
        return "en"
    if lowered.startswith("ru"):
        return "ru"
    return default


def batch_transcribe(
    input_dir: Path = Path("video"),
    output_dir: Path = Path("outputs"),
    model_size: str = "medium",
    language: str | None = "ru",
) -> None:
    """Batch-transcribe every media file in *input_dir* by reusing the
    single-file `transcribe` helper.

    Language handling
    -----------------
    If *language* is provided (e.g. "ru"), it will be used as a fallback.
    For each file we try to auto-detect the language from the file name:

    - If the stem starts with ``en`` -> force English.
    - If the stem starts with ``ru`` -> force Russian.
    - Otherwise use the fallback *language* value.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Directory {input_dir} does not exist.")

    media_files = [p for p in input_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTS]
    if not media_files:
        print("[INFO] No supported media files found in", input_dir)
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    with tqdm(total=len(media_files), desc="Transcribing files", unit="file") as progress:
        for media_path in media_files:
            duration_seconds = _probe_duration_seconds(str(media_path))
            if duration_seconds:
                file_bar = tqdm(
                    total=duration_seconds,
                    desc=f"{media_path.name}",
                    unit="s",
                    position=1,
                    leave=False,
                )
            else:
                file_bar = tqdm(
                    total=3,
                    desc=f"{media_path.name}",
                    unit="step",
                    position=1,
                    leave=False,
                )
            # Choose language for this particular file based on its name.
            # Example: "en_interview1.mp4" -> "en", "ru_sozvon.wav" -> "ru".
            file_language = _detect_language_from_name(
                media_path.stem,
                default=language or "ru",
            )
            file_bar.set_postfix(lang=file_language)
            out_txt = output_dir / f"{media_path.stem}.txt"
            if out_txt.exists():
                tqdm.write(f"[skip] {out_txt.name} already exists, skipping.")
                file_bar.set_postfix(status="skip (exists)")
                if duration_seconds:
                    file_bar.update(max(0.0, duration_seconds - file_bar.n))
                else:
                    file_bar.update(3)
                file_bar.close()
                progress.update(1)
                continue
            file_bar.set_description(f"{media_path.name} (transcribing)")
            tqdm.write(f"[->] {media_path.name} (lang={file_language}) -> {out_txt.name}")
            def _on_progress(seconds_done: float) -> None:
                if not duration_seconds:
                    return
                if seconds_done > file_bar.n:
                    file_bar.update(seconds_done - file_bar.n)
            transcribe(
                str(media_path),
                str(out_txt),
                model_size=model_size,
                language=file_language,
                progress_callback=_on_progress,
                progress_total=duration_seconds,
            )
            if duration_seconds:
                file_bar.update(max(0.0, duration_seconds - file_bar.n))
            else:
                file_bar.update(2)  # transcription done + wrap up
            file_bar.set_description(f"{media_path.name} (done)")
            file_bar.close()
            progress.update(1)
            tqdm.write(f"    OK done ({progress.n}/{progress.total})")

    print(f"[OK] Completed {len(media_files)} files. Transcripts saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch-transcribe all media files in a directory (delegates to transcribe() helper)."
    )
    parser.add_argument("--input-dir", type=Path, default=Path("video"), help="Directory with media files (default: ./video)")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Where to write transcripts (default: ./outputs)")
    parser.add_argument("-l", "--language", default="ru", help="ISO language code (default: ru)")
    parser.add_argument("-m", "--model", default="medium", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model size (default: medium)")
    args = parser.parse_args()
    batch_transcribe(args.input_dir, args.output_dir, args.model, args.language)


if __name__ == "__main__":
    main()
