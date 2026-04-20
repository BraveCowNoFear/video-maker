from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


DEFAULT_SHARED_SKILLS = Path(r"C:\Users\Clr\.agents\skills")
DEFAULT_QWEN_PYTHON = Path(r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe")
DEFAULT_QWEN_HELPER = Path(r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py")
DEFAULT_QWEN_MODEL = Path(
    r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\models\Qwen3-TTS-12Hz-1.7B-CustomVoice"
)
EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
FFMPEG_CANDIDATES = [
    Path(r"C:\Program Files\File Converter\ffmpeg.exe"),
    Path(r"C:\Program Files\Tecplot\Tecplot 360 EX 2017 R2\bin\ffmpeg.exe"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root")
    return parser.parse_args()


def path_status(path: Path) -> dict:
    return {
        "path": str(path),
        "exists": path.exists(),
    }


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def resolve_ffmpeg() -> str:
    for candidate in FFMPEG_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    found = shutil.which("ffmpeg")
    return found or ""


def resolve_edge() -> str:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return ""


def resolve_project_qwen(project_root: Path) -> dict:
    project_json = project_root / "content" / "project.json"
    if not project_json.exists():
        return {
            "project_json": str(project_json),
            "exists": False,
        }

    project = json.loads(project_json.read_text(encoding="utf-8"))
    local_qwen = ((project.get("voice_settings") or {}).get("local_qwen") or {})
    return {
        "project_json": str(project_json),
        "exists": True,
        "enabled": bool(local_qwen.get("enabled", False)),
        "python_executable": str(local_qwen.get("python_executable") or ""),
        "helper_script": str(local_qwen.get("helper_script") or ""),
        "model_dir": str(local_qwen.get("model_dir") or ""),
    }


def gh_login() -> str:
    if not command_exists("gh"):
        return ""
    proc = subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def main() -> None:
    args = parse_args()

    desktop_control_dir = DEFAULT_SHARED_SKILLS / "desktop-control-for-windows"
    video_maker_dir = DEFAULT_SHARED_SKILLS / "video-maker"
    ffmpeg_path = resolve_ffmpeg()
    edge_path = resolve_edge()

    report = {
        "skills": {
            "video_maker": path_status(video_maker_dir),
            "desktop_control_for_windows": path_status(desktop_control_dir),
        },
        "binaries": {
            "edge": {"path": edge_path, "exists": bool(edge_path)},
            "ffmpeg": {"path": ffmpeg_path, "exists": bool(ffmpeg_path)},
            "gh": {"exists": command_exists("gh"), "login": gh_login()},
        },
        "local_qwen_defaults": {
            "python_executable": path_status(DEFAULT_QWEN_PYTHON),
            "helper_script": path_status(DEFAULT_QWEN_HELPER),
            "model_dir": path_status(DEFAULT_QWEN_MODEL),
        },
        "project": None,
        "assessment": {
            "local_render_ready": False,
            "local_qwen_ready": False,
            "bilibili_upload_automation_ready": False,
        },
        "recommended_next_steps": [],
    }

    if args.project_root:
        report["project"] = resolve_project_qwen(Path(args.project_root).resolve())

    local_qwen_ready = all(
        item["exists"] for item in report["local_qwen_defaults"].values()
    )
    local_render_ready = bool(edge_path and ffmpeg_path)
    upload_ready = bool(edge_path) and desktop_control_dir.exists()

    report["assessment"]["local_render_ready"] = local_render_ready
    report["assessment"]["local_qwen_ready"] = local_qwen_ready
    report["assessment"]["bilibili_upload_automation_ready"] = upload_ready

    if not desktop_control_dir.exists():
        report["recommended_next_steps"].append(
            "Install desktop-control-for-windows if you want automatic Bilibili upload."
        )
    if not edge_path:
        report["recommended_next_steps"].append(
            "Install Microsoft Edge for slide rendering and upload automation."
        )
    if not ffmpeg_path:
        report["recommended_next_steps"].append(
            "Install ffmpeg or place it at C:\\Program Files\\File Converter\\ffmpeg.exe."
        )
    if not local_qwen_ready:
        report["recommended_next_steps"].append(
            "Prepare the local Qwen runtime or update voice_settings.local_qwen in project.json."
        )
    if not command_exists("gh"):
        report["recommended_next_steps"].append(
            "Install GitHub CLI if you want repo-oriented publish and release workflows."
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
