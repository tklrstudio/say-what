#!/usr/bin/env python3
"""
transcribe.py — Fast local audio/video transcription using OpenAI Whisper.

Transcribes any audio or video file to timestamped text, SRT subtitles,
or plain text. Runs entirely on your machine — nothing is sent to the cloud.

Usage:
  python3 transcribe.py meeting.mp4
  python3 transcribe.py podcast.mp3 --format srt
  python3 transcribe.py interview.wav --language de --model large-v3
  python3 transcribe.py call.m4a --format all --output ./transcripts/

Requirements:
  pip install faster-whisper

ffmpeg must be installed for video/non-WAV input:
  brew install ffmpeg        # macOS
  sudo apt install ffmpeg    # Linux

License: MIT
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time

# Suppress OpenMP duplicate library warning on macOS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

AUDIO_EXTENSIONS = {".wav", ".flac", ".ogg", ".opus"}
HALLUCINATION_STRINGS = {"", ".", "Thank you.", "Thanks for watching!",
                          "Thank you for watching.", "Bye.", "you",
                          "Thanks for watching.", "Thank you for listening."}


def format_timestamp(seconds):
    """Format seconds as HH:MM:SS.mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def format_timestamp_srt(seconds):
    """Format seconds as HH:MM:SS,mmm (SRT format)."""
    return format_timestamp(seconds).replace(".", ",")


def format_timestamp_short(seconds):
    """Format seconds as MM:SS for progress display."""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def extract_audio(input_path, wav_path):
    """Extract 16kHz mono WAV from any audio/video file."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000", "-vn", "-f", "wav",
        wav_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: ffmpeg failed to extract audio.", file=sys.stderr)
        print(f"  {result.stderr.strip().splitlines()[-1]}", file=sys.stderr)
        sys.exit(1)


def needs_extraction(input_path):
    """Check if the input file needs audio extraction via ffmpeg."""
    ext = os.path.splitext(input_path)[1].lower()
    return ext not in AUDIO_EXTENSIONS


def transcribe(input_path, model_size="medium", language=None, device="cpu",
               compute_type="int8"):
    """Transcribe an audio file and yield (start, end, text) tuples."""
    from faster_whisper import WhisperModel

    print(f"Loading model ({model_size}/{compute_type})...", flush=True)
    t0 = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"  Model loaded in {time.time() - t0:.1f}s", flush=True)

    print(f"Transcribing...", flush=True)

    kwargs = dict(
        beam_size=5,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=400),
        no_speech_threshold=0.6,
        log_prob_threshold=-1.0,
    )
    if language:
        kwargs["language"] = language

    segments, info = model.transcribe(input_path, **kwargs)

    detected = info.language
    prob = info.language_probability
    print(f"  Detected language: {detected} ({prob:.0%})", flush=True)

    count = 0
    for segment in segments:
        text = segment.text.strip()
        if text in HALLUCINATION_STRINGS:
            continue
        count += 1
        if count % 100 == 0:
            print(f"  {format_timestamp_short(segment.start)} "
                  f"({count} segments)...", flush=True)
        yield segment.start, segment.end, text

    print(f"  Done: {count} segments", flush=True)


def write_txt(segments, path):
    """Write timestamped plain text format."""
    with open(path, "w") as f:
        for start, end, text in segments:
            f.write(f"[{format_timestamp(start)} --> {format_timestamp(end)}] {text}\n")


def write_srt(segments, path):
    """Write SRT subtitle format."""
    with open(path, "w") as f:
        for i, (start, end, text) in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}\n")
            f.write(f"{text}\n\n")


def write_plain(segments, path):
    """Write plain text (no timestamps)."""
    with open(path, "w") as f:
        for _start, _end, text in segments:
            f.write(f"{text}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video files using OpenAI Whisper (local, offline).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s meeting.mp4                          Transcribe to .transcript.txt
  %(prog)s podcast.mp3 --format srt             Output as SRT subtitles
  %(prog)s interview.wav --format all           Output all formats (.txt, .srt, .plain.txt)
  %(prog)s call.m4a --language de               Transcribe German audio
  %(prog)s lecture.mkv --model large-v3         Use larger model for better accuracy
  %(prog)s audio.wav --output ./out/            Write output to specific directory
        """,
    )
    parser.add_argument("input", help="Audio or video file to transcribe")
    parser.add_argument("--format", choices=["txt", "srt", "plain", "all"],
                        default="txt",
                        help="Output format (default: txt)")
    parser.add_argument("--output", "-o",
                        help="Output directory (default: same directory as input)")
    parser.add_argument("--language", "-l",
                        help="Language code, e.g. 'en', 'de', 'ja' (default: auto-detect)")
    parser.add_argument("--model", "-m", default="medium",
                        help="Whisper model size: tiny, base, small, medium, large-v3 "
                             "(default: medium)")
    parser.add_argument("--device", default="cpu",
                        help="Device: cpu or cuda (default: cpu)")
    parser.add_argument("--compute-type", default="int8", dest="compute_type",
                        help="Compute type: int8, float16, float32 (default: int8)")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output paths
    output_dir = args.output or os.path.dirname(input_path)
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0])

    print(f"Input:  {input_path}")
    print(f"Output: {output_dir}/")
    print(f"Model:  {args.model} ({args.compute_type})")
    if args.language:
        print(f"Language: {args.language}")
    print()

    # Extract audio if needed
    cleanup_wav = False
    audio_path = input_path
    if needs_extraction(input_path):
        print("Extracting audio...", flush=True)
        t0 = time.time()
        wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_file.close()
        audio_path = wav_file.name
        cleanup_wav = True
        extract_audio(input_path, audio_path)
        print(f"  Extracted in {time.time() - t0:.1f}s", flush=True)
        print()

    try:
        # Collect segments (needed for multi-format output)
        t0 = time.time()
        segments = list(transcribe(
            audio_path,
            model_size=args.model,
            language=args.language,
            device=args.device,
            compute_type=args.compute_type,
        ))
        elapsed = time.time() - t0

        if not segments:
            print("\nNo speech detected.", file=sys.stderr)
            sys.exit(0)

        # Write outputs
        print()
        formats = ["txt", "srt", "plain"] if args.format == "all" else [args.format]

        for fmt in formats:
            if fmt == "txt":
                path = base + ".transcript.txt"
                write_txt(segments, path)
            elif fmt == "srt":
                path = base + ".transcript.srt"
                write_srt(segments, path)
            elif fmt == "plain":
                path = base + ".plain.txt"
                write_plain(segments, path)
            print(f"Written: {path}")

        print(f"\n{len(segments)} segments in {elapsed / 60:.1f} minutes")

    finally:
        if cleanup_wav and os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    main()
