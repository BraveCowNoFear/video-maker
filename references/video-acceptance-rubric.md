# Video Acceptance Rubric

这份 rubric 给专门的 `acceptance-reviewer` 使用。目标不是“挑刺”，而是在出片前做最后一道 gate。

## 必过项

### 1. Content depth

通过标准：

- 不是只有定义，没有判断
- 有清晰的 audience problem
- 有一层 higher-order takeaway
- `08-choice` 真正给了观众可执行的判断顺序

打回信号：

- 全片都在解释术语
- 观众看完只知道名词，不知道为什么重要
- 收尾没有给选择方法

### 2. UI supports content

通过标准：

- 每页只有一个视觉中心
- 玻璃主要承担功能层，不是把正文全包起来
- 页面层级和叙事层级一致
- 没有假状态栏、无意义装饰、抢戏 chrome

打回信号：

- 玻璃卡片比主结论更显眼
- 页面像 UI 展示，不像内容表达
- 一页里有多个同样响的焦点

### 3. Voice consistency

Execution rule:
- Treat it as `revise` or `hard fail` when `voice_persona` / `voice_consistency` only exist in metadata but are not injected into the TTS helper call.

通过标准：

- 同一个 speaker / voice_id
- 同一 persona
- 情绪基线稳定
- 语速和停顿风格没有明显漂移

打回信号：

- 某一段突然更甜、更急、更兴奋
- 某一段像主播腔，另一段像客服腔
- 一段一个人设

## Reviewer output format

每次验收只给三类结论：

- `pass`
- `revise`
- `hard fail`

如果不是 `pass`，必须同时给：

- `owner`
- `reason`
- `fix direction`

推荐格式：

```text
[revise] voice_consistency
owner: voice-director
reason: 第 04 段和前后相比语速更急，句尾更硬，已经不像同一个人一口气讲完
fix direction: 回到统一 persona contract，只重生异常段，并与 01 段对齐
```

## Skill write-back

如果 reviewer 连续两次发现同类问题，应补一条可复用规则到 skill：

- 内容类 -> `references/bilibili-tech-explainer-workflow.md`
- UI 类 -> `references/quiet-glass-lab-v3.md`
- 配音类 -> `references/chinese-voice-rules.md`
