# Environment Setup

Use this reference when `video-maker` is installed on a new Windows machine or when an agent needs to understand how it cooperates with `desktop-control-for-windows`.

## Skill dependency model

`video-maker` is not meant to replace desktop UI automation.

Split of responsibility:

- `video-maker`
  - bootstrap video projects
  - maintain `project.json` / `segments.json`
  - generate narration
  - render slides
  - assemble MP4
  - generate `publish/bilibili_publish_job.json`
- `desktop-control-for-windows`
  - operate visible Windows UI
  - use the logged-in Edge session
  - upload the rendered video to Bilibili
  - fill title, description, tags, and other publish fields

When the user asks for end-to-end Bilibili publishing, both skills should be active in the same turn.

## Install locations

Recommended shared skills root on this machine family:

- `C:\Users\Clr\.agents\skills`

Recommended installed directories:

- `C:\Users\Clr\.agents\skills\video-maker`
- `C:\Users\Clr\.agents\skills\desktop-control-for-windows`

If the repo is maintained elsewhere, use a junction or symlink instead of copying.

## Local Qwen runtime

`video-maker` intentionally does not vendor local TTS weights or venvs.

Generated projects store runtime pointers in:

- `content/project.json`
  - `voice_settings.local_qwen.python_executable`
  - `voice_settings.local_qwen.helper_script`
  - `voice_settings.local_qwen.model_dir`

On this machine, the validated example points to:

- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\models\Qwen3-TTS-12Hz-1.7B-CustomVoice`

On another machine, adjust these fields after bootstrap or prepare the same directory structure.

## Minimal machine requirements

- Windows desktop environment
- Microsoft Edge installed
- `ffmpeg` available
- Python available for the generated project scripts
- optional but recommended GPU-backed local Qwen runtime for Chinese publish-grade narration

## First-run validation

Run:

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py"
```

If validating a specific generated project:

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py" `
  --project-root "C:\path\to\video-project"
```

The checker reports:

- whether `desktop-control-for-windows` is installed
- whether Edge exists
- whether `ffmpeg` is available
- whether local Qwen paths are configured and present
- whether GitHub CLI is available

## Publish workflow on a new machine

1. Install `video-maker`
2. Install `desktop-control-for-windows`
3. Prepare local Qwen runtime or accept Edge preview fallback
4. Bootstrap a project
5. Run `render_all.ps1`
6. Run `prepare_publish_job.py`
7. Hand off to a `desktop-control-for-windows` UI worker for real Bilibili upload

## Guardrail

If `desktop-control-for-windows` is missing, do not claim full automatic Bilibili publishing is available. Report that local video production works, but visible-UI upload automation is not installed yet.
