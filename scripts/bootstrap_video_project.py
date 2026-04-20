from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent


BASE_CSS = dedent(
    """
    :root {
      --bg-1: #eef4ff;
      --bg-2: #f7f8fb;
      --bg-3: #fff2f5;
      --ink: #101216;
      --muted: #5e6673;
      --line: rgba(255, 255, 255, 0.58);
      --glass: rgba(255, 255, 255, 0.42);
      --glass-strong: rgba(255, 255, 255, 0.6);
      --accent: #2d6df6;
      --danger: #ff5d5d;
      --radius: 30px;
      --shadow: 0 30px 90px rgba(92, 110, 143, 0.18);
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      width: 1600px;
      height: 900px;
      overflow: hidden;
    }

    body {
      position: relative;
      font-family: "Segoe UI Variable Display", "PingFang SC", "Noto Sans SC", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 14%, rgba(105, 175, 255, 0.28), transparent 28%),
        radial-gradient(circle at 85% 18%, rgba(255, 162, 195, 0.24), transparent 24%),
        radial-gradient(circle at 76% 82%, rgba(180, 213, 255, 0.24), transparent 26%),
        linear-gradient(135deg, var(--bg-1), var(--bg-2) 48%, var(--bg-3));
    }

    body::before {
      content: "";
      position: absolute;
      inset: 24px;
      border-radius: 36px;
      border: 1px solid rgba(255, 255, 255, 0.5);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
      pointer-events: none;
    }

    .slide { position: relative; width: 100%; height: 100%; padding: 58px 64px 54px; }
    .eyebrow {
      font-size: 20px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
      color: rgba(45, 109, 246, 0.9); margin-bottom: 18px;
    }
    .title {
      margin: 0; max-width: 1080px; font-size: 86px; line-height: 1.02;
      letter-spacing: -0.055em; font-weight: 700;
    }
    .subtitle {
      margin-top: 18px; max-width: 900px; font-size: 28px; line-height: 1.45; color: var(--muted);
    }
    .chips { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 28px; }
    .chip {
      padding: 16px 22px; font-size: 26px; font-weight: 600; border-radius: var(--radius);
      border: 1px solid var(--line); background: var(--glass);
      backdrop-filter: blur(28px) saturate(150%); box-shadow: var(--shadow);
    }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .card {
      border-radius: var(--radius); border: 1px solid var(--line); background: var(--glass);
      backdrop-filter: blur(28px) saturate(150%); box-shadow: var(--shadow); padding: 22px 22px 20px;
    }
    .card h3 { margin: 0; font-size: 26px; line-height: 1.2; }
    .card p { margin: 12px 0 0; font-size: 20px; line-height: 1.45; color: var(--muted); }
    .flow { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 30px; }
    .node {
      border-radius: var(--radius); border: 1px solid var(--line); background: var(--glass);
      backdrop-filter: blur(28px) saturate(150%); box-shadow: var(--shadow); padding: 22px;
    }
    .node h3 { margin: 0; font-size: 28px; }
    .node p { margin: 14px 0 0; font-size: 20px; line-height: 1.4; color: var(--muted); }
    .meta-table { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 28px; }
    .meta-item {
      border-radius: var(--radius); border: 1px solid var(--line); background: var(--glass);
      backdrop-filter: blur(28px) saturate(150%); box-shadow: var(--shadow); padding: 20px 22px;
    }
    .k {
      font-size: 16px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
      color: rgba(45, 109, 246, 0.82);
    }
    .v { margin-top: 10px; font-size: 28px; line-height: 1.3; }
    .danger { color: var(--danger); }
    .footer {
      position: absolute; left: 64px; right: 64px; bottom: 48px;
      display: flex; justify-content: space-between; align-items: center;
      color: var(--muted); font-size: 20px;
    }
    """
).strip() + "\n"


