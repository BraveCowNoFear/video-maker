from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent

from project_defaults import (
    apply_project_defaults,
    build_audience_contract_data,
    build_cover_prompt,
    build_acceptance_report_data,
    build_depth_contract_data,
    build_detail_weave_data,
    build_evidence_map_data,
    build_meaning_contract_data,
    build_narration_polish_data,
    build_opening_contract_data,
    build_outline_plan_data,
    build_problem_contract_data,
    build_script_draft_data,
    build_shot_intents_data,
    build_screenshot_plan_data,
    build_style_contract_data,
    build_visual_qa_report_data,
    build_visual_asset_plan_data,
    default_shot_role_for_index,
)


LOCAL_QWEN_BASE_INSTRUCT = (
    "请用年轻的中文女声做科技讲解。整体气质沉稳、大方、清晰、友好，带一点自然可爱的亲和感。"
    "全程保持同一个人设、同一种情绪基线和同一套说话习惯。"
    "语速保持中速偏快且稳定，不忽快忽慢，不忽然兴奋，也不要突然压低情绪。"
    "开头必须直接用标准自然中文进入正文，不要出现乱码、拟声、外语、无意义音节或非中文热场。"
    "句间停顿自然，呼吸轻、短、克制，重点词只做轻微强调，不要夸张，不要急躁，不要播音腔。"
    "不要幼态，不要撒娇，不要夹子音。像二十五岁左右、表达很稳的女生，在冷静而友好地讲解工具、工作流和 AI 概念。"
)

LEGACY_MUST_ANSWER = [
    "这是什么",
    "为什么现在值得讲",
    "最容易混淆的点是什么",
    "最后应该怎么判断或行动",
]

GENERATE_TTS_PUBLISH = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import asyncio
    import subprocess
    import sys
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument(
            "--provider",
            default="auto",
            choices=["auto", "local-qwen", "edge-preview"],
        )
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()

    from video_pipeline_common import load_project, local_qwen_ready


    def choose_provider(root: Path, project: dict, segments: list[dict], requested: str) -> str:
        if requested != "auto":
            return requested
        if local_qwen_ready(project):
            return "local-qwen"
        return "edge-preview"


    def run_local_qwen(root: Path, force: bool) -> None:
        script = root / "scripts" / "generate_tts_local_qwen.py"
        cmd = [
            sys.executable,
            str(script),
            "--root",
            str(root),
        ]
        if force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)


    def run_edge_preview(root: Path, force: bool) -> None:
        script = root / "scripts" / "generate_tts_edge.py"
        cmd = [
            sys.executable,
            str(script),
            "--root",
            str(root),
        ]
        if force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project, segments = load_project(root)
        provider = choose_provider(root, project, segments, args.provider)

        if provider == "local-qwen":
            print("[tts] provider=local-qwen")
            run_local_qwen(root, args.force)
            return

        print("[tts] provider=edge-preview")
        run_edge_preview(root, args.force)


    if __name__ == "__main__":
        asyncio.run(main())
    """
).strip() + "\n"


PREPARE_WEB_TTS_MANIFEST = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        return parser.parse_args()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8-sig"))

        manifest = {
            "topic": project.get("topic", root.name),
            "voice_language": project.get("voice_language", "zh-CN"),
            "narration_mode": ((project.get("voice_workflow") or {}).get("narration_mode") or "master-track-preferred"),
            "full_narration_text": "\n\n".join(str(item.get("voice") or "").strip() for item in segments if str(item.get("voice") or "").strip()),
            "preferred_master_audio": str((root / "audio" / "master.wav").resolve()),
            "segments": [],
        }
        for item in segments:
            manifest["segments"].append(
                {
                    "id": item["id"],
                    "text": item.get("voice", ""),
                    "target_audio_candidates": [
                        str((root / "audio" / f"{item['id']}.wav").resolve()),
                        str((root / "audio" / f"{item['id']}.mp3").resolve()),
                    ],
                }
            )

        out_path = root / "voice_jobs" / "web_tts_manifest.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(out_path)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


PREPARE_PUBLISH_JOB = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        return parser.parse_args()


    def resolve_project_path(root: Path, raw_value: str, default_rel: str) -> Path:
        value = str(raw_value or default_rel).strip()
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        return path.resolve()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        notes = (root / "publish_notes.md").read_text(encoding="utf-8-sig") if (root / "publish_notes.md").exists() else ""
        publish = project.get("publish", {}) or {}
        video_name = project.get("output_name") or f"{root.name}.mp4"
        video_path = (root / video_name).resolve()
        cover_required = bool(publish.get("cover_required", True))
        cover_path = resolve_project_path(root, str(publish.get("cover_path") or ""), "publish/cover.png")
        cover_prompt_path = resolve_project_path(root, str(publish.get("cover_prompt_path") or ""), "publish/cover_prompt.md")
        cover_prompt = cover_prompt_path.read_text(encoding="utf-8-sig") if cover_prompt_path.exists() else ""

        if not video_path.exists():
            raise FileNotFoundError(f"Missing rendered video for Bilibili publish handoff: {video_path}")

        if cover_required and not cover_path.exists():
            hint = f"Missing required Bilibili cover: {cover_path}"
            if cover_prompt_path.exists():
                hint += f". Have visual-architect generate it with imagegen using {cover_prompt_path}, then have visual-qa-fixer visually verify or repair it before prepare_publish_job.py."
            raise FileNotFoundError(hint)

        job = {
            "platform": publish.get("platform", "bilibili"),
            "topic": project.get("topic", root.name),
            "video_path": str(video_path),
            "notes_path": str((root / "publish_notes.md").resolve()),
            "publish_notes_markdown": notes,
            "style": project.get("visual_style", "web-design-engineer + quiet-glass-lab"),
            "voice_provider": project.get("voice_provider", "local-qwen"),
            "browser_preference": publish.get("browser_preference", "microsoft-edge-stable"),
            "browser_channel": publish.get("browser_channel", "stable"),
            "browser_channel_avoid": publish.get("browser_channel_avoid", ["edge-dev"]),
            "browser_login_requirement": publish.get(
                "browser_login_requirement",
                "open bilibili in the already signed-in Microsoft Edge stable window, not Edge Dev",
            ),
            "cover_required": cover_required,
            "cover_path": str(cover_path),
            "cover_prompt_path": str(cover_prompt_path),
            "cover_prompt_markdown": cover_prompt,
            "cover_upload_verification_required": bool(publish.get("cover_upload_verification_required", True)),
            "cover_upload_verification_rule": publish.get(
                "cover_upload_verification_rule",
                "after uploading cover_path, verify the Bilibili form visibly shows the custom cover before final publish",
            ),
        }
        out_path = root / "publish" / "bilibili_publish_job.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(out_path)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


RECORD_VOICE_PROFILE = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--provider", default="")
        parser.add_argument("--voice-name", default="")
        parser.add_argument("--locale", default="")
        parser.add_argument("--source-type", default="")
        parser.add_argument("--review-status", default="passed")
        parser.add_argument("--note", action="append", default=[])
        return parser.parse_args()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        path = root / "content" / "project.json"
        project = json.loads(path.read_text(encoding="utf-8-sig"))
        profile = project.setdefault("voice_profile", {})
        profile["provider"] = args.provider
        profile["voice_name"] = args.voice_name
        profile["locale"] = args.locale
        profile["source_type"] = args.source_type
        profile["review_status"] = args.review_status
        if args.note:
            profile["review_notes"] = args.note
        path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(path)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


GENERATE_TTS_EDGE = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import asyncio
    import json
    from pathlib import Path

    import edge_tts


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    def join_voice_blocks(segments: list[dict]) -> str:
        return "\n\n".join(str(item.get("voice") or "").strip() for item in segments if str(item.get("voice") or "").strip())


    async def synthesize(text: str, out_path: Path, voice: str, rate: str, pitch: str) -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8-sig"))
        edge_cfg = ((project.get("voice_settings") or {}).get("edge_preview") or {})
        voice = str(edge_cfg.get("voice") or "zh-CN-XiaoxiaoNeural")
        rate = str(edge_cfg.get("rate") or "+2%")
        pitch = str(edge_cfg.get("pitch") or "+0Hz")

        out_dir = root / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / "master.mp3"
        if out_path.exists() and not args.force:
            print(f"[skip] {out_path}")
            return
        text = join_voice_blocks(segments)
        await synthesize(text, out_path, voice, rate, pitch)
        print(f"[ok] {out_path}")


    if __name__ == "__main__":
        asyncio.run(main())
    """
).strip() + "\n"


