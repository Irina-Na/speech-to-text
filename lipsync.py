#!/usr/bin/env python
import argparse
import os
import subprocess
import sys


def run_cmd(cmd):
    print(f"> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def clone_wav2lip(repo_dir):
    if not os.path.exists(repo_dir):
        run_cmd(["git", "clone", "https://github.com/Rudrabha/Wav2Lip.git", repo_dir])
    else:
        print(f"Wav2Lip repository found at '{repo_dir}'")


def download_weights(checkpoint_folder):
    folder_url = "https://drive.google.com/drive/folders/153HLrqlBNxzZcHi17PEvP09kkAfzRshM"
    print(f"Downloading Wav2Lip weights into '{checkpoint_folder}' from {folder_url}")
    import gdown
    gdown.download_folder(folder_url, output=checkpoint_folder, quiet=False)
    print("Download complete.")


def main():
    parser = argparse.ArgumentParser(description="Lip-sync video using Wav2Lip")
    parser.add_argument("--input_file", help="Input video file path")
    parser.add_argument("--audio_file", help="Audio file path or video file containing audio")
    parser.add_argument("--output_file", help="Output video file path")
    parser.add_argument("--checkpoint_path", default="Wav2Lip/checkpoints/Wav2Lip.pth", help="Path to Wav2Lip checkpoint")
    parser.add_argument("--repo_dir", default="Wav2Lip", help="Directory for Wav2Lip repository")
    parser.add_argument("--download_weights", action="store_true", help="Download Wav2Lip weights and exit")
    args = parser.parse_args()

    clone_wav2lip(args.repo_dir)
    if args.download_weights:
        checkpoint_folder = os.path.dirname(args.checkpoint_path)
        os.makedirs(checkpoint_folder, exist_ok=True)
        download_weights(checkpoint_folder)
        sys.exit(0)

    if not args.input_file or not args.audio_file or not args.output_file:
        parser.error("Arguments --input_file, --audio_file, --output_file are required for lip-syncing")

    if not os.path.exists(args.checkpoint_path):
        print(f"Checkpoint not found at '{args.checkpoint_path}'. Please download using --download_weights")
        sys.exit(1)

    cmd = [
        sys.executable, os.path.join(args.repo_dir, "inference.py"),
        "--checkpoint_path", args.checkpoint_path,
        "--face", args.input_file,
        "--audio", args.audio_file,
        "--outfile", args.output_file
    ]
    run_cmd(cmd)
    print(f"Lip-syncing completed. Output saved to '{args.output_file}'")

if __name__ == "__main__":
    try:
        import gdown
    except ImportError:
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    main() 