from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from project_defaults import (
    DEFAULT_LOCAL_QWEN_HELPER,
    DEFAULT_LOCAL_QWEN_MODEL,
    DEFAULT_LOCAL_QWEN_PYTHON,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_SKILLS = Path(r"C:\Users\Clr\.codex\skills")
DEFAULT_SHARED_SKILLS = Path(r"C:\Users\Clr\.agents\skills")
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
    return {"path": str(path), "exists": path.exists()}


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def resolve_skill_dir(name: str, preferred: Path | None = None) -> Path:
    candidates: list[Path] = []
    if preferred is not None:
        candidates.append(preferred)
    candidates.extend(
        [
            DEFAULT_CODEX_SKILLS / name,
            DEFAULT_SHARED_SKILLS / name,
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


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


def resolve_node_binary(name: str) -> str:
    return shutil.which(name) or ""


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


def read_json_or_none(path: Path) -> object | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


def resolve_project_status(project_root: Path) -> dict:
    project_json = project_root / "content" / "project.json"
    problem_contract = project_root / "content" / "problem_contract.json"
    audience_contract = project_root / "content" / "audience_contract.json"
    opening_contract = project_root / "content" / "opening_contract.json"
    meaning_contract = project_root / "content" / "meaning_contract.json"
    outline_plan = project_root / "content" / "outline_plan.json"
    depth_contract = project_root / "content" / "depth_contract.json"
    detail_weave = project_root / "content" / "detail_weave.json"
    evidence_map = project_root / "content" / "evidence_map.json"
    script_draft = project_root / "content" / "script_draft.json"
    narration_polish = project_root / "content" / "narration_polish.json"
    style_contract = project_root / "content" / "style_contract.json"
    shot_intents = project_root / "content" / "shot_intents.json"
    visual_asset_plan = project_root / "content" / "visual_asset_plan.json"
    segments_json = project_root / "content" / "segments.json"
    screenshot_plan = project_root / "content" / "screenshot_plan.json"
    visual_qa_report = project_root / "content" / "visual_qa_report.json"
    acceptance_report = project_root / "content" / "acceptance_report.json"
    master_wav = project_root / "audio" / "master.wav"
    master_mp3 = project_root / "audio" / "master.mp3"
    remotion_dir = project_root / "remotion"
    remotion_entry = remotion_dir / "src" / "index.ts"
    remotion_video = remotion_dir / "src" / "Video.tsx"
    remotion_package = remotion_dir / "package.json"
    remotion_props = remotion_dir / "input-props.json"

    report = {
        "project_json": str(project_json),
        "exists": project_json.exists(),
        "artifacts": {
            "problem_contract": path_status(problem_contract),
            "audience_contract": path_status(audience_contract),
            "opening_contract": path_status(opening_contract),
            "meaning_contract": path_status(meaning_contract),
            "outline_plan": path_status(outline_plan),
            "depth_contract": path_status(depth_contract),
            "detail_weave": path_status(detail_weave),
            "evidence_map": path_status(evidence_map),
            "script_draft": path_status(script_draft),
            "narration_polish": path_status(narration_polish),
            "style_contract": path_status(style_contract),
            "shot_intents": path_status(shot_intents),
            "visual_asset_plan": path_status(visual_asset_plan),
            "segments": path_status(segments_json),
            "screenshot_plan": path_status(screenshot_plan),
            "visual_qa_report": path_status(visual_qa_report),
            "acceptance_report": path_status(acceptance_report),
        },
        "render": {
            "engine": "remotion",
            "entry": path_status(remotion_entry),
            "video_component": path_status(remotion_video),
            "package": path_status(remotion_package),
            "props": path_status(remotion_props),
        },
        "voice": {
            "narration_mode": "",
            "local_qwen_enabled": False,
            "local_qwen_python": "",
            "local_qwen_helper": "",
            "local_qwen_model_dir": "",
            "master_audio_candidates": [
                {"path": str(master_wav), "exists": master_wav.exists()},
                {"path": str(master_mp3), "exists": master_mp3.exists()},
            ],
        },
    }

    if not project_json.exists():
        return report

    project = json.loads(project_json.read_text(encoding="utf-8"))
    local_qwen = ((project.get("voice_settings") or {}).get("local_qwen") or {})
    workflow = project.get("voice_workflow", {}) or {}

    report["voice"].update(
        {
            "narration_mode": str(workflow.get("narration_mode") or ""),
            "local_qwen_enabled": bool(local_qwen.get("enabled", False)),
            "local_qwen_python": str(local_qwen.get("python_executable") or ""),
            "local_qwen_helper": str(local_qwen.get("helper_script") or ""),
            "local_qwen_model_dir": str(local_qwen.get("model_dir") or ""),
        }
    )
    return report


def main() -> None:
    args = parse_args()

    desktop_control_dir = resolve_skill_dir("desktop-control-for-windows")
    video_maker_dir = resolve_skill_dir("video-maker", preferred=SKILL_ROOT)
    ffmpeg_path = resolve_ffmpeg()
    edge_path = resolve_edge()
    node_path = resolve_node_binary("node")
    npm_path = resolve_node_binary("npm")

    report = {
        "skills": {
            "video_maker": path_status(video_maker_dir),
            "desktop_control_for_windows": path_status(desktop_control_dir),
        },
        "binaries": {
            "edge": {"path": edge_path, "exists": bool(edge_path)},
            "ffmpeg": {"path": ffmpeg_path, "exists": bool(ffmpeg_path)},
            "node": {"path": node_path, "exists": bool(node_path)},
            "npm": {"path": npm_path, "exists": bool(npm_path)},
            "gh": {"exists": command_exists("gh"), "login": gh_login()},
        },
        "local_qwen_defaults": {
            "python_executable": path_status(DEFAULT_LOCAL_QWEN_PYTHON),
            "helper_script": path_status(DEFAULT_LOCAL_QWEN_HELPER),
            "model_dir": path_status(DEFAULT_LOCAL_QWEN_MODEL),
        },
        "project": None,
        "assessment": {
            "local_render_ready": False,
            "local_qwen_ready": False,
            "bilibili_upload_automation_ready": False,
            "content_contract_ready": False,
            "master_track_ready": False,
        },
        "recommended_next_steps": [],
    }

    if args.project_root:
        report["project"] = resolve_project_status(Path(args.project_root).resolve())

    local_qwen_ready = (
        report["local_qwen_defaults"]["python_executable"]["exists"]
        and report["local_qwen_defaults"]["model_dir"]["exists"]
    )
    local_render_ready = bool(ffmpeg_path and node_path and npm_path)
    upload_ready = bool(edge_path) and desktop_control_dir.exists()

    report["assessment"]["local_render_ready"] = local_render_ready
    report["assessment"]["local_qwen_ready"] = local_qwen_ready
    report["assessment"]["bilibili_upload_automation_ready"] = upload_ready

    if report["project"]:
        artifacts = report["project"]["artifacts"]
        master_candidates = report["project"]["voice"]["master_audio_candidates"]
        all_required_files_exist = all(item["exists"] for item in artifacts.values())
        project_root = Path(args.project_root).resolve()
        segments_payload = read_json_or_none(project_root / "content" / "segments.json")
        shot_intents_payload = read_json_or_none(project_root / "content" / "shot_intents.json")
        segments_ready = isinstance(segments_payload, list) and len(segments_payload) > 0
        shot_intents_ready = (
            isinstance(shot_intents_payload, dict)
            and isinstance(shot_intents_payload.get("beats"), list)
            and len(shot_intents_payload.get("beats") or []) > 0
        )
        artifacts["segments"]["nonempty"] = segments_ready
        artifacts["shot_intents"]["beats_nonempty"] = shot_intents_ready
        report["assessment"]["content_contract_ready"] = all_required_files_exist and segments_ready and shot_intents_ready
        report["assessment"]["master_track_ready"] = any(item["exists"] for item in master_candidates)

    if not desktop_control_dir.exists():
        report["recommended_next_steps"].append(
            "Install desktop-control-for-windows if you want automatic Bilibili upload."
        )
    if not edge_path:
        report["recommended_next_steps"].append(
            "Install Microsoft Edge for upload automation."
        )
    if not ffmpeg_path:
        report["recommended_next_steps"].append(
            "Install ffmpeg or place it at C:\\Program Files\\File Converter\\ffmpeg.exe."
        )
    if not node_path or not npm_path:
        report["recommended_next_steps"].append(
            "Install Node.js / npm for Remotion rendering."
        )
    if not local_qwen_ready:
        report["recommended_next_steps"].append(
            "Prepare the local Qwen 12Hz runtime or update voice_settings.local_qwen.model_dir in project.json."
        )
    if report["project"] and not report["assessment"]["content_contract_ready"]:
        report["recommended_next_steps"].append(
            "Fill the content contracts and compile non-empty shot_intents.json plus segments.json before render-time validation."
        )
    if report["project"] and report["project"]["voice"]["narration_mode"] == "master-track-preferred":
        if not report["assessment"]["master_track_ready"]:
            report["recommended_next_steps"].append(
                "This project uses a single master narration track; synthesize audio/master.wav or audio/master.mp3 before final QA."
            )
    if not command_exists("gh"):
        report["recommended_next_steps"].append(
            "Install GitHub CLI if you want repo-oriented publish and release workflows."
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
