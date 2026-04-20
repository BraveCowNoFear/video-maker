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

## License

MIT
