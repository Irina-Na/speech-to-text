import argparse
import glob
import os
import shutil
import subprocess
import sys
import re
from typing import Callable, Optional

try:
    import torch
except OSError as e:
    if "DLL" in str(e) or "dll" in str(e).lower() or "WinError" in str(e):
        print("=" * 60)
        print("ОШИБКА: Не удается загрузить библиотеки PyTorch (DLL)")
        print("=" * 60)
        print(f"\nДетали: {e}")
        print("\nРЕШЕНИЕ:")
        print("1. Установите Visual C++ Redistributables:")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("\n2. Переустановите PyTorch:")
        print("   pip uninstall torch torchvision torchaudio")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126")
        sys.exit(1)
    else:
        raise

import whisper

DEFAULT_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_TS_RE = re.compile(r"\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]")


def _format_timestamp(seconds: float, for_vtt: bool = False) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    sep = "." if for_vtt else ","
    return f"{hours:02}:{minutes:02}:{secs:02}{sep}{millis:03}"


def _build_timestamp_lines(segments, fmt: str) -> str:
    if fmt == "tsv":
        lines = []
        for s in segments:
            lines.append(f"{s['start']:.3f}\t{s['end']:.3f}\t{s['text'].strip()}")
        return "\n".join(lines) + "\n"
    if fmt == "vtt":
        lines = ["WEBVTT", ""]
        for s in segments:
            start = _format_timestamp(s["start"], for_vtt=True)
            end = _format_timestamp(s["end"], for_vtt=True)
            lines.append(f"{start} --> {end}")
            lines.append(s["text"].strip())
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    if fmt == "srt":
        lines = []
        for idx, s in enumerate(segments, start=1):
            start = _format_timestamp(s["start"])
            end = _format_timestamp(s["end"])
            lines.append(str(idx))
            lines.append(f"{start} --> {end}")
            lines.append(s["text"].strip())
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    lines = []
    for s in segments:
        start = _format_timestamp(s["start"], for_vtt=True)
        end = _format_timestamp(s["end"], for_vtt=True)
        lines.append(f"[{start} - {end}] {s['text'].strip()}")
    return "\n".join(lines) + "\n"


def _timestamps_output_path(output_path: str, fmt: str) -> str:
    base, _ = os.path.splitext(output_path)
    ext = "txt" if fmt == "txt" else fmt
    return f"{base}.{ext}"


def _ensure_ffmpeg_on_path() -> None:
    """On Windows, if ffmpeg is not in PATH, try to add WinGet Gyan.FFmpeg bin."""
    if os.name != "nt":
        return
    if shutil.which("ffmpeg"):
        return
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if not os.path.isdir(base):
        return
    for d in glob.glob(os.path.join(base, "Gyan.FFmpeg*", "*", "bin")):
        if os.path.isfile(os.path.join(d, "ffmpeg.exe")):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            return


