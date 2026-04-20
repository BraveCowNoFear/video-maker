from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent


OLD_DEFAULT_ELEVENLABS_VOICE_ID = "XB0fDUnXU5powFXDhCwa"
LOCAL_QWEN_BASE_INSTRUCT = (
    "请用年轻的中文女声做科技讲解。整体气质沉稳、大方、清晰、友好，带一点自然可爱的亲和感。"
    "全程保持同一个人设、同一种情绪基线和同一套说话习惯。"
    "语速保持中速偏稳，不忽快忽慢，不忽然兴奋，也不要突然压低情绪。"
    "句间停顿自然，呼吸轻、短、克制，重点词只做轻微强调，不要夸张，不要急躁，不要播音腔。"
    "不要幼态，不要撒娇，不要夹子音。像二十五岁左右、表达很稳的女生，在冷静而友好地讲解工具、工作流和 AI 概念。"
)

DEFAULT_PROJECT_QWEN_INSTRUCT = (
    "请继续沿用完全相同的人设、音色、情绪基线、语速和呼吸风格完成整条视频。"
    "沉稳、大方、亲和，带一点自然可爱感，但不要幼态，不要撒娇，不要夹子音。"
    "中速偏稳，轻呼吸，轻强调，不要播音腔，不要突然兴奋。"
)