SLIDES = {
    "01-hook.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">BILIBILI EXPLAINER</div>
          <h1 class="title">__TOPIC__</h1>
          <div class="chips">
            <div class="chip">能做什么</div>
            <div class="chip">强在哪</div>
            <div class="chip">缺点</div>
            <div class="chip">demo</div>
          </div>
          <div class="footer"><span>iOS 18 glass minimal</span><span>01</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "02-problem.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">WHY THIS EXISTS</div>
          <h1 class="title">它补的是哪一层</h1>
          <p class="subtitle">没有 DOM / API / CLI 时，怎么继续把事做完。</p>
          <div class="footer"><span>少字，别堆段落</span><span>02</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "03-capabilities.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">CAPABILITIES</div>
          <h1 class="title">会看 · 会点 · 会验</h1>
          <div class="chips">
            <div class="chip">screenshot</div>
            <div class="chip">click / type</div>
            <div class="chip">window</div>
            <div class="chip">clipboard</div>
          </div>
          <div class="footer"><span>03</span><span>只留关键词</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "04-flow.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">ARCHITECTURE</div>
          <h1 class="title">不是乱点，是受控执行</h1>
          <section class="flow">
            <div class="node"><h3>Coordinator</h3><p>想</p></div>
            <div class="node"><h3>UI worker</h3><p>动手</p></div>
            <div class="node"><h3>Lock</h3><p>防抢桌面</p></div>
            <div class="node"><h3>Overlay</h3><p>告诉人现在是谁在控</p></div>
          </section>
          <div class="footer"><span>04</span><span>结构比命令更重要</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "05-pros-cons.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">TRADEOFFS</div>
          <h1 class="title">稳，但不快</h1>
          <section class="grid-2">
            <div class="card"><h3>优点</h3><p>跨应用 / 真闭环 / 人能看懂状态</p></div>
            <div class="card"><h3>缺点</h3><p><span class="danger">UI 本来就慢</span><br>高思考 UI worker 更稳，也更慢</p></div>
          </section>
          <div class="footer"><span>05</span><span>缺点直接讲</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "06-demo.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">DEMO</div>
          <h1 class="title">看完整闭环</h1>
          <div class="chips">
            <div class="chip">overlay start</div>
            <div class="chip">lock</div>
            <div class="chip">action</div>
            <div class="chip">verify</div>
          </div>
          <div class="footer"><span>06</span><span>下一段接录屏</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
    "07-open-source.html": dedent(
        """
        <!doctype html>
        <html lang="zh-CN">
        <head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
        <body><main class="slide">
          <div class="eyebrow">OPEN SOURCE</div>
          <h1 class="title">把来源和现状分开讲</h1>
          <section class="meta-table">
            <div class="meta-item"><div class="k">Origin</div><div class="v">__TOPIC__ upstream</div></div>
            <div class="meta-item"><div class="k">Repo</div><div class="v">replace with verified URL</div></div>
            <div class="meta-item"><div class="k">License</div><div class="v">replace after verify</div></div>
            <div class="meta-item"><div class="k">Latest</div><div class="v">replace after verify</div></div>
          </section>
          <div class="footer"><span>07</span><span>别把未核实信息写死</span></div>
        </main></body></html>
        """
    ).strip()
    + "\n",
}


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
        parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
        parser.add_argument("--rate", default="+2%")
        parser.add_argument("--pitch", default="+0Hz")
        parser.add_argument("--force", action="store_true")
        return parser.parse_args()


    async def synthesize(text: str, out_path: Path, voice: str, rate: str, pitch: str) -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(str(out_path))


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
            if out_path.exists() and not args.force:
                continue
            print(f"[tts-preview] {item['id']} -> {out_path}")
            await synthesize(item["voice"], out_path, args.voice, args.rate, args.pitch)


    if __name__ == "__main__":
        asyncio.run(main())
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
            audio = root / "audio" / f"{seg_id}.mp3"
            if not audio.exists():
                raise FileNotFoundError(f"Missing audio: {audio}")
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
                    html_name = Path(placeholder_html).stem
                    image = root / "slide_png" / f"{html_name}.png"
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

    $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (-not (Test-Path $edge)) {
      throw "Edge not found at $edge"
    }

    $slidesDir = Join-Path $Root "slides"
    $outDir = Join-Path $Root "slide_png"
    New-Item -ItemType Directory -Force $outDir | Out-Null

    $files = Get-ChildItem $slidesDir -Filter "*.html" | Sort-Object Name
    foreach ($file in $files) {
      $png = Join-Path $outDir ($file.BaseName + ".png")
      if ((Test-Path $png) -and -not $Force) {
        continue
      }

      $uri = "file:///" + ($file.FullName -replace "\\", "/")
      Write-Output "[slide] $($file.Name) -> $png"
      & $edge `
        --headless=new `
        --disable-gpu `
        --hide-scrollbars `
        --run-all-compositor-stages-before-draw `
        --virtual-time-budget=3000 `
        --force-device-scale-factor=1 `
        --window-size=1600,900 `
        --screenshot="$png" `
        "$uri" | Out-Null
    }
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
    & $python (Join-Path $Root "scripts\generate_tts_edge.py") --root $Root
    & (Join-Path $Root "scripts\render_slides.ps1") -Root $Root
    & $python (Join-Path $Root "scripts\assemble_video.py") --root $Root
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

        for required in [project_path, segments_path, notes_path]:
            if not required.exists():
                hard_failures.append(f"missing required file: {required}")

        if hard_failures:
            for item in hard_failures:
                print(f"[FAIL] {item}")
            sys.exit(1)

        project = json.loads(project_path.read_text(encoding="utf-8"))
        segments = json.loads(segments_path.read_text(encoding="utf-8"))

        if project.get("voice_provider") in {"preview-edge-tts", "edge-tts"}:
            warnings.append("voice_provider 仍是预览级 TTS；适合粗剪，不建议直接发布")

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
            warnings.append("没有 demo 段；如果这是讲解型视频，建议至少保留一段实机录屏")

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


def render_template(content: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        content = content.replace(f"__{key}__", value)
    return content


def build_project_json(topic: str, slug: str) -> str:
    data = {
        "topic": topic,
        "slug": slug,
        "output_name": f"{slug}.mp4",
        "audience": "B站上的 Codex / OpenClaw / agent / automation 爱好者",
        "visual_style": "ios18-glass-minimal",
        "tone_rules": ["少官话", "句子短", "缺点直说", "画面字少", "先能不能用，再讲设计"],
        "voice_provider": "preview-edge-tts",
        "voice_quality_bar": "publish_requires_natural_humanlike_speech",
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_segments_json(topic: str) -> str:
    segments = [
        {
            "id": "01",
            "type": "slide",
            "html": "slides/01-hook.html",
            "voice": f"这期聊 {topic}。先看它能做什么，再看它为什么有用，最后直接看 demo。",
        },
        {
            "id": "02",
            "type": "slide",
            "html": "slides/02-problem.html",
            "voice": "很多任务不是模型不会想，而是最后一步没有 API、没有 DOM，也没有靠谱 CLI。",
        },
        {
            "id": "03",
            "type": "slide",
            "html": "slides/03-capabilities.html",
            "voice": "它的核心很直接，会看屏幕，会点，会输，会切窗口，还会回头验结果。",
        },
        {
            "id": "04",
            "type": "slide",
            "html": "slides/04-flow.html",
            "voice": "真正值钱的不是命令数量，而是 coordinator、UI worker、lock、overlay 这一整套受控执行结构。",
        },
        {
            "id": "05",
            "type": "slide",
            "html": "slides/05-pros-cons.html",
            "voice": "优点是闭环和稳，缺点也很明显，真实 UI 天生比 API 慢，高思考 UI worker 更稳，但也更慢。",
        },
        {
            "id": "06",
            "type": "slide",
            "html": "slides/06-demo.html",
            "voice": "下面不空谈，直接看一次从进入受控态到结果验证的完整 demo。",
        },
        {
            "id": "07",
            "type": "demo",
            "video": "demo/demo.mp4",
            "placeholder_html": "slides/06-demo.html",
            "voice": "这里替换成你的实机旁白。把关键动作、验证点和结束态讲清楚。",
        },
        {
            "id": "08",
            "type": "slide",
            "html": "slides/07-open-source.html",
            "voice": "最后把开源情况讲清楚，来源、仓库、许可证和最新状态分开核实，别混着讲。",
        },
    ]
    return json.dumps(segments, ensure_ascii=False, indent=2) + "\n"


def build_publish_notes(topic: str) -> str:
    return dedent(
        f"""
        # 标题候选

        1. {topic} 到底值不值得上手？
        2. 不靠 API，也能把事做完？{topic} 实机讲解
        3. {topic}：能力、架构、缺点、demo 一次讲清

        # 建议标题

        {topic}：能力、架构、缺点、demo 一次讲清

        # 简介

        这期视频会讲：

        - 它到底能做什么
        - 它补的是哪一层
        - 它为什么不是普通自动化脚本
        - 它的缺点是什么
        - 一段端到端实机 demo

        # 标签建议

        - codex
        - openclaw
        - ai agent
        - 自动化
        - windows
        - 开源项目

        # 备注

        - 风格统一：iOS 18 毛玻璃极简风
        - 画面字少于旁白
        - 如果配音仍是 preview-edge-tts，不要直接发
        """
    ).lstrip()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if root.exists() and any(root.iterdir()) and not args.force:
        raise SystemExit(f"Target directory already exists and is not empty: {root}")

    mapping = {"TOPIC": args.topic}

    for rel in ["content", "slides", "scripts", "audio", "clips", "slide_png", "demo"]:
        (root / rel).mkdir(parents=True, exist_ok=True)

    write_text(root / "content" / "project.json", build_project_json(args.topic, args.slug))
    write_text(root / "content" / "segments.json", build_segments_json(args.topic))
    write_text(root / "publish_notes.md", build_publish_notes(args.topic))
    write_text(root / "slides" / "base.css", BASE_CSS)
    for name, content in SLIDES.items():
        write_text(root / "slides" / name, render_template(content, mapping))

    write_text(root / "scripts" / "generate_tts_edge.py", GENERATE_TTS_EDGE)
    write_text(root / "scripts" / "assemble_video.py", ASSEMBLE_VIDEO)
    write_text(root / "scripts" / "render_slides.ps1", RENDER_SLIDES)
    write_text(root / "scripts" / "render_all.ps1", RENDER_ALL)
    write_text(root / "scripts" / "quick_check.py", QUICK_CHECK)

    print(f"[ok] scaffold created at {root}")


if __name__ == "__main__":
    main()
