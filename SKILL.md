---
name: video-maker
description: End-to-end B 站视频制作主 skill。用于起项目、串行研究内容、生成画面、优先走本地 Qwen3-TTS 整段配音、导出成片，并在本地 QA 后把发布信息整理给 B 站上传流程。
---

# Video Maker

如果任务包含真实 B 站上传、Edge 页面操作、桌面点击、拖拽或其他可见 UI 控制，同时也要用 `desktop-control-for-windows`。

## Use This Skill For

- 从零起一个 B 站讲解视频工程
- 升级旧的 B 站讲解视频工程到 `content-driven beats + serial content research + master-track TTS` 链路
- 在本地完成脚本、画面、配音、装配、QA、发布元数据整理
- 准备交给 `desktop-control-for-windows` 的 UI worker 去上传 B 站

## Main Flow

新项目：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\bootstrap_project.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project" `
  --topic "desktop-control-for-windows" `
  --slug "desktop-control-for-windows-bilibili"
```

旧项目升级：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\upgrade_project.py" `
  --root "C:\Users\Clr\Documents\Playground\output\my-video-maker-project"
```

### 2. Build content before scenes

先不要直接写固定页模板，也不要先挑 UI 模块。先锁内容 contract，再把内容研究结果编译成 render-ready 场景。

按阶段加载参考，避免一次把无关上下文全吃进来：

- 内容研究：`references/agent-orchestration.md` + `references/bilibili-tech-explainer-workflow.md`
- 视觉阶段：`references/quiet-glass-lab-v3.md`
- 配音阶段：`references/chinese-voice-rules.md`
- 验收阶段：`references/video-acceptance-rubric.md`

- `content/project.json`
- `content/outline_plan.json`
- `content/depth_contract.json`
- `content/detail_weave.json`
- `content/style_contract.json`
- `content/shot_intents.json`
- `content/segments.json`
- `publish_notes.md`

最小流程：

- 内容研究默认必须按 `outline-researcher -> depth-builder -> detail-filler` 串行执行
- 如果当前回合明确允许 subagent，就按这个顺序真正委派
- `outline-researcher` 只锁 coverage shape
- `depth-builder` 只把 `provisional_claim` 升级成判断 contract
- `detail-filler` 只补支撑细节，不改主线
- `narration-polisher` 只修口播自然度，不新增事实或主张
- `chief-editor` 先编译 `shot_intents`，再让 `visual-architect` 依据 `style_contract + shot_intents` 生成 scene prompt
- 视觉系统只规定材质逻辑、层级、可读性和禁忌项，不规定固定模块清单
- `segments.json` 是最终编译产物，不是最早的思考入口

角色细则直接看 `references/agent-orchestration.md`，不要把整套角色提示词再重复塞回当前上下文。

### 3. Generate scenes and render locally

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
如果本地 Qwen 需要加速，默认按其中已经验证过的 Windows 方案安装 `torch==2.10.0+cu130` 和对应 `flash-attn` wheel，不要先走源码编译。

环境检查：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\doctor.py"
```

## Voice Strategy

- 中文项目且本地 `voice_settings.local_qwen` 可用：优先 `local-qwen`
- 本地 Qwen 不可用：退回 `edge-preview`
- 如果 provider 支持长段单次合成，默认生成一条 `audio/master.*`
- 默认直接整条单次合成 `audio/master.*`；如果失败，优先改脚本、文案或环境，不保留 scene-level 音频主路径
- 顶层 `voice_persona` / `voice_consistency` 必须真正注入 TTS 执行链
- `auto` 现在默认只在 `local-qwen` 和 `edge-preview` 之间切换
- 默认 `model_dir` 统一回到 Qwen `12Hz-1.7B-CustomVoice`

## Visual Strategy

- 默认视觉方向继续沿用 `Quiet Glass Lab`，但它现在明确是 `黑绿 + iOS 18-inspired frosted glass science deck` 的风格提示词包和基础 token，不是固定页面清单
- 默认 scene 编译链路是 `style contract -> shot intent -> scene prompt`
- 默认允许每次版式、信息分布和模块数量不同；只要整体仍满足 content-first、phone-readable、Apple-informed-but-not-cosplay
- `slides/base.css` 与脚手架初始 HTML 只保留中性渲染外壳，不预置任何风格模板或结构骨架
- `16:9` 画布仍是默认横版输出
- 主阅读平面保持 `solid / near-solid`、深色、稳定、高对比
- 毛玻璃可以用于图解卡、数据卡、对照卡、标签和短时解释层，但正文必须有更实的承载底
- 使用大圆角模块、soft blur、细亮边、克制高光与深色空间背景
- 不做假状态栏、不做 Apple 截图 cosplay、不做 `glass-on-glass`、不做手机 App 界面复刻

详细规则直接引用 `references/quiet-glass-lab-v3.md`。

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

## Working Rules

- 内容 contract 优先于模板
- 内容 research 优先于细节
- 视觉 contract 优先于模块
- 配音 contract 优先于切段
- skill 里只沉淀：编排逻辑、脚手架、QA、发布元数据、调用接口
- 重模型、虚拟环境、权重目录属于本地项目/机器资产，不直接塞进 skill 仓库
- 项目文件保持 UTF-8，Windows 路径默认友好
- 涉及 B 站真实上传时，不要让 coordinator 自己碰实时桌面；交给单一 UI worker
