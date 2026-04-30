# Environment Setup

Use this reference when `video-maker` is installed on a new Windows machine or when an agent needs to understand how it cooperates with `desktop-control-for-windows`.

## Skill dependency model

`video-maker` is not meant to replace desktop UI automation.

Split of responsibility:

- `video-maker`
  - bootstrap video projects
  - maintain `project.json`, `meaning_contract.json`, `outline_plan.json`, `depth_contract.json`, `detail_weave.json`, `narration_polish.json`, `style_contract.json`, `shot_intents.json`, and `segments.json`
  - generate narration
  - generate Remotion props
  - render MP4 through Remotion
  - generate `publish/cover_prompt.md`
  - require `publish/cover.png` before generating `publish/bilibili_publish_job.json`
- `desktop-control-for-windows`
  - operate visible Windows UI
  - use the logged-in Microsoft Edge stable session for Bilibili
  - do not switch to Edge Dev for the Bilibili upload flow unless the user explicitly says the login state moved there
  - upload the rendered video to Bilibili
  - upload the cover image referenced by `cover_path`
  - fill title, description, tags, and other publish fields

When the user asks for end-to-end Bilibili publishing, both skills should be active in the same turn.

## Install locations

Recommended shared skills root on this machine family:

- Shared or cross-runtime skills often live under `C:\Users\Clr\.agents\skills`, but do not assume every skill is installed there.

Recommended installed directories on the current machine:

- `C:\Users\Clr\.codex\skills\video-maker`
- `C:\Users\Clr\.agents\skills\desktop-control-for-windows`

If the repo is maintained elsewhere, use a junction or symlink instead of copying.

## Local Qwen runtime

`video-maker` intentionally does not vendor local TTS weights or venvs.

Generated projects store runtime pointers in:

- `content/project.json`
  - `voice_settings.local_qwen.python_executable`
  - `voice_settings.local_qwen.model_dir`
  - `voice_settings.local_qwen.helper_script` for legacy compatibility only
- `voice_settings.local_qwen.trim_silence_ms` / `fade_ms`
  - `voice_workflow.narration_mode`

On this machine, the validated example points to:

- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\models\Qwen3-TTS-12Hz-1.7B-CustomVoice`

On another machine, adjust these fields after bootstrap or prepare the same directory structure.

The current `video-maker` runtime no longer requires the external helper script to be present as long as the Qwen Python environment and `model_dir` are valid. The default master path now calls Qwen once for the full narration instead of chunking and stitching a long track.

## FlashAttention on this machine

For this Windows machine, the validated fast path is:

- Python `3.12`
- `torch==2.10.0+cu130`
- `flash-attn==2.8.3`
- wheel source:
  - `https://huggingface.co/ussoewwin/Flash-Attention-2_for_Windows`

Important constraints:

- Do not assume the stock `torch==2.10.0+cu128` environment can load a Windows `flash-attn` wheel.
- Do not default to `pip install flash-attn --no-build-isolation` on this machine. The official project still treats Windows compilation as insufficiently tested, and the source-build path was not reliable here.
- An older third-party `torch2.10/cu130` wheel from another source was tested and failed with `flash_attn_2_cuda` DLL load errors. Use the validated `ussoewwin` wheel first.

Recommended install sequence for the local Qwen venv:

```powershell
$qwenPy = "C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe"

& $qwenPy -m pip install --force-reinstall `
  --index-url https://download.pytorch.org/whl/cu130 `
  torch==2.10.0

& $qwenPy -m pip install --force-reinstall --no-deps `
  "https://huggingface.co/ussoewwin/Flash-Attention-2_for_Windows/resolve/main/flash_attn-2.8.3%2Bcu130torch2.10.0cxx11abiTRUE-cp312-cp312-win_amd64.whl"
```

Minimal validation:

```powershell
$qwenPy = "C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe"

& $qwenPy -c "import torch, flash_attn; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"

& $qwenPy -c "from qwen_tts.core.tokenizer_25hz.vq import whisper_encoder; print(whisper_encoder.flash_attn_varlen_func is None)"
```

Expected result:

- the first command prints `2.10.0+cu130`
- the second command prints `False`
- local Qwen TTS no longer prints the `flash-attn is not installed` warning during generation

## Minimal machine requirements

- Windows desktop environment
- Microsoft Edge installed
- `ffmpeg` available
- Node.js / npm available for Remotion
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

The checker now reports:

- whether `desktop-control-for-windows` is installed
- whether Edge exists
- whether `ffmpeg` is available
- whether Node.js / npm are available for Remotion rendering
- whether local Qwen defaults exist
- whether `meaning_contract.json`, `outline_plan.json`, `depth_contract.json`, `detail_weave.json`, `narration_polish.json`, `style_contract.json`, `shot_intents.json`, and `segments.json` are present
- whether the project is configured for `master-track-preferred`
- whether a master narration file already exists
- whether GitHub CLI is available

For a real smoke test after the environment is ready, run the generated project's publish TTS entrypoint once and confirm it produces `audio/master.wav` without the flash-attn warning:

```powershell
& "C:\path\to\video-project\scripts\generate_tts_publish.py" `
  --root "C:\path\to\video-project" `
  --provider local-qwen `
  --force
```

## Publish workflow on a new machine

1. Install `video-maker`.
2. Install `desktop-control-for-windows`.
3. Prepare local Qwen runtime or accept Edge preview fallback.
4. Bootstrap a project.
5. Fill `meaning_contract.json`, `outline_plan.json`, `depth_contract.json`, `detail_weave.json`, `narration_polish.json`, compile `style_contract.json + shot_intents.json`, and then compile `segments.json`.
6. Run `render_all.ps1`.
7. After local QA and title lock, use `imagegen` to create `publish/cover.png` from `publish/cover_prompt.md`.
8. Run `prepare_publish_job.py`.
9. Hand off to a `desktop-control-for-windows` UI worker for real Bilibili upload, including the cover asset.

## Guardrail

If `desktop-control-for-windows` is missing, do not claim full automatic Bilibili publishing is available. Report that local video production works, but visible-UI upload automation is not installed yet.
