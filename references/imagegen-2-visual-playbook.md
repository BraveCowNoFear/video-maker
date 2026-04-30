# Imagegen 2 Visual Playbook

这份手册把 `imagegen` / GPT Image 2 的强项转成 `video-maker` 的可执行规则：让画面更漂亮、更有空间感、更像真实的科普视频，并让模型直接承担画面文字、公式、标签和 UI 状态；准确性由视觉核对和重生保证。

## Source Notes

- OpenAI model page: `gpt-image-2` 是高质量图像生成与编辑模型，支持文本和图像输入、图像输出，并支持灵活尺寸与高保真图像输入。
- OpenAI image generation guide: GPT Image 可做生成与编辑；Responses API 支持多轮编辑和灵活图像输入；可调 quality / size / format / compression；透明背景取决于模型支持。
- OpenAI image generation tool guide: `gpt-image-2` 支持灵活尺寸，但当前不支持透明背景；使用工具时主模型会优化提示词；图像生成支持多轮编辑和部分流式预览。
- B 站 / YouTube 科普视频观察：高质量科普通常不是“漂亮背景 + 旁白”，而是持续把抽象概念变成可见对象、空间关系、对比、过程和证据锚点。

## What Imagegen Is Best At

Use imagegen when the beat needs one of these:

- `tactile_anchor`: 把抽象概念变成一个有材质、尺度、光影的对象，例如“任务形状”“瓶颈”“队列”“内存墙”。
- `hero_silhouette`: 一个一眼能懂的主形态，可直接包含少量关键文字、标签和箭头。
- `mechanism_base`: 剖面图、爆炸图、分层结构、流动路径的底图。
- `scale_scene`: 用空间和参照物让观众感到“大/小/快/慢/多/少”。
- `contrast_key_visual`: 两个状态的情绪化对比，例如“顺流并行”和“来回搬运”。
- `chapter_bumper`: 章节转场或概念重置，不承担精确事实，但承担节奏和记忆点。
- `cover_base`: B 站封面主视觉，负责冲击力、形态、情绪和少量大字；逐字正确由视觉核对保证。
- `texture_or_depth_plate`: 给 Remotion 场景提供高质量材质、深度、空间背景或局部对象。

## Text And Symbol Rule

Default to direct imagegen rendering for:

- exact Chinese text
- formulas, code, terminal output, table values, axes, legends, units
- labels, component names, source marks, claim boundaries
- UI-like states and small explanatory callouts

The rule is simple: generate it in the image, inspect it visually, and regenerate if anything is wrong. Do not default to patching failed text with separate rendered layers.

Still keep source text, formulas, labels, data, and source refs in content artifacts so the reviewer knows what the image was supposed to say.

## Direct Imagegen Scene Pattern

Default production stack:

1. `imagegen_direct_render`: one strong bitmap containing the visual, short Chinese text, formulas, labels, numbers or UI state when needed.
2. `motion_shell`: Remotion React/CSS only for timing, cropping, transitions, parallax, subtitles, audio mounting or scene composition.
3. `proof_anchor`: when a claim depends on reality, insert a real screenshot/data/source frame rather than an AI substitute.
4. `visual_qa`: inspect actual pixels; regenerate imagegen outputs until text, symbols, crop and legibility pass.

This keeps production simple: imagegen makes the final visual; visual QA protects correctness.

## Prompt Recipe For Video Assets

Use short, role-labeled prompts:

```text
Use case: scientific-educational
Asset type: <scene hero base / mechanism base / cover base / texture plate>
Primary request: <one sentence describing the concept as a visible object>
Audience purpose: <what the viewer should understand faster after seeing it>
Subject: <main object or spatial metaphor>
Style/medium: polished 3D / cinematic editorial illustration / clean technical cutaway
Composition: 16:9, one clear focal point, readable text zones
Palette: black carbon base, sparse acid-lime highlight #D0F810, restrained neutrals
Text to render exactly: "<short Chinese title / labels / formula / code snippet>"
Constraints: no watermark, no unrelated logos, no fake source evidence, no extra decoration
QA instruction: all Chinese, formula symbols, labels, numbers and source marks must be visually checked; regenerate if wrong
```

For covers:

```text
Use case: ads-marketing
Asset type: Bilibili cover base
Primary request: <topic as a striking visual metaphor>
Composition: 16:9, bold thumbnail-readable silhouette, large readable Chinese text
Palette: near-black + acid-lime #D0F810 + restrained secondary contrast
Constraints: no small text, no fake brand marks, no watermark, no clutter, no UI screenshot cosplay; regenerate until text is exact
```

## Visual Narrative Patterns

Use imagegen to make content more alive:

- `wrong_model_vs_real_model`: 先给一个直觉上合理但错误的视觉，再揭示缺失变量。
- `inside_the_black_box`: 外部看不懂时，用剖面/爆炸图/半透明层让机制可见。
- `scale_jump`: 从人的尺度跳到芯片、网络、星球、毫秒或海量数据尺度。
- `bottleneck_reveal`: 先展示看似强大的系统，再高亮真正卡住的窄口。
- `counterfactual_pair`: 同一系统在两种条件下的结果并排，差异直接画进 imagegen 图里。
- `evidence_cutaway`: 把真实截图/数据锚点嵌进漂亮场景，但不伪造真实来源。
- `memory_object`: 给核心结论一个可记住的对象，比如“收费站”“传送带”“热管”“分拣中心”。

## Benchmark Without Copying

Before making a visual system, fill `visual_benchmark` inside `content/visual_asset_plan.json`:

- `reference_family`: 例如数学可视化、工程剖面、数据新闻、AI 工具实测、电影级产品片。
- `borrowed_pattern`: 借它的“认知动作”，例如逐层揭示、错误模型对照、证据锚点、尺度跳跃。
- `not_to_copy`: 不复制具体角色、画风、构图、品牌符号、固定 palette 或标志性转场。
- `evidence_carrier`: 这一期最可信的证明载体是什么：真实截图、论文图、公式、实测产物、源码片段、数据图、硬件结构。
- `asset_stack`: `imagegen direct render -> motion shell -> QA/regenerate` 中需要哪些层。
- `qa_risk`: 最容易出错的视觉点，例如中文标题、公式、假数据、过密标签、重复版式、伪造真实画面。

Borrow the thinking pattern, not the look.

## Key Visual Contract

每期视频应在 `content/visual_asset_plan.json` 里写 `key_visual`，让封面、片头、章节转场和结尾有同一个记忆锚点。

字段建议：

- `main_object`: 观众能记住的主物体或空间隐喻。
- `visual_question`: 这张图提出的问题张力。
- `thumbnail_promise`: 封面承诺视频会回答什么。
- `cover_text_candidates`: 1-3 个短句，由 imagegen 直接生成，视觉核对不通过就重生。
- `base_visual_prompt`: imagegen 封面/主视觉基底提示词。
- `text_and_symbol_plan`: 哪些中文、公式、代码、标签、数字、来源、UI 状态需要 imagegen 直接画对。
- `reuse_plan`: 片头、章节转场、结尾如何复用这个主视觉，并更换不同文字、符号或证据目标。
- `mobile_readability_check`: 缩略图尺寸下还能不能看清主物体和短句。

## Frontend Integration Rules

- Imagegen bitmap can be the whole visual surface when it carries the scene; Remotion mostly负责裁切、节奏、字幕、时间轴和组合。
- Never put long Chinese paragraphs directly on top of busy bitmap regions.
- Reserve safe zones for title, labels, formulas and source notes inside the imagegen prompt.
- Use CSS masks, soft shadows, depth blur, parallax, and clipped hero panels to integrate bitmap assets with Remotion scenes.
- Make the bitmap explain one thing and render the exact short text or symbols needed for that thing.
- Every high-effort bitmap needs a `visual_job`: `orient`, `compare`, `explain`, `prove`, or `hedge`.

## Quality Gates

`visual-qa-fixer` must check:

- the generated bitmap adds explanation, not just atmosphere
- the scene still works if all decorative glow is removed
- no fake data, fake UI, fake screenshot, fake instrument or fake source appears
- all text-like marks from imagegen are intended, readable, and exact; accidental text artifacts trigger regeneration
- cover base is thumbnail-readable at mobile size
- final cover text is generated by imagegen and visually verified; regenerate until correct

## Safe Research Boundary

When researching visual inspiration, keep searches and references focused on design, education, animation, storytelling, science communication, and platform presentation. Avoid security/offense/defense/incident-response topics unless the user explicitly requests a compliant, benign educational treatment.
