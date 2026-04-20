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

默认新项目已经带上统一的 `Quiet Glass Lab v3` 模板和 8 段 tech explainer 结构。概念型 B 站科普优先在这个骨架上改，不要每次重新发明页面风格。

如果用户明确要求“用 subagent 研究内容/UI/声音”，推荐编排是：

- 主 agent：定论点、定 segment map、做最终合稿
- 内容 subagent：查事实、找误区、补相邻概念
- 质疑 subagent：逼出更高一层的观点，不让脚本只停留在定义
- UI subagent：把内容层级映射成玻璃层级
- voice subagent：锁定声音 persona 和一致性策略

默认先读：

- `references/agent-orchestration.md`
- `references/bilibili-tech-explainer-workflow.md`
- `references/chinese-voice-rules.md`
- `references/quiet-glass-lab-v3.md`
- `references/video-acceptance-rubric.md`

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
- `scripts/generate_tts_local_qwen.py` 和 `scripts/generate_tts_publish.py` 都会复用 `project.json` 里的 `voice_settings.local_qwen`
- 同时把顶层 `voice_persona` / `voice_consistency` 编译成显式的一致性锁提示词，再传给本地 Qwen helper；这一步缺失时，`acceptance-reviewer` 应直接判 `voice_consistency` 不通过

## Demo Strategy

- 工具 / 工作流讲解可以保留 demo 段
- 概念型科普可以直接用 8 段静态 explainer 骨架收尾，不强制带 demo
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

- `Quiet Glass Lab v3` 默认继续沿用这次确认的极简黑绿方向：画布固定 `16:9`；不做假状态栏；中文大标题字距和行距不要压到发挤；最小说明文字再保守放大一档，优先保证手机可读性；主视觉面板优先做出上左下三边接近等宽的呼吸感
- 默认中文 tech explainer 先追求可稳定复用，再追求单次最优音色
- 默认视觉模板统一走 `Quiet Glass Lab v3`：黑碳底、`#D0F810` 酸性荧光绿点题、iOS 26 / iPadOS 26 风格的 Liquid Glass 浮层与极简 chrome、每页一个视觉中心
- 默认 4-5 分钟 explainer 先走 8 段结构：hook、definition、why, map, deep dive, contrast, tradeoff, choice
- UI 不只是“看起来像苹果”，而是要把 glass 用在内容分层上：焦点内容尽量直接说话，辅助信息才进入玻璃层，chrome 要主动后退
- 每一期除了概念本身，还要多给观众半层思考：为什么这件事在今天重要，它改变了什么判断顺序
- 成片前默认加一个专门的 `acceptance-reviewer`：只看内容深度、UI 是否服务内容、配音是否一致；不通过就打回对应 agent，并把复盘沉淀回 skill
- 重模型、虚拟环境、权重目录属于本地项目/机器资产，不直接塞进 skill 仓库
- skill 里只沉淀：编排逻辑、脚手架、QA、发布元数据、调用接口
- 项目文件保持 UTF-8，Windows 路径默认友好
- 涉及 B 站真实上传时，不要让 coordinator 自己碰实时桌面；交给单一 UI worker
