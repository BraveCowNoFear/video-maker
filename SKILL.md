---
name: video-maker
description: End-to-end B 站视频制作主 skill。用于起项目、生成讲稿与画面、优先走本地 Qwen3-TTS 终版配音、导出成片，并在本地 QA 后把发布信息整理给 B 站上传流程。
---

# Video Maker

这是当前唯一主入口。历史旧入口已经迁移并删除，默认只使用 `video-maker`。

如果任务包含真实 B 站上传、Edge 页面操作、桌面点击、拖拽或其他可见 UI 控制，同时也要用 `desktop-control-for-windows`。

## Use This Skill For

- 从零起一个 B 站讲解视频工程
- 升级旧的 B 站讲解视频工程到本地 Qwen / ElevenLabs / Edge 三路可切换的配音链路
- 在本地完成脚本、画面、配音、装配、发布元数据整理
- 准备交给 `desktop-control-for-windows` 的 UI worker 去上传 B 站

如果用户要的是纯短视频生成、数字人、或者完全不需要可编辑项目结构的 text-to-video，不用这个 skill。

## Main Flow

### 1. Bootstrap or upgrade

新项目：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\.agents\skills\video-maker\scripts\bootstrap_project.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project" `
  --topic "desktop-control-for-windows" `
  --slug "desktop-control-for-windows-bilibili"
```

旧项目升级：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\.agents\skills\video-maker\scripts\upgrade_project.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project"
```

### 2. Edit the core files

- `content/project.json`
- `content/segments.json`
- `slides/*.html`
- `publish_notes.md`

### 3. Render locally

先看环境：

```powershell
& "C:\Users\Clr\Documents\Playground\output\my-video-maker-project\scripts\check_voice_env.ps1"
```

只做 QA：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\Documents\Playground\output\my-video-maker-project\scripts\quick_check.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project"
```

整条本地链路：

```powershell
& "C:\Users\Clr\Documents\Playground\output\my-video-maker-project\scripts\render_all.ps1" `
  -Root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project"
```

首次上机或换机器时，先读 [environment-setup.md](references/environment-setup.md)。

环境检查：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\.agents\skills\video-maker\scripts\doctor.py"
```

## Voice Strategy

默认优先级：

- 中文项目且本地 `voice_settings.local_qwen` 可用：优先 `local-qwen`
- 已验收的 ElevenLabs API voice：可走 `elevenlabs-api`
- 已经人工审过并下载好的网页配音：显式走 `elevenlabs-web`
- 以上都不满足：退回 `edge-preview`

注意：

- `auto` 现在默认优先本地 Qwen，不会因为机器上有 `ELEVENLABS_API_KEY` 就把整条链路卡在网页人工配音上
- `scripts/generate_tts_publish.py --provider elevenlabs-web` 仍然保留，适合你已经手工选好网页 voice 的场景
- `scripts/generate_tts_local_qwen.py` 会复用 `project.json` 里的 `voice_settings.local_qwen`

## Demo Strategy

- 新项目默认保留 demo 段
- 如果 `demo/demo.mp4` 还没录，`quick_check.py` 只给 warning
- `render_all.ps1` 会先用 `placeholder_html` 占位页把整条链路跑通

这能保证项目“先能闭环出片”，再换成真实 demo。

## Publish Handoff

先整理发布元数据：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\Documents\Playground\output\my-video-maker-project\scripts\prepare_publish_job.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project"
```

它会输出：

- `publish/bilibili_publish_job.json`

上传到 B 站时：

- 默认让 `desktop-control-for-windows` 的专用 UI worker 读取这份 JSON
- 用用户当前已登录的 Edge 会话上传
- 只有在本地 QA 通过、视频文件存在、发布元数据已准备好之后，才进入上传阶段

## Dependency Rules

- 只做脚手架、讲稿、配音、装配、QA：用 `video-maker`
- 进入真实桌面或真实网页上传：同时用 `desktop-control-for-windows`
- 如果 `desktop-control-for-windows` 缺失，不要声称“已具备全自动发布”；应明确说明目前只具备本地出片能力
- 如果换了一台机器，先运行 `scripts/doctor.py`，再决定是否能直接走 `local-qwen` 或 B 站自动上传

## Working Rules

- 默认中文 tech explainer 先追求可稳定复用，再追求单次最优音色
- 重模型、虚拟环境、权重目录属于本地项目/机器资产，不直接塞进 skill 仓库
- skill 里只沉淀：编排逻辑、脚手架、QA、发布元数据、调用接口
- 项目文件保持 UTF-8，Windows 路径默认友好
- 涉及 B 站真实上传时，不要让 coordinator 自己碰实时桌面；交给单一 UI worker