def _parse_timestamp_seconds(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(".")
    return (int(hours) * 3600) + (int(minutes) * 60) + int(seconds) + (int(millis) / 1000.0)


def _probe_duration_seconds(media_path: str) -> Optional[float]:
    _ensure_ffmpeg_on_path()
    try:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                media_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    value = (completed.stdout or "").strip()
    try:
        return float(value)
    except ValueError:
        return None


class _ProgressStdout:
    def __init__(
        self,
        original,
        total_seconds: float,
        progress_callback: Callable[[float], None],
    ) -> None:
        self._original = original
        self._total_seconds = total_seconds
        self._progress_callback = progress_callback
        self._buffer = ""
        self._last_seconds = 0.0

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._handle_line(line)
        return self._original.write(text)

    def flush(self) -> None:
        if self._buffer:
            self._handle_line(self._buffer)
            self._buffer = ""
        self._original.flush()

    def _handle_line(self, line: str) -> None:
        match = _TS_RE.search(line)
        if not match:
            return
        end_ts = match.group(2)
        seconds = _parse_timestamp_seconds(end_ts)
        if seconds <= self._last_seconds:
            return
        self._last_seconds = seconds
        if self._total_seconds > 0:
            seconds = min(seconds, self._total_seconds)
        self._progress_callback(seconds)


def make_progress_printer(total_seconds: Optional[float], label: Optional[str] = None) -> Optional[Callable[[float], None]]:
    if total_seconds is None or total_seconds <= 0:
        return None

    prefix = f"{label} " if label else ""

    def _progress_printer(current_seconds: float) -> None:
        percent = min(100.0, (current_seconds / total_seconds) * 100.0)
        print(
            f"\r{prefix}Progress: {percent:6.2f}% ({current_seconds:,.1f}s / {total_seconds:,.1f}s)",
            end="",
            flush=True,
        )

    return _progress_printer


def transcribe(
    video_path: str,
    output_path: str,
    model_size: str = "small",
    language: str = "ru",
    timestamps_format: str = "none",
    progress_callback: Optional[Callable[[float], None]] = None,
    progress_total: Optional[float] = None,
    verbose: Optional[bool] = None,
) -> None:
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
        Defaults to "ru".

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
    _ensure_ffmpeg_on_path()

    # Determine computation device with diagnostic information
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        gpu_count = torch.cuda.device_count()
        print(f"✓ CUDA доступна: {gpu_count} GPU обнаружено")
        print(f"✓ Используется GPU: {gpu_name}")
    else:
        device = "cpu"
        print("⚠ CUDA недоступна, используется CPU")
        print("  Возможные причины:")
        print("  1. PyTorch установлен без поддержки CUDA (CPU-only версия)")
        print("  2. Драйверы CUDA не установлены или устарели")
        print("  3. Несовместимость версий CUDA")
        print("\n  Для установки PyTorch с поддержкой CUDA:")
        print("  https://pytorch.org/get-started/locally/")
        print("  Пример: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    # Set fp16 to False when running on CPU to avoid unsupported half precision
    use_fp16 = device != "cpu"
    # Load the chosen Whisper model
    os.makedirs(DEFAULT_MODELS_DIR, exist_ok=True)
    model = whisper.load_model(model_size, device=device, download_root=DEFAULT_MODELS_DIR)
    # Perform transcription. The language hint helps Whisper focus on the selected language.
    duration_seconds = progress_total
    if duration_seconds is None and progress_callback is not None:
        duration_seconds = _probe_duration_seconds(video_path)
    needs_progress = progress_callback is not None and duration_seconds is not None
    kwargs = {"language": language, "fp16": use_fp16}
    if verbose is not None:
        kwargs["verbose"] = verbose
    elif needs_progress:
        kwargs["verbose"] = True
    original_stdout = sys.stdout
    if needs_progress:
        sys.stdout = _ProgressStdout(original_stdout, duration_seconds, progress_callback)
    try:
        result = model.transcribe(video_path, **kwargs)
    finally:
        if sys.stdout is not original_stdout:
            sys.stdout.flush()
            sys.stdout = original_stdout
    text = result["text"].strip()
    # Write the transcription to the specified output file using UTF‑8 encoding
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"Saved transcription to {output_path}")
    if timestamps_format != "none":
        segments = result.get("segments", [])
        timestamps_text = _build_timestamp_lines(segments, timestamps_format)
        timestamps_path = _timestamps_output_path(output_path, timestamps_format)
        with open(timestamps_path, "w", encoding="utf-8") as f:
            f.write(timestamps_text)
        print(f"Saved timestamps to {timestamps_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Transcribe an audio or video file using OpenAI's open‑source "
            "Whisper model."
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
        help="Language code of the audio to transcribe (default: ru).",
    )
    parser.add_argument(
        "--timestamps",
        choices=["none", "txt", "srt", "vtt", "tsv"],
        default="none",
        help="Save timestamps to a separate file (none, txt, srt, vtt, tsv).",
    )
    progress_group = parser.add_mutually_exclusive_group()
    progress_group.add_argument(
        "--progress",
        dest="progress",
        action="store_true",
        help="Show progress in the terminal (default).",
    )
    progress_group.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="Disable progress output.",
    )
    parser.set_defaults(progress=True)
    args = parser.parse_args()
    progress_total = None
    progress_callback = None
    if args.progress:
        progress_total = _probe_duration_seconds(args.input)
        if progress_total is None:
            print("⚠ Не удалось определить длительность через ffprobe; прогресс отключен.")
        else:
            print(f"Длительность: {progress_total:,.1f}s")
            progress_callback = make_progress_printer(progress_total)
    transcribe(
        args.input,
        args.output,
        args.model,
        args.language,
        args.timestamps,
        progress_callback=progress_callback,
        progress_total=progress_total,
    )
    if args.progress and progress_total:
        print()


if __name__ == "__main__":
    main()
