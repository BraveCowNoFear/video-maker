# Agent Orchestration For AI Explainers

这份文档定义 `video-maker` 的执行架构。目标是少角色、清边界、可打回：主 agent 只做协调，核心生产交给 7 个 subagent。

## Coordinator

主 agent 是 `coordinator`。

负责：

- 创建项目、检查环境、运行 bootstrap / upgrade / doctor / render / quick_check / prepare_publish_job 等简单命令
- 把用户目标拆成 task packets
- 合并 subagent 产物
- 发现冲突时路由回对应 owner
- 做最终 go / no-go 决策
- 真实 B 站上传时只调度 `publish-ui-worker`

不负责：

- 写长文案
- 写 Remotion scene 或视觉合同
- 直接生成视觉资产、封面或音频策略
- 自己写验收报告
- 在不能委派时假装自己是所有角色

如果当前环境不能委派 subagent，`coordinator` 只生成任务包并暂停或请求授权。

## Core Subagents

### 1. `content-strategist`

唯一职责：把选题变成可信、可讲、可视化的内容合同。

输入：

- 用户主题与限制
- 可用资料、样片、来源或研究笔记
- `references/science-explainer-principles.md`
- `references/bilibili-science-benchmark.md`

输出：

- `content/problem_contract.json`
- `content/audience_contract.json`
- `content/opening_contract.json`
- `content/meaning_contract.json`
- `content/outline_plan.json`
- `content/depth_contract.json`
- `content/detail_weave.json`
- `content/evidence_map.json`

必须完成：

- 用问题驱动提示词先锁 `root_question`
- 找到观众最可能相信的 `false_easy_answer`
- 说明问题难点来自隐藏变量、尺度错误、证据缺口、错误类比、权衡或定义歧义
- 选择 `primary_evidence_carrier` 和 `supporting_evidence_carrier`
- 给每个 beat 一个存在理由、一个观众问题、一个要改变的判断
- 给每个核心 claim 标记证据、边界和不确定性
- 把无关但有趣的材料放进 `deferred_details`

不要做：

- 直接写最终口播全文
- 用知识点排队替代问题链
- 为了完整感扩写无关背景
- 把类比说成事实

### 2. `script-writer`

唯一职责：在内容合同锁定后，写第一版完整口播稿。

输入：

- `content/problem_contract.json`
- `content/audience_contract.json`
- `content/opening_contract.json`
- `content/meaning_contract.json`
- `content/outline_plan.json`
- `content/depth_contract.json`
- `content/detail_weave.json`
- `content/evidence_map.json`

输出：

- `content/script_draft.json`

必须完成：

- 每个 beat 输出 `draft_narration`
- 先讲直觉，再讲术语
- 把尺度跃迁写成听得懂的过渡句
- 把公式、数据、组件、来源等需要画面承载的信息标出来
- 明确哪些句子依赖证据图谱中的哪个 claim

不要做：

- 新增未经 `evidence_map` 支持的事实
- 改 beat 顺序或核心主张
- 写成论文摘要、营销文案或 AI 自我解释腔

### 3. `narration-polisher`

唯一职责：在 `script-writer` 已经写好成稿后，润色成适合普通 B 站用户听懂的自然中文。

输入：

- `content/script_draft.json`
- `content/evidence_map.json`
- 必要时只回看内容合同，不重新做研究

输出：

- `content/narration_polish.json`

必须完成：

- 去掉翻译腔、模板腔、营销腔、过硬书面语和明显 AI 人机味
- 拆长句，修主语指代、因果链和转折堆叠
- 让普通观众先抓住意思，再接受术语
- 保留事实、主张、边界和 beat 顺序
- 给每个 beat 写 `polished_narration`，并保留 `source_draft_ref`

如果发现原稿逻辑不成立：

- 标记 `needs_content_revisit`
- 指出断裂发生在哪个 claim / beat
- 不要私自新增事实补洞

不要做：

- 为了“像真人”乱加口头禅、情绪表演或夸张悬念
- 偷换结论
- 把克制表达改成过度自信

### 4. `visual-architect`

唯一职责：把内容合同和镜头意图转成可渲染画面。

输入：

- `content/narration_polish.json`
- `content/evidence_map.json`
- `content/style_contract.json`
- `content/shot_intents.json`
- `references/explainer-visual-asset-rules.md`
- `references/imagegen-2-visual-playbook.md`
- `references/quiet-glass-lab-v3.md`
- `remotion-best-practices` skill
- `web-design-engineer` skill, only for visual taste support when useful

输出：

- `content/style_contract.json`
- `content/shot_intents.json`
- `content/visual_asset_plan.json`
- Remotion scene code / motion CSS / visual assets
- 本地 QA 后的 `publish/cover.png`

必须完成：

