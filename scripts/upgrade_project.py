from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent

from project_defaults import (
    apply_project_defaults,
    build_depth_contract_data,
    build_detail_weave_data,
    build_narration_polish_data,
    build_outline_plan_data,
    build_shot_intents_data,
    build_style_contract_data,
    default_shot_role_for_index,
)


LOCAL_QWEN_BASE_INSTRUCT = (
    "请用年轻的中文女声做科技讲解。整体气质沉稳、大方、清晰、友好，带一点自然可爱的亲和感。"
    "全程保持同一个人设、同一种情绪基线和同一套说话习惯。"
    "语速保持中速偏稳，不忽快忽慢，不忽然兴奋，也不要突然压低情绪。"
    "句间停顿自然，呼吸轻、短、克制，重点词只做轻微强调，不要夸张，不要急躁，不要播音腔。"
    "不要幼态，不要撒娇，不要夹子音。像二十五岁左右、表达很稳的女生，在冷静而友好地讲解工具、工作流和 AI 概念。"
)

STYLE_FOUNDATION_DIR = Path(__file__).resolve().parents[1] / "references" / "quiet-glass-lab"

LEGACY_MUST_ANSWER = [
    "这是什么",
    "为什么现在值得讲",
    "最容易混淆的点是什么",
    "最后应该怎么判断或行动",
]

