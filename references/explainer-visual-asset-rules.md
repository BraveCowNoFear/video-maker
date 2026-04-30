# Explainer Visual Asset Rules

这份规则用于让 `video-maker` 做跨领域科普，而不是只做静态文字页。

## Representation Decision Tree

每一拍先选 `primary_representation`，再写画面：

- `imagegen`：整体形态感、爆炸图、剖面概念图、机制图、封面主视觉、中文标题、公式、代码、标签、数字、UI 状态。
- `remotion`：视频 composition、动画、字幕、音频挂载、时间轴和最终渲染。
- `react-css`：Remotion 内的布局、裁切、动效节奏、场景组合；不默认作为 imagegen 文字修复层。
- `latex`：公式源文本和验收基准；最终公式画面可由 imagegen 直接生成。
- `animation`：随时间展开才成立的过程，例如反馈控制、轨道/姿态变化、信号传播、算法迭代、状态切换、误差积累。
- `real-screenshot`：真实软件界面、真实网站、真实实验/视频帧。
- `hybrid`：`imagegen` 直接生成含文字/公式/标签的主图，Remotion React/CSS 只做外壳、裁切、转场或必要组合。

## Asset Economy

解释型视觉的目标是减少认知负担，不是把每秒都装满。

- 每页默认只允许 `1 个 hero asset`。
- 每页默认不超过 `3 个 annotation clusters`，每个 cluster 由 imagegen 直接画进主图且只服务一个判断。
- 每个 beat 至少有一个真正承担解释责任的元素：关系图、流程图、公式可视化、剖面图、受力/轨迹线、真实截图或 proof anchor。
- 没有解释增益的 bitmap、玻璃、发光、粒子、纹理和装饰直接删。
- 能用 imagegen 直接画清楚时，不要拆成额外文字层；也不要用气氛图替代解释图。
- 同一种版式连续出现不超过 2-3 页；连续相同构图会让观众误以为信息没有推进。
- 长视频至少安排少量 `proof anchor scene`：真实截图、原始数据、公开来源、板书推导、实验画面或可追溯图表。
- 极简不是空白，而是每个留在画面上的东西都有 job：`orient` / `compare` / `explain` / `prove` / `hedge`。

## Imagegen Policy

`video-maker` 默认把 GPT Image 2 / `imagegen` 当成高质量成图器。它不仅负责形态、材质、空间、光影和记忆点，也默认直接负责画面里的短中文、公式、代码、标签、数字和 UI 状态；准确性由视觉核对和重生保证。

`imagegen` 适合：

- 观众先需要整体形态感，再需要精确定义。
- 真实摄影拿不到，或真实画面看不见内部机制。
- 需要爆炸图、剖面图、机制图来解释部件关系。
- 需要统一审美的 B 站封面或视频关键视觉。
- 需要直接生成少量短中文、公式、代码、标签、数字或 UI 状态。
- 需要一个可记住的视觉隐喻、尺度场景、失败/成功对比、章节主视觉或 motion texture。

`imagegen` 不适合：

- 精密仪表读数、芯片版图、未验证内部构造、假 UI、假实验结果、假轨迹。
- 大段正文、密集表格、整页代码、必须像真实系统截图一样逐像素准确的界面。

硬规则：

- `imagegen` 直接负责最终图里的短文字、公式、标签、箭头、尺寸、单位和关键数字；`visual-qa-fixer` 必须逐项核对。
- 任何文字、公式、代码、标签、数字或 UI 状态不准确，默认重生 imagegen 图，不用额外文字层修补。
- 所有 AI 生成图必须标注表达性质：`示意`、`非按比例`、`概念结构`、`为便于观察已夸张`。
- 不把 AI 生成的纹理、几何细节、内部构造或仪表读数当事实。
- 每张 imagegen 图都要声明 `asset_job`: `tactile_anchor` / `hero_silhouette` / `mechanism_base` / `scale_scene` / `contrast_key_visual` / `chapter_bumper` / `cover_base` / `texture_or_depth_plate`。
- 需要透明贴纸或 cutout 时，默认先按 `imagegen` skill 的 chroma-key + 本地抠图流程；不要假设 GPT Image 2 原生透明背景可用。

## Explainer-Mode Visual Recipes

Use these recipes to escape generic card decks. `visual-architect` may combine or simplify them, but should preserve the explanatory job.

