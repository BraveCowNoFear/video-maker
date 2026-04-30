---
name: video-maker
description: End-to-end B 站视频制作主 skill。用于起项目、内容研究、成稿润色、生成画面、优先走本地 Qwen3-TTS 整段配音、导出成片，并在本地 QA 后用 imagegen 生成封面、把发布信息整理给 B 站上传流程。
---

# Video Maker

如果任务包含真实 B 站上传、Edge 页面操作、桌面点击或拖拽，同时使用 `desktop-control-for-windows`。
如果任务包含视频封面、视觉资产、结构图、机制图或动画素材，同时使用 `imagegen`，并默认由 `visual-architect` 负责生成、`visual-qa-fixer` 负责看渲染结果后修正。
如果任务包含视频 composition、动画、字幕、音频挂载、时间轴或最终渲染，同时使用 `remotion-best-practices`；`video-maker` 只负责内容、资产、QA 与发布链路。
如果任务包含封面、关键视觉、结构图、机制图或动画位图素材，继续使用 `imagegen`；Remotion 只负责编排这些位图，不削弱生图能力。

## Use This Skill For

- 从零创建 B 站讲解视频工程
- 把旧工程升级到 content-first、master-track TTS、本地 QA、发布交付链路
- 生成脚本、画面、配音、导出视频、封面与发布元数据
- 准备交给 UI worker 的 B 站上传任务

## Main Flow

新项目：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\bootstrap_project.py" `
  --root "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project" `
  --topic "desktop-control-for-windows" `
  --slug "desktop-control-for-windows-bilibili"
```

旧项目升级：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\upgrade_project.py" `
  --root "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project"
```

环境检查：

```powershell
$skillRoot = "C:\Users\Clr\.codex\skills\video-maker"
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "$skillRoot\scripts\doctor.py"
```

整条本地链路：

```powershell
& "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project\scripts\render_all.ps1" `
  -Root "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project"
```

## Architecture

主 agent 是 `coordinator`，只做统筹、简单命令、任务包、合并、冲突仲裁和 go/no-go 决策；不要亲自写长文案、Remotion scene、视觉资产、封面、音频策略或验收报告。

核心 subagent 共 7 个：

1. `content-strategist`: 问题链、观众基线、开头承诺、证据图谱、故事脊柱和细节预算。
2. `script-writer`: 在内容合同锁定后写第一版完整口播稿。
3. `narration-polisher`: 在成稿之后专门去掉 AI 人机味、翻译腔和书面腔，让普通 B 站用户第一次听就懂；不新增事实，不改主张。
4. `visual-architect`: 生成 Remotion scene 设计、React/CSS motion 方案，按需用 `imagegen` 生成底图、结构图、机制图、动画素材和封面。
5. `visual-qa-fixer`: 专门看实际 Remotion frame samples 和封面图，发现错字、缺字、乱码、重叠、白边、坏裁切或过期封面时，直接重生 imagegen 图片或修 Remotion 代码，并重渲染到通过。
6. `production-engineer`: 负责 Qwen master-track、Remotion props、时间轴、音频挂载、渲染和导出。
7. `acceptance-reviewer`: 看实际截图、Remotion 代码、内容合同、证据链，并完整听完 master 音频，失败时打回对应 owner。

可选 subagent：真实上传 B 站时再启用 `publish-ui-worker`，只负责已登录 Edge 里的上传 UI，不参与内容生产。

如果当前运行环境不能委派 subagent，`coordinator` 只生成任务包并暂停或请求授权，不要把自己伪装成所有角色继续生产成品。

详细角色提示词见 `references/agent-orchestration.md`，不要把整套角色说明重复塞进主上下文。

## Required Artifacts

内容入口不是 `segments.json`，而是问题驱动的内容合同：