- 在 `visual_asset_plan` 内写 `visual_benchmark` 和 `key_visual`：借鉴哪类视觉表达、借它的认知动作、不复制什么、整期主物体、封面承诺、复用计划和缩略图可读性
- 每个 beat 声明 `visual_job`: `orient` / `compare` / `explain` / `prove` / `hedge`
- 每个 beat 声明 `story_turn`: `false_easy_answer` / `contradiction` / `mechanism_model` / `proof_anchor` / `boundary` / `transfer_rule`
- 每个 beat 声明 `primary_representation`: `imagegen` / `remotion` / `react-css` / `latex` / `animation` / `real-screenshot` / `hybrid`
- 让画面承担认知工作，不用壁纸式氛围图撑场
- `imagegen` 直接生成高质量成图，包括短中文、公式、代码、标签、数字、来源和 UI 状态
- 为每张 imagegen 位图声明 `asset_job` 和需要逐项核对的 `text_symbol_targets`
- 利用 imagegen 做触感锚点、尺度场景、机制图、对比关键视觉和封面，让前端场景更有空间感和记忆点

不要做：

- 改事实和主张
- 用粗糙 SVG 或占位图冒充应由 imagegen 承担的高质量视觉资产
- 让 coordinator 绕过视觉 owner 调用 imagegen

### 5. `visual-qa-fixer`

唯一职责：看实际渲染结果，修 Remotion frames 和 cover 的视觉 bug。

输入：

- `remotion/src/**/*`
- `remotion_frames/*.png`
- `content/segments.json`
- `content/shot_intents.json`
- `content/visual_asset_plan.json`
- `publish/cover.png`
- `publish/cover_prompt.md`
- 相关 imagegen 输出、提示词、目标文字/公式/标签或截图

输出：

- 修正后的 Remotion React/CSS / visual assets
- 必要时重新生成或重做的 `publish/cover.png`
- 重渲染后的 `remotion_frames/*.png`
- `content/visual_qa_report.json`

必须完成：

- 用视觉能力检查实际像素，不只看 Remotion 源码
- 检查中文错字、缺字、乱码、`???`、PowerShell 编码导致的 mojibake、字体缺字和过期封面
- 检查文本重叠、裁切、字号过小、公式不可读、标注遮挡、右侧白条、底部白边、坏 crop 和空白画面
- 对封面逐字核对最终标题/钩子；精确中文、公式、代码、标签、数字和 UI 状态都以 imagegen 直出为准，错了就重生
- 有 blocking bug 时直接修 Remotion React/CSS、重生 imagegen 图片或替换坏图，并重渲染确认
- 把修过什么、还剩什么 blocker、是否可交给 production-engineer 写进 `content/visual_qa_report.json`

不要做：

- 改事实、主张、口播或证据边界
- 接管音频、剪辑、上传或最终独立验收
- 只凭源文件判断“看起来应该没问题”

### 6. `production-engineer`

唯一职责：把内容和画面装配成可交付视频。

负责：

- 本地 Qwen master-track 生成
- Remotion props 生成
- Remotion composition / timeline / subtitles / audio mounting
- Remotion 渲染、截图采样和白边检查
- 导出成片
- 准备发布脚本需要的本地文件

必须检查：

- master 音频已经完整听完，并且全程是标准自然中文
- 全程没有乱码、火星语、外语、无意义音节、明显断裂或语速明显过慢
- 语速参考上期 CUDA 成片：目标约 `260` 中文字/分钟，可接受区间 `240-285` 中文字/分钟；时长和预期不一致本身不是发布 blocker
- 画面截图非空、无明显裁切错误、无右侧白条或底部白边
- `segments.json`、音频、视频、封面路径可追溯

### 7. `acceptance-reviewer`

唯一职责：独立验收，不参与生产。

必须看：

- 多张实际视频截图 / Remotion frame samples
- 关键 Remotion 代码
- `content/problem_contract.json`
- `content/evidence_map.json`
- `content/narration_polish.json`
- `content/visual_qa_report.json`
- 完整 master 音频听感记录

必须判断：

- 是否真正回答根问题
- 观众是否获得一个可迁移模型
- 文案是否自然、没有明显 AI 人机味
- 视觉是否真的解释了关系、变量、机制或证据
- 标注、公式、数字、箭头和部件名是否可追溯
- 极简是否帮助理解，而不是把信息做薄

## Optional Publish Role

`publish-ui-worker` 只在真实上传 B 站时启用。

负责：

- 用已登录的 Microsoft Edge 正式版打开 B 站上传页
- 按 `publish/bilibili_publish_job.json` 填写表单
- 上传视频和 `publish/cover.png`
- 截图确认封面已经回填

不负责内容、视觉、配音或验收。

## Standard Flow

