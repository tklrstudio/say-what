# Say What — Project Charter

> Say What is open source. Built for anyone who needs local transcription.

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| **Status**     | Canonical                                                             |
| **Workspace**  | SW                                                                    |
| **Created**    | 2026-03-10                                                            |
| **Version**    | 1.0.0                                                                 |
| **Visibility** | Open source || **Origin**     | https://github.com/tklrstudio/say-what.git                           |

---

## Purpose

A simple, local-first CLI transcription tool for anyone who wants speech-to-text without cloud uploads.

Say What is the community-friendly, local-only counterpart to Transcriber (private TKLR tool). They are independent codebases.

---

## Success Criteria

- User can transcribe a file with a single command
- No cloud dependency
- Works on CPU and GPU
- Output is accurate enough for most use cases

---

## Boundaries

- Not a TKLR platform tool (that's Transcriber)
- Not a recording tool
- Not a SaaS
- Not a pipeline — single command, single file, done

---

## Design Principles

1. **Local first** — No uploads. Audio never leaves the user's machine.
2. **Single command** — No config files, no setup wizards. Point at a file, get a transcript.
3. **Honest about quality** — Model selection determines accuracy. The tool doesn't pretend otherwise.
4. **Zero infrastructure** — Runs on the user's machine. No servers, no accounts, no API keys.

---

## Architecture

Simple CLI — `saywhat.py` reads media, runs Whisper, writes output files.

Supported inputs: MP4, MP3, WAV, M4A, MKV.
Supported outputs: timestamped text, SRT subtitles, plain text.

---

## Quality Criteria

- Works with a single command
- Output formats are standard
- Errors are clear

---

## Failure Patterns

- Scope creep toward platform features
- Adding cloud dependencies
- Making it harder to use

---

## Binding Rules

- No cloud uploads
- No mandatory config
- No external service dependencies