- `content/problem_contract.json`
- `content/audience_contract.json`
- `content/opening_contract.json`
- `content/meaning_contract.json`
- `content/outline_plan.json`
- `content/depth_contract.json`
- `content/detail_weave.json`
- `content/evidence_map.json`
- `content/script_draft.json`
- `content/narration_polish.json`
- `content/style_contract.json`
- `content/shot_intents.json`
- `content/visual_asset_plan.json`
- `content/segments.json`
- `remotion/input-props.json`
- `content/screenshot_plan.json`
- `content/visual_qa_report.json`
- `content/acceptance_report.json`
- `publish_notes.md`
- `publish/cover_prompt.md`

`segments.json` 是编译后的渲染产物，不是最早的思考入口。

## Content Rules

先读：

- `references/science-explainer-principles.md`
- `references/bilibili-tech-explainer-workflow.md`
- `references/bilibili-science-benchmark.md`
- `references/agent-orchestration.md`

默认先用问题驱动提示词锁定：

- `root_question`
- `false_easy_answer`
- `why_it_is_hard`
- `what_would_change_the_viewer_judgment`
- `answer_shape`
- `primary_evidence_carrier`
- `supporting_evidence_carrier`

每个核心 claim 必须进入 `evidence_map`，至少声明 `support_type`、`confidence_level`、`proof_anchor`、`source_refs`、`overclaim_boundary`。顺口但证据不老实，不通过。

`script-writer` 写出的 `script_draft.json` 只能使用已锁定合同和来源；`narration-polisher` 只改表达自然度、可听性和普通用户理解成本，发现逻辑站不住时标记 `needs_content_revisit`。

内容深度默认按“判断改变顺序”组织：`false_easy_answer -> contradiction -> mechanism_model -> proof_anchor -> boundary -> transfer_rule`。不要只排知识点；每期必须明确观众看完以后能多做出的一个判断。

## Visual Rules

视觉阶段先读：

- `remotion-best-practices` skill
- `web-design-engineer` skill
- `references/imagegen-2-visual-playbook.md`
- `references/explainer-visual-asset-rules.md`
- `references/quiet-glass-lab-v3.md`

默认视觉方向是：content-first、黑绿、极简、可读、克制的 iOS-inspired frosted science deck。`Quiet Glass Lab` 只是品牌约束，不是固定页面模板；Remotion 是唯一生产级视频 composition / animation / subtitle / audio / timeline / render 路径。

每个 `shot_intent` 必须声明：

- `story_turn`: `false_easy_answer` / `contradiction` / `mechanism_model` / `proof_anchor` / `boundary` / `transfer_rule`
- `visual_job`: `orient` / `compare` / `explain` / `prove` / `hedge`
- `primary_representation`: `imagegen` / `remotion` / `react-css` / `latex` / `animation` / `real-screenshot` / `hybrid`
- `evidence_carrier`
- `viewer_should_notice`

每期默认在 `content/visual_asset_plan.json` 里写清 `visual_benchmark` 和 `key_visual`：前者说明借鉴哪类科普视觉模式、借它的认知动作而不是画风；后者锁定封面、片头、章节转场和结尾复用的主视觉记忆点。不要为它们单独新增文件。

`imagegen` / GPT Image 2 的主力用途是高质量成图：封面、概念视觉、材质/空间感、剖面/爆炸图、机制图、章节关键视觉、对比隐喻、motion texture，以及短中文、公式、代码、标签、数字、来源和 UI 状态。不要只生成气氛图；每张位图都必须有 `visual_job` 和文字/符号核对目标。

公式、尺寸、箭头、部件名、关键数字、来源和可读标签默认直接由 `imagegen` 生成；`visual-qa-fixer` 逐项视觉核对，不准确就重新生成。Remotion React/CSS 只作为编排、动效、字幕、时间轴、源文本或验收基准，不作为默认文字修补层。

封面和 16:9 主视觉默认用 16:9 构图，中文大字也由 imagegen 直接生成；如果走显式 CLI/API fallback，草稿用低质量快速探索，最终封面/密集信息图用高质量。不要默认要求 `gpt-image-2` 透明背景；需要透明资产时按 `imagegen` skill 的 chroma-key + 本地抠图流程，复杂透明再另行确认 fallback。

