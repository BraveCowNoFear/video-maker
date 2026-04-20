# Bilibili Tech Explainer Workflow

This is the default reusable workflow for 3-5 minute Chinese Bilibili explainer videos bootstrapped by `video-maker`.

## Default structure

Use this 8-segment order unless the topic strongly needs a demo or a case study:

1. `01-hook`
   Frame the audience problem in one sentence and preview the payoff.
2. `02-problem`
   Explain what the concept is before introducing dense vocabulary.
3. `03-capabilities`
   Clarify why it matters: constraint, payoff, cost.
4. `04-flow`
   Build a terminology map so the audience stops mixing layers.
5. `05-pros-cons`
   Deep dive into the single most commonly misunderstood keyword.
6. `06-demo`
   Contrast it with a nearby but non-equivalent concept.
7. `07-open-source`
   Explain the real tradeoffs and list the most common myths.
8. `08-choice`
   End on a practical, scenario-based recommendation.

## Main-agent framing

Before writing any segment, the main agent should lock three statements:

- `audience_problem`: 观众到底卡在哪个误解上
- `episode_thesis`: 这一期最核心的一句判断
- `higher_order_takeaway`: 除了定义以外，观众应该带走什么观察框架

默认要求：

- 不只解释术语，还要解释这个概念为什么在当下变重要
- 不只讲“是什么”，还要讲“为什么容易讲混”
- 不只给印象，还要给选择顺序

推荐把研究、质疑、UI、voice 四类任务分给 subagent，再由主 agent 统一回收。

## Visual system

Default theme: `Quiet Glass Lab v3`.

Default canvas:

- `16:9` only for standard Bilibili horizontal videos
- keep the composition safe for phone viewers even when the export canvas is desktop-wide

Visual goals:

- relaxed Chinese typography on oversized headlines: do not compress line-height or tracking until characters feel crowded
- mobile-first readability: treat the smallest explanatory copy as phone-safe text, not desktop-only detail
- let the primary left pane breathe with near-equal top, left, and bottom margins instead of floating mid-canvas
- black-carbon composition inspired by iOS 26 / iPadOS 26 Liquid Glass controls, sidebars, and floating panels
- avatar-inspired acid green accent (`#D0F810`) with near-black (`#101010`) details
- translucent dark glass surfaces instead of fake system screenshots or giant white canvases
- one visual center per page
- generous negative space
- muted chrome and restrained glass, not fake status bars or glossy “AI poster” gradients

Glass should map to information hierarchy:

- content layer: the one idea that this segment wants the viewer to remember
- support layer: one or two clarifying comparisons, data points, or labels
- chrome layer: navigation, framing, and ambient structure only

If the glass competes with the message, the page is overdesigned.

Avoid:

- empty lower-right filler zones, decorative bar charts, or chrome that adds no information
- tiny low-priority copy; if a label feels merely acceptable on desktop, it is still too small for Bilibili phone viewing
- loud purple-blue SaaS gradients
- fake system status bars with time / Wi-Fi / battery
- icon walls and decorative chip illustrations
- dense dashboards
- multiple equally loud cards fighting for attention

## Narration rules

- Default to short Chinese sentences.
- Explain the intuition first, terminology second.
- Say the downside directly; do not oversell.
- Keep each segment voice short enough to feel conversational.
- Keep the same narrator persona, emotional baseline, and speaking rhythm across all segments.

## Demo guidance

- Concept-first explainers may ship without a real demo segment.
- Tool or workflow explainers should add a demo clip only when it genuinely improves understanding.
- If a demo is missing, use the static 8-page structure to preserve pacing and finish on `08-choice`.

## Publish notes

Each project should keep:

- 2-3 title candidates
- one recommended title
- short description bullets
- tags
- style reminders

Prefer titles that promise clarity, distinctions, and practical guidance rather than hype.
