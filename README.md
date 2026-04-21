# Video Maker

[English](./README.md) | [简体中文](./README.zh-CN.md)

`video-maker` is a Codex skill for end-to-end Bilibili explainer-video production on Windows.

It is built around one practical goal:

- bootstrap a reusable project
- build the content contract before scene generation
- render slides
- generate narration with local Qwen3-TTS first
- fall back to Edge preview when needed
- assemble a final MP4 locally
- prepare structured publish metadata for a Bilibili upload worker

The default visual system for new explainers is now `Quiet Glass Lab v3`: a black-carbon, acid-green frosted-glass layout tuned for content-first Chinese Bilibili tech explainers.

## What is in this repo

- `SKILL.md`: the skill entrypoint and operator guide
- `scripts/bootstrap_project.py`: self-contained project bootstrap
- `scripts/bootstrap_video_project.py`: base Bilibili video scaffold generator
- `scripts/upgrade_project.py`: local-Qwen-first upgrade path plus publish helpers
- `references/`: voice, workflow, and rubric notes
- `references/agent-orchestration.md`: recommended main-agent / sub-agent content pipeline
- `references/video-acceptance-rubric.md`: dedicated reviewer-agent gate before final render or publish
- `references/quiet-glass-lab-v3.md`: content-first Liquid Glass rules and design tokens
- `references/quiet-glass-lab/`: default reusable HTML/CSS slide templates for the black-green Liquid Glass variant
- `references/bilibili-tech-explainer-workflow.md`: the default 8-segment explainer workflow
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
The generated local-Qwen path does not only reuse `voice_settings.local_qwen`; it also compiles `voice_persona` and `voice_consistency` into an explicit per-run voice lock so the helper receives the same speaker, same pacing baseline, and the same acceptance constraint on every segment.

Provider order:

1. `local-qwen`
2. `edge-preview`

## Content system

The current recommended production split is:

1. `chief-editor` owns the episode contract
2. content runs in serial `outline -> depth -> detail -> narration-polish`
3. `chief-editor` compiles `style_contract`, `shot_intents`, and `segments`

The key rule is: a video should not stop at "what this term means." Each episode should also answer why the idea matters now, what confusion it clears up, and what judgment the viewer can carry away after the video ends.

See [references/agent-orchestration.md](C:\Users\Clr\Desktop\github\video-maker\references\agent-orchestration.md) and [references/bilibili-tech-explainer-workflow.md](C:\Users\Clr\Desktop\github\video-maker\references\bilibili-tech-explainer-workflow.md).

## Acceptance

A final video is not considered ready just because it rendered.

Recommended gate:

1. `content_depth`
2. `ui_supports_content`
3. `voice_consistency`

Use a dedicated acceptance reviewer agent to decide pass / revise / hard fail, and route issues back to the relevant owner instead of patching them ad hoc.
If the project only stores voice-consistency metadata but the execution path does not inject that lock into the TTS helper, treat `voice_consistency` as a fail.

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
- For future Bilibili tech explainers, prefer the default `Quiet Glass Lab v3` prompt pack first and only diverge when the topic truly needs a different visual language

## License

MIT
