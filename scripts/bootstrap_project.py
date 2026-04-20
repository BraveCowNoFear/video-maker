from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--voice-provider", default="auto-natural-tts")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scripts_dir = Path(__file__).resolve().parent
    legacy_bootstrap = scripts_dir / "bootstrap_video_project.py"
    upgrade_script = scripts_dir / "upgrade_project.py"

    if not legacy_bootstrap.exists():
        raise FileNotFoundError(f"Missing bootstrap video script: {legacy_bootstrap}")

    bootstrap_cmd = [
        sys.executable,
        str(legacy_bootstrap),
        "--root",
        args.root,
        "--topic",
        args.topic,
        "--slug",
        args.slug,
    ]
    if args.force:
        bootstrap_cmd.append("--force")
    subprocess.run(bootstrap_cmd, check=True)

    upgrade_cmd = [
        sys.executable,
        str(upgrade_script),
        "--root",
        args.root,
        "--voice-provider",
        args.voice_provider,
    ]
    if args.force:
        upgrade_cmd.append("--force")
    subprocess.run(upgrade_cmd, check=True)

    print(f"[ok] video-maker scaffold ready at {Path(args.root).resolve()}")


if __name__ == "__main__":
    main()
