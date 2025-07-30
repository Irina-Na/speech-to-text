import argparse
import whisper
import torch

DEFAULT_MODELS_DIR = '/models'

def transcribe(video_path: str, output_path: str, model_size: str = "small", language: str = "ru") -> None:
    """
    Transcribe an audio or video file to text using OpenAI's Whisper model.

    Parameters
    ----------
    video_path : str
        Path to the input video or audio file (e.g. MP4, MP3, WAV).
    output_path : str
        Path to the output text file where the transcription will be saved.
    model_size : str, optional
        Size of the Whisper model to load. Valid options are: "tiny", "base", "small",
        "medium", or "large". Smaller models run faster but may be less accurate.
        Defaults to "small".
    language : str, optional
        ISO‑639‑1 code of the language spoken in the audio. When set, Whisper does not
        attempt to detect the language automatically which can improve accuracy.
        Defaults to "ru" (Russian).

    Notes
    -----
    This function will automatically attempt to use a CUDA‑enabled GPU if one is
    available; otherwise it falls back to the CPU. On CPU, Whisper requires a
    recent PyTorch version with support for FP32 precision.

    To ensure this script runs correctly on Windows, make sure FFmpeg is installed
    and added to your system PATH. Whisper relies on FFmpeg to decode many media
    formats. You can install FFmpeg on Windows using a package manager like
    Chocolatey:

        choco install ffmpeg

    Additionally, install the required Python packages:

        pip install -U openai-whisper torch

    Examples
    --------
    >>> transcribe("meeting.mp4", "meeting.txt")
    """


    # Determine computation device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Set fp16 to False when running on CPU to avoid unsupported half precision
    use_fp16 = device != "cpu"
    # Load the chosen Whisper model
    model = whisper.load_model(model_size, device=device, download_root=DEFAULT_MODELS_DIR)  # <-- ключевая правка
    # Perform transcription. The language hint helps Whisper to lock onto Russian.
    result = model.transcribe(video_path, language=language, fp16=use_fp16)
    text = result["text"].strip()
    # Write the transcription to the specified output file using UTF‑8 encoding
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"Saved transcription to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Transcribe an audio or video file to Russian text using OpenAI's "
            "open‑source Whisper model."
        )
    )
    parser.add_argument(
        "input",
        help="Path to the input video or audio file (MP4, MP3, WAV, etc.).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="transcript.txt",
        help="Path to the output text file (default: transcript.txt).",
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="small",
        help="Size of the Whisper model to use (default: small).",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="ru",
        help="Language code of the audio to transcribe (default: ru for Russian).",
    )
    args = parser.parse_args()
    transcribe(args.input, args.output, args.model, args.language)


if __name__ == "__main__":
    main()