`visual-architect` 生成后，必须让 `visual-qa-fixer` 读取实际 `remotion_frames/*.png` 和 `publish/cover.png`。它看的是渲染像素，不是只读源码；中文、公式、代码、标签、数字、来源或 UI 状态不对，默认重新调用 `imagegen`，直到 `content/visual_qa_report.json` 没有 blocking finding。

禁止连续用“旁白 + 氛围图/壁纸”撑场。极简不是少做，而是只留下能增加理解的东西。

## Voice Strategy

- 中文项目且本地 `voice_settings.local_qwen` 可用：优先 `local-qwen`
- 本地 Qwen 不可用：退回 `edge-preview`
- 默认生成一条 `audio/master.*`
- 发布前必须完整听完 master 音频；任何位置出现乱码、火星语、非中文热场、外语、无意义音节、明显断裂或语速明显过慢，直接判失败并重生
- `voice_profile.full_audio_review_status` 必须单独写成 `passed` 才能代表完整 master 已听完；只抽听开头或中段不能替代完整听审
- 本地 Qwen master-track 生成必须带硬超时和 `voice_jobs/qwen_master_status.json` 状态 manifest；超时或失败时不要拼接不同 TTS 来源，先重生单一 master 或临时切到 Edge preview 保持全片声线一致
- 语速量化默认按上期 CUDA 成片校准：目标约 `260` 中文字/分钟，可接受区间 `240-285` 中文字/分钟；这里的“中文字”按最终 `tts_text` 里的 CJK 汉字数统计
- 默认 `model_dir` 使用 Qwen `12Hz-1.7B-CustomVoice`

语音细则见 `references/chinese-voice-rules.md`。

## Cover And Publish

封面只在本地 QA 通过、标题候选锁定之后生成。

- 默认路径：`publish/cover.png`
- 默认生成 owner：`visual-architect`
- 默认修图/验字 owner：`visual-qa-fixer`
- 默认方式：`imagegen` 直接生成封面主视觉和中文标题；逐字视觉确认，不对就重生
- 禁止用 `cover.html`、HTML 截图、SVG 占位图、canvas、Remotion 截图或 slide 截图冒充正式封面

默认封面提示词保持简洁：

```text
帮我设计一个视频封面，视频标题是“【标题】”，这是b站视频，你可以发挥你的设计审美，可以不需要原封不动的出现视频标题哦！极简风格，有视觉冲击力，主题色黑和荧光绿#【实际logo色号】
```

整理发布元数据：

```powershell
& "C:\Users\Clr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project\scripts\prepare_publish_job.py" `
  --root "C:\Users\Clr\Desktop\Video Maker\bilibili projects\my-video-maker-project"
```

上传到 B 站时：

- 默认让 `desktop-control-for-windows` 的单一 UI worker 读取 `publish/bilibili_publish_job.json`
- 使用用户当前已登录的 Microsoft Edge 正式版，不要改用 Edge Dev
- 上传封面后必须截图确认 B 站表单已显示自定义封面；否则不能点击最终发布
- 如果只是预期时长和最终时长不一致，但内容、中文听感、视觉 QA、封面和发布元数据都通过，时长本身不阻塞发布

## Acceptance

本地 QA 不是只看导出成功。必须检查：

- 内容合同是否回答了根问题
- 证据链是否覆盖核心 claim
- 每个画面是否承担认知工作
- `content/visual_qa_report.json` 是否完成且无 unresolved blocking findings
- Remotion frame samples 是否真实可读、无重叠、无白边、无廉价 AI 视觉套路
- 公式、数字、标签和箭头是否可追溯
- master 音频是否已经完整听完并通过中文听感检查
- 发布资产、封面和 `publish/bilibili_publish_job.json` 是否齐全

验收细则见 `references/video-acceptance-rubric.md`。
