from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_defaults import (
    build_depth_contract_data,
    build_detail_weave_data,
    build_narration_polish_data,
    build_outline_plan_data,
    build_project_data,
    build_publish_notes,
    build_shot_intents_data,
    build_segments_data,
    build_style_contract_data,
)


STYLE_FOUNDATION_DIR = Path(__file__).resolve().parents[1] / "references" / "quiet-glass-lab"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_template_asset(name: str, fallback: str) -> str:
    path = STYLE_FOUNDATION_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return fallback


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if root.exists() and any(root.iterdir()) and not args.force:
        raise SystemExit(f"Target directory already exists and is not empty: {root}")

    for rel in ["content", "slides", "scripts", "audio", "clips", "slide_png", "demo", "publish", "voice_jobs"]:
        (root / rel).mkdir(parents=True, exist_ok=True)

    write_text(
        root / "content" / "project.json",
        json.dumps(build_project_data(args.topic, args.slug), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "outline_plan.json",
        json.dumps(build_outline_plan_data(args.topic), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "depth_contract.json",
        json.dumps(build_depth_contract_data(args.topic), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "detail_weave.json",
        json.dumps(build_detail_weave_data(), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "narration_polish.json",
        json.dumps(build_narration_polish_data(), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "style_contract.json",
        json.dumps(build_style_contract_data(), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "shot_intents.json",
        json.dumps(build_shot_intents_data(args.topic), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(
        root / "content" / "segments.json",
        json.dumps(build_segments_data(), ensure_ascii=False, indent=2) + "\n",
    )
    write_text(root / "publish_notes.md", build_publish_notes(args.topic))
    write_text(root / "slides" / "base.css", read_template_asset("base.css", ""))

    print(f"[ok] scaffold created at {root}")


if __name__ == "__main__":
    main()
