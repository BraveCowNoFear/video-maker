# Video Acceptance Rubric

一期视频不是因为“能导出 mp4”就算通过。

默认 reviewer 至少要看九项：

- `coverage_complete`
- `content_depth`
- `meaning_gain`
- `narration_naturalness`
- `ui_supports_content`
- `visual_screenshot_bug_review`
- `remotion_content_authenticity`
- `content_authenticity`
- `formula_legibility`
- `diagram_annotation_truthfulness`
- `screenshot_traceability`
- `voice_consistency`

## 1. coverage_complete

必须确认全片完成了当前 coverage contract 里要求回答的问题，并且没有漏掉主线需要的说明项。

如果 coverage contract 里明确要求的关键问题没有被回答，直接不通过。

## 2. content_depth

建议把 `content_depth` 做成 7 条检查：

1. `audience_problem_locked`
2. `thesis_is_clear`
3. `episode_scope_is_clear`
4. `ending_resolves_core_question`
5. `tradeoff_present`
6. `misconception_resolved`
7. `support_density_ok`
8. `opening_strength_without_distortion`
9. `claim_source_traceability`
10. `audience_level_fit`

判定规则：

- 前 4 项任一失败：`hard fail`
- 非关键项失败 1-2 个：`revise`
- 全通过：`pass`

## 3. meaning_gain

建议把 `meaning_gain` 做成 4 条检查：

1. `worth_watching_now`
2. `meaningful_scale_jump`
3. `transferable_takeaway`
4. `human_weight_present`

判定规则：

- 前 2 项任一失败：`hard fail`
- 后 2 项失败 1 个：`revise`
- 全通过：`pass`

## 4. narration_naturalness

必须确认：

- 每一拍的旁白第一次听就顺，不需要观众回放找主语
- 因果链、转折词和代词指向是清楚的
- 没有明显翻译腔、模板腔、营销腔或模型自述口吻
- 句长可口播，重音位置明确，不是一长串书面复句
- 自然但不油，不会为了“像真人”乱加口头禅或夸张情绪

如果问题来自内容合同本身而不是措辞层，应判 `revise` 并路由回上游，不要让 reviewer 自己重写。

## 5. ui_supports_content

必须确认：

- 每页只有一个视觉中心
- 主内容层比 glass chrome 更稳、更重要
- 页面手机截图仍可读
- `visual_asset_plan.visual_benchmark` 借的是认知模式，不是复制某个创作者的画风、角色、构图或转场
- `visual_asset_plan.key_visual` 的主视觉在封面、片头、章节转场或结尾中形成可识别记忆点
- 每个 imagegen 资产都有明确 `asset_job`、目标文字/公式/标签和视觉核对记录
- 风格像是被 Apple 设计逻辑启发，而不是在 cosplay Apple
- glass 没有替内容抢戏
- `style_contract -> shot_intent -> Remotion scene` 链路完整存在
- 每个 segment 都有明确 `shot_role`，不是只会重复某种页面模板

## 6. visual_screenshot_bug_review

必须用实际导出的 Remotion frame samples / 视频截图验收，而不是只看源码想象效果。

最低要求：

- 抽查多张不同段落截图，覆盖开头、中段、结尾和高信息密度页面
- 检查文字溢出、遮挡、白边、裁切、空白、低清、错帧、层级错乱
- 检查画面是否有廉价发光、紫蓝粉渐变、假状态栏、假 App 截图、占位 icon 或假数据
- 检查手机端观看时中文标题、关键数字和解释短句是否仍可读

发现 frame/cover 的错字、缺字、乱码、重叠、不可读、过期图、坏 crop 或白边，优先路由 `visual-qa-fixer`；发现 Remotion 渲染或 props 链路问题路由 `production-engineer`；发现视觉策略不服务内容路由 `visual-architect`。

## 6A. visual_restraint_and_asset_hierarchy

必须确认：

- 一秒钟内能看出主视觉中心。
- 页面有明确的 `focal plane / support plane / transient explanation plane`。
- 去掉一半 blur、glow 和绿色后，页面不会失去解释能力；如果更清楚，就应降效果。
- imagegen 资产确实承担 `hero`、`explainer` 或 `proof` 职责，而不是气氛壁纸。
- proof / schematic / analogy 一眼可分，非精确图已经标注 `示意`、`非按比例` 或 `概念结构`。
- 每页 annotation clusters 不超过可读预算，标签没有把主图淹没。

失败时路由 `visual-architect`。

## 6B. visual_qa_fix_pass

必须读取 `content/visual_qa_report.json`，并抽查它声称已修复的实际输出。

必须确认：