LEGACY_SCENE_MARKERS = [
    "Scene placeholder",
    "先锁内容，再决定这一页长什么样",
    "prompt-driven layout",
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


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        notes = (root / "publish_notes.md").read_text(encoding="utf-8-sig") if (root / "publish_notes.md").exists() else ""
        video_name = project.get("output_name") or f"{root.name}.mp4"
        job = {
            "topic": project.get("topic", root.name),
            "video_path": str((root / video_name).resolve()),
            "notes_path": str((root / "publish_notes.md").resolve()),
            "publish_notes_markdown": notes,
            "style": project.get("visual_style", "quiet-glass-lab"),
            "voice_provider": project.get("voice_provider", "local-qwen"),
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
            subprocess.run(cmd, check=True)
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


ASSEMBLE_VIDEO = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import re
    import shutil
    import subprocess
    from pathlib import Path


    AUDIO_EXTENSIONS = (".wav", ".mp3")


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--fps", type=int, default=30)
        return parser.parse_args()


    def find_ffmpeg() -> str:
        candidates = [
            r"C:\Program Files\File Converter\ffmpeg.exe",
            shutil.which("ffmpeg"),
            r"C:\Program Files\Tecplot\Tecplot 360 EX 2017 R2\bin\ffmpeg.exe",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return candidate
        raise FileNotFoundError("No ffmpeg executable found")


    def media_duration(ffmpeg: str, path: Path) -> float:
        proc = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True, check=False)
        text = proc.stderr + proc.stdout
        match = re.search(r"Duration:\s+(\d+):(\d+):(\d+(?:\.\d+)?)", text)
        if not match:
            raise RuntimeError(f"Could not read duration for {path}")
        hh, mm, ss = match.groups()
        return int(hh) * 3600 + int(mm) * 60 + float(ss)


    def run(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True)


    def find_master_audio(root: Path) -> Path | None:
        for name in ("master.wav", "master.mp3"):
            candidate = root / "audio" / name
            if candidate.exists():
                return candidate
        return None


    def text_weight(text: str) -> float:
        cleaned = text.strip()
        if not cleaned:
            return 1.0
        punctuation_bonus = sum(cleaned.count(ch) for ch in "，。！？；：,.!?;:")
        return max(len(cleaned) + punctuation_bonus * 2, 1)


    def scene_duration_plan(root: Path, ffmpeg: str, segments: list[dict], total_duration: float) -> dict[str, float]:
        explicit: dict[str, float] = {}
        weighted: list[tuple[str, float]] = []

        for item in segments:
            seg_id = item["id"]
            duration_sec = item.get("duration_sec")
            if duration_sec:
                explicit[seg_id] = float(duration_sec)
                continue
            spoken_text = (
                item.get("tts_text")
                or item.get("spoken_text")
                or item.get("voice_spoken")
                or item.get("narration_text")
                or item.get("voice")
                or ""
            )
            weighted.append((seg_id, float(item.get("duration_weight") or text_weight(str(spoken_text)))))

        remaining = max(total_duration - sum(explicit.values()), 0.0)
        if not weighted:
            return explicit
        total_weight = sum(weight for _, weight in weighted) or 1.0
        for seg_id, weight in weighted:
            explicit[seg_id] = remaining * (weight / total_weight)
        return explicit


    def build_slide_clip(ffmpeg: str, image: Path, out_clip: Path, duration: float, fps: int, with_audio: Path | None = None) -> None:
        fade_out = max(duration - 0.45, 0)
        vf = (
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#020302,"
            f"fade=t=in:st=0:d=0.35,fade=t=out:st={fade_out:.2f}:d=0.35"
        )
        cmd = [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(fps),
            "-i",
            str(image),
        ]
        if with_audio:
            cmd.extend(["-i", str(with_audio)])
        cmd.extend(
            [
                "-vf",
                vf,
                "-t",
                f"{duration:.3f}",
                "-r",
                str(fps),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
            ]
        )
        if with_audio:
            cmd.extend(["-c:a", "aac", "-shortest"])
        else:
            cmd.append("-an")
        cmd.append(str(out_clip))
        run(cmd)


    def build_demo_clip(ffmpeg: str, source: Path, out_clip: Path, duration: float, fps: int, with_audio: Path | None = None) -> None:
        if source.suffix.lower() == ".png":
            build_slide_clip(ffmpeg, source, out_clip, duration, fps, with_audio)
            return
        source_duration = media_duration(ffmpeg, source)
        ratio = duration / source_duration if source_duration else 1.0
        vf = (
            f"setpts={ratio:.6f}*PTS,"
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        cmd = [ffmpeg, "-y", "-i", str(source)]
        if with_audio:
            cmd.extend(["-i", str(with_audio)])
        cmd.extend(
            [
                "-vf",
                vf,
                "-r",
                str(fps),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-t",
                f"{duration:.3f}",
            ]
        )
        if with_audio:
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-shortest"])
        else:
            cmd.extend(["-an"])
        cmd.append(str(out_clip))
        run(cmd)


    def placeholder_source(root: Path, item: dict) -> Path:
        placeholder_html = item.get("placeholder_html") or item.get("html")
        if not placeholder_html:
            raise FileNotFoundError(f"No placeholder html for {item['id']}")
        image = root / "slide_png" / f"{Path(placeholder_html).stem}.png"
        if not image.exists():
            raise FileNotFoundError(f"Missing placeholder image: {image}")
        return image


    def concat_video(ffmpeg: str, concat_file: Path, out_path: Path) -> None:
        run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(out_path)])


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        ffmpeg = find_ffmpeg()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8-sig"))

        clips_dir = root / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        concat_file = clips_dir / "concat.txt"
        concat_lines: list[str] = []
        final_name = project.get("output_name") or (root.name + ".mp4")
        final_path = root / final_name

        master_audio = find_master_audio(root)
        if master_audio:
            durations = scene_duration_plan(root, ffmpeg, segments, media_duration(ffmpeg, master_audio))
            for item in segments:
                seg_id = item["id"]
                duration = max(durations.get(seg_id, 0.1), 0.1)
                out_clip = clips_dir / f"{seg_id}.mp4"
                if item.get("type") == "demo":
                    demo = root / item["video"]
                    source = demo if demo.exists() else placeholder_source(root, item)
                    build_demo_clip(ffmpeg, source, out_clip, duration, args.fps)
                else:
                    image = root / "slide_png" / f"{Path(item['html']).stem}.png"
                    if not image.exists():
                        raise FileNotFoundError(f"Missing slide image: {image}")
                    build_slide_clip(ffmpeg, image, out_clip, duration, args.fps)
                concat_lines.append(f"file '{out_clip.as_posix()}'")

            concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
            video_only = clips_dir / "_video_only.mp4"
            concat_video(ffmpeg, concat_file, video_only)
            run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(video_only),
                    "-i",
                    str(master_audio),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(final_path),
                ]
            )
            print(f"[video] {final_path}")
            return
        raise FileNotFoundError("Missing master audio: audio/master.wav or audio/master.mp3")


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
    & (Join-Path $Root "scripts\render_slides.ps1") -Root $Root
    & $python (Join-Path $Root "scripts\assemble_video.py") --root $Root
    """
).strip() + "\n"


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
    import sys
    from pathlib import Path


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--strict", action="store_true")
        return parser.parse_args()


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
                warnings.append(f"segment {item.get('id')} 仍是占位旁白，先完成 narration-polisher + chief-editor 的口播编译再出片")

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


RENDER_SLIDES = dedent(
    r"""
    param(
      [string]$Root,
      [switch]$Force
    )

    $ErrorActionPreference = "Stop"

    if (-not $Root) {
      $Root = Split-Path -Parent $PSScriptRoot
    }

    Add-Type -AssemblyName System.Drawing

    function Save-CroppedSlide {
      param(
        [string]$Source,
        [string]$Target,
        [int]$Width = 1600,
        [int]$Height = 900
      )

      $image = $null
      $bitmap = $null
      $graphics = $null
      try {
        $image = [System.Drawing.Image]::FromFile($Source)
        if ($image.Width -lt $Width -or $image.Height -lt $Height) {
          throw "Rendered image too small: $Source ($($image.Width)x$($image.Height))"
        }
        $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.DrawImage(
          $image,
          (New-Object System.Drawing.Rectangle 0, 0, $Width, $Height),
          0,
          0,
          $Width,
          $Height,
          [System.Drawing.GraphicsUnit]::Pixel
        )
        $bitmap.Save($Target, [System.Drawing.Imaging.ImageFormat]::Png)
      } finally {
        if ($graphics) { $graphics.Dispose() }
        if ($bitmap) { $bitmap.Dispose() }
        if ($image) { $image.Dispose() }
      }
    }

    function Test-WhiteFooter {
      param([string]$Path)
      $bitmap = $null
      try {
        $bitmap = [System.Drawing.Bitmap]::FromFile($Path)
        $samples = 0
        $white = 0
        for ($y = [Math]::Max(0, $bitmap.Height - 36); $y -lt $bitmap.Height; $y += 4) {
          for ($x = 0; $x -lt $bitmap.Width; $x += 24) {
            $pixel = $bitmap.GetPixel($x, $y)
            $brightness = ($pixel.R + $pixel.G + $pixel.B) / 3
            if ($brightness -ge 250) {
              $white++
            }
            $samples++
          }
        }
        return ($samples -gt 0) -and (($white / [double]$samples) -ge 0.98)
      } finally {
        if ($bitmap) { $bitmap.Dispose() }
      }
    }

    function Test-WhiteRightStrip {
      param(
        [string]$Path,
        [int]$StripWidth = 28
      )
      $bitmap = $null
      try {
        $bitmap = [System.Drawing.Bitmap]::FromFile($Path)
        $samples = 0
        $white = 0
        $startX = [Math]::Max(0, $bitmap.Width - $StripWidth)
        for ($x = $startX; $x -lt $bitmap.Width; $x += 3) {
          for ($y = 0; $y -lt $bitmap.Height; $y += 12) {
            $pixel = $bitmap.GetPixel($x, $y)
            $brightness = ($pixel.R + $pixel.G + $pixel.B) / 3
            if ($brightness -ge 248) {
              $white++
            }
            $samples++
          }
        }
        return ($samples -gt 0) -and (($white / [double]$samples) -ge 0.985)
      } finally {
        if ($bitmap) { $bitmap.Dispose() }
      }
    }

    $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (-not (Test-Path $edge)) {
      throw "Edge not found at $edge"
    }

    $slidesDir = Join-Path $Root "slides"
    $outDir = Join-Path $Root "slide_png"
    $captureWidths = @(1632, 1728, 1792, 1920)
    New-Item -ItemType Directory -Force $outDir | Out-Null

    $files = Get-ChildItem $slidesDir -Filter "*.html" | Sort-Object Name
    foreach ($file in $files) {
      $png = Join-Path $outDir ($file.BaseName + ".png")
      $tmp = Join-Path $outDir ($file.BaseName + ".raw.png")
      if ((Test-Path $png) -and -not $Force) {
        continue
      }

      if (Test-Path $tmp) {
        Remove-Item $tmp -Force
      }

      $uri = "file:///" + ($file.FullName -replace "\\", "/")
      Write-Output "[slide] $($file.Name) -> $png"
      $rendered = $false
      foreach ($captureWidth in $captureWidths) {
        if (Test-Path $tmp) {
          Remove-Item $tmp -Force
        }
        if (Test-Path $png) {
          Remove-Item $png -Force
        }

        & $edge `
          --headless=new `
          --disable-gpu `
          --hide-scrollbars `
          --run-all-compositor-stages-before-draw `
          --virtual-time-budget=3000 `
          --force-device-scale-factor=1 `
          --window-size=$captureWidth,995 `
          --screenshot="$tmp" `
          "$uri" | Out-Null

        Save-CroppedSlide -Source $tmp -Target $png
        Remove-Item $tmp -Force

        $hasWhiteFooter = Test-WhiteFooter -Path $png
        $hasWhiteRightStrip = Test-WhiteRightStrip -Path $png
        if (-not $hasWhiteFooter -and -not $hasWhiteRightStrip) {
          $rendered = $true
          break
        }

        Write-Warning "retrying slide render with wider viewport: $($file.Name) width=$captureWidth footer=$hasWhiteFooter rightStrip=$hasWhiteRightStrip"
      }

      if (-not $rendered) {
        throw "Rendered slide still contains browser white region after retries: $png"
      }
    }
    """
).strip() + "\n"


PUBLISH_NOTES_MARKER = (
    "- 内容研究默认走 outline -> depth -> detail -> narration polish 四段串行\n"
    "- narration-polisher 只修逻辑、语法、翻译腔和口播自然度，不改主线判断\n"
    "- scene 编译默认走 style contract -> shot intent -> scene prompt，不直接套模板\n"
    "- 风格只锁黑绿 + iOS 18-inspired frosted glass 的材质逻辑与层级，不锁固定模块或固定布局\n"
    "- slides/base.css 与脚手架 scene HTML 只保留渲染外壳，不内置视觉模板\n"
    "- 配音默认走本地 Qwen 12Hz 整段单次合成；不行时优先改脚本或退回预览，不再默认分段拼接\n"
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


def read_style_foundation_asset(name: str) -> str:
    return (STYLE_FOUNDATION_DIR / name).read_text(encoding="utf-8-sig")


def neutral_scene_html(topic: str, beat_id: str) -> str:
    return dedent(
        f"""
        <!doctype html>
        <html lang="zh-CN">
        <head>
          <meta charset="utf-8">
          <link rel="stylesheet" href="base.css">
          <title>{topic}</title>
        </head>
        <body>
          <main class="scene-root" data-scene-id="{beat_id}" data-topic="{topic}"></main>
        </body>
        </html>
        """
    ).strip() + "\n"


def looks_like_legacy_base_css(content: str) -> bool:
    markers = ["--accent: #d0f810", ".window {", ".glass-panel", ".pill-row"]
    return all(marker in content for marker in markers)


def looks_like_legacy_scene_html(content: str) -> bool:
    return any(marker in content for marker in LEGACY_SCENE_MARKERS)


def sync_visual_foundation(root: Path, topic: str) -> None:
    slides_dir = root / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    base_css_path = slides_dir / "base.css"
    if not base_css_path.exists():
        write_text(base_css_path, read_style_foundation_asset("base.css"))
    else:
        current_base_css = base_css_path.read_text(encoding="utf-8-sig")
        if looks_like_legacy_base_css(current_base_css):
            write_text(base_css_path, read_style_foundation_asset("base.css"))

    for html_path in sorted(slides_dir.glob("*.html")):
        content = html_path.read_text(encoding="utf-8-sig")
        if not looks_like_legacy_scene_html(content):
            continue
        beat_id = html_path.stem
        write_text(html_path, neutral_scene_html(topic, beat_id))


def default_scene_prompt_basis(beat_id: str) -> dict:
    return {
        "style_contract": "content/style_contract.json",
        "shot_intent": f"content/shot_intents.json#{beat_id}",
        "content_contracts": [
            f"content/outline_plan.json#{beat_id}",
            f"content/depth_contract.json#{beat_id}",
            f"content/detail_weave.json#{beat_id}",
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
            if not isinstance(content_contracts, list) or len(content_contracts) < 3:
                basis["content_contracts"] = default_scene_prompt_basis(beat_id)["content_contracts"]
                changed = True
    if changed:
        path.write_text(json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_depth_beat(outline_beat: dict) -> dict:
    beat_id = str(outline_beat.get("beat_id") or "scene-001")
    provisional_claim = str(outline_beat.get("provisional_claim") or "待由 outline-researcher 提供")
    return {
        "beat_id": beat_id,
        "provisional_claim": provisional_claim,
        "resolved_claim": "待由 depth-builder 锁定",
        "claim_job": "define",
        "beat_progression": "待定义：这一拍相对前后内容推进了什么。",
        "context_role": str(outline_beat.get("context_role") or "待定义：这一拍与前后内容的关系。"),
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


def make_narration_polish_beat(detail_beat: dict) -> dict:
    beat_id = str(detail_beat.get("beat_id") or "scene-001")
    return {
        "beat_id": beat_id,
        "spoken_goal": "待由 narration-polisher 把这一拍改写成自然、可口播的中文旁白。",
        "draft_narration": "待由 narration-polisher 产出 2-5 句旁白，优先修正逻辑连接、语法和翻译腔。",
        "logic_guardrail": "不要改 resolved_claim，只修正因果链、主语指代、句子连接和人机味。",
        "grammar_watchouts": [],
        "humanity_adjustments": ["减少翻译腔", "避免空泛口号", "避免过度书面语"],
        "locked_terms": [],
    }


def sync_content_artifacts(root: Path) -> None:
    project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8-sig"))
    topic = str(project.get("topic") or root.name)

    outline_path = root / "content" / "outline_plan.json"
    outline_changed = not outline_path.exists()
    outline = build_outline_plan_data(topic) if outline_changed else json.loads(outline_path.read_text(encoding="utf-8-sig"))
    outline.setdefault("version", "v3")
    outline.setdefault("topic", topic)
    outline.setdefault("outline_status", "needs_outline")
    outline.setdefault("next_owner", "outline-researcher")
    if "episode_scope" not in outline:
        outline["episode_scope"] = outline.pop("higher_order_takeaway", "待定义：这期需要覆盖到什么范围、边界或重点。")
        outline_changed = True
    else:
        outline.pop("higher_order_takeaway", None)
    outline.setdefault("story_shape", "to-be-decided")
    outline.setdefault("pacing_strategy", "to-be-decided")
    coverage_contract = outline.setdefault("coverage_contract", {})
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
            beat["provisional_claim"] = beat.pop("key_claim", "待由 outline-researcher 提供")
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

    depth_path = root / "content" / "depth_contract.json"
    depth_changed = not depth_path.exists()
    depth = build_depth_contract_data(topic) if depth_changed else json.loads(depth_path.read_text(encoding="utf-8-sig"))
    depth.setdefault("version", "v1")
    depth.setdefault("topic", topic)
    depth.setdefault("status", "needs_depth")
    depth.setdefault("next_owner", "depth-builder")
    depth.setdefault("based_on_outline", "content/outline_plan.json")
    episode_depth_goal = depth.setdefault("episode_depth_goal", {})
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
        depth_beat.setdefault("provisional_claim", str(outline_beat.get("provisional_claim") or "待由 outline-researcher 提供"))
        depth_beat.setdefault("resolved_claim", "待由 depth-builder 锁定")
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
    detail.setdefault("next_owner", "detail-filler")
    source_contracts = detail.setdefault("source_contracts", {})
    source_contracts.setdefault("outline_plan", "content/outline_plan.json")
    source_contracts.setdefault("depth_contract", "content/depth_contract.json")
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

    narration_path = root / "content" / "narration_polish.json"
    narration_changed = not narration_path.exists()
    narration_polish = (
        build_narration_polish_data()
        if narration_changed
        else json.loads(narration_path.read_text(encoding="utf-8-sig"))
    )
    narration_polish.setdefault("version", "v1")
    narration_polish.setdefault("status", "needs_narration_polish")
    narration_polish.setdefault("next_owner", "narration-polisher")
    narration_sources = narration_polish.setdefault("source_contracts", {})
    narration_sources.setdefault("outline_plan", "content/outline_plan.json")
    narration_sources.setdefault("depth_contract", "content/depth_contract.json")
    narration_sources.setdefault("detail_weave", "content/detail_weave.json")
    narration_constraints = narration_polish.setdefault("constraints", {})
    narration_constraints.setdefault("beat_order_locked", True)
    narration_constraints.setdefault("resolved_claim_locked", True)
    narration_constraints.setdefault("no_new_facts_without_source", True)
    narration_constraints.setdefault("spoken_chinese_required", True)
    narration_beats = narration_polish.setdefault("beats", [])
    if not narration_beats or len(narration_beats) != len(detail["beats"]):
        narration_polish["beats"] = [make_narration_polish_beat(beat) for beat in detail["beats"]]
        narration_beats = narration_polish["beats"]
        narration_changed = True
    for detail_beat, narration_beat in zip(detail["beats"], narration_beats, strict=False):
        beat_id = str(detail_beat.get("beat_id") or "scene-001")
        narration_beat.setdefault("beat_id", beat_id)
        narration_beat.setdefault("spoken_goal", "待由 narration-polisher 把这一拍改写成自然、可口播的中文旁白。")
        narration_beat.setdefault("draft_narration", "待由 narration-polisher 产出 2-5 句旁白，优先修正逻辑连接、语法和翻译腔。")
        narration_beat.setdefault("logic_guardrail", "不要改 resolved_claim，只修正因果链、主语指代、句子连接和人机味。")
        narration_beat.setdefault("grammar_watchouts", [])
        narration_beat.setdefault("humanity_adjustments", ["减少翻译腔", "避免空泛口号", "避免过度书面语"])
        narration_beat.setdefault("locked_terms", [])
    narration_polish.setdefault(
        "global_avoid",
        ["营销腔", "为了显得聪明而堆术语", "一句里塞太多转折", "像模型解释模型一样的自我指涉"],
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
        "next_owner": "chief-editor",
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
                    "narrative_job": str(outline_beat.get("purpose") or "待由 chief-editor 补齐这一拍的叙事职责。"),
                    "visual_goal": str(outline_beat.get("visual_focus") or "待定义这一拍的主视觉焦点。"),
                    "must_show": ["本页唯一关键结论"],
                    "must_avoid": ["固定模板复用", "无关 glass 摆件"],
                    "chrome_level": "minimal",
                    "motion_source": "from-primary-focus",
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
            "narrative_job": str(outline_beat.get("purpose") or "待由 chief-editor 补齐这一拍的叙事职责。"),
            "visual_goal": str(outline_beat.get("visual_focus") or "待定义这一拍的主视觉焦点。"),
            "must_show": ["本页唯一关键结论"],
            "must_avoid": ["固定模板复用", "无关 glass 摆件"],
            "chrome_level": "minimal",
            "motion_source": "from-primary-focus",
            "scene_prompt_stub": "先锁这一拍的主结论，再决定需要哪种构图和少量功能层。",
        }
        for key, value in defaults.items():
            if key not in intent_beat:
                intent_beat[key] = value
                shot_intents_changed = True
    if shot_intents_changed:
        shot_intents_path.write_text(json.dumps(shot_intents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        cmd = ["python", str(root / "scripts" / "generate_tts_local_qwen.py"), "--root", str(root)]
        if force:
            cmd.append("--force")
        subprocess.run(cmd, check=True)


    def run_edge_preview(root: Path, force: bool) -> None:
        cmd = ["python", str(root / "scripts" / "generate_tts_edge.py"), "--root", str(root)]
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
    import sys
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


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        hard_failures: list[str] = []
        warnings: list[str] = []

        project_path = root / "content" / "project.json"
        segments_path = root / "content" / "segments.json"
        notes_path = root / "publish_notes.md"
        outline_path = root / "content" / "outline_plan.json"
        depth_path = root / "content" / "depth_contract.json"
        detail_path = root / "content" / "detail_weave.json"
        style_contract_path = root / "content" / "style_contract.json"
        shot_intents_path = root / "content" / "shot_intents.json"

        for required in [
            project_path,
            segments_path,
            notes_path,
            outline_path,
            depth_path,
            detail_path,
            style_contract_path,
            shot_intents_path,
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
                        warnings.append(f"segment {item.get('id')} demo 录像缺失；render_all 会先用占位场景 {placeholder_html} 顶上。")
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
            hard_failures.append("shot_intents.json 为空；chief-editor 需要先把 beat 职责翻译成 shot intent。")
        elif len(intent_beats) != len(segments):
            warnings.append("shot_intents.json 与 segments.json 数量不一致；可能存在未对齐的镜头职责。")

        if workflow.get("narration_mode") == "master-track-preferred" and not find_existing_master_audio(root):
            warnings.append("当前项目要求整段 master-track，但还没有生成 master audio。")

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
    sync_visual_foundation(root, str(project.get("topic") or root.name))
    sync_content_artifacts(root)
    patch_segments_json(root)
    patch_publish_notes(root / "publish_notes.md")

    write_text(scripts_dir / "video_pipeline_common.py", PROJECT_RUNTIME_COMMON)
    write_text(scripts_dir / "generate_tts_publish.py", GENERATE_TTS_PUBLISH)
    write_text(scripts_dir / "prepare_publish_job.py", PREPARE_PUBLISH_JOB)
    write_text(scripts_dir / "record_voice_profile.py", RECORD_VOICE_PROFILE)
    write_text(scripts_dir / "generate_tts_edge.py", GENERATE_TTS_EDGE)
    write_text(scripts_dir / "generate_tts_local_qwen.py", GENERATE_TTS_LOCAL_QWEN)
    write_text(scripts_dir / "assemble_video.py", ASSEMBLE_VIDEO)
    write_text(scripts_dir / "render_slides.ps1", RENDER_SLIDES)
    write_text(scripts_dir / "render_all.ps1", RENDER_ALL)
    write_text(scripts_dir / "check_voice_env.ps1", CHECK_VOICE_ENV)
    write_text(scripts_dir / "quick_check.py", QUICK_CHECK)
    remove_if_exists(scripts_dir / "prepare_web_tts_manifest.py")

    print(f"[ok] upgraded project at {root}")


if __name__ == "__main__":
    main()