GENERATE_TTS_LOCAL_QWEN = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import subprocess
    import tempfile
    from pathlib import Path

    from video_pipeline_common import segment_narration_text


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    def choose_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]


    def join_instruction_parts(*parts: str) -> str:
        cleaned: list[str] = []
        seen: set[str] = set()
        for part in parts:
            text = str(part or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            cleaned.append(text)
        return " ".join(cleaned)


    def parse_int(value: object, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default


    def statement(text: str, suffix: str = "。") -> str:
        cleaned = str(text or "").strip().rstrip("。！？!?；;，,、：:")
        if not cleaned:
            return ""
        return f"{cleaned}{suffix}"


    def build_local_qwen_config(project: dict) -> dict:
        local_qwen = ((project.get("voice_settings") or {}).get("local_qwen") or {})
        voice_persona = project.get("voice_persona", {}) or {}
        voice_consistency = project.get("voice_consistency", {}) or {}

        identity = str(voice_persona.get("identity") or "").strip()
        core_traits = "、".join(choose_list(voice_persona.get("core_traits")))
        forbidden_traits = "、".join(choose_list(voice_persona.get("forbidden_traits")))
        locked_fields = "、".join(choose_list(voice_consistency.get("lock_fields")))
        baseline_emotion = str(voice_persona.get("baseline_emotion") or "").strip()
        pace = str(voice_persona.get("pace") or "").strip()
        breath = str(voice_persona.get("breath") or "").strip()
        emphasis = str(voice_persona.get("emphasis") or "").strip()
        strategy = str(voice_consistency.get("strategy") or "master-track-preferred").strip()
        fallback_mode = str(voice_consistency.get("fallback_mode") or "fix-master-pass-or-preview-edge").strip()

        instruct = join_instruction_parts(
            statement(f"全程保持同一个中文女声人设：{identity}") if identity else "全程保持同一个中文女声人设。",
            statement(f"核心气质固定为：{core_traits}") if core_traits else "",
            statement(f"禁止出现这些倾向：{forbidden_traits}") if forbidden_traits else "",
            (
                statement(f"情绪基线保持 {baseline_emotion}，语速保持 {pace}，呼吸保持 {breath}，重音规则保持 {emphasis}")
                if any([baseline_emotion, pace, breath, emphasis])
                else ""
            ),
            "如果当前链路支持长段合成，优先像一次性录完整条视频一样生成。",
            statement(f"一致性策略为 {strategy}，退化策略为 {fallback_mode}"),
            statement(f"锁定字段：{locked_fields}") if locked_fields else "",
            "不要在不同场景之间突然变成熟、变稚嫩、变兴奋、变播音腔，或者像换了另一个人。",
        )
        return {
            "profile": str(local_qwen.get("profile") or "young_calm_cn_female_explainer"),
            "speaker": str(local_qwen.get("speaker") or "serena"),
            "language": str(local_qwen.get("language") or "Chinese"),
            "format": str(local_qwen.get("format") or "wav"),
            "attn_implementation": str(local_qwen.get("attn_implementation") or "sdpa"),
            "dtype": str(local_qwen.get("dtype") or "bfloat16"),
            "model_dir": str(local_qwen.get("model_dir") or ""),
            "python_executable": str(local_qwen.get("python_executable") or ""),
            "instruct": instruct,
            "synthesis_timeout_sec": parse_int(local_qwen.get("synthesis_timeout_sec"), 900),
            "status_manifest": str(local_qwen.get("status_manifest") or "voice_jobs/qwen_master_status.json"),
            "trim_silence_ms": parse_int(local_qwen.get("trim_silence_ms"), 18),
            "fade_ms": parse_int(local_qwen.get("fade_ms"), 12),
        }


    def build_items(project: dict, segments: list[dict]) -> list[dict]:
        items: list[dict] = []
        for item in segments:
            text = segment_narration_text(item, project)
            if not text:
                continue
            items.append(
                {
                    "id": str(item.get("id") or f"scene-{len(items) + 1:03d}"),
                    "text": text,
                }
            )
        return items


    def write_status(path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


    def run_qwen_job(root: Path, project: dict, force: bool) -> None:
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8-sig"))
        items = build_items(project, segments)
        if not items:
            raise RuntimeError("No narration text found in segments.json")

        settings = build_local_qwen_config(project)
        qwen_python = Path(settings["python_executable"])
        if not qwen_python.exists():
            raise FileNotFoundError(f"Missing Qwen python executable: {qwen_python}")
        model_dir = Path(settings["model_dir"])
        if not model_dir.exists():
            raise FileNotFoundError(f"Missing Qwen model directory: {model_dir}")

        master_output = root / "audio" / "master.wav"
        if master_output.exists() and not force:
            print(f"[skip] {master_output}")
            return
        status_manifest = root / str(settings.get("status_manifest") or "voice_jobs/qwen_master_status.json")
        timeout_sec = max(parse_int(settings.get("synthesis_timeout_sec"), 900), 60)

        runner = r'''
    import argparse
    import json
    import subprocess
    import tempfile
    from pathlib import Path
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel

    parser = argparse.ArgumentParser()
    parser.add_argument("--job-file", required=True)
    args = parser.parse_args()

    def load_job(path: str) -> dict:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))


    def trim_edges(audio: np.ndarray, sample_rate: int, margin_ms: int) -> np.ndarray:
        if margin_ms <= 0 or audio.size == 0:
            return audio
        threshold = 0.003
        active = np.where(np.abs(audio) > threshold)[0]
        if active.size == 0:
            return audio
        margin = int(sample_rate * margin_ms / 1000)
        start = max(int(active[0]) - margin, 0)
        end = min(int(active[-1]) + margin + 1, len(audio))
        return audio[start:end]


    def apply_fade(audio: np.ndarray, sample_rate: int, fade_ms: int) -> np.ndarray:
        if fade_ms <= 0 or audio.size == 0:
            return audio
        samples = min(int(sample_rate * fade_ms / 1000), len(audio) // 2)
        if samples <= 0:
            return audio
        ramp = np.linspace(0.0, 1.0, samples, dtype=np.float32)
        audio[:samples] *= ramp
        audio[-samples:] *= ramp[::-1]
        return audio


    def convert_with_ffmpeg(src_wav: Path, dst_audio: Path) -> Path:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(src_wav),
            "-acodec",
            "libmp3lame",
            "-ab",
            "192k",
            str(dst_audio),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return dst_audio
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="ignore")
            if "Unknown encoder" not in stderr:
                raise
            fallback_wav = dst_audio.with_suffix(".wav")
            fallback_wav.write_bytes(src_wav.read_bytes())
            print(f"[warn] ffmpeg mp3 encoder unavailable, wrote wav instead: {fallback_wav}")
            return fallback_wav


    def save_audio(audio: np.ndarray, sample_rate: int, output_path: Path, fmt: str) -> Path:
        if fmt == "wav":
            sf.write(output_path, audio, sample_rate)
            return output_path
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = Path(temp_file.name)
        try:
            sf.write(temp_wav, audio, sample_rate)
            return convert_with_ffmpeg(temp_wav, output_path.with_suffix(".mp3"))
        finally:
            temp_wav.unlink(missing_ok=True)


    def synthesize_text(model, text: str, settings: dict) -> tuple[np.ndarray, int]:
        wavs, sample_rate = model.generate_custom_voice(
            text=text,
            language=settings["language"],
            speaker=settings["speaker"],
            instruct=settings["instruct"],
        )
        audio = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        audio = trim_edges(audio, sample_rate, settings["trim_silence_ms"])
        audio = apply_fade(audio, sample_rate, settings["fade_ms"])
        return audio, sample_rate


    job = load_job(args.job_file)
    dtype = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }[job["settings"]["dtype"]]

    device_map = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = Qwen3TTSModel.from_pretrained(
        job["settings"]["model_dir"],
        device_map=device_map,
        dtype=dtype,
        attn_implementation=job["settings"]["attn_implementation"],
    )

    print(
        "[qwen3] "
        f"profile={job['settings']['profile']} "
        f"speaker={job['settings']['speaker']} "
        f"language={job['settings']['language']}"
    )
    print(f"[qwen3] instruct={job['settings']['instruct']}")

    output_dir = Path(job["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    full_text = "\n\n".join(item["text"] for item in job["items"] if item["text"].strip())
    if not full_text:
        raise RuntimeError("No narration text found for master-track synthesis")
    master_audio, sample_rate = synthesize_text(model, full_text, job["settings"])
    out_path = Path(job["master_output"])
    save_audio(master_audio, sample_rate, out_path, "wav")
    print(f"[ok] {out_path}")
    '''

        job = {
            "output_dir": str((root / "audio").resolve()),
            "master_output": str(master_output.resolve()),
            "items": items,
            "settings": settings,
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as job_file:
            json.dump(job, job_file, ensure_ascii=False, indent=2)
            job_path = Path(job_file.name)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as runner_file:
            runner_file.write(runner)
            runner_path = Path(runner_file.name)

        try:
            cmd = [
                str(qwen_python),
                str(runner_path),
                "--job-file",
                str(job_path),
            ]
            write_status(
                status_manifest,
                {
                    "status": "running",
                    "provider": "local-qwen",
                    "mode": "master-track",
                    "timeout_sec": timeout_sec,
                    "item_count": len(items),
                    "text_chars": sum(len(item["text"]) for item in items),
                    "master_output": str(master_output.resolve()),
                },
            )
            try:
                subprocess.run(cmd, check=True, timeout=timeout_sec)
            except subprocess.TimeoutExpired as exc:
                write_status(
                    status_manifest,
                    {
                        "status": "timed_out",
                        "provider": "local-qwen",
                        "mode": "master-track",
                        "timeout_sec": timeout_sec,
                        "master_output": str(master_output.resolve()),
                        "recovery": "kill the stalled Qwen process chain, adjust voice_settings.local_qwen.synthesis_timeout_sec or switch to edge-preview for this run, then regenerate a single consistent master track",
                    },
                )
                raise RuntimeError(f"Local Qwen master-track synthesis timed out after {timeout_sec} seconds") from exc
            except subprocess.CalledProcessError as exc:
                write_status(
                    status_manifest,
                    {
                        "status": "failed",
                        "provider": "local-qwen",
                        "mode": "master-track",
                        "returncode": exc.returncode,
                        "master_output": str(master_output.resolve()),
                    },
                )
                raise
            write_status(
                status_manifest,
                {
                    "status": "passed",
                    "provider": "local-qwen",
                    "mode": "master-track",
                    "master_output": str(master_output.resolve()),
                },
            )
        finally:
            job_path.unlink(missing_ok=True)
            runner_path.unlink(missing_ok=True)


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        (root / "audio").mkdir(parents=True, exist_ok=True)
        run_qwen_job(root, project, args.force)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


RENDER_ALL = dedent(
    r"""
    param(
      [string]$Root
    )

    $ErrorActionPreference = "Stop"

    if (-not $Root) {
      $Root = Split-Path -Parent $PSScriptRoot
    }

    $python = "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

    & $python (Join-Path $Root "scripts\quick_check.py") --root $Root
    & $python (Join-Path $Root "scripts\generate_tts_publish.py") --root $Root --provider auto
    & $python (Join-Path $Root "scripts\prepare_remotion_props.py") --root $Root
    & (Join-Path $Root "scripts\render_remotion.ps1") -Root $Root
    """
).strip() + "\n"


PREPARE_REMOTION_PROPS = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import math
    import re
    import shutil
    import subprocess
    import wave
    from pathlib import Path

    from video_pipeline_common import find_existing_master_audio, load_project, segment_narration_text


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--fps", type=int, default=30)
        parser.add_argument("--width", type=int, default=1920)
        parser.add_argument("--height", type=int, default=1080)
        return parser.parse_args()


    def audio_duration_sec(path: Path) -> float | None:
        if path.suffix.lower() == ".wav":
            try:
                with wave.open(str(path), "rb") as audio:
                    frames = audio.getnframes()
                    rate = audio.getframerate()
                return frames / float(rate or 1)
            except wave.Error:
                return None
        ffmpeg = shutil.which("ffmpeg") or r"C:\Program Files\File Converter\ffmpeg.exe"
        if Path(ffmpeg).exists() or shutil.which("ffmpeg"):
            proc = subprocess.run(
                [ffmpeg, "-i", str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
            )
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stdout)
            if match:
                hours, minutes, seconds = match.groups()
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return None


    def text_weight(text: str) -> float:
        cleaned = text.strip()
        if not cleaned:
            return 1.0
        punctuation_bonus = sum(cleaned.count(ch) for ch in "，。！？；：,.!?;:")
        return max(len(cleaned) + punctuation_bonus * 2, 1)


    def public_asset_ref(root: Path, value: str) -> str:
        raw = str(value or "").strip()
        if not raw or re.match(r"^(https?:|data:)", raw):
            return raw
        normalized = raw.replace("\\", "/")
        if normalized.startswith(("assets/", "audio/")):
            return normalized
        source = Path(raw)
        if not source.is_absolute():
            source = root / source
        if not source.exists() or not source.is_file():
            return normalized
        public_assets = root / "remotion" / "public" / "assets"
        public_assets.mkdir(parents=True, exist_ok=True)
        target = public_assets / source.name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        return f"assets/{target.name}"


    def plan_segments(root: Path, project: dict, segments: list[dict], total_duration: float, fps: int) -> list[dict]:
        explicit_total = 0.0
        weighted: list[tuple[int, float]] = []
        planned: list[dict] = []
        for index, item in enumerate(segments):
            seg_id = str(item.get("id") or f"scene-{index + 1:03d}")
            narration = segment_narration_text(item, project)
            duration = item.get("duration_sec")
            if duration:
                explicit_total += float(duration)
            else:
                weighted.append((index, float(item.get("duration_weight") or text_weight(narration))))
            planned.append(
                {
                    "id": seg_id,
                    "type": str(item.get("type") or "scene"),
                    "title": str(item.get("title") or item.get("heading") or seg_id),
                    "subtitle": str(item.get("subtitle") or item.get("caption") or ""),
                    "narration": narration,
                    "visualJob": str(item.get("visual_job") or item.get("shot_role") or "explain"),
                    "storyTurn": str(item.get("story_turn") or ""),
                    "asset": public_asset_ref(root, str(item.get("asset") or item.get("image") or item.get("visual_asset") or "")),
                    "durationSec": float(duration) if duration else 0.0,
                    "startFrame": 0,
                    "durationFrames": 1,
                }
            )

        remaining = max(total_duration - explicit_total, 0.0)
        total_weight = sum(weight for _, weight in weighted) or 1.0
        for index, weight in weighted:
            planned[index]["durationSec"] = max(remaining * (weight / total_weight), 0.8)

        cursor = 0
        for item in planned:
            frames = max(int(round(item["durationSec"] * fps)), 1)
            item["startFrame"] = cursor
            item["durationFrames"] = frames
            cursor += frames
        return planned


    def copy_master_audio(root: Path, audio: Path) -> str:
        public_audio = root / "remotion" / "public" / "audio"
        public_audio.mkdir(parents=True, exist_ok=True)
        target = public_audio / audio.name
        if audio.resolve() != target.resolve():
            shutil.copy2(audio, target)
        return f"audio/{target.name}"


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project, segments = load_project(root)
        if not segments:
            raise SystemExit("segments.json is empty; compile content into Remotion segments first")
        master_audio = find_existing_master_audio(root)
        if not master_audio:
            raise FileNotFoundError("Missing master audio: audio/master.wav or audio/master.mp3")
        duration = audio_duration_sec(master_audio)
        if not duration:
            raise RuntimeError(f"Could not read master audio duration: {master_audio}")

        render_pipeline = project.get("render_pipeline", {}) or {}
        fps = int(render_pipeline.get("fps") or args.fps)
        composition_id = str(render_pipeline.get("composition_id") or "VideoMaker")
        output_name = str(project.get("output_name") or (root.name + ".mp4"))
        props = {
            "topic": str(project.get("topic") or root.name),
            "fps": fps,
            "width": int(render_pipeline.get("width") or args.width),
            "height": int(render_pipeline.get("height") or args.height),
            "compositionId": composition_id,
            "outputName": output_name,
            "audio": {"src": copy_master_audio(root, master_audio), "durationSec": duration},
            "segments": plan_segments(root, project, segments, duration, fps),
        }
        total_frames = sum(item["durationFrames"] for item in props["segments"])
        props["durationInFrames"] = max(total_frames, int(math.ceil(duration * fps)), 1)

        remotion_dir = root / "remotion"
        remotion_dir.mkdir(parents=True, exist_ok=True)
        (remotion_dir / "input-props.json").write_text(
            json.dumps(props, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[remotion] props -> {remotion_dir / 'input-props.json'}")


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


RENDER_REMOTION = dedent(
    r"""
    param(
      [string]$Root
    )

    $ErrorActionPreference = "Stop"

    if (-not $Root) {
      $Root = Split-Path -Parent $PSScriptRoot
    }

    $remotionDir = Join-Path $Root "remotion"
    $propsPath = Join-Path $remotionDir "input-props.json"
    if (-not (Test-Path $propsPath)) {
      throw "Missing Remotion props: $propsPath"
    }

    Push-Location $remotionDir
    try {
      if (-not (Test-Path "node_modules")) {
        npm install
      }
      $props = Get-Content $propsPath -Raw | ConvertFrom-Json
      $output = Join-Path $Root $props.outputName
      npx remotion render src/index.ts $props.compositionId $output --props input-props.json --codec h264 --audio-codec aac --pixel-format yuv420p --overwrite

      $frameDir = Join-Path $Root "remotion_frames"
      New-Item -ItemType Directory -Force $frameDir | Out-Null
      $last = [Math]::Max([int]$props.durationInFrames - 1, 0)
      $samples = @(0, [Math]::Floor($last / 2), $last) | Select-Object -Unique
      foreach ($frame in $samples) {
        $frameName = "frame_{0:D6}.png" -f [int]$frame
        $framePath = Join-Path $frameDir $frameName
        npx remotion still src/index.ts $props.compositionId $framePath --props input-props.json --frame $frame --image-format png --overwrite
      }
    } finally {
      Pop-Location
    }
    """
).strip() + "\n"


REMOTION_PACKAGE_JSON = """{
  "scripts": {
    "studio": "remotion studio src/index.ts",
    "render": "remotion render src/index.ts VideoMaker ../video-maker-output.mp4"
  },
  "dependencies": {
    "@remotion/cli": "latest",
    "@remotion/media": "latest",
    "react": "latest",
    "react-dom": "latest",
    "remotion": "latest"
  },
  "devDependencies": {
    "@types/react": "latest",
    "typescript": "latest"
  }
}
"""


REMOTION_TSCONFIG = """{
  "compilerOptions": {
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "module": "ESNext",
    "target": "ES2021",
    "moduleResolution": "Node",
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
"""


REMOTION_INDEX_TS = """import {registerRoot} from 'remotion';
import {Root} from './Root';

registerRoot(Root);
"""


REMOTION_ROOT_TSX = """import React from 'react';
import {Composition} from 'remotion';
import {VideoMaker} from './Video';
import type {VideoMakerProps} from './types';

const defaultProps: VideoMakerProps = {
  topic: 'Video Maker',
  fps: 30,
  width: 1920,
  height: 1080,
  compositionId: 'VideoMaker',
  outputName: 'video-maker-output.mp4',
  durationInFrames: 180,
  audio: undefined,
  segments: [
    {
      id: 'scene-001',
      type: 'scene',
      title: '等待内容编译',
      subtitle: 'Remotion composition shell',
      narration: '',
      visualJob: 'orient',
      storyTurn: 'setup',
      asset: '',
      durationSec: 6,
      startFrame: 0,
      durationFrames: 180,
    },
  ],
};

export const Root: React.FC = () => {
  return (
    <Composition
      id="VideoMaker"
      component={VideoMaker}
      durationInFrames={defaultProps.durationInFrames}
      fps={defaultProps.fps}
      width={defaultProps.width}
      height={defaultProps.height}
      defaultProps={defaultProps}
      calculateMetadata={({props}) => ({
        durationInFrames: Math.max(1, props.durationInFrames),
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />
  );
};
"""


REMOTION_TYPES_TS = """export type Segment = {
  id: string;
  type: string;
  title: string;
  subtitle?: string;
  narration?: string;
  visualJob?: string;
  storyTurn?: string;
  asset?: string;
  durationSec: number;
  startFrame: number;
  durationFrames: number;
};

export type VideoMakerProps = {
  topic: string;
  fps: number;
  width: number;
  height: number;
  compositionId: string;
  outputName: string;
  durationInFrames: number;
  audio?: {
    src: string;
    durationSec: number;
  };
  segments: Segment[];
};
"""


REMOTION_VIDEO_TSX = """import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import type {Segment, VideoMakerProps} from './types';
import './styles.css';

const maybeStatic = (src?: string) => {
  if (!src) {
    return '';
  }
  if (/^(https?:|data:|file:)/.test(src)) {
    return src;
  }
  return staticFile(src.replace(/^public\\//, ''));
};

const Scene: React.FC<{segment: Segment}> = ({segment}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, Math.max(segment.durationFrames - 1, 1)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const asset = maybeStatic(segment.asset);

  return (
    <AbsoluteFill className="scene">
      <div className="ambient" style={{transform: `translate3d(${progress * -28}px, ${progress * 18}px, 0)`}} />
      {asset ? <Img className="sceneAsset" src={asset} /> : null}
      <div className="contentPlane">
        <div className="meta">{segment.storyTurn || segment.visualJob || segment.id}</div>
        <h1>{segment.title}</h1>
        {segment.subtitle ? <p className="subtitle">{segment.subtitle}</p> : null}
      </div>
      {segment.narration ? <div className="caption">{segment.narration}</div> : null}
    </AbsoluteFill>
  );
};

export const VideoMaker: React.FC<VideoMakerProps> = ({audio, segments}) => {
  return (
    <AbsoluteFill className="root">
      {audio?.src ? <Audio src={staticFile(audio.src)} /> : null}
      {segments.map((segment) => (
        <Sequence key={segment.id} from={segment.startFrame} durationInFrames={segment.durationFrames}>
          <Scene segment={segment} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
"""


REMOTION_STYLES_CSS = """:root {
  font-family: Inter, "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
  color: #f7faf4;
  background: #020302;
}

.root,
.scene {
  background: #020302;
  overflow: hidden;
}

.scene {
  justify-content: center;
  padding: 86px;
}

.ambient {
  position: absolute;
  inset: -20%;
  background:
    radial-gradient(circle at 20% 20%, rgba(208, 248, 16, 0.18), transparent 28%),
    linear-gradient(135deg, #020302 0%, #101010 58%, #182006 100%);
  filter: blur(18px);
}

.sceneAsset {
  position: absolute;
  right: 72px;
  top: 72px;
  width: 46%;
  height: calc(100% - 144px);
  object-fit: contain;
}

.contentPlane {
  position: relative;
  z-index: 2;
  max-width: 960px;
  padding: 52px;
  background: rgba(8, 10, 8, 0.82);
  border: 1px solid rgba(208, 248, 16, 0.22);
}

.meta {
  margin-bottom: 22px;
  color: #d0f810;
  font-size: 28px;
}

h1 {
  margin: 0;
  font-size: 82px;
  line-height: 1.06;
  font-weight: 760;
}

.subtitle {
  margin: 24px 0 0;
  max-width: 760px;
  color: rgba(247, 250, 244, 0.76);
  font-size: 34px;
  line-height: 1.36;
}

.caption {
  position: absolute;
  z-index: 4;
  left: 86px;
  right: 86px;
  bottom: 56px;
  padding: 18px 26px;
  background: rgba(2, 3, 2, 0.86);
  border-left: 5px solid #d0f810;
  color: #f7faf4;
  font-size: 30px;
  line-height: 1.42;
}
"""


CHECK_VOICE_ENV = dedent(
    r"""
    param(
      [switch]$ShowHints
    )

    $ErrorActionPreference = "Stop"

    $projectJson = Join-Path (Split-Path -Parent $PSScriptRoot) "content\project.json"
    $localQwen = $null
    if (Test-Path $projectJson) {
      try {
        $project = Get-Content -Raw -Encoding UTF8 $projectJson | ConvertFrom-Json
        $localQwen = $project.voice_settings.local_qwen
      } catch {
        $localQwen = $null
      }
    }

    $localQwenEnabled = [bool]($localQwen -and $localQwen.enabled)
    $localQwenPython = if ($localQwen) { [string]$localQwen.python_executable } else { "" }
    $localQwenHelper = if ($localQwen) { [string]$localQwen.helper_script } else { "" }
    $localQwenModelDir = if ($localQwen) { [string]$localQwen.model_dir } else { "" }
    $localQwenReady = $localQwenEnabled -and (Test-Path $localQwenPython) -and (Test-Path $localQwenModelDir)

    [PSCustomObject]@{
      local_qwen = [PSCustomObject]@{
        enabled = $localQwenEnabled
        python_executable = $localQwenPython
        helper_script = $localQwenHelper
        model_dir = $localQwenModelDir
        ready = $localQwenReady
      }
      recommendation = if ($localQwenReady) {
        "Local Qwen 12Hz is ready. Auto mode will prefer local Qwen and use one-pass master-track narration for Chinese projects."
      } else {
        "Local Qwen 12Hz is not ready. This project will fall back to Edge preview audio until model_dir is fixed."
      }
    } | ConvertTo-Json -Depth 4
    """
).strip() + "\n"


QUICK_CHECK = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import re
    import shutil
    import subprocess
    import sys
    import wave
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--strict", action="store_true")
        return parser.parse_args()


    def narration_text(item: dict) -> str:
        for key in ("tts_text", "spoken_text", "voice_spoken", "narration_text", "voice"):
            value = str(item.get(key) or "").strip()
            if value:
                return value
        return ""


    def cjk_count(text: str) -> int:
        return len(re.findall(r"[\u3400-\u9fff]", text))


    def audio_duration_sec(path: Path) -> float | None:
        if path.suffix.lower() == ".wav":
            try:
                with wave.open(str(path), "rb") as audio:
                    frames = audio.getnframes()
                    rate = audio.getframerate()
                return frames / float(rate or 1)
            except wave.Error:
                return None

        try:
            from mutagen.mp3 import MP3  # type: ignore

            return float(MP3(str(path)).info.length)
        except Exception:
            pass

        ffmpeg = shutil.which("ffmpeg") or r"C:\Program Files\File Converter\ffmpeg.exe"
        if Path(ffmpeg).exists() or shutil.which("ffmpeg"):
            proc = subprocess.run(
                [ffmpeg, "-i", str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
            )
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stdout)
            if match:
                hours, minutes, seconds = match.groups()
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return None


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        hard_failures: list[str] = []
        warnings: list[str] = []

        project_path = root / "content" / "project.json"
        segments_path = root / "content" / "segments.json"
        notes_path = root / "publish_notes.md"
        narration_path = root / "content" / "narration_polish.json"

        for required in [project_path, segments_path, notes_path, narration_path]:
            if not required.exists():
                hard_failures.append(f"missing required file: {required}")

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        project = json.loads(project_path.read_text(encoding="utf-8-sig"))
        segments = json.loads(segments_path.read_text(encoding="utf-8-sig"))

        if not segments:
            hard_failures.append("segments.json is empty; generate a beat-driven scene list before rendering")

        provider = str(project.get("voice_provider", "local-qwen"))
        voice_language = str(project.get("voice_language", "zh-CN")).lower()
        workflow = project.get("voice_workflow", {}) or {}
        voice_profile = project.get("voice_profile", {}) or {}
        local_qwen = ((project.get("voice_settings") or {}).get("local_qwen") or {})
        local_qwen_enabled = bool(local_qwen.get("enabled", False))
        local_qwen_python = Path(str(local_qwen.get("python_executable") or "")) if local_qwen else Path()
        local_qwen_model_dir = Path(str(local_qwen.get("model_dir") or "")) if local_qwen else Path()
        local_qwen_ready = local_qwen_enabled and local_qwen_python.exists() and local_qwen_model_dir.exists()

        if provider in {"preview-edge-tts", "edge-tts"}:
            warnings.append("voice_provider 仍是预览级 TTS；适合粗剪，不建议直接发布")
        elif provider == "local-qwen" and local_qwen_enabled and not local_qwen_ready:
            warnings.append("voice_settings.local_qwen 已启用，但本地 Qwen 12Hz Python 或 model_dir 路径不存在")

        if voice_language.startswith("zh") and workflow.get("accent_review_required", True):
            if provider != "local-qwen" and str(voice_profile.get("review_status", "unreviewed")).lower() != "passed":
                warnings.append("中文终版配音尚未通过听感验收；先确认没有外国人口音或明显翻译腔")

        voice_locale = str(voice_profile.get("locale", "")).lower()
        if voice_language.startswith("zh") and voice_locale and not voice_locale.startswith("zh"):
            warnings.append(f"当前 voice_profile.locale={voice_locale}；中文旁白存在外国人口音风险")

        for item in segments:
            if item.get("type") == "slide":
                html_path = root / item["html"]
                if not html_path.exists():
                    hard_failures.append(f"missing slide html: {html_path}")
            if item.get("type") == "demo":
                video_path = root / item["video"]
                if not video_path.exists():
                    placeholder_html = item.get("placeholder_html") or item.get("html")
                    if placeholder_html and (root / placeholder_html).exists():
                        warnings.append(
                            f"segment {item.get('id')} demo 录像缺失；render_all 会先用占位场景 {placeholder_html} 顶上"
                        )
                    else:
                        hard_failures.append(f"missing demo video and placeholder: {video_path}")
            if "待由" in str(item.get("voice") or ""):
                warnings.append(f"segment {item.get('id')} 仍是占位旁白，先完成 script-writer -> narration-polisher -> coordinator 的口播合并再出片")

        if workflow.get("narration_mode") == "master-track-preferred":
            audio_dir = root / "audio"
            has_master = any((audio_dir / name).exists() for name in ("master.wav", "master.mp3"))
            if not has_master:
                warnings.append("当前项目偏好整段 master-track，但还没有生成 master audio")

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        for item in warnings:
            print(f"[WARN] {item}")

        print("[OK] project structure looks usable")
        if warnings and args.strict:
            sys.exit(2)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


PUBLISH_NOTES_MARKER = (
    "- 内容研究默认走 outline -> depth -> detail -> narration polish 四段串行\n"
        "- 主 agent 是 coordinator，只负责统筹、简单命令、合并和最终决策；内容、视觉、音频、装配和验收都交给 subagent\n"
    "- 内容默认走 content-strategist -> script-writer -> narration-polisher；成稿后再润色，去掉 AI 人机味和翻译腔，不改主线判断\n"
    "- scene 编译默认走 style contract -> shot intent -> Remotion React composition，不再走 HTML slide 渲染路径\n"
    "- visual-architect 在 visual_asset_plan 内记录 benchmark 和 key_visual：借鉴认知模式，不复制画风；封面、片头、章节和结尾共享一个主视觉记忆点\n"
    "- 风格只锁黑绿 + iOS 18-inspired frosted glass 的材质逻辑与层级，不锁固定模块或固定布局；视频 composition、动画、字幕、音频、时间轴和渲染默认交给 Remotion\n"
    "- visual-architect 可调用 imagegen 生成视觉设计、爆炸图、机制图、动画素材和 B 站封面\n"
    "- imagegen 负责高质量成图，包含中文大字、公式、标签、数字、代码和 UI 状态；visual-qa-fixer 逐字/逐项核对，不对就重生 imagegen 图\n"
    "- visual-qa-fixer 必须读取实际 Remotion frame samples 和封面图，发现错字、缺字、乱码、重叠、白边、坏裁切或过期封面就直接修 Remotion 代码/图片并重渲染\n"
    "- production-engineer 合并配音和装配职责：默认走本地 Qwen 12Hz 整段单次合成，负责 Remotion props、渲染和导出\n"
    "- 中文语速按上期 CUDA 成片校准：目标约 260 中文字/分钟，可接受区间 240-285；时长不匹配但内容和 QA 通过时不阻塞发布\n"
        "- acceptance-reviewer 必须看多张实际截图、读 Remotion 代码和内容合同，并完整听完 master 音频；不自然、不真实、不像人会这么讲/这么展示都要打回\n"
    "- 封面默认在本地 QA 通过且标题锁定后由 visual-architect 用 imagegen 生成，再由 visual-qa-fixer 看图修正；输出到 publish/cover.png，并在上传 B 站时一并上传且截图确认已回填\n"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument(
        "--voice-provider",
        default="local-qwen",
        choices=["local-qwen", "preview-edge-tts"],
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def patch_publish_notes(path: Path) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8-sig")
    if PUBLISH_NOTES_MARKER.strip() in content:
        return
    content = content.rstrip() + "\n" + PUBLISH_NOTES_MARKER
    path.write_text(content, encoding="utf-8")


def sync_publish_assets(root: Path, topic: str) -> None:
    publish_dir = root / "publish"
    publish_dir.mkdir(parents=True, exist_ok=True)
    cover_prompt = publish_dir / "cover_prompt.md"
    if not cover_prompt.exists():
        write_text(cover_prompt, build_cover_prompt(topic))


def sync_remotion_foundation(root: Path) -> None:
    remotion_dir = root / "remotion"
    src_dir = remotion_dir / "src"
    public_assets = remotion_dir / "public" / "assets"
    public_audio = remotion_dir / "public" / "audio"
    frame_dir = root / "remotion_frames"
    for path in [src_dir, public_assets, public_audio, frame_dir]:
        path.mkdir(parents=True, exist_ok=True)

    files = {
        remotion_dir / "package.json": REMOTION_PACKAGE_JSON,
        remotion_dir / "tsconfig.json": REMOTION_TSCONFIG,
        src_dir / "index.ts": REMOTION_INDEX_TS,
        src_dir / "Root.tsx": REMOTION_ROOT_TSX,
        src_dir / "Video.tsx": REMOTION_VIDEO_TSX,
        src_dir / "types.ts": REMOTION_TYPES_TS,
        src_dir / "styles.css": REMOTION_STYLES_CSS,
    }
    for path, content in files.items():
        if not path.exists():
            write_text(path, content)


def default_scene_prompt_basis(beat_id: str) -> dict:
    return {
        "style_contract": "content/style_contract.json",
        "shot_intent": f"content/shot_intents.json#{beat_id}",
        "content_contracts": [
            "content/problem_contract.json",
            "content/audience_contract.json",
            "content/opening_contract.json",
            f"content/meaning_contract.json#{beat_id}",
            f"content/outline_plan.json#{beat_id}",
            f"content/depth_contract.json#{beat_id}",
            f"content/detail_weave.json#{beat_id}",
            f"content/evidence_map.json#{beat_id}",
            f"content/narration_polish.json#{beat_id}",
        ],
    }


def patch_segments_json(root: Path) -> None:
    path = root / "content" / "segments.json"
    if not path.exists():
        return
    segments = json.loads(path.read_text(encoding="utf-8-sig"))
    changed = False
    total = len(segments)
    for index, item in enumerate(segments, start=1):
        beat_id = str(item.get("id") or f"scene-{index:03d}")
        if item.get("id") != beat_id:
            item["id"] = beat_id
            changed = True
        if item.get("type") == "demo" and not item.get("placeholder_html") and item.get("html"):
            item["placeholder_html"] = item["html"]
            changed = True
        shot_role = str(item.get("shot_role") or "").strip()
        if not shot_role:
            item["shot_role"] = default_shot_role_for_index(index, total)
            changed = True
        shot_intent_ref = f"content/shot_intents.json#{beat_id}"
        if item.get("shot_intent_ref") != shot_intent_ref:
            item["shot_intent_ref"] = shot_intent_ref
            changed = True
        basis = item.get("scene_prompt_basis")
        if not isinstance(basis, dict):
            item["scene_prompt_basis"] = default_scene_prompt_basis(beat_id)
            changed = True
        else:
            if basis.get("style_contract") != "content/style_contract.json":
                basis["style_contract"] = "content/style_contract.json"
                changed = True
            if basis.get("shot_intent") != shot_intent_ref:
                basis["shot_intent"] = shot_intent_ref
                changed = True
            content_contracts = basis.get("content_contracts")
            if not isinstance(content_contracts, list) or len(content_contracts) < 4:
                basis["content_contracts"] = default_scene_prompt_basis(beat_id)["content_contracts"]
                changed = True
    if changed:
        path.write_text(json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_depth_beat(outline_beat: dict) -> dict:
    beat_id = str(outline_beat.get("beat_id") or "scene-001")
    provisional_claim = str(outline_beat.get("provisional_claim") or "待由 content-strategist 提供")
    return {
        "beat_id": beat_id,
        "provisional_claim": provisional_claim,
        "resolved_claim": "待由 content-strategist 锁定",
        "claim_job": "define",
        "beat_progression": "待定义：这一拍相对前后内容推进了什么。",
        "meaning_gain": "待定义：这一拍让观众多会什么。",
        "scale_jump": "待定义：这一拍是否完成尺度跃迁。",
        "context_role": str(outline_beat.get("context_role") or "待定义：这一拍与前后内容的关系。"),
        "support_type": "to-be-selected",
        "confidence_level": "to-be-rated",
        "proof_anchor": "待定义：这一拍的证据载体。",
        "counterexample_or_boundary": "待定义：反例、边界或限制。",
        "misconception_to_break": str(outline_beat.get("confusion_target") or "待定义"),
        "overclaim_boundary": "待定义：这一拍不能说过头的地方。",
        "required_support": [],
        "detail_budget": "standard",
        "status": "ready_for_detail",
    }


def make_detail_beat(depth_beat: dict) -> dict:
    beat_id = str(depth_beat.get("beat_id") or "scene-001")
    return {
        "beat_id": beat_id,
        "resolved_claim_ref": f"{beat_id}.claim",
        "required_support_refs": [],
        "detail_budget": {
            "default_max": 2,
            "expanded_max": 3,
            "expansion_reason": "depth-red-flag|none",
        },
        "details": [],
        "deferred_details": [],
        "risk_flags": [],
    }


def make_script_draft_beat(depth_beat: dict) -> dict:
    beat_id = str(depth_beat.get("beat_id") or "scene-001")
    return {
        "beat_id": beat_id,
        "source_claim_refs": [f"content/evidence_map.json#{beat_id}"],
        "draft_narration": "待由 script-writer 基于内容合同写出第一版完整口播稿。",
        "visual_cues_for_this_text": [],
        "terms_to_define_before_use": [],
        "risk_notes": [],
    }


def make_narration_polish_beat(script_beat: dict) -> dict:
    beat_id = str(script_beat.get("beat_id") or "scene-001")
    return {
        "beat_id": beat_id,
        "source_draft_ref": f"content/script_draft.json#{beat_id}",
        "spoken_goal": "待由 narration-polisher 在成稿后润色成自然、可口播、普通 B 站用户易懂的中文。",
        "polished_narration": "待由 narration-polisher 基于 script_draft 改写；不新增事实，不改主张。",
        "plain_language_changes": [],
        "humanity_adjustments": ["减少翻译腔", "避免空泛口号", "避免过度书面语", "去掉明显 AI 人机味"],
        "locked_terms": [],
        "needs_content_revisit": False,
    }


def sync_content_artifacts(root: Path) -> None:
    project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
    topic = str(project.get("topic") or root.name)

    problem_path = root / "content" / "problem_contract.json"
    if not problem_path.exists():
        problem_path.write_text(
            json.dumps(build_problem_contract_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    audience_path = root / "content" / "audience_contract.json"
    if not audience_path.exists():
        audience_path.write_text(
            json.dumps(build_audience_contract_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    opening_path = root / "content" / "opening_contract.json"
    if not opening_path.exists():
        opening_path.write_text(
            json.dumps(build_opening_contract_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    outline_path = root / "content" / "outline_plan.json"
    outline_changed = not outline_path.exists()
    outline = build_outline_plan_data(topic) if outline_changed else json.loads(outline_path.read_text(encoding="utf-8-sig"))
    outline.setdefault("version", "v3")
    outline.setdefault("topic", topic)
    outline.setdefault("outline_status", "needs_outline")
    if str(outline.get("next_owner") or "") in {"", "outline-researcher", "depth-builder", "detail-filler"}:
        outline["next_owner"] = "content-strategist"
        outline_changed = True
    for key, value in {
        "based_on_problem_contract": "content/problem_contract.json",
        "based_on_audience_contract": "content/audience_contract.json",
        "based_on_opening_contract": "content/opening_contract.json",
        "audience_baseline": "待定义：普通 B 站用户理解这期需要的起点。",
        "term_budget": {"max_new_terms_per_minute": 2, "must_define_before_use": True},
        "opening_contract": "content/opening_contract.json",
    }.items():
        if key not in outline:
            outline[key] = value
            outline_changed = True
    if "episode_scope" not in outline:
        outline["episode_scope"] = outline.pop("higher_order_takeaway", "待定义：这期需要覆盖到什么范围、边界或重点。")
        outline_changed = True
    else:
        outline.pop("higher_order_takeaway", None)
    outline.setdefault("story_shape", "to-be-decided")
    outline.setdefault("pacing_strategy", "to-be-decided")
    coverage_contract = outline.setdefault("coverage_contract", {})
    if not isinstance(coverage_contract, dict):
        coverage_contract = {"summary": str(coverage_contract)}
        outline["coverage_contract"] = coverage_contract
        outline_changed = True
    if "must_answer" not in coverage_contract or coverage_contract.get("must_answer") == LEGACY_MUST_ANSWER:
        coverage_contract["must_answer"] = []
        outline_changed = True
    if coverage_contract.get("question_policy") != "content-decides":
        coverage_contract["question_policy"] = "content-decides"
        outline_changed = True
    coverage_contract.setdefault("what_not_to_overclaim", [])
    outline.setdefault("open_questions", [])
    beats = outline.setdefault("beats", [])
    if not beats:
        outline["beats"] = build_outline_plan_data(topic)["beats"]
        beats = outline["beats"]
        outline_changed = True
    for index, beat in enumerate(beats, start=1):
        beat.setdefault("beat_id", f"scene-{index:03d}")
        beat.setdefault("order", index)
        if "provisional_claim" not in beat:
            beat["provisional_claim"] = beat.pop("key_claim", "待由 content-strategist 提供")
            outline_changed = True
        beat.setdefault("purpose", "placeholder")
        beat.setdefault("viewer_question", "待补充")
        if "context_role" not in beat:
            beat["context_role"] = beat.pop("why_now_role", "to-be-defined")
            outline_changed = True
        else:
            beat.pop("why_now_role", None)
        beat.setdefault("confusion_target", "to-be-defined")
        beat.setdefault("visual_focus", "待生成")
        beat.setdefault("bridge_out", "待生成")
        beat.setdefault("depth_need", "standard")
    if outline_changed:
        outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    meaning_path = root / "content" / "meaning_contract.json"
    meaning_changed = not meaning_path.exists()
    meaning = (
        build_meaning_contract_data(topic)
        if meaning_changed
        else json.loads(meaning_path.read_text(encoding="utf-8-sig"))
    )
    meaning.setdefault("version", "v1")
    meaning.setdefault("topic", topic)
    meaning.setdefault("status", "needs_meaning_contract")
    if str(meaning.get("next_owner") or "") in {"", "outline-researcher", "depth-builder", "detail-filler"}:
        meaning["next_owner"] = "content-strategist"
        meaning_changed = True
    meaning.setdefault("viewer_before", "待定义：观众看这期之前通常卡在哪里。")
    meaning.setdefault("viewer_after", "待定义：观众看完后会多一种什么判断方式或行动能力。")
    meaning.setdefault("core_judgment", "待定义：这期最终要交给观众的核心判断。")
    meaning.setdefault("why_watch_now", "待定义：为什么这个主题现在值得看。")
    meaning.setdefault("must_not_be", ["知识点堆叠", "只解释名词", "为了显得完整而扩写无关内容"])
    meaning_beats = meaning.setdefault("beats", [])
    if not isinstance(meaning_beats, list) or len(meaning_beats) != len(outline["beats"]):
        meaning["beats"] = []
        meaning_beats = meaning["beats"]
        for index, outline_beat in enumerate(outline["beats"], start=1):
            beat_id = str(outline_beat.get("beat_id") or f"scene-{index:03d}")
            meaning_beats.append(
                {
                    "beat_id": beat_id,
                    "viewer_gain": "待定义：这一拍让观众多会什么。",
                    "existence_reason": "待定义：为什么这一拍必须存在。",
                    "not_just_information": "待定义：它不是单纯知识点的原因。",
                }
            )
        meaning_changed = True
    for index, (outline_beat, meaning_beat) in enumerate(zip(outline["beats"], meaning_beats, strict=False), start=1):
        beat_id = str(outline_beat.get("beat_id") or f"scene-{index:03d}")
        meaning_beat.setdefault("beat_id", beat_id)
        meaning_beat.setdefault("viewer_gain", "待定义：这一拍让观众多会什么。")
        meaning_beat.setdefault("existence_reason", "待定义：为什么这一拍必须存在。")
        meaning_beat.setdefault("not_just_information", "待定义：它不是单纯知识点的原因。")
    if meaning_changed:
        meaning_path.write_text(json.dumps(meaning, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    depth_path = root / "content" / "depth_contract.json"
    depth_changed = not depth_path.exists()
    depth = build_depth_contract_data(topic) if depth_changed else json.loads(depth_path.read_text(encoding="utf-8-sig"))
    depth.setdefault("version", "v1")
    depth.setdefault("topic", topic)
    depth.setdefault("status", "needs_depth")
    if str(depth.get("next_owner") or "") in {"", "outline-researcher", "depth-builder", "detail-filler"}:
        depth["next_owner"] = "content-strategist"
        depth_changed = True
    depth.setdefault("based_on_outline", "content/outline_plan.json")
    if "based_on_problem_contract" not in depth:
        depth["based_on_problem_contract"] = "content/problem_contract.json"
        depth_changed = True
    episode_depth_goal = depth.setdefault("episode_depth_goal", {})
    if not isinstance(episode_depth_goal, dict):
        episode_depth_goal = {"summary": str(episode_depth_goal)}
        depth["episode_depth_goal"] = episode_depth_goal
        depth_changed = True
    if "context_note" not in episode_depth_goal:
        episode_depth_goal["context_note"] = episode_depth_goal.pop("why_now", "待定义：这期与上下文、背景或使用场景的关系。")
        depth_changed = True
    else:
        episode_depth_goal.pop("why_now", None)
    episode_depth_goal.setdefault("confusion_knot", "待定义：这期最容易长期讲混的核心结在哪里。")
    if "resolution_note" not in episode_depth_goal:
        episode_depth_goal["resolution_note"] = episode_depth_goal.pop("judgment_rule", "待定义：这期最终要收束到什么理解或结论。")
        depth_changed = True
    else:
        episode_depth_goal.pop("judgment_rule", None)
    routing = depth.setdefault("routing", {})
    routing.setdefault("needs_outline_rework", [])
    routing.setdefault("ready_for_detail", [])
    depth_beats = depth.setdefault("beats", [])
    if not depth_beats or len(depth_beats) != len(outline["beats"]):
        depth["beats"] = [make_depth_beat(beat) for beat in outline["beats"]]
        depth_beats = depth["beats"]
        routing["ready_for_detail"] = [beat["beat_id"] for beat in depth_beats]
        depth_changed = True
    for outline_beat, depth_beat in zip(outline["beats"], depth_beats, strict=False):
        depth_beat.setdefault("beat_id", str(outline_beat.get("beat_id") or "scene-001"))
        depth_beat.setdefault("provisional_claim", str(outline_beat.get("provisional_claim") or "待由 content-strategist 提供"))
        if str(depth_beat.get("resolved_claim") or "") in {"", "待由 depth-builder 锁定"}:
            depth_beat["resolved_claim"] = "待由 content-strategist 锁定"
            depth_changed = True
        depth_beat.setdefault("claim_job", "define")
        if "beat_progression" not in depth_beat:
            depth_beat["beat_progression"] = depth_beat.pop("judgment_shift", "待定义：这一拍相对前后内容推进了什么。")
            depth_changed = True
        else:
            depth_beat.pop("judgment_shift", None)
        if "context_role" not in depth_beat:
            depth_beat["context_role"] = depth_beat.pop(
                "why_now_role",
                str(outline_beat.get("context_role") or "待定义：这一拍与前后内容的关系。"),
            )
            depth_changed = True
        else:
            depth_beat.pop("why_now_role", None)
        depth_beat.setdefault("misconception_to_break", str(outline_beat.get("confusion_target") or "待定义"))
        for key, value in {
            "meaning_gain": "待定义：这一拍让观众多会什么。",
            "scale_jump": "待定义：这一拍是否完成尺度跃迁。",
            "support_type": "to-be-selected",
            "confidence_level": "to-be-rated",
            "proof_anchor": "待定义：这一拍的证据载体。",
            "counterexample_or_boundary": "待定义：反例、边界或限制。",
        }.items():
            if key not in depth_beat:
                depth_beat[key] = value
                depth_changed = True
        depth_beat.setdefault("overclaim_boundary", "待定义：这一拍不能说过头的地方。")
        depth_beat.setdefault("required_support", [])
        depth_beat.setdefault("detail_budget", "standard")
        depth_beat.setdefault("status", "ready_for_detail")
    if depth_changed:
        depth_path.write_text(json.dumps(depth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    detail_path = root / "content" / "detail_weave.json"
    detail_changed = not detail_path.exists()
    detail = build_detail_weave_data() if detail_changed else json.loads(detail_path.read_text(encoding="utf-8-sig"))
    detail.setdefault("version", "v1")
    detail.setdefault("detail_status", "needs_detail")
    if str(detail.get("next_owner") or "") in {"", "detail-filler", "narration-polisher"}:
        detail["next_owner"] = "script-writer"
        detail_changed = True
    source_contracts = detail.setdefault("source_contracts", {})
    if "problem_contract" not in source_contracts:
        source_contracts["problem_contract"] = "content/problem_contract.json"
        detail_changed = True
    source_contracts.setdefault("outline_plan", "content/outline_plan.json")
    source_contracts.setdefault("depth_contract", "content/depth_contract.json")
    if "evidence_map" not in source_contracts:
        source_contracts["evidence_map"] = "content/evidence_map.json"
        detail_changed = True
    locks = detail.setdefault("locks", {})
    locks.setdefault("coverage_shape_locked", True)
    locks.setdefault("beat_order_locked", True)
    locks.setdefault("claims_locked", True)
    detail_beats = detail.setdefault("beats", [])
    if not detail_beats or len(detail_beats) != len(depth["beats"]):
        detail["beats"] = [make_detail_beat(beat) for beat in depth["beats"]]
        detail_beats = detail["beats"]
        detail_changed = True
    for depth_beat, detail_beat in zip(depth["beats"], detail_beats, strict=False):
        beat_id = str(depth_beat.get("beat_id") or "scene-001")
        detail_beat.setdefault("beat_id", beat_id)
        detail_beat.setdefault("resolved_claim_ref", f"{beat_id}.claim")
        detail_beat.setdefault("required_support_refs", [])
        detail_budget = detail_beat.setdefault("detail_budget", {})
        detail_budget.setdefault("default_max", 2)
        detail_budget.setdefault("expanded_max", 3)
        detail_budget.setdefault("expansion_reason", "depth-red-flag|none")
        detail_beat.setdefault("details", [])
        detail_beat.setdefault("deferred_details", [])
        detail_beat.setdefault("risk_flags", [])
    detail.setdefault("sources", [])
    detail.setdefault("deferred_details", [])
    if detail_changed:
        detail_path.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    evidence_path = root / "content" / "evidence_map.json"
    evidence_changed = not evidence_path.exists()
    evidence_map = (
        build_evidence_map_data(topic)
        if evidence_changed
        else json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    )
    evidence_map.setdefault("version", "v1")
    evidence_map.setdefault("topic", topic)
    evidence_map.setdefault("status", "needs_evidence_map")
    if str(evidence_map.get("next_owner") or "") in {"", "depth-builder", "detail-filler"}:
        evidence_map["next_owner"] = "script-writer"
        evidence_changed = True
    for key, value in {
        "claims": [],
        "source_refs": [],
        "known_unknowns": [],
        "disagreement_notes": [],
        "deferred_but_important_questions": [],
    }.items():
        if key not in evidence_map:
            evidence_map[key] = value
            evidence_changed = True
    if evidence_changed:
        evidence_path.write_text(json.dumps(evidence_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    script_draft_path = root / "content" / "script_draft.json"
    script_changed = not script_draft_path.exists()
    script_draft = (
        build_script_draft_data()
        if script_changed
        else json.loads(script_draft_path.read_text(encoding="utf-8-sig"))
    )
    script_draft.setdefault("version", "v1")
    script_draft.setdefault("status", "needs_script_draft")
    if str(script_draft.get("next_owner") or "") in {"", "detail-filler", "narration-polisher"}:
        script_draft["next_owner"] = "script-writer"
        script_changed = True
    script_sources = script_draft.setdefault("source_contracts", {})
    for key, value in {
        "problem_contract": "content/problem_contract.json",
        "audience_contract": "content/audience_contract.json",
        "opening_contract": "content/opening_contract.json",
        "meaning_contract": "content/meaning_contract.json",
        "outline_plan": "content/outline_plan.json",
        "depth_contract": "content/depth_contract.json",
        "detail_weave": "content/detail_weave.json",
        "evidence_map": "content/evidence_map.json",
    }.items():
        if key not in script_sources:
            script_sources[key] = value
            script_changed = True
    script_beats = script_draft.setdefault("beats", [])
    if not script_beats or len(script_beats) != len(depth["beats"]):
        script_draft["beats"] = [make_script_draft_beat(beat) for beat in depth["beats"]]
        script_beats = script_draft["beats"]
        script_changed = True
    for depth_beat, script_beat in zip(depth["beats"], script_beats, strict=False):
        beat_id = str(depth_beat.get("beat_id") or "scene-001")
        script_beat.setdefault("beat_id", beat_id)
        script_beat.setdefault("source_claim_refs", [f"content/evidence_map.json#{beat_id}"])
        script_beat.setdefault("draft_narration", "待由 script-writer 基于内容合同写出第一版完整口播稿。")
        script_beat.setdefault("visual_cues_for_this_text", [])
        script_beat.setdefault("terms_to_define_before_use", [])
        script_beat.setdefault("risk_notes", [])
    if script_changed:
        script_draft_path.write_text(json.dumps(script_draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    narration_path = root / "content" / "narration_polish.json"
    narration_changed = not narration_path.exists()
    narration_polish = (
        build_narration_polish_data()
        if narration_changed
        else json.loads(narration_path.read_text(encoding="utf-8-sig"))
    )
    if str(narration_polish.get("version") or "") != "v2":
        narration_polish["version"] = "v2"
        narration_changed = True
    narration_polish.setdefault("status", "needs_narration_polish")
    narration_polish.setdefault("next_owner", "narration-polisher")
    narration_sources = narration_polish.setdefault("source_contracts", {})
    for key, value in {
        "script_draft": "content/script_draft.json",
        "evidence_map": "content/evidence_map.json",
    }.items():
        if key not in narration_sources:
            narration_sources[key] = value
            narration_changed = True
    narration_constraints = narration_polish.setdefault("constraints", {})
    narration_constraints.setdefault("beat_order_locked", True)
    narration_constraints.setdefault("resolved_claim_locked", True)
    narration_constraints.setdefault("no_new_facts_without_source", True)
    narration_constraints.setdefault("spoken_chinese_required", True)
    narration_constraints.setdefault("plain_bilibili_audience_required", True)
    narration_beats = narration_polish.setdefault("beats", [])
    if not narration_beats or len(narration_beats) != len(script_draft["beats"]):
        narration_polish["beats"] = [make_narration_polish_beat(beat) for beat in script_draft["beats"]]
        narration_beats = narration_polish["beats"]
        narration_changed = True
    for script_beat, narration_beat in zip(script_draft["beats"], narration_beats, strict=False):
        beat_id = str(script_beat.get("beat_id") or "scene-001")
        narration_beat.setdefault("beat_id", beat_id)
        narration_beat.setdefault("source_draft_ref", f"content/script_draft.json#{beat_id}")
        if "draft_narration" in narration_beat and "polished_narration" not in narration_beat:
            narration_beat["polished_narration"] = narration_beat.pop("draft_narration")
            narration_changed = True
        narration_beat.setdefault("spoken_goal", "待由 narration-polisher 在成稿后润色成自然、可口播、普通 B 站用户易懂的中文。")
        narration_beat.setdefault("polished_narration", "待由 narration-polisher 基于 script_draft 改写；不新增事实，不改主张。")
        narration_beat.setdefault("plain_language_changes", [])
        narration_beat.setdefault("humanity_adjustments", ["减少翻译腔", "避免空泛口号", "避免过度书面语", "去掉明显 AI 人机味"])
        narration_beat.setdefault("locked_terms", [])
        narration_beat.setdefault("needs_content_revisit", False)
    narration_polish.setdefault(
        "global_avoid",
        ["营销腔", "为了显得聪明而堆术语", "一句里塞太多转折", "像模型解释模型一样的自我指涉", "AI 人机味"],
    )
    if narration_changed:
        narration_path.write_text(json.dumps(narration_polish, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    style_contract_path = root / "content" / "style_contract.json"
    style_contract_changed = not style_contract_path.exists()
    style_contract = (
        build_style_contract_data()
        if style_contract_changed
        else json.loads(style_contract_path.read_text(encoding="utf-8-sig"))
    )
    default_style_contract = build_style_contract_data()
    for key, value in default_style_contract.items():
        if key not in style_contract:
            style_contract[key] = value
            style_contract_changed = True
    if style_contract_changed:
        style_contract_path.write_text(json.dumps(style_contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    shot_intents_path = root / "content" / "shot_intents.json"
    shot_intents_changed = not shot_intents_path.exists()
    shot_intents = (
        build_shot_intents_data(topic)
        if shot_intents_changed
        else json.loads(shot_intents_path.read_text(encoding="utf-8-sig"))
    )
    for key, value in {
        "version": "v1",
        "topic": topic,
        "status": "needs_shot_intents",
        "next_owner": "visual-architect",
        "style_contract_ref": "content/style_contract.json",
    }.items():
        if key not in shot_intents:
            shot_intents[key] = value
            shot_intents_changed = True
    intent_beats = shot_intents.get("beats")
    if not isinstance(intent_beats, list):
        shot_intents["beats"] = []
        intent_beats = shot_intents["beats"]
        shot_intents_changed = True
    if not intent_beats or len(intent_beats) != len(outline["beats"]):
        intent_beats = []
        total = len(outline["beats"])
        for index, outline_beat in enumerate(outline["beats"], start=1):
            beat_id = str(outline_beat.get("beat_id") or f"scene-{index:03d}")
            intent_beats.append(
                {
                    "beat_id": beat_id,
                    "shot_role": str(outline_beat.get("shot_role_hint") or default_shot_role_for_index(index, total)),
                    "narrative_job": str(outline_beat.get("purpose") or "待由 coordinator 路由对应内容 owner 补齐这一拍的叙事职责。"),
                    "visual_goal": str(outline_beat.get("visual_focus") or "待定义这一拍的主视觉焦点。"),
                    "must_show": ["本页唯一关键结论"],
                    "must_avoid": ["固定模板复用", "无关 glass 摆件"],
                    "chrome_level": "minimal",
                    "motion_source": "from-primary-focus",
                    "story_turn": "to-be-selected",
                    "viewer_question": str(outline_beat.get("viewer_question") or ""),
                    "primary_representation": "to-be-selected",
                    "base_visual_kind": "to-be-selected",
                    "imagegen_text_required": True,
                    "imagegen_text_exactness_check": "visual-qa-required",
                    "evidence_mode": "to-be-selected",
                    "visual_truth_label": "to-be-labeled",
                    "formula_latex": "",
                    "latex_required": False,
                    "proof_anchor_ref": "",
                    "boundary_label": "",
                    "imagegen_direct_text_required": True,
                    "scene_prompt_stub": "先锁这一拍的主结论，再决定需要哪种构图和少量功能层。",
                }
            )
        shot_intents["beats"] = intent_beats
        shot_intents_changed = True
    total = len(intent_beats)
    for index, (outline_beat, intent_beat) in enumerate(zip(outline["beats"], intent_beats, strict=False), start=1):
        beat_id = str(outline_beat.get("beat_id") or f"scene-{index:03d}")
        defaults = {
            "beat_id": beat_id,
            "shot_role": str(outline_beat.get("shot_role_hint") or default_shot_role_for_index(index, total)),
            "narrative_job": str(outline_beat.get("purpose") or "待由 coordinator 路由对应内容 owner 补齐这一拍的叙事职责。"),
            "visual_goal": str(outline_beat.get("visual_focus") or "待定义这一拍的主视觉焦点。"),
            "must_show": ["本页唯一关键结论"],
            "must_avoid": ["固定模板复用", "无关 glass 摆件"],
            "chrome_level": "minimal",
            "motion_source": "from-primary-focus",
            "story_turn": "to-be-selected",
            "viewer_question": str(outline_beat.get("viewer_question") or ""),
            "primary_representation": "to-be-selected",
            "base_visual_kind": "to-be-selected",
            "imagegen_text_required": True,
            "imagegen_text_exactness_check": "visual-qa-required",
            "evidence_mode": "to-be-selected",
            "visual_truth_label": "to-be-labeled",
            "formula_latex": "",
            "latex_required": False,
            "proof_anchor_ref": "",
            "boundary_label": "",
            "imagegen_direct_text_required": True,
            "scene_prompt_stub": "先锁这一拍的主结论，再决定需要哪种构图和少量功能层。",
        }
        for key, value in defaults.items():
            if key not in intent_beat:
                intent_beat[key] = value
                shot_intents_changed = True
    if shot_intents_changed:
        shot_intents_path.write_text(json.dumps(shot_intents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    visual_asset_plan_path = root / "content" / "visual_asset_plan.json"
    if not visual_asset_plan_path.exists():
        visual_asset_plan_path.write_text(
            json.dumps(build_visual_asset_plan_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        visual_asset_plan = json.loads(visual_asset_plan_path.read_text(encoding="utf-8-sig"))
        default_visual_asset_plan = build_visual_asset_plan_data(topic)
        visual_asset_plan_changed = False
        for key in ("visual_benchmark", "key_visual"):
            if key not in visual_asset_plan:
                visual_asset_plan[key] = default_visual_asset_plan[key]
                visual_asset_plan_changed = True
        source_contracts = visual_asset_plan.setdefault("source_contracts", {})
        for stale_key in ("visual_" + "benchmark_contract", "key_" + "visual_contract"):
            if stale_key in source_contracts:
                del source_contracts[stale_key]
                visual_asset_plan_changed = True
        for key, value in default_visual_asset_plan["source_contracts"].items():
            if key not in source_contracts:
                source_contracts[key] = value
                visual_asset_plan_changed = True
        asset_rules = visual_asset_plan.setdefault("asset_rules", {})
        for stale_key in (
            "must_" + "over" + "lay_structurally",
            "truth_" + "over" + "lay_plan",
            "annotation_" + "over" + "lay_required",
        ):
            if stale_key in asset_rules:
                del asset_rules[stale_key]
                visual_asset_plan_changed = True
        for key, value in default_visual_asset_plan["asset_rules"].items():
            if key not in asset_rules:
                asset_rules[key] = value
                visual_asset_plan_changed = True
        if visual_asset_plan_changed:
            visual_asset_plan_path.write_text(json.dumps(visual_asset_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    screenshot_plan_path = root / "content" / "screenshot_plan.json"
    if not screenshot_plan_path.exists():
        screenshot_plan_path.write_text(
            json.dumps(build_screenshot_plan_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    visual_qa_report_path = root / "content" / "visual_qa_report.json"
    if not visual_qa_report_path.exists():
        visual_qa_report_path.write_text(
            json.dumps(build_visual_qa_report_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    acceptance_report_path = root / "content" / "acceptance_report.json"
    if not acceptance_report_path.exists():
        acceptance_report_path.write_text(
            json.dumps(build_acceptance_report_data(topic), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


PROJECT_RUNTIME_COMMON = dedent(
    r"""
    from __future__ import annotations

    import json
    import os
    import re
    from pathlib import Path


    AUDIO_EXTENSIONS = (".wav", ".mp3")
    SPOKEN_TEXT_KEYS = ("tts_text", "spoken_text", "voice_spoken", "narration_text", "voice")


    def load_project(root: Path) -> tuple[dict, list[dict]]:
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8-sig"))
        return project, segments


    def target_language(project: dict) -> str:
        return str(project.get("voice_language") or "zh-CN")


    def is_chinese_target(project: dict) -> bool:
        return target_language(project).lower().startswith("zh")


    def local_qwen_config(project: dict) -> dict:
        return ((project.get("voice_settings") or {}).get("local_qwen") or {})


    def local_qwen_ready(project: dict) -> bool:
        cfg = local_qwen_config(project)
        if not bool(cfg.get("enabled", False)):
            return False
        python_executable = Path(str(cfg.get("python_executable") or ""))
        model_dir = Path(str(cfg.get("model_dir") or ""))
        return python_executable.exists() and model_dir.exists()


    def narration_mode(project: dict) -> str:
        workflow = project.get("voice_workflow", {}) or {}
        return str(workflow.get("narration_mode") or "master-track-preferred")


    def audio_candidates(root: Path, seg_id: str) -> list[Path]:
        return [root / "audio" / f"{seg_id}{ext}" for ext in AUDIO_EXTENSIONS]


    def find_existing_audio(root: Path, seg_id: str) -> Path | None:
        for candidate in audio_candidates(root, seg_id):
            if candidate.exists():
                return candidate
        return None


    def find_existing_master_audio(root: Path) -> Path | None:
        for name in ("master.wav", "master.mp3"):
            candidate = root / "audio" / name
            if candidate.exists():
                return candidate
        return None


    def normalize_narration_text(text: str, language: str = "zh-CN") -> str:
        cleaned = str(text or "")
        if not cleaned:
            return ""
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = cleaned.replace("\u3000", " ").replace("\xa0", " ")
        cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", cleaned)
        cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"(?m)^\s{0,3}(?:[-*•]|\d+\.)\s+", "", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"\.\.\.+", "……", cleaned)
        cleaned = re.sub(r"([。！？；，、,.!?;:])\1+", r"\1", cleaned)
        cleaned = re.sub(r"\s+\n", "\n", cleaned)
        cleaned = re.sub(r"\n\s+", "\n", cleaned)
        if language.lower().startswith("zh"):
            cleaned = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", cleaned)
            cleaned = re.sub(r"\s+(?=[，。！？；：、])", "", cleaned)
            cleaned = re.sub(r"(?<=[（《“])\s+", "", cleaned)
        return cleaned.strip()


    def segment_narration_text(segment: dict, project: dict | None = None) -> str:
        for key in SPOKEN_TEXT_KEYS:
            value = str(segment.get(key) or "").strip()
            if value:
                language = target_language(project or {}) if project else "zh-CN"
                return normalize_narration_text(value, language=language)
        return ""


    def join_voice_blocks(segments: list[dict], project: dict | None = None) -> str:
        parts = [segment_narration_text(item, project) for item in segments]
        return "\n\n".join(part for part in parts if part)
    """
).strip() + "\n"


GENERATE_TTS_PUBLISH = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import asyncio
    import subprocess
    import sys
    from pathlib import Path

    from video_pipeline_common import (
        load_project,
        local_qwen_ready,
    )


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument(
            "--provider",
            default="auto",
            choices=["auto", "local-qwen", "edge-preview"],
        )
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    def choose_provider(root: Path, project: dict, segments: list[dict], requested: str) -> str:
        if requested != "auto":
            return requested
        if local_qwen_ready(project):
            return "local-qwen"
        return "edge-preview"


    def run_local_qwen(root: Path, force: bool) -> None:
        cmd = [sys.executable, str(root / "scripts" / "generate_tts_local_qwen.py"), "--root", str(root)]
        if force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)


    def run_edge_preview(root: Path, force: bool) -> None:
        cmd = [sys.executable, str(root / "scripts" / "generate_tts_edge.py"), "--root", str(root)]
        if force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project, segments = load_project(root)
        provider = choose_provider(root, project, segments, args.provider)

        if provider == "local-qwen":
            print("[tts] provider=local-qwen")
            run_local_qwen(root, args.force)
            return

        print("[tts] provider=edge-preview")
        run_edge_preview(root, args.force)


    if __name__ == "__main__":
        asyncio.run(main())
    """
).strip() + "\n"


PREPARE_WEB_TTS_MANIFEST = dedent(
    r"""
    from __future__ import annotations

    import argparse
    from pathlib import Path

    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        return parser.parse_args()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        raise RuntimeError(
            "prepare_web_tts_manifest.py has been removed from video-maker. "
            "This skill now uses local Qwen 12Hz or Edge preview only."
        )


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


GENERATE_TTS_EDGE = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import asyncio
    from pathlib import Path

    import edge_tts

    from video_pipeline_common import join_voice_blocks, load_project


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    async def synthesize(text: str, out_path: Path, voice: str, rate: str, pitch: str) -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project, segments = load_project(root)
        edge_cfg = ((project.get("voice_settings") or {}).get("edge_preview") or {})
        voice = str(edge_cfg.get("voice") or "zh-CN-XiaoxiaoNeural")
        rate = str(edge_cfg.get("rate") or "+2%")
        pitch = str(edge_cfg.get("pitch") or "+0Hz")

        out_dir = root / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / "master.mp3"
        if out_path.exists() and not args.force:
            print(f"[skip] {out_path}")
            return
        text = join_voice_blocks(segments, project)
        await synthesize(text, out_path, voice, rate, pitch)
        print(f"[ok] {out_path}")


    if __name__ == "__main__":
        asyncio.run(main())
    """
).strip() + "\n"


QUICK_CHECK = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import re
    import shutil
    import subprocess
    import sys
    import wave
    from pathlib import Path

    from video_pipeline_common import (
        find_existing_master_audio,
        load_project,
    )


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--strict", action="store_true")
        return parser.parse_args()


    def narration_text(item: dict) -> str:
        for key in ("tts_text", "spoken_text", "voice_spoken", "narration_text", "voice"):
            value = str(item.get(key) or "").strip()
            if value:
                return value
        return ""


    def cjk_count(text: str) -> int:
        return len(re.findall(r"[\u3400-\u9fff]", text))


    def audio_duration_sec(path: Path) -> float | None:
        if path.suffix.lower() == ".wav":
            try:
                with wave.open(str(path), "rb") as audio:
                    frames = audio.getnframes()
                    rate = audio.getframerate()
                return frames / float(rate or 1)
            except wave.Error:
                return None

        try:
            from mutagen.mp3 import MP3  # type: ignore

            return float(MP3(str(path)).info.length)
        except Exception:
            pass

        ffmpeg = shutil.which("ffmpeg") or r"C:\Program Files\File Converter\ffmpeg.exe"
        if Path(ffmpeg).exists() or shutil.which("ffmpeg"):
            proc = subprocess.run(
                [ffmpeg, "-i", str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
            )
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stdout)
            if match:
                hours, minutes, seconds = match.groups()
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return None


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        hard_failures: list[str] = []
        warnings: list[str] = []

        project_path = root / "content" / "project.json"
        problem_path = root / "content" / "problem_contract.json"
        audience_path = root / "content" / "audience_contract.json"
        opening_path = root / "content" / "opening_contract.json"
        meaning_path = root / "content" / "meaning_contract.json"
        evidence_path = root / "content" / "evidence_map.json"
        script_draft_path = root / "content" / "script_draft.json"
        narration_path = root / "content" / "narration_polish.json"
        segments_path = root / "content" / "segments.json"
        notes_path = root / "publish_notes.md"
        outline_path = root / "content" / "outline_plan.json"
        depth_path = root / "content" / "depth_contract.json"
        detail_path = root / "content" / "detail_weave.json"
        style_contract_path = root / "content" / "style_contract.json"
        shot_intents_path = root / "content" / "shot_intents.json"
        visual_asset_plan_path = root / "content" / "visual_asset_plan.json"
        screenshot_plan_path = root / "content" / "screenshot_plan.json"
        visual_qa_report_path = root / "content" / "visual_qa_report.json"
        acceptance_report_path = root / "content" / "acceptance_report.json"
        remotion_dir = root / "remotion"
        remotion_entry_path = remotion_dir / "src" / "index.ts"
        remotion_video_path = remotion_dir / "src" / "Video.tsx"
        remotion_package_path = remotion_dir / "package.json"

        for required in [
            project_path,
            problem_path,
            audience_path,
            opening_path,
            meaning_path,
            evidence_path,
            script_draft_path,
            narration_path,
            segments_path,
            notes_path,
            outline_path,
            depth_path,
            detail_path,
            style_contract_path,
            shot_intents_path,
            visual_asset_plan_path,
            screenshot_plan_path,
            visual_qa_report_path,
            acceptance_report_path,
            remotion_entry_path,
            remotion_video_path,
            remotion_package_path,
        ]:
            if not required.exists():
                hard_failures.append(f"missing required file: {required}")

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        project, segments = load_project(root)
        shot_intents = json.loads(shot_intents_path.read_text(encoding="utf-8-sig"))
        style_contract = json.loads(style_contract_path.read_text(encoding="utf-8-sig"))

        if not segments:
            hard_failures.append("segments.json is empty; generate a beat-driven scene list before rendering")
        if str(style_contract.get("prompt_mode") or "") != "style-not-template":
            warnings.append("style_contract.json 没有明确声明 style-not-template；可能会重新滑回固定模板思路。")

        provider = str(project.get("voice_provider", "local-qwen"))
        voice_language = str(project.get("voice_language", "zh-CN")).lower()
        workflow = project.get("voice_workflow", {}) or {}
        voice_profile = project.get("voice_profile", {}) or {}
        local_qwen = ((project.get("voice_settings") or {}).get("local_qwen") or {})
        local_qwen_enabled = bool(local_qwen.get("enabled", False))
        local_qwen_python = Path(str(local_qwen.get("python_executable") or "")) if local_qwen else Path()
        local_qwen_model_dir = Path(str(local_qwen.get("model_dir") or "")) if local_qwen else Path()
        local_qwen_ready = local_qwen_enabled and local_qwen_python.exists() and local_qwen_model_dir.exists()

        if provider in {"preview-edge-tts", "edge-tts"}:
            warnings.append("voice_provider 仍是预览级 TTS，适合粗剪，不建议直接发布。")
        elif provider == "local-qwen" and local_qwen_enabled and not local_qwen_ready:
            warnings.append("voice_settings.local_qwen 已启用，但本地 Qwen 12Hz Python 或 model_dir 路径不存在。")

        if voice_language.startswith("zh") and workflow.get("accent_review_required", True):
            if provider != "local-qwen" and str(voice_profile.get("review_status", "unreviewed")).lower() != "passed":
                warnings.append("中文终版配音尚未通过听感验收；先确认没有外国人口音或明显翻译腔。")

        voice_locale = str(voice_profile.get("locale", "")).lower()
        if voice_language.startswith("zh") and voice_locale and not voice_locale.startswith("zh"):
            warnings.append(f"当前 voice_profile.locale={voice_locale}；中文旁白存在外国人口音风险。")

        render_pipeline = project.get("render_pipeline", {}) or {}
        if str(render_pipeline.get("engine") or "").lower() != "remotion":
            hard_failures.append("render_pipeline.engine must be remotion; legacy slide/html assembly is no longer the production path.")

        for item in segments:
            if item.get("type") == "slide":
                warnings.append(f"segment {item.get('id')} still uses legacy type=slide; treat it as a Remotion scene before final render.")
            if item.get("type") == "demo":
                video_path = root / item["video"]
                if not video_path.exists():
                    placeholder_html = item.get("placeholder_html") or item.get("html")
                    if placeholder_html and (root / placeholder_html).exists():
                        warnings.append(f"segment {item.get('id')} demo 录像缺失；Remotion 可先用占位场景信息顶上，但不要把 HTML 当终版渲染路径。")
                    else:
                        hard_failures.append(f"missing demo video and placeholder: {video_path}")
            if "待由" in str(item.get("voice") or ""):
                warnings.append(f"segment {item.get('id')} 仍是占位旁白；先完成 content compile 再出片。")
            if not str(item.get("shot_role") or "").strip():
                hard_failures.append(f"segment {item.get('id')} 缺少 shot_role；scene compiler 必须按镜头职责而不是页面模板工作。")
            if not isinstance(item.get("scene_prompt_basis"), dict):
                hard_failures.append(f"segment {item.get('id')} 缺少 scene_prompt_basis；无法追溯 style contract -> shot intent -> scene prompt 链路。")
            elif str((item.get("scene_prompt_basis") or {}).get("style_contract") or "") != "content/style_contract.json":
                warnings.append(f"segment {item.get('id')} 的 style_contract 引用异常；检查 scene_prompt_basis。")

        intent_beats = shot_intents.get("beats")
        if not isinstance(intent_beats, list) or not intent_beats:
            hard_failures.append("shot_intents.json 为空；coordinator 需要先把 beat 职责路由给 visual/content owner 编译成 shot intent。")
        elif len(intent_beats) != len(segments):
            warnings.append("shot_intents.json 与 segments.json 数量不一致；可能存在未对齐的镜头职责。")

        master_audio = find_existing_master_audio(root)
        if workflow.get("narration_mode") == "master-track-preferred" and not master_audio:
            warnings.append("当前项目要求整段 master-track，但还没有生成 master audio。")
        elif master_audio:
            duration = audio_duration_sec(master_audio)
            total_cjk = cjk_count("\n".join(narration_text(item) for item in segments))
            target_cpm = int(local_qwen.get("target_cjk_chars_per_minute") or 260)
            min_cpm = int(local_qwen.get("acceptable_cjk_chars_per_minute_min") or 240)
            max_cpm = int(local_qwen.get("acceptable_cjk_chars_per_minute_max") or 285)
            if duration and total_cjk:
                actual_cpm = total_cjk / (duration / 60.0)
                if actual_cpm < min_cpm or actual_cpm > max_cpm:
                    warnings.append(
                        f"master audio 语速偏离参考：约 {actual_cpm:.0f} 中文字/分钟，目标 {target_cpm}，可接受区间 {min_cpm}-{max_cpm}；若内容、中文听感、视觉 QA 和发布资产都通过，可直接发布。"
                    )
            full_review_status = str(voice_profile.get("full_audio_review_status") or "unreviewed").lower()
            if voice_language.startswith("zh") and full_review_status != "passed":
                warnings.append(
                    "中文终版必须完整听完 master 音频并确认全程不是乱码/火星语/外语/无意义音节、语速不过慢；voice_profile.full_audio_review_status 仍未 passed。"
                )

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        for item in warnings:
            print(f"[WARN] {item}")

        print("[OK] project structure looks usable")
        if warnings and args.strict:
            sys.exit(2)


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


def merge_project_json(path: Path, provider: str) -> None:
    project = json.loads(path.read_text(encoding="utf-8-sig"))
    project = apply_project_defaults(project, voice_provider=provider)
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    project_path = root / "content" / "project.json"
    scripts_dir = root / "scripts"

    if not project_path.exists():
        raise FileNotFoundError(f"Missing project.json at {project_path}")

    merge_project_json(project_path, args.voice_provider)
    project = json.loads(project_path.read_text(encoding="utf-8-sig"))
    sync_remotion_foundation(root)
    sync_content_artifacts(root)
    patch_segments_json(root)
    patch_publish_notes(root / "publish_notes.md")
    sync_publish_assets(root, str(project.get("topic") or root.name))

    write_text(scripts_dir / "video_pipeline_common.py", PROJECT_RUNTIME_COMMON)
    write_text(scripts_dir / "generate_tts_publish.py", GENERATE_TTS_PUBLISH)
    write_text(scripts_dir / "prepare_publish_job.py", PREPARE_PUBLISH_JOB)
    write_text(scripts_dir / "record_voice_profile.py", RECORD_VOICE_PROFILE)
    write_text(scripts_dir / "generate_tts_edge.py", GENERATE_TTS_EDGE)
    write_text(scripts_dir / "generate_tts_local_qwen.py", GENERATE_TTS_LOCAL_QWEN)
    write_text(scripts_dir / "prepare_remotion_props.py", PREPARE_REMOTION_PROPS)
    write_text(scripts_dir / "render_remotion.ps1", RENDER_REMOTION)
    write_text(scripts_dir / "render_all.ps1", RENDER_ALL)
    write_text(scripts_dir / "check_voice_env.ps1", CHECK_VOICE_ENV)
    write_text(scripts_dir / "quick_check.py", QUICK_CHECK)
    remove_if_exists(scripts_dir / "prepare_web_tts_manifest.py")
    remove_if_exists(scripts_dir / "assemble_video.py")
    remove_if_exists(scripts_dir / "render_slides.ps1")

    print(f"[ok] upgraded project at {root}")


if __name__ == "__main__":
    main()