- `visual-qa-fixer` 看过实际 `remotion_frames/*.png` 和 `publish/cover.png`。
- 报告里没有 unresolved blocking findings。
- 如果封面含中文，已经逐字核对最终标题/钩子，没有 imagegen 幻字、缺字或旧版本文案。
- 修过 Remotion 代码或图片后，已经重渲染相应 frame samples。
- imagegen 直接生成的精确标签、公式、单位、数字和来源已经逐项视觉核对；不准用错图发布。
- 缩略图尺寸下封面主物体和短句仍然可读。
- 同一版式没有连续重复到让信息推进不明显。

失败时路由 `visual-qa-fixer`。

## 7. remotion_content_authenticity

必须阅读关键 Remotion 代码和对应内容合同，确认画面真实服务内容。

必须确认：

- Remotion scene 里的元素都能追溯到 `shot_intents` 或内容合同
- 没有用假数据、无来源数字、伪品牌 logo、模板化指标墙或占位文案撑画面
- 没有“看起来高级但不表达任何内容”的装饰层
- 动效、爆炸图、机制图或 imagegen 资产没有制造事实误导

失败时按根因路由到 `visual-architect`、`content-strategist` 或 `script-writer`。

## 8. content_authenticity

必须对照旁白、画面和内容合同，寻找“不自然、不真实、不像人会这么讲/这么展示”的地方。

还必须核对：

- `evidence_map` 覆盖核心 claim。
- 开头没有用夸张 hook 扭曲事实。
- 关键边界、争议和未知项没有被讲成定论。
- 受众基线匹配：没有默认观众懂还没定义的术语，也没有把简单事实过度幼稚化。

典型失败：

- 旁白为了顺口而把因果讲过头
- 页面展示了内容里没证明的关系
- 术语解释像模板复述，缺少人的使用场景或现实锚点
- 画面和口播不是同一个节奏，像两个系统拼起来

## 9. voice_consistency

必须确认：

- 人设统一
- 情绪基线统一
- 语速统一
- 语速量化接近参考：目标约 `260` 中文字/分钟，可接受区间 `240-285` 中文字/分钟
- 重音和停顿习惯统一
- 没有明显外国人口音
- narration mode 与项目策略一致

如果项目要求单一 `master-track`，却仍残留逐 scene 漂移生成或拼接回退，应判不通过。

如果只是预期时长与最终时长不一致，但内容完整、中文听感自然、视觉 QA 和发布资产都通过，不因时长本身阻塞发布。

## 10. formula_legibility

必须确认公式不是图片幻觉：

- LaTeX 源存在且能追溯到对应 beat。
- 变量、单位、边界条件和假设可读。
- 手机截图里公式主体仍能读清。
- 没有把 imagegen 生成的伪公式当成真实公式。

## 11. diagram_annotation_truthfulness

必须确认标注图不是伪真实：

- 尺寸、单位、部件名、箭头方向和阶段顺序都有来源，并且 imagegen 成图里逐项正确。
- imagegen 可以直接生成精确标注，但必须由 `visual-qa-fixer` 视觉核对，不对就重生。
- 非按比例、示意、概念结构和夸张展示都已标注。
- 无法验证的内部结构没有被画成精确复原。

## 12. screenshot_traceability

必须确认真实截图链路完整：

- 所有声明为真实截图 / demo / UI 的画面都有原始截图路径。
- 截图、裁切、高亮、遮挡和二次处理有记录。
- placeholder 没有进入终版。

## Routing

- `coverage_complete` 失败 -> `content-strategist`
- `content_depth` 失败 -> `content-strategist`
- `meaning_gain` 失败 -> `content-strategist`
- `narration_naturalness` 失败 -> `narration-polisher`
- `ui_supports_content` 失败 -> `visual-architect`
- `visual_screenshot_bug_review` 失败 -> `visual-qa-fixer`；若根因是渲染器/装配链路，再给 `production-engineer`
- `visual_qa_fix_pass` 失败 -> `visual-qa-fixer`
- `remotion_content_authenticity` 失败 -> `visual-architect` + 对应内容 owner
- `content_authenticity` 失败 -> `content-strategist` / `script-writer` / `narration-polisher`
- `formula_legibility` 失败 -> `visual-qa-fixer`；若公式选型或证据错，再给 `visual-architect` / `content-strategist`
- `diagram_annotation_truthfulness` 失败 -> `visual-qa-fixer` + `visual-architect` + `content-strategist`
- `screenshot_traceability` 失败 -> `production-engineer`
- `voice_consistency` 失败 -> `production-engineer`

Reviewer 不自己偷偷补一块然后宣称通过。