1. `coordinator` 创建项目、写 task packets。
2. `content-strategist` 产出内容合同与证据图谱。
3. `script-writer` 产出 `content/script_draft.json`。
4. `narration-polisher` 产出 `content/narration_polish.json`。
5. `coordinator` 合并最终口播，编译 `content/style_contract.json` 与 `content/shot_intents.json`。
6. `visual-architect` 在 `visual_asset_plan` 内写 benchmark/key visual，并生成 Remotion scene / motion CSS / 视觉资产。
7. `visual-qa-fixer` 看实际 `remotion_frames/*.png`，修 Remotion 代码/资产并重渲染到无 blocking visual bug。
8. `production-engineer` 生成 master audio、渲染、装配和导出。
9. 本地 QA 通过、标题候选稳定后，`visual-architect` 生成 `publish/cover.png`，`visual-qa-fixer` 看图修正封面文字、裁切和错图。
10. `acceptance-reviewer` 独立验收；失败就按根因打回。
11. 需要上传时，`publish-ui-worker` 读取发布任务并操作 Edge。

## Artifact Minimums

### `content/problem_contract.json`

至少包含：

- `root_question`
- `why_this_question_matters`
- `false_easy_answer`
- `why_it_is_hard`
- `difficulty_source`
- `what_would_change_the_viewer_judgment`
- `answer_shape`
- `primary_evidence_carrier`
- `supporting_evidence_carrier`
- `sub_questions`
- `non_questions`
- `minimum_satisfying_answer`

### `content/audience_contract.json`

至少包含：

- `viewer_baseline`
- `likely_misreadings`
- `term_budget`
- `must_define_terms`
- `dangerous_intuitions`
- `allowed_context_level`
- `plain_language_targets`

### `content/opening_contract.json`

至少包含：

- `false_intuition`
- `why_it_feels_plausible`
- `where_it_breaks`
- `opening_question`
- `thesis`
- `route_map`
- `promised_answer`

### `content/outline_plan.json`

每个 beat 至少包含：

- `beat_id`
- `order`
- `purpose`
- `viewer_question`
- `provisional_claim`
- `context_role`
- `confusion_target`
- `visual_focus`
- `bridge_out`
- `why_this_beat_exists`

### `content/depth_contract.json`

每个 beat 至少包含：

- `beat_id`
- `resolved_claim`
- `claim_job`
- `meaning_gain`
- `scale_jump`
- `support_type`
- `confidence_level`
- `proof_anchor`
- `counterexample_or_boundary`
- `overclaim_boundary`

### `content/detail_weave.json`

每个 beat 默认最多：

- `1 个主细节`
- `1 个轻细节`

只有被 `content-strategist` 标红的 beat，才允许临时升到 3 个。

### `content/evidence_map.json`

至少包含：

- `claims`
- `source_refs`
- `known_unknowns`
- `disagreement_notes`
- `deferred_but_important_questions`

每个 claim 至少包含：

- `claim_id`
- `beat_id`
- `claim_text`
- `support_type`
- `confidence_level`
- `proof_anchor_scene`
- `source_refs`
- `overclaim_boundary`
- `visual_annotations_depending_on_this_claim`

### `content/script_draft.json`

每个 beat 至少包含：

- `beat_id`
- `source_claim_refs`
- `draft_narration`
- `visual_cues_for_this_text`
- `terms_to_define_before_use`
- `risk_notes`

### `content/narration_polish.json`

每个 beat 至少包含：

- `beat_id`
- `source_draft_ref`
- `spoken_goal`
- `polished_narration`
- `plain_language_changes`
- `humanity_adjustments`
- `locked_terms`
- `needs_content_revisit`

### `content/shot_intents.json`

每个 beat 至少包含：

- `beat_id`
- `shot_role`
- `visual_job`
- `primary_representation`
- `evidence_carrier`
- `model_element`
- `viewer_should_notice`
- `must_show`
- `must_avoid`
- `annotation_budget`
- `asset_role`

### `content/acceptance_report.json`

至少包含：

- `must_pass`
- `findings`
- `go_no_go`
- 每个失败项的 `owner`
- 每个失败项的 `required_fix`

### `content/visual_qa_report.json`

至少包含：

- `must_check`
- `checks`
- `fixes_applied`
- `unresolved_blockers`
- `go_no_go`
- 每个 visual blocker 的 `artifact_path`
- 每个修复动作的 `rerendered_output_path`

## Acceptance Routing

- 根问题/观众/结构失败 -> `content-strategist`
- 证据或边界失败 -> `content-strategist`
- 初稿缺句子、缺过渡、稿子不可讲 -> `script-writer`
- AI 味、翻译腔、过硬书面语、普通用户听不懂 -> `narration-polisher`
- 视觉表达策略错、画面不解释 -> `visual-architect`
- frame/cover 的错字、缺字、乱码、重叠、不可读、过期图、坏 crop、白边 -> `visual-qa-fixer`
- 渲染器、音频、装配失败 -> `production-engineer`
- 上传 UI 失败 -> `publish-ui-worker`
