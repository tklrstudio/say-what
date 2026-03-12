# Say What?

**AI-powered** local audio/video transcription. Runs a deep learning speech model entirely on your machine — your audio never touches a network, never hits a server, never leaves your device.

> Say What uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper), a quantised implementation of OpenAI's Whisper neural network. It is AI. The difference is where it runs: locally, on your hardware, with zero data transmission.

## Install

```bash
pip install faster-whisper
brew install ffmpeg  # macOS (or: sudo apt install ffmpeg)
```

## Usage

```bash
# Transcribe a meeting recording
python3 saywhat.py meeting.mp4

# Output as SRT subtitles
python3 saywhat.py podcast.mp3 --format srt

# All formats at once (.txt, .srt, .plain.txt)
python3 saywhat.py interview.wav --format all

# Specify language (default: auto-detect)
python3 saywhat.py call.m4a --language de

# Use a larger model for better accuracy
python3 saywhat.py lecture.mkv --model large-v3

# Write output to a specific directory
python3 saywhat.py audio.wav --output ./transcripts/
```

## Output formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `txt` | `.transcript.txt` | Timestamped text: `[00:01:23.456 --> 00:01:27.890] Hello everyone` |
| `srt` | `.transcript.srt` | Standard SRT subtitles (works with VLC, YouTube, etc.) |
| `plain` | `.plain.txt` | Plain text, no timestamps |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format` | `txt` | Output format: `txt`, `srt`, `plain`, or `all` |
| `--output` | same as input | Output directory |
| `--language` | auto-detect | Language code (`en`, `de`, `ja`, `fr`, etc.) |
| `--model` | `medium` | Model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `--device` | `cpu` | `cpu` or `cuda` (for NVIDIA GPUs) |
| `--compute-type` | `int8` | `int8`, `float16`, or `float32` |

## Models

| Model | Size | Speed | Accuracy | Best for |
|-------|------|-------|----------|----------|
| `tiny` | 75 MB | ~30x | Low | Quick drafts, testing |
| `base` | 140 MB | ~15x | OK | Short clips |
| `small` | 460 MB | ~6x | Good | Most use cases |
| `medium` | 1.5 GB | ~2x | Very good | Recommended default |
| `large-v3` | 3 GB | ~1x | Best | When accuracy matters most |

Speed is approximate relative to audio duration on CPU.

## How it works

1. Extracts audio from video files using ffmpeg (16kHz mono WAV)
2. Runs [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — a CTranslate2-optimised port of OpenAI's Whisper, a transformer neural network trained on 680,000 hours of audio
3. Filters hallucination artefacts (phantom "Thank you" segments, etc.)
4. Writes the chosen output format(s)

**No API keys. No accounts. No network requests. No data leaves your machine — ever.**

The AI runs on your hardware. That's the whole point.

## License

MIT