- `math-formula`: intuition object -> coordinate frame -> one animated variable -> invariant highlight -> imagegen-rendered formula -> boundary/counterexample card.
- `hardware-teardown`: clean hero silhouette -> scale reference -> exploded/section visual with generated labels -> force/heat/signal/material flow arrows -> tradeoff comparison.
- `system-mechanism`: system boundary map -> actor/node diagram -> flow animation -> bottleneck/failure point -> control loop or feedback view -> takeaway rule.
- `comparison-tradeoff`: common goal card -> axis definition -> side-by-side state -> hidden cost reveal -> decision matrix with one highlighted rule.
- `concept-mental-model`: wrong model sketch -> contradiction scene -> replacement model -> 2-3 quick applications -> old-model boundary label.
- `tool-workflow`: before-state screenshot or sketch -> workflow path -> key operation zoom -> failure branch -> final checklist.
- `mission-or-operation-system`: objective -> object/process scale map -> phase timeline -> force/flow/control layer -> failure boundary -> system tradeoff.
- `manufacturing-process`: finished object -> whole process timeline -> local machine close-up -> material transformation -> quality-control proof -> scale implication.

For complex engineered objects, natural structures, instruments, machines, organisms, software systems, mathematical objects, or social systems, prefer a direct imagegen stack when visual precision matters:

1. `imagegen` creates the hero silhouette, conceptual scene, exploded view, section visual, texture, labels, arrows, formulas and key numbers directly.
2. Remotion React/CSS only handles crop-safe framing, reveal timing, transitions, subtitles, audio mounting, and optional scene composition.
3. Keep formula/code/source text in project artifacts as the target string for QA.
4. Motion reveals one relationship at a time; do not show every arrow, label, variable, and caveat on frame one.

## Formula Policy

公式场景默认保留 LaTeX 源文本供验收，但画面里的公式可以直接由 imagegen 生成。

每个公式 beat 至少声明：

- `formula_latex`
- `variables`
- `assumptions`
- `what_stays_invariant`
- `where_it_breaks`
- `spoken_intuition`

公式页的目标不是堆公式墙，而是展示：

- 对象如何变换
- 哪些量保持不变
- 边界条件如何改变结论
- 推导中哪一步真正改变观众判断

Formula visual rules:

- Introduce one new variable at a time.
- Map every variable to a visible object, color, axis, arrow, or region.
- Highlight invariants more strongly than algebraic manipulation.
- Keep LaTeX source in the project artifact; use it to visually check the formula rendered by imagegen.
- On mobile screenshots, the main formula and variable labels must still be readable.

## Text And Label QA Policy

标注图默认直接由 imagegen 生成完整画面，包括短中文、标签、箭头、尺寸、单位、公式和关键数字。

图中文字和符号必须能追溯到：

- `content/depth_contract.json`
- `content/detail_weave.json`
- `content/shot_intents.json`
- 真实截图或公开来源

无法追溯的标注不得进入终版。生成后发现错字、缺字、乱码、伪公式、伪代码、数字错误或标签错位，默认重生 imagegen 图。

## Visual QA Fix Pass

`visual-qa-fixer` 必须在视觉交付后检查实际渲染像素，而不是只看源文件。

必须看：

- `remotion_frames/*.png`
- `remotion/src/**/*` 和相关 CSS
- `publish/cover.png`
- `publish/cover_prompt.md`
- 任何 imagegen 输出、提示词、目标文字/公式/标签、真实截图来源

必须修：

- 中文错字、缺字、乱码、`???`、字体缺字或编码问题
- 标题/封面文案与最终标题不一致，或仍引用旧封面
- 文本重叠、裁切、过小、被装饰物遮挡
- 公式、标签、箭头、数字不可读或不可追溯
- 右侧白条、底部白边、坏 crop、空白画面

允许动作：

- 修改 Remotion React/CSS
- 重新生成或替换 imagegen 视觉资产
- 重新生成封面或视觉资产，直到 imagegen 直接生成的中文、公式、标签和数字正确
- 重渲染 `remotion_frames/*.png`
- 写 `content/visual_qa_report.json`

不得改事实、口播、证据边界或结论。

## Screenshot Provenance Policy

凡声明为真实截图、真实 UI、真实 demo 或真实视频帧：

- 必须保存原始截图路径。
- 必须写入 `content/screenshot_plan.json` 或 `content/screenshot_manifest.json`。
- 不得用重绘图、AI 图或 placeholder 冒充真实截图。
- 如果为了隐私或清晰度做了裁切/遮挡/高亮，必须保留处理说明。

## Beat-Level Contract

每个 `shot_intents.beats[]` 至少补齐：

- `primary_representation`
- `evidence_mode`: `exact` / `schematic` / `metaphor`
- `visual_truth_label`
- `imagegen_text_required`
- `imagegen_text_exactness_check`
- `formula_latex`
- `asset_refs`
- `screenshot_refs`

如果这一拍无法说明为什么选这种视觉形式，默认打回 `visual-architect`。