GENERATE_TTS_PUBLISH = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import asyncio
    import json
    import os
    import subprocess
    from pathlib import Path
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen


    OLD_DEFAULT_ELEVENLABS_VOICE_ID = "XB0fDUnXU5powFXDhCwa"
    AUDIO_EXTENSIONS = (".wav", ".mp3")


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument(
            "--provider",
            default="auto",
            choices=["auto", "local-qwen", "elevenlabs-api", "elevenlabs-web", "edge-preview"],
        )
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    def load_project(root: Path) -> tuple[dict, list[dict]]:
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8"))
        return project, segments


    def resolve_env(name: str) -> str | None:
        value = os.environ.get(name)
        if value:
            return value
        try:
            import winreg

            for hive, subkey in (
                (winreg.HKEY_CURRENT_USER, r"Environment"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            ):
                try:
                    with winreg.OpenKey(hive, subkey) as key:
                        value, _ = winreg.QueryValueEx(key, name)
                        if value:
                            return str(value)
                except FileNotFoundError:
                    continue
        except Exception:
            return None
        return None


    def target_language(project: dict) -> str:
        return str(project.get("voice_language") or "zh-CN")


    def is_chinese_target(project: dict) -> bool:
        return target_language(project).lower().startswith("zh")


    def approved_api_voice(project: dict) -> bool:
        voice_profile = project.get("voice_profile", {})
        review_status = str(voice_profile.get("review_status") or "").lower()
        mode = str(voice_profile.get("mode") or "").lower()
        voice_locale = str(voice_profile.get("locale") or "").lower()
        source_type = str(voice_profile.get("source_type") or "").lower()
        if review_status != "passed":
            return False
        if mode != "elevenlabs-api":
            return False
        if source_type == "library":
            return False
        if is_chinese_target(project) and voice_locale and not voice_locale.startswith("zh"):
            return False
        voice_id = str((project.get("voice_settings", {}).get("elevenlabs", {}) or {}).get("voice_id") or "")
        if not voice_id or voice_id == OLD_DEFAULT_ELEVENLABS_VOICE_ID:
            return False
        return True


    def local_qwen_config(project: dict) -> dict:
        settings = project.get("voice_settings", {})
        return settings.get("local_qwen", {}) or {}


    def choose_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                items.append(text)
        return items


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


    def build_local_qwen_args(project: dict) -> list[str]:
        local_qwen = local_qwen_config(project)
        voice_persona = project.get("voice_persona", {}) or {}
        voice_consistency = project.get("voice_consistency", {}) or {}
        acceptance = project.get("acceptance", {}) or {}

        cmd_args: list[str] = []
        for flag, key in (
            ("--profile", "profile"),
            ("--speaker", "speaker"),
            ("--language", "language"),
            ("--format", "format"),
            ("--attn-implementation", "attn_implementation"),
            ("--dtype", "dtype"),
        ):
            value = str(local_qwen.get(key) or "").strip()
            if value:
                cmd_args.extend([flag, value])

        identity = str(voice_persona.get("identity") or "").strip()
        core_traits = "、".join(choose_list(voice_persona.get("core_traits")))
        forbidden_traits = "、".join(choose_list(voice_persona.get("forbidden_traits")))
        locked_fields = "、".join(choose_list(voice_consistency.get("locked_fields")))
        anchor_segment = str(voice_consistency.get("anchor_segment_id") or "01").strip()
        baseline_emotion = str(voice_persona.get("baseline_emotion") or "").strip()
        pace = str(voice_persona.get("pace") or "").strip()
        breath = str(voice_persona.get("breath") or "").strip()
        emphasis = str(voice_persona.get("emphasis") or "").strip()
        reviewer = str(acceptance.get("reviewer") or "").strip()

        instruct = join_instruction_parts(
            (
                f"全程保持同一个中文女声人设：{identity}。"
                if identity
                else "全程保持同一个中文女声人设。"
            ),
            f"核心气质固定为：{core_traits}。" if core_traits else "",
            f"禁止出现这些倾向：{forbidden_traits}。" if forbidden_traits else "",
            (
                f"情绪基线保持 {baseline_emotion}，语速保持 {pace}，呼吸保持 {breath}，重音规则保持 {emphasis}。"
                if any([baseline_emotion, pace, breath, emphasis])
                else ""
            ),
            (
                f"整条视频都要延续锚点片段 {anchor_segment} 的同一位说话人、同一音色、同一情绪基线和同一说话习惯。"
            ),
            f"锁定字段：{locked_fields}。" if locked_fields else "",
            "不要在不同分段之间突然变成熟、变稚嫩、变兴奋、变播音腔，或者像换了另一个人。",
            "即使切到总结、强调或转场，也只允许轻微关键词强调，不要改变整体音色、人设和说话节奏。",
            (
                f"这条视频最终需要通过 {reviewer} 的 voice_consistency 验收，不一致就视为失败。"
                if reviewer
                else "这条视频最终需要通过 voice_consistency 验收，不一致就视为失败。"
            ),
        )
        if instruct:
            cmd_args.extend(["--instruct", instruct])
        return cmd_args


    def local_qwen_ready(project: dict) -> bool:
        cfg = local_qwen_config(project)
        if not bool(cfg.get("enabled", False)):
            return False
        python_executable = Path(str(cfg.get("python_executable") or ""))
        helper_script = Path(str(cfg.get("helper_script") or ""))
        return python_executable.exists() and helper_script.exists()


    def reviewed_web_audio_ready(root: Path, project: dict, segments: list[dict]) -> bool:
        review_status = str((project.get("voice_profile", {}) or {}).get("review_status", "unreviewed")).lower()
        if review_status != "passed":
            return False
        return all(find_existing_audio(root, item["id"]) for item in segments)


    def resolve_provider(root: Path, project: dict, segments: list[dict], requested: str) -> str:
        if requested != "auto":
            return requested
        if is_chinese_target(project):
            if local_qwen_ready(project):
                return "local-qwen"
            if resolve_env("ELEVENLABS_API_KEY") and approved_api_voice(project):
                return "elevenlabs-api"
            if resolve_env("ELEVENLABS_API_KEY") and reviewed_web_audio_ready(root, project, segments):
                return "elevenlabs-web"
            return "edge-preview"
        if resolve_env("ELEVENLABS_API_KEY") and approved_api_voice(project):
            return "elevenlabs-api"
        return "edge-preview"


    def elevenlabs_config(project: dict) -> dict:
        settings = project.get("voice_settings", {})
        cfg = settings.get("elevenlabs", {})
        return {
            "voice_id": cfg.get("voice_id") or resolve_env("ELEVENLABS_VOICE_ID") or "",
            "voice_name": cfg.get("voice_name", ""),
            "model_id": cfg.get("model_id", "eleven_multilingual_v2"),
            "output_format": cfg.get("output_format", "mp3_44100_128"),
            "stability": cfg.get("stability", 0.72),
            "similarity_boost": cfg.get("similarity_boost", 0.8),
            "style": cfg.get("style", 0.05),
            "use_speaker_boost": cfg.get("use_speaker_boost", True),
            "language_code": cfg.get("language_code", "zh"),
        }


    def edge_config(project: dict) -> dict:
        settings = project.get("voice_settings", {})
        cfg = settings.get("edge_preview", {})
        return {
            "voice": cfg.get("voice", "zh-CN-XiaoxiaoNeural"),
            "rate": cfg.get("rate", "+2%"),
            "pitch": cfg.get("pitch", "+0Hz"),
        }


    def audio_candidates(root: Path, seg_id: str) -> list[Path]:
        return [root / "audio" / f"{seg_id}{ext}" for ext in AUDIO_EXTENSIONS]


    def find_existing_audio(root: Path, seg_id: str) -> Path | None:
        for candidate in audio_candidates(root, seg_id):
            if candidate.exists():
                return candidate
        return None


    def build_web_manifest(root: Path, project: dict, segments: list[dict]) -> Path:
        workflow = project.get("voice_workflow", {})
        manifest_rel = workflow.get("web_manifest", "voice_jobs/web_tts_manifest.json")
        manifest_path = root / manifest_rel
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        voice_profile = project.get("voice_profile", {})
        manifest = {
            "topic": project.get("topic", root.name),
            "target_language": target_language(project),
            "publish_mode": workflow.get("publish_mode", "elevenlabs-web-first"),
            "accent_review_required": bool(workflow.get("accent_review_required", True)),
            "recommended_actions": [
                "Choose a Chinese-native or clearly Chinese-capable voice.",
                "Do not use an English-native voice for Chinese narration.",
                "After listening, update project.json voice_profile.review_status.",
            ],
            "voice_profile": {
                "provider": voice_profile.get("provider", ""),
                "mode": voice_profile.get("mode", ""),
                "voice_name": voice_profile.get("voice_name", ""),
                "locale": voice_profile.get("locale", ""),
                "source_type": voice_profile.get("source_type", ""),
                "review_status": voice_profile.get("review_status", "unreviewed"),
            },
            "segments": [],
        }
        for item in segments:
            manifest["segments"].append(
                {
                    "id": item["id"],
                    "text": item["voice"],
                    "target_audio_preferred": str((root / "audio" / f"{item['id']}.wav").resolve()),
                    "target_audio_candidates": [str(path.resolve()) for path in audio_candidates(root, item["id"])],
                }
            )
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return manifest_path


    def ensure_web_audio_ready(root: Path, project: dict, segments: list[dict], force: bool) -> None:
        manifest_path = build_web_manifest(root, project, segments)
        voice_profile = project.get("voice_profile", {})
        review_status = str(voice_profile.get("review_status", "unreviewed")).lower()
        missing = []
        for item in segments:
            if not find_existing_audio(root, item["id"]):
                missing.extend(str(path) for path in audio_candidates(root, item["id"]))

        if force or missing or review_status != "passed":
            raise RuntimeError(
                "Chinese publish path requires reviewed web-generated audio.\n"
                f"Manifest written to: {manifest_path}\n"
                "Use the ElevenLabs website with a Chinese-native voice, download each segment, "
                "place them at the manifest target paths, then optionally run record_voice_profile.py "
                "to mark the accepted voice."
            )

        print(f"[tts] provider=elevenlabs-web")
        print(f"[tts] using existing reviewed web audio files; manifest at {manifest_path}")


    def run_local_qwen(root: Path, project: dict, force: bool) -> None:
        cfg = local_qwen_config(project)
        qwen_python = Path(str(cfg.get("python_executable") or ""))
        qwen_helper = Path(str(cfg.get("helper_script") or ""))
        if not qwen_python.exists():
            raise FileNotFoundError(f"Missing Qwen python executable: {qwen_python}")
        if not qwen_helper.exists():
            raise FileNotFoundError(f"Missing Qwen helper script: {qwen_helper}")

        cmd = [
            str(qwen_python),
            str(qwen_helper),
            "--segments-json",
            str(root / "content" / "segments.json"),
            "--project-json",
            str(root / "content" / "project.json"),
            "--output-dir",
            str(root / "audio"),
        ]
        cmd.extend(build_local_qwen_args(project))
        if force:
            cmd.append("--force")

        subprocess.run(cmd, check=True)


    def synthesize_elevenlabs(text: str, out_path: Path, cfg: dict, previous_text: str, next_text: str) -> None:
        api_key = resolve_env("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set")
        if not cfg["voice_id"]:
            raise RuntimeError(
                "No approved ElevenLabs API voice_id configured. "
                "For Chinese narration, prefer the web workflow unless you have a reviewed Chinese-capable API voice."
            )

        payload = {
            "text": text,
            "model_id": cfg["model_id"],
            "output_format": cfg["output_format"],
            "voice_settings": {
                "stability": cfg["stability"],
                "similarity_boost": cfg["similarity_boost"],
                "style": cfg["style"],
                "use_speaker_boost": cfg["use_speaker_boost"],
            },
            "language_code": cfg["language_code"],
        }
        if previous_text:
            payload["previous_text"] = previous_text
        if next_text:
            payload["next_text"] = next_text

        req = Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        try:
            with urlopen(req) as response:
                out_path.write_bytes(response.read())
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 402 and "paid_plan_required" in detail:
                raise RuntimeError(
                    "ElevenLabs API rejected this voice on the current plan. "
                    "This usually means a library voice cannot be used via API on a free plan. "
                    "Switch to the website generation workflow and choose a Chinese-native voice."
                ) from exc
            raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"ElevenLabs request failed: {exc}") from exc


    async def synthesize_edge(text: str, out_path: Path, cfg: dict) -> None:
        import edge_tts

        communicate = edge_tts.Communicate(
            text=text,
            voice=cfg["voice"],
            rate=cfg["rate"],
            pitch=cfg["pitch"],
        )
        await communicate.save(str(out_path))


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project, segments = load_project(root)
        provider = resolve_provider(root, project, segments, args.provider)

        if provider == "elevenlabs-api" and not resolve_env("ELEVENLABS_API_KEY"):
            raise RuntimeError("Requested provider=elevenlabs-api but ELEVENLABS_API_KEY is missing")

        out_dir = root / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)

        if provider == "local-qwen":
            print("[tts] provider=local-qwen")
            run_local_qwen(root, project, args.force)
            return

        if provider == "elevenlabs-web":
            ensure_web_audio_ready(root, project, segments, args.force)
            return

        print(f"[tts] provider={provider}")
        if provider == "edge-preview" and args.provider == "auto":
            print("[tts] note: local Qwen / reviewed ElevenLabs provider not ready; using Edge preview voice")

        eleven_cfg = elevenlabs_config(project)
        edge_cfg = edge_config(project)

        for idx, item in enumerate(segments):
            out_path = out_dir / f"{item['id']}.mp3"
            existing = find_existing_audio(root, item["id"])
            if existing and not args.force:
                continue

            previous_text = segments[idx - 1]["voice"] if idx > 0 else ""
            next_text = segments[idx + 1]["voice"] if idx + 1 < len(segments) else ""
            print(f"[tts] {item['id']} -> {out_path}")

            if provider == "elevenlabs-api":
                synthesize_elevenlabs(item["voice"], out_path, eleven_cfg, previous_text, next_text)
            else:
                await synthesize_edge(item["voice"], out_path, edge_cfg)


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


    AUDIO_EXTENSIONS = (".wav", ".mp3")


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        return parser.parse_args()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8"))
        segments = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8"))

        workflow = project.get("voice_workflow", {})
        manifest_rel = workflow.get("web_manifest", "voice_jobs/web_tts_manifest.json")
        manifest_path = root / manifest_rel
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        voice_profile = project.get("voice_profile", {})
        manifest = {
            "topic": project.get("topic", root.name),
            "target_language": project.get("voice_language", "zh-CN"),
            "publish_mode": workflow.get("publish_mode", "elevenlabs-web-first"),
            "accent_review_required": bool(workflow.get("accent_review_required", True)),
            "voice_profile": {
                "provider": voice_profile.get("provider", ""),
                "mode": voice_profile.get("mode", ""),
                "voice_name": voice_profile.get("voice_name", ""),
                "locale": voice_profile.get("locale", ""),
                "source_type": voice_profile.get("source_type", ""),
                "review_status": voice_profile.get("review_status", "unreviewed"),
            },
            "segments": [],
        }
        for item in segments:
            manifest["segments"].append(
                {
                    "id": item["id"],
                    "text": item["voice"],
                    "target_audio_preferred": str((root / "audio" / f"{item['id']}.wav").resolve()),
                    "target_audio_candidates": [
                        str((root / "audio" / f"{item['id']}{ext}").resolve()) for ext in AUDIO_EXTENSIONS
                    ],
                }
            )

        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(str(manifest_path))


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


    def parse_sections(text: str) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current = "__root__"
        sections[current] = []
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if line.startswith("#"):
                current = line.lstrip("#").strip()
                sections.setdefault(current, [])
                continue
            sections.setdefault(current, []).append(line)
        return sections


    def pick_title(sections: dict[str, list[str]], fallback: str) -> str:
        for key in ("建议标题", "标题候选"):
            for line in sections.get(key, []):
                cleaned = line.strip().lstrip("-").strip()
                if cleaned and not cleaned[0].isdigit():
                    return cleaned
                if ". " in cleaned:
                    suffix = cleaned.split(". ", 1)[1].strip()
                    if suffix:
                        return suffix
        return fallback


    def pick_description(sections: dict[str, list[str]], fallback: str) -> str:
        lines = [line.strip() for line in sections.get("简介", []) if line.strip()]
        return "\n".join(lines) if lines else fallback


    def pick_tags(sections: dict[str, list[str]]) -> list[str]:
        tags: list[str] = []
        for line in sections.get("标签建议", []):
            cleaned = line.strip()
            if cleaned.startswith("-"):
                cleaned = cleaned[1:].strip()
            if cleaned and cleaned not in tags:
                tags.append(cleaned)
        return tags


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8"))
        notes_path = root / "publish_notes.md"
        notes_text = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
        sections = parse_sections(notes_text)

        topic = str(project.get("topic") or root.name)
        video_path = root / str(project.get("output_name") or f"{root.name}.mp4")
        payload = {
            "topic": topic,
            "video_path": str(video_path.resolve()),
            "title": pick_title(sections, topic),
            "description": pick_description(sections, topic),
            "tags": pick_tags(sections),
            "publish_notes_path": str(notes_path.resolve()),
            "project_json_path": str((root / "content" / "project.json").resolve()),
            "segments_json_path": str((root / "content" / "segments.json").resolve()),
        }

        out_path = root / "publish" / "bilibili_publish_job.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(str(out_path))


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
        parser.add_argument("--provider", required=True)
        parser.add_argument("--mode", required=True)
        parser.add_argument("--voice-name", default="")
        parser.add_argument("--voice-id", default="")
        parser.add_argument("--locale", default="")
        parser.add_argument("--source-type", default="")
        parser.add_argument(
            "--review-status",
            default="unreviewed",
            choices=["passed", "failed", "unreviewed"],
        )
        parser.add_argument("--note", action="append", default=[])
        return parser.parse_args()


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project_path = root / "content" / "project.json"
        project = json.loads(project_path.read_text(encoding="utf-8"))

        voice_profile = project.setdefault("voice_profile", {})
        voice_profile["provider"] = args.provider
        voice_profile["mode"] = args.mode
        voice_profile["voice_name"] = args.voice_name
        voice_profile["voice_id"] = args.voice_id
        voice_profile["locale"] = args.locale
        voice_profile["source_type"] = args.source_type
        voice_profile["review_status"] = args.review_status
        voice_profile["review_notes"] = list(args.note)

        settings = project.setdefault("voice_settings", {})
        elevenlabs = settings.setdefault("elevenlabs", {})
        if args.voice_id:
            elevenlabs["voice_id"] = args.voice_id
        if args.voice_name:
            elevenlabs["voice_name"] = args.voice_name

        project_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("[ok] voice profile updated")


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


    AUDIO_EXTENSIONS = (".wav", ".mp3")


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
        parser.add_argument("--rate", default="+2%")
        parser.add_argument("--pitch", default="+0Hz")
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    async def synthesize(text: str, out_path: Path, voice: str, rate: str, pitch: str) -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))


    def has_existing_audio(audio_dir: Path, seg_id: str) -> bool:
        return any((audio_dir / f"{seg_id}{ext}").exists() for ext in AUDIO_EXTENSIONS)


    async def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8"))
        if project.get("voice_provider") not in {"preview-edge-tts", "edge-tts"}:
            print(f"[tts] note: project voice_provider={project.get('voice_provider')}, but edge preview generator was called")
        content = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8"))
        out_dir = root / "audio"
        out_dir.mkdir(parents=True, exist_ok=True)
        for item in content:
            out_path = out_dir / f"{item['id']}.mp3"
            if has_existing_audio(out_dir, item["id"]) and not args.force:
                continue
            print(f"[tts-preview] {item['id']} -> {out_path}")
            await synthesize(item["voice"], out_path, args.voice, args.rate, args.pitch)


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
    from pathlib import Path


    DEFAULT_QWEN_PYTHON = Path(
        r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe"
    )
    DEFAULT_QWEN_HELPER = Path(
        r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py"
    )


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--segment-ids", help="Comma-separated subset like 01,02,03")
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    def local_qwen_config(project: dict) -> dict:
        settings = project.get("voice_settings", {})
        return settings.get("local_qwen", {}) or {}


    def choose_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                items.append(text)
        return items


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


    def build_qwen_cli_args(project: dict) -> list[str]:
        local_qwen = local_qwen_config(project)
        voice_persona = project.get("voice_persona", {}) or {}
        voice_consistency = project.get("voice_consistency", {}) or {}
        acceptance = project.get("acceptance", {}) or {}

        cmd_args: list[str] = []
        for flag, key in (
            ("--profile", "profile"),
            ("--speaker", "speaker"),
            ("--language", "language"),
            ("--format", "format"),
            ("--attn-implementation", "attn_implementation"),
            ("--dtype", "dtype"),
        ):
            value = str(local_qwen.get(key) or "").strip()
            if value:
                cmd_args.extend([flag, value])

        identity = str(voice_persona.get("identity") or "").strip()
        core_traits = "、".join(choose_list(voice_persona.get("core_traits")))
        forbidden_traits = "、".join(choose_list(voice_persona.get("forbidden_traits")))
        locked_fields = "、".join(choose_list(voice_consistency.get("locked_fields")))
        anchor_segment = str(voice_consistency.get("anchor_segment_id") or "01").strip()
        baseline_emotion = str(voice_persona.get("baseline_emotion") or "").strip()
        pace = str(voice_persona.get("pace") or "").strip()
        breath = str(voice_persona.get("breath") or "").strip()
        emphasis = str(voice_persona.get("emphasis") or "").strip()
        reviewer = str(acceptance.get("reviewer") or "").strip()

        instruct = join_instruction_parts(
            (
                f"全程保持同一个中文女声人设：{identity}。"
                if identity
                else "全程保持同一个中文女声人设。"
            ),
            f"核心气质固定为：{core_traits}。" if core_traits else "",
            f"禁止出现这些倾向：{forbidden_traits}。" if forbidden_traits else "",
            (
                f"情绪基线保持 {baseline_emotion}，语速保持 {pace}，呼吸保持 {breath}，重音规则保持 {emphasis}。"
                if any([baseline_emotion, pace, breath, emphasis])
                else ""
            ),
            f"整条视频都要延续锚点片段 {anchor_segment} 的同一位说话人、同一音色、同一情绪基线和同一说话习惯。",
            f"锁定字段：{locked_fields}。" if locked_fields else "",
            "不要在不同分段之间突然变成熟、变稚嫩、变兴奋、变播音腔，或者像换了另一个人。",
            "即使切到总结、强调或转场，也只允许轻微关键词强调，不要改变整体音色、人设和说话节奏。",
            (
                f"这条视频最终需要通过 {reviewer} 的 voice_consistency 验收，不一致就视为失败。"
                if reviewer
                else "这条视频最终需要通过 voice_consistency 验收，不一致就视为失败。"
            ),
        )
        if instruct:
            cmd_args.extend(["--instruct", instruct])
        return cmd_args


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        project_path = root / "content" / "project.json"
        segments_path = root / "content" / "segments.json"
        output_dir = root / "audio"
        output_dir.mkdir(parents=True, exist_ok=True)

        project = json.loads(project_path.read_text(encoding="utf-8"))
        local_qwen = local_qwen_config(project)
        qwen_python = Path(local_qwen.get("python_executable") or DEFAULT_QWEN_PYTHON)
        qwen_helper = Path(local_qwen.get("helper_script") or DEFAULT_QWEN_HELPER)

        if not qwen_python.exists():
            raise FileNotFoundError(f"Missing Qwen python executable: {qwen_python}")
        if not qwen_helper.exists():
            raise FileNotFoundError(f"Missing Qwen helper script: {qwen_helper}")

        cmd = [
            str(qwen_python),
            str(qwen_helper),
            "--segments-json",
            str(segments_path),
            "--project-json",
            str(project_path),
            "--output-dir",
            str(output_dir),
        ]
        cmd.extend(build_qwen_cli_args(project))
        if args.segment_ids:
            cmd.extend(["--segment-ids", args.segment_ids])
        if args.force:
            cmd.append("--force")

        print("[tts] provider=local-qwen")
        print(f"[tts] helper={qwen_helper}")
        subprocess.run(cmd, check=True)


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


    def resolve_audio_path(audio_dir: Path, seg_id: str) -> Path:
        for ext in AUDIO_EXTENSIONS:
            candidate = audio_dir / f"{seg_id}{ext}"
            if candidate.exists():
                return candidate
        expected = ", ".join(str(audio_dir / f"{seg_id}{ext}") for ext in AUDIO_EXTENSIONS)
        raise FileNotFoundError(f"Missing audio for {seg_id}. Looked for: {expected}")


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        ffmpeg = find_ffmpeg()
        project = json.loads((root / "content" / "project.json").read_text(encoding="utf-8"))
        content = json.loads((root / "content" / "segments.json").read_text(encoding="utf-8"))

        clips_dir = root / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        concat_file = clips_dir / "concat.txt"
        concat_lines: list[str] = []

        for item in content:
            seg_id = item["id"]
            audio = resolve_audio_path(root / "audio", seg_id)
            audio_duration = media_duration(ffmpeg, audio)
            out_clip = clips_dir / f"{seg_id}.mp4"

            if item["type"] == "slide":
                html_name = Path(item["html"]).stem
                image = root / "slide_png" / f"{html_name}.png"
                if not image.exists():
                    raise FileNotFoundError(f"Missing slide image: {image}")
                fade_out = max(audio_duration - 0.45, 0)
                vf = (
                    "scale=1920:1080:force_original_aspect_ratio=decrease,"
                    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#f4efe7,"
                    f"fade=t=in:st=0:d=0.35,fade=t=out:st={fade_out:.2f}:d=0.35"
                )
                run(
                    [
                        ffmpeg, "-y", "-loop", "1", "-framerate", str(args.fps), "-i", str(image),
                        "-i", str(audio), "-vf", vf, "-t", f"{audio_duration:.3f}", "-r", str(args.fps),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out_clip),
                    ]
                )
            else:
                demo = root / item["video"]
                if not demo.exists():
                    placeholder_html = item.get("placeholder_html")
                    if not placeholder_html:
                        raise FileNotFoundError(f"Missing demo video: {demo}")
                    image = root / "slide_png" / f"{Path(placeholder_html).stem}.png"
                    if not image.exists():
                        raise FileNotFoundError(
                            f"Missing demo video: {demo}; placeholder slide image also missing: {image}"
                        )
                    vf = (
                        "scale=1920:1080:force_original_aspect_ratio=decrease,"
                        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
                    )
                    run(
                        [
                            ffmpeg, "-y", "-loop", "1", "-framerate", str(args.fps), "-i", str(image),
                            "-i", str(audio), "-vf", vf, "-t", f"{audio_duration:.3f}", "-r", str(args.fps),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out_clip),
                        ]
                    )
                    concat_lines.append(f"file '{out_clip.as_posix()}'")
                    continue
                demo_duration = media_duration(ffmpeg, demo)
                ratio = audio_duration / demo_duration if demo_duration else 1.0
                vf = (
                    f"setpts={ratio:.6f}*PTS,"
                    "scale=1920:1080:force_original_aspect_ratio=decrease,"
                    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
                )
                run(
                    [
                        ffmpeg, "-y", "-i", str(demo), "-i", str(audio), "-vf", vf, "-map", "0:v:0",
                        "-map", "1:a:0", "-r", str(args.fps), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-t", f"{audio_duration:.3f}", "-shortest", str(out_clip),
                    ]
                )

            concat_lines.append(f"file '{out_clip.as_posix()}'")

        concat_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        final_name = project.get("output_name") or (root.name + ".mp4")
        final_path = root / final_name
        run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(final_path)])
        print(f"[video] {final_path}")


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

    function Get-MaskedState {
      param([string]$ScopeName)
      $value = [Environment]::GetEnvironmentVariable("ELEVENLABS_API_KEY", $ScopeName)
      [PSCustomObject]@{
        Scope = $ScopeName
        Present = [bool]$value
        Preview = if ($value) { ("*" * [Math]::Min($value.Length, 8)) } else { "" }
      }
    }

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

    $states = @(
      Get-MaskedState "Process"
      Get-MaskedState "User"
      Get-MaskedState "Machine"
    )

    $found = $states | Where-Object { $_.Present }
    $resolvedScope = if ($found) { ($found | Select-Object -First 1).Scope } else { "" }
    $localQwenEnabled = [bool]($localQwen -and $localQwen.enabled)
    $localQwenPython = if ($localQwen) { [string]$localQwen.python_executable } else { "" }
    $localQwenHelper = if ($localQwen) { [string]$localQwen.helper_script } else { "" }
    $localQwenReady = $localQwenEnabled -and (Test-Path $localQwenPython) -and (Test-Path $localQwenHelper)

    [PSCustomObject]@{
      elevenlabs_api_key_present = [bool]$found
      resolved_scope = $resolvedScope
      scopes = $states
      local_qwen = [PSCustomObject]@{
        enabled = $localQwenEnabled
        python_executable = $localQwenPython
        helper_script = $localQwenHelper
        ready = $localQwenReady
      }
      recommendation = if ($found) {
        if ($localQwenReady) {
          "Local Qwen and ElevenLabs are both available. Auto mode will prefer local Qwen for Chinese narration."
        } else {
          "ElevenLabs is available. For Chinese narration, auto mode still prefers local Qwen when configured; otherwise use a reviewed voice path."
        }
      } elseif ($localQwenReady) {
        "Local Qwen is ready. Auto mode will use local Qwen for Chinese narration."
      } else {
        "Neither ElevenLabs nor local Qwen is ready. This project will fall back to Edge preview audio."
      }
    } | ConvertTo-Json -Depth 4

    if ($ShowHints -and -not $found) {
      Write-Host ""
      Write-Host "Set for current shell:" -ForegroundColor Yellow
      Write-Host '$env:ELEVENLABS_API_KEY="your_key_here"'
      Write-Host ""
      Write-Host "Persist for current user:" -ForegroundColor Yellow
      Write-Host '[Environment]::SetEnvironmentVariable("ELEVENLABS_API_KEY", "your_key_here", "User")'
    }
    """
).strip() + "\n"


QUICK_CHECK = dedent(
    r"""
    from __future__ import annotations

    import argparse
    import json
    import os
    import sys
    from pathlib import Path
    import winreg


    OLD_DEFAULT_ELEVENLABS_VOICE_ID = "XB0fDUnXU5powFXDhCwa"


    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--strict", action="store_true")
        return parser.parse_args()


    def resolve_env(name: str) -> str | None:
        value = os.environ.get(name)
        if value:
            return value
        for hive, subkey in (
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        ):
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    value, _ = winreg.QueryValueEx(key, name)
                    if value:
                        return str(value)
            except FileNotFoundError:
                continue
        return None


    def main() -> None:
        args = parse_args()
        root = Path(args.root).resolve()
        hard_failures: list[str] = []
        warnings: list[str] = []

        project_path = root / "content" / "project.json"
        segments_path = root / "content" / "segments.json"
        notes_path = root / "publish_notes.md"

        for required in [project_path, segments_path, notes_path]:
            if not required.exists():
                hard_failures.append(f"missing required file: {required}")

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        project = json.loads(project_path.read_text(encoding="utf-8"))
        segments = json.loads(segments_path.read_text(encoding="utf-8"))
        elevenlabs_api_key = resolve_env("ELEVENLABS_API_KEY")

        provider = str(project.get("voice_provider", "auto-natural-tts"))
        voice_language = str(project.get("voice_language", "zh-CN")).lower()
        workflow = project.get("voice_workflow", {})
        voice_profile = project.get("voice_profile", {})
        voice_settings = project.get("voice_settings", {}).get("elevenlabs", {})
        local_qwen = (project.get("voice_settings", {}) or {}).get("local_qwen", {}) or {}
        local_qwen_enabled = bool(local_qwen.get("enabled", False))
        local_qwen_python = Path(str(local_qwen.get("python_executable") or "")) if local_qwen else Path()
        local_qwen_helper = Path(str(local_qwen.get("helper_script") or "")) if local_qwen else Path()
        local_qwen_ready = (
            local_qwen_enabled
            and local_qwen_python.exists()
            and local_qwen_helper.exists()
        )

        if provider in {"preview-edge-tts", "edge-tts"}:
            warnings.append("voice_provider 仍是预览级 TTS；适合粗剪，不建议直接发布")
        elif provider in {"local-qwen", "auto-natural-tts"} and local_qwen_enabled and not local_qwen_ready:
            warnings.append("voice_settings.local_qwen 已启用，但本地 Qwen helper 或 Python 路径不存在")
        elif provider in {"auto-natural-tts", "elevenlabs", "elevenlabs-api", "elevenlabs-web"}:
            if not elevenlabs_api_key and not local_qwen_ready:
                warnings.append("未检测到 ELEVENLABS_API_KEY，且本地 Qwen 未就绪；render_all 将回退到 Edge 预览音轨")

        if voice_language.startswith("zh") and workflow.get("accent_review_required", True):
            if provider != "local-qwen" and str(voice_profile.get("review_status", "unreviewed")).lower() != "passed":
                warnings.append("中文终版配音尚未通过听感验收；先确认没有外国人口音或明显翻译腔")

        voice_locale = str(voice_profile.get("locale", "")).lower()
        if voice_language.startswith("zh") and voice_locale and not voice_locale.startswith("zh"):
            warnings.append(f"当前 voice_profile.locale={voice_locale}；中文旁白存在外国人口音风险")

        source_type = str(voice_profile.get("source_type", "")).lower()
        mode = str(voice_profile.get("mode", "")).lower()
        if mode == "elevenlabs-api" and source_type == "library":
            warnings.append("当前 voice_profile 使用 ElevenLabs library voice API；免费账户常见 402，且中文口音风险更高")

        if voice_language.startswith("zh") and voice_settings.get("voice_id") == OLD_DEFAULT_ELEVENLABS_VOICE_ID:
            warnings.append("project.json 仍保留旧的默认英文 ElevenLabs voice_id；不应继续用于中文终版")

        if voice_language.startswith("zh") and provider in {"elevenlabs-web"}:
            manifest_rel = workflow.get("web_manifest", "voice_jobs/web_tts_manifest.json")
            manifest_path = root / manifest_rel
            if not manifest_path.exists():
                warnings.append("中文 web-first 配音还没有 manifest；先运行 prepare_web_tts_manifest.py")

        if not 6 <= len(segments) <= 10:
            warnings.append(f"当前 segments 数量为 {len(segments)}；讲解视频通常控制在 6-10 段更稳")

        has_demo = False
        for item in segments:
            voice_len = len(item.get("voice", ""))
            if voice_len > 140:
                warnings.append(f"segment {item.get('id')} 旁白过长（{voice_len} 字），建议再压短")
            if item.get("type") == "slide":
                html_path = root / item["html"]
                if not html_path.exists():
                    hard_failures.append(f"missing slide html: {html_path}")
            if item.get("type") == "demo":
                has_demo = True
                video_path = root / item["video"]
                if not video_path.exists():
                    placeholder_html = item.get("placeholder_html")
                    if placeholder_html and (root / placeholder_html).exists():
                        warnings.append(
                            f"segment {item.get('id')} demo 录像缺失；render_all 会先用占位页 {placeholder_html} 顶上"
                        )
                    else:
                        hard_failures.append(f"missing demo video: {video_path}")

        if not has_demo:
            warnings.append("没有 demo 段；概念型科普可接受，如是工具实操类视频建议补一段录屏")

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
    "- 中文终版优先走 reviewed web voice；除非已经验过中文 API voice，否则不要默认用 ElevenLabs API library voices\n"
    "- 出片前必须过 acceptance-reviewer：内容深度、UI 服务内容、配音一致性三项都要过\n"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument(
        "--voice-provider",
        default="auto-natural-tts",
        choices=["auto-natural-tts", "elevenlabs-api", "elevenlabs-web", "preview-edge-tts"],
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def merge_project_json(path: Path, provider: str) -> None:
    project = json.loads(path.read_text(encoding="utf-8"))
    voice_language = str(project.get("voice_language") or "zh-CN")

    project["voice_provider"] = provider
    project["voice_language"] = voice_language
    project["preview_voice_provider"] = "preview-edge-tts"
    project["voice_quality_bar"] = "publish_requires_reviewed_natural_voice_for_chinese"
    project.setdefault("visual_style", "bilibili-quiet-glass-lab-v3")

    content_strategy = project.setdefault("content_strategy", {})
    content_strategy.setdefault("series_goal", "把 AI / 技术概念讲成观众能直接带走的判断方法")
    content_strategy.setdefault("episode_goal", "先拆误解，再给地图，最后给场景化选择")
    content_strategy.setdefault(
        "higher_order_takeaway",
        "不要只解释术语，还要解释这个概念为什么在今天重要，以及它改变了什么判断顺序",
    )
    content_strategy.setdefault("main_agent_role", "chief-editor")
    content_strategy.setdefault(
        "subagents",
        ["research-scout", "skeptic-elevator", "visual-architect", "voice-director", "acceptance-reviewer"],
    )

    ui_system = project.setdefault("ui_system", {})
    ui_system.setdefault("theme", "quiet-glass-lab-v3")
    ui_system.setdefault("glass_look", "tinted")
    ui_system.setdefault(
        "content_layers",
        ["content-base", "glass-function-layer", "temporary-explainer-layer"],
    )
    ui_system.setdefault(
        "rules",
        ["功能层用玻璃，内容层少用玻璃", "每页只保留一个视觉中心", "不要假状态栏", "glass 要为内容退后，不要抢戏"],
    )

    workflow = project.setdefault("voice_workflow", {})
    workflow.setdefault(
        "publish_mode",
        "elevenlabs-web-first" if voice_language.lower().startswith("zh") else "elevenlabs-api-first",
    )
    workflow.setdefault("web_manifest", "voice_jobs/web_tts_manifest.json")
    workflow.setdefault("accent_review_required", True)

    voice_profile = project.setdefault("voice_profile", {})
    voice_profile.setdefault("provider", "")
    voice_profile.setdefault("mode", "")
    voice_profile.setdefault("voice_name", "")
    voice_profile.setdefault("voice_id", "")
    voice_profile.setdefault("locale", "")
    voice_profile.setdefault("source_type", "")
    voice_profile.setdefault("review_status", "unreviewed")
    voice_profile.setdefault("review_notes", [])

    voice_persona = project.setdefault("voice_persona", {})
    voice_persona.setdefault("id", "cn_female_steady_graceful_cute_v1")
    voice_persona.setdefault("display_name", "沉稳大方可爱女声")
    voice_persona.setdefault("identity", "熟悉 AI 和工具工作流、表达克制但友好的年轻中文女生")
    voice_persona.setdefault("core_traits", ["沉稳", "大方", "亲和", "轻微可爱"])
    voice_persona.setdefault("forbidden_traits", ["幼态", "撒娇", "夹子音", "播音腔", "突然兴奋"])
    voice_persona.setdefault("baseline_emotion", "calm_friendly")
    voice_persona.setdefault("pace", "medium_steady")
    voice_persona.setdefault("breath", "light_short_controlled")
    voice_persona.setdefault("emphasis", "light_keyword_only")
    voice_persona.setdefault("qwen_base_instruct", LOCAL_QWEN_BASE_INSTRUCT)

    voice_consistency = project.setdefault("voice_consistency", {})
    voice_consistency.setdefault("anchor_segment_id", "01")
    voice_consistency.setdefault(
        "locked_fields",
        ["profile", "speaker", "language", "voice_id", "model_id", "base_instruct"],
    )
    voice_consistency.setdefault("emotion_variance", "low")
    voice_consistency.setdefault("pace_variance", "low")
    voice_consistency.setdefault("breath_variance", "low")
    voice_consistency.setdefault("regen_policy", "regen_outliers_only")

    acceptance = project.setdefault("acceptance", {})
    acceptance.setdefault("reviewer", "acceptance-reviewer")
    acceptance.setdefault("must_pass", ["content_depth", "ui_supports_content", "voice_consistency"])
    acceptance.setdefault("fail_action", "route_back_to_owner_and_regen")
    acceptance.setdefault("write_back", "summarize_reusable_findings_into_skill")

    settings = project.setdefault("voice_settings", {})
    elevenlabs = settings.setdefault("elevenlabs", {})
    current_voice_id = str(elevenlabs.get("voice_id") or "")
    if current_voice_id == OLD_DEFAULT_ELEVENLABS_VOICE_ID and voice_profile.get("review_status") != "passed":
        current_voice_id = ""
    elevenlabs["voice_id"] = current_voice_id
    elevenlabs.setdefault("voice_name", "")
    elevenlabs.setdefault("model_id", "eleven_multilingual_v2")
    elevenlabs.setdefault("output_format", "mp3_44100_128")
    elevenlabs.setdefault("stability", 0.72)
    elevenlabs.setdefault("similarity_boost", 0.8)
    elevenlabs.setdefault("style", 0.05)
    elevenlabs.setdefault("use_speaker_boost", True)
    elevenlabs.setdefault("language_code", "zh")

    edge = settings.setdefault("edge_preview", {})
    edge.setdefault("voice", "zh-CN-XiaoxiaoNeural")
    edge.setdefault("rate", "+2%")
    edge.setdefault("pitch", "+0Hz")

    local_qwen = settings.setdefault("local_qwen", {})
    local_qwen.setdefault("enabled", True)
    local_qwen.setdefault("profile", "young_calm_cn_female_explainer")
    local_qwen.setdefault("speaker", "serena")
    local_qwen.setdefault("language", "Chinese")
    if str(local_qwen.get("instruct") or "") == LOCAL_QWEN_BASE_INSTRUCT:
        local_qwen["instruct"] = DEFAULT_PROJECT_QWEN_INSTRUCT
    local_qwen.setdefault("instruct", DEFAULT_PROJECT_QWEN_INSTRUCT)
    local_qwen.setdefault(
        "model_dir",
        r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\models\Qwen3-TTS-12Hz-1.7B-CustomVoice",
    )
    local_qwen.setdefault(
        "helper_script",
        r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py",
    )
    local_qwen.setdefault(
        "python_executable",
        r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe",
    )
    local_qwen.setdefault("format", "wav")
    local_qwen.setdefault("attn_implementation", "sdpa")
    local_qwen.setdefault("dtype", "bfloat16")

    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_publish_notes(path: Path) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if PUBLISH_NOTES_MARKER.strip() in content:
        return
    content = content.rstrip() + "\n" + PUBLISH_NOTES_MARKER
    path.write_text(content, encoding="utf-8")


def patch_segments_json(path: Path) -> None:
    if not path.exists():
        return
    segments = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for item in segments:
        if item.get("type") == "demo" and not item.get("placeholder_html"):
            item["placeholder_html"] = "slides/06-demo.html"
            changed = True
    if changed:
        path.write_text(json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    project_path = root / "content" / "project.json"
    scripts_dir = root / "scripts"

    if not project_path.exists():
        raise FileNotFoundError(f"Missing project.json at {project_path}")

    merge_project_json(project_path, args.voice_provider)
    patch_segments_json(root / "content" / "segments.json")
    patch_publish_notes(root / "publish_notes.md")

    write_text(scripts_dir / "generate_tts_publish.py", GENERATE_TTS_PUBLISH)
    write_text(scripts_dir / "prepare_web_tts_manifest.py", PREPARE_WEB_TTS_MANIFEST)
    write_text(scripts_dir / "prepare_publish_job.py", PREPARE_PUBLISH_JOB)
    write_text(scripts_dir / "record_voice_profile.py", RECORD_VOICE_PROFILE)
    write_text(scripts_dir / "generate_tts_edge.py", GENERATE_TTS_EDGE)
    write_text(scripts_dir / "generate_tts_local_qwen.py", GENERATE_TTS_LOCAL_QWEN)
    write_text(scripts_dir / "assemble_video.py", ASSEMBLE_VIDEO)
    write_text(scripts_dir / "render_all.ps1", RENDER_ALL)
    write_text(scripts_dir / "check_voice_env.ps1", CHECK_VOICE_ENV)
    write_text(scripts_dir / "quick_check.py", QUICK_CHECK)

    print(f"[ok] upgraded project at {root}")


if __name__ == "__main__":
    main()
