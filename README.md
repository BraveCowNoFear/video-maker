# Video Maker

`video-maker` is a Codex skill for end-to-end Bilibili explainer-video production on Windows.

It is built around one practical goal:

- bootstrap a reusable project
- write and refine Chinese explainer segments
- render slides
- generate narration with local Qwen3-TTS first
- fall back to ElevenLabs or Edge when needed
- assemble a final MP4 locally
- prepare structured publish metadata for a Bilibili upload worker

## What is in this repo

- `SKILL.md`: the skill entrypoint and operator guide
- `scripts/bootstrap_project.py`: self-contained project bootstrap
- `scripts/bootstrap_video_project.py`: base Bilibili video scaffold generator
- `scripts/upgrade_project.py`: local-Qwen-first upgrade path plus publish helpers
- `references/`: voice, workflow, and provider notes
- `agents/openai.yaml`: launcher metadata
- `scripts/doctor.py`: environment and dependency checker

## Install as a skill

Clone this repo into your shared skills directory, or create a junction/symlink to it.

Recommended shared location on this machine family:

- `C:\Users\Clr\.agents\skills\video-maker`

Typical layout:

```text
C:\Users\...\skills\
├── video-maker\
└── desktop-control-for-windows\
```

`video-maker` is the production orchestrator. It is not a full desktop automation stack by itself.

## Required companion skill

For real Bilibili publishing, this repo must be used together with:

- `desktop-control-for-windows`

Reason:

- `video-maker` handles project scaffold, narration, rendering, QA, and publish metadata
- `desktop-control-for-windows` handles the real logged-in Windows / Edge UI needed for Bilibili upload

Without `desktop-control-for-windows`, local rendering still works, but actual publish automation does not.

## External runtime assets

This repo intentionally does not vendor heavyweight local assets.

Keep these outside the skill repo:

- Qwen model weights
- Python virtual environment for Qwen TTS
- generated project outputs
- browser login state

For the current local-Qwen-first setup, generated projects expect `voice_settings.local_qwen` to point to a local helper and Python executable. On this machine, the working example is:

- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py`

These paths are configurable in each generated project's `content/project.json`.

## Environment checklist

- Microsoft Edge installed
- `ffmpeg` available, preferably `C:\Program Files\File Converter\ffmpeg.exe`
- local Qwen runtime prepared if you want Chinese auto mode to use publish-grade local TTS
- `desktop-control-for-windows` installed if you want automatic Bilibili upload
- logged-in Edge session for Bilibili if you want publish automation

Run the built-in checker:

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py"
```

Or check a specific generated project:

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py" `
  --project-root "C:\path\to\my-video-project"
```

## Architecture

The repo only keeps reusable orchestration logic.

It does not vendor heavyweight local runtime assets such as:

- Qwen model weights
- Python virtual environments
- local browser sessions
- per-project audio / clips / renders

Those stay on the local machine or inside each generated video project.

## Default voice path

For Chinese narration, auto mode now prefers local Qwen when `voice_settings.local_qwen` is ready.

Provider order:

1. `local-qwen`
2. reviewed `elevenlabs-api`
3. explicit reviewed `elevenlabs-web`
4. `edge-preview`

## Publish handoff

Run `scripts/prepare_publish_job.py` inside a generated project to emit:

- `publish/bilibili_publish_job.json`

That JSON is intended to be consumed by a dedicated upload automation flow or a Codex UI worker using the user's logged-in Edge session.

The intended upload pairing is:

1. `video-maker` renders and writes `publish/bilibili_publish_job.json`
2. a coordinator agent invokes `desktop-control-for-windows`
3. the UI worker opens the logged-in Edge Bilibili upload page and submits using that JSON

## Agent-facing integration notes

- If the task is local project creation, narration, QA, or video assembly, use `video-maker`
- If the task crosses into visible Windows UI control, also use `desktop-control-for-windows`
- For first-run setup or debugging on a new machine, run `scripts/doctor.py` before attempting a full publish pipeline

## License

MIT
