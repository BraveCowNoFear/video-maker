# Video Maker

[English](./README.md) | [简体中文](./README.zh-CN.md)

`video-maker` 是一个面向 Codex 的 skill，用于在 Windows 上完成 B 站讲解类视频的端到端制作。

它围绕一个很实际的目标构建：

- 初始化可复用的视频项目
- 先锁内容合同，再编译镜头和页面
- 渲染幻灯片画面
- 优先使用本地 Qwen3-TTS 生成旁白
- 必要时回退到 Edge 预览
- 在本地拼装最终 MP4
- 为 B 站上传 worker 准备结构化发布元数据

当前新项目默认视觉系统为 `Quiet Glass Lab v3`：以黑色碳感底色和荧光酸绿为主的磨砂玻璃风格，但它是内容优先的提示词包，不是固定模板库。

## 仓库内容

- `SKILL.md`：skill 入口和操作说明
- `scripts/bootstrap_project.py`：自包含项目初始化脚本
- `scripts/bootstrap_video_project.py`：基础 B 站视频脚手架生成器
- `scripts/upgrade_project.py`：优先本地 Qwen 的升级路径和发布辅助脚本
- `references/`：语音、工作流和验收说明
- `references/agent-orchestration.md`：推荐的主 agent / 子 agent 内容生产流程
- `references/video-acceptance-rubric.md`：最终渲染或发布前的 reviewer agent 验收标准
- `references/quiet-glass-lab-v3.md`：内容优先的 Liquid Glass 规则和设计 token
- `references/quiet-glass-lab/`：黑绿版 Liquid Glass 默认可复用 HTML/CSS 幻灯片模板
- `references/bilibili-tech-explainer-workflow.md`：默认的 8 段式讲解视频工作流
- `agents/openai.yaml`：launcher 元数据
- `scripts/doctor.py`：环境与依赖检查脚本

## 作为 Skill 安装

把这个仓库 clone 到共享 skills 目录，或者给它创建 junction / symlink。

这台机器族推荐的共享位置：

- `C:\Users\Clr\.agents\skills\video-maker`

典型目录结构：

```text
C:\Users\...\skills\
├── video-maker\
└── desktop-control-for-windows\
```

`video-maker` 是生产编排器，但它本身不是完整的桌面自动化栈。

## 必需的配套 Skill

如果要真正把视频发到 B 站，这个仓库需要和下面的 skill 搭配使用：

- `desktop-control-for-windows`

原因：

- `video-maker` 负责项目脚手架、旁白、渲染、质检和发布元数据
- `desktop-control-for-windows` 负责已登录 Windows / Edge 环境中的真实 B 站上传界面操作

如果没有 `desktop-control-for-windows`，本地渲染仍然能做，但自动发布流程无法完成。

## 外部运行时资产

这个仓库刻意不内置体积较大的本地运行时资产。

下面这些内容应保留在 skill 仓库之外：

- Qwen 模型权重
- Qwen TTS 的 Python 虚拟环境
- 生成出来的视频项目产物
- 浏览器登录态

在当前“本地 Qwen 优先”的配置里，生成出来的项目会期望 `voice_settings.local_qwen` 指向本地 helper 脚本和 Python 可执行文件。当前机器上的可用示例是：

- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe`
- `C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py`

这些路径都可以在每个生成项目的 `content/project.json` 中调整。

## 环境检查清单

- 已安装 Microsoft Edge
- 已安装 `ffmpeg`，最好位于 `C:\Program Files\File Converter\ffmpeg.exe`
- 如果希望中文自动模式直接使用可发布质量的本地 TTS，需要准备好本地 Qwen 运行时
- 如果希望自动上传 B 站，需要安装 `desktop-control-for-windows`
- 如果希望自动发布，需要有已登录 B 站的 Edge 会话

运行内置检查器：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py"
```

或者检查某个具体的生成项目：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\path\to\video-maker\scripts\doctor.py" `
  --project-root "C:\path\to\my-video-project"
```

## 架构

这个仓库只保留可复用的编排逻辑。

它不会把这些体积较大的本地运行时资产直接放进仓库：

- Qwen 模型权重
- Python 虚拟环境
- 本地浏览器会话
- 各项目自己的音频、素材和渲染结果

这些内容应保留在本机或每个具体的视频项目目录中。

## 默认语音路径

对于中文旁白，只要 `voice_settings.local_qwen` 准备好了，自动模式现在会优先使用本地 Qwen。
生成出的本地 Qwen 路径不只是复用 `voice_settings.local_qwen`，还会把 `voice_persona` 和 `voice_consistency` 编译成显式的每次运行语音锁，确保 helper 在每个分段里都拿到同一个说话人、同一套节奏基线和同一条验收约束。

Provider 优先级：

1. `local-qwen`
2. `edge-preview`

## 内容系统

当前推荐的生产拆分方式是：

1. `chief-editor` 负责整期内容合同
2. 内容默认串行走 `outline -> depth -> detail -> narration-polish`
3. `chief-editor` 再编译 `style_contract`、`shot_intents` 和 `segments`

核心规则是：视频不能只停留在“这个词是什么意思”。每一期还应回答它为什么现在重要、它消除了什么误解，以及观众看完后能带走什么判断。

参见 [references/agent-orchestration.md](./references/agent-orchestration.md) 和 [references/bilibili-tech-explainer-workflow.md](./references/bilibili-tech-explainer-workflow.md)。

## 验收

视频不是“渲染成功了”就算可以发布。

推荐的最终闸门：

1. `content_depth`
2. `ui_supports_content`
3. `voice_consistency`

建议使用专门的验收 reviewer agent 来决定 pass / revise / hard fail，并把问题回流给对应 owner，而不是临时打补丁。
如果项目里只保存了语音一致性元数据，但执行路径没有把这层锁真正注入 TTS helper，那么 `voice_consistency` 应判定为 fail。

## 发布交接

在生成项目里运行 `scripts/prepare_publish_job.py`，会输出：

- `publish/bilibili_publish_job.json`

这个 JSON 预期交给专门的上传自动化流程，或者交给使用用户已登录 Edge 会话的 Codex UI worker。

预期的上传协作方式是：

1. `video-maker` 负责渲染并写出 `publish/bilibili_publish_job.json`
2. 协调 agent 调用 `desktop-control-for-windows`
3. UI worker 打开已登录的 Edge B 站上传页，并使用该 JSON 完成提交

## 面向 Agent 的集成说明

- 如果任务是本地项目创建、旁白、质检或视频拼装，使用 `video-maker`
- 如果任务跨入真实可见的 Windows UI 控制，同时使用 `desktop-control-for-windows`
- 如果是在新机器上首次配置或排障，先运行 `scripts/doctor.py`，再尝试完整发布链路
- 未来制作 B 站 tech explainer 时，优先使用默认的 `Quiet Glass Lab v3` 提示词包，只有题材确实不适合时再偏离

## 许可证

MIT
