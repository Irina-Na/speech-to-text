from pathlib import Path
import argparse
from transcribe_video_to_russian import transcribe

SUPPORTED_EXTS = {".mp4", ".m4a", ".mp3", ".wav"}


def batch_transcribe(
    input_dir: Path = Path("video"),
    output_dir: Path = Path("outputs"),
    model_size: str = "medium",
    language: str = "ru",
) -> None:
    """Batch‑transcribe every media file in *input_dir* by reusing the
    single‑file `transcribe` helper.

    Notes
    -----
    • Simply forwards each file to `transcribe()` from transcribe_video_to_russian.py.
    • Sacrifices a bit of speed (model loads per file) in exchange for DRY code.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Directory {input_dir} does not exist.")

    media_files = [p for p in input_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTS]
    if not media_files:
        print("[INFO] No supported media files found in", input_dir)
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for media_path in media_files:
        out_txt = output_dir / f"{media_path.stem}.txt"
        print(f"[→] Transcribing {media_path.name} → {out_txt.name}")
        transcribe(str(media_path), str(out_txt), model_size=model_size, language=language)
        print("    ✔ done")

    print(f"[✓] Completed {len(media_files)} files. Transcripts saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch‑transcribe all media files in a directory (delegates to transcribe() helper)."
    )
    parser.add_argument("--input-dir", type=Path, default=Path("video"), help="Directory with media files (default: ./video)")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Where to write transcripts (default: ./outputs)")
    parser.add_argument("-l", "--language", default="ru", help="ISO language code (default: ru)")
    parser.add_argument("-m", "--model", default="medium", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model size (default: medium)")
    args = parser.parse_args()
    batch_transcribe(args.input_dir, args.output_dir, args.model, args.language)


if __name__ == "__main__":
    main()
