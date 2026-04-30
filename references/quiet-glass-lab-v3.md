# Quiet Glass Lab

这是 `video-maker` 当前默认的视觉方向说明。这里规定的是风格提示词包和材质逻辑，不是固定模块清单，更不是现成 Apple 截图模板。

## Scope

- 这个版本把默认风格重心从 `iOS 26 Liquid Glass` 收束为更适合 B 站科普 Remotion 的 `iOS 18-inspired frosted glass science deck`。
- 重点不是复刻手机 App，而是转译出 `半透明材料 + 模块化卡片 + 深色空间 + 强层级文字 + 克制高光` 的宽屏信息设计。
- 它仍然是 prompt pack，不是模板库；版式、模块数量、镜头组织继续由内容决定。

## Design Intent

- 视觉方向不是“复刻苹果截图”，而是把 `iOS 18-inspired frosted glass` 的材料气质翻译成 B 站 tech explainer 的原创 Remotion 语言。
- 画面必须坚持主内容先成立，再让毛玻璃卡片、轻 chrome 与说明层辅助理解。
- 整体气质是 `black-green minimalist`：近黑碳底、酸性黄绿点题、静谧、克制、清醒、手机可读。
- 每次允许不同版式、不同镜头组织和不同信息密度；这里锁的是风格约束，不是模块模板。
- 每一页只有一个视觉中心，观众应能快速看出这一页最重要的意思是什么。

## Visual Principles

- `content-first`: 主阅读平面保持 `solid / near-solid`、高对比、稳定，玻璃感不要吞掉正文。
- `modular frost`: 毛玻璃可用于图解卡、数据卡、对照卡、提示卡和轻量 chrome，但正文区必须有更实的承载层。
- `wide-screen deck`: 目标是宽屏科普演示页，而不是手机导航层叠界面；页面应该先像 keynote / explainer slide，再像 UI。
- `concentricity`: 优先使用大圆角模块、胶囊和圆角矩形，同一家族的圆角关系要统一。
- `soft optics`: 使用柔和模糊、细亮边、微弱高光和轻微空间深度，不追求强反射、强折射或夸张透镜变形。
- `readability first`: 玻璃再漂亮，也不能牺牲大标题、关键句和图表标签的清晰度；文字优先级高于材料效果。
- `grouping over decoration`: 层级靠 `grouping / spacing / size / tint emphasis` 建立，不靠多余装饰。
- `separation without clutter`: 用柔和边界、轻微 dimming、细腻模糊分隔 UI 与内容，不靠硬分割线。
- `bold + left-aligned`: 标题和短说明优先更清楚、更偏粗、偏左对齐，减少居中堆叠海报感。
- `restraint`: 高光、blur、绿色强调、背景纹理都要克制；一旦去掉一半效果，页面应仍然成立。

## Composition Budgets

- One focal plane: the main object, formula, process step, map, comparison, or proof anchor.
- One support plane: labels, small comparison cards, term locks, or local explanations that help read the focal plane.
- One transient explanation plane: a temporary caveat, analogy, warning, or next-step hint that should fade or stay visually secondary.
- Accent green is functional, not decorative: use it for direction, active variable, current step, selected component, or final takeaway.
- Glass may organize support information, but it must not swallow the focal plane or carry long body text by itself.
- Keep visible text hierarchy to 2 levels in dense scenes: primary claim and secondary label. A third level is allowed only for tiny proof/source tags.
- Same composition family should not repeat for more than 2-3 consecutive scenes.
- Every scene should survive a restraint test: reduce blur, glow, and green by half; if the explanation becomes clearer, keep the reduced version.

## High-Quality Prompt

将场景设计成受 Apple `iOS 18-inspired frosted glass` 启发的 `content-first` 科普演示页，而不是苹果截图复刻。每页允许不同构图与模块数量，但要保持黑碳底 + 稀疏荧光绿强调。整体以深色空间背景、模块化大圆角卡片、半透明磨砂材质、细亮边和克制高光建立气质。主信息层保持 `solid / near-solid`、深色、稳定、高对比；毛玻璃可用于图解卡、数据卡、对照卡、标签、轻量控件和短暂说明层，但承载正文的区域必须叠加更实的深浅蒙版。层级靠 `grouping`、`spacing`、`typography` 与稀疏 `emphasis` 建立，避免手机状态栏、底部 tab bar、App 图标、设置页既视感、`glass-on-glass`、过度透明正文、彩虹霓虹和 Apple UI cosplay。

## Compact Prompt

采用 Apple `iOS 18-inspired frosted glass` 的 `content-first` 科普 deck 风格：版式可变，正文层稳、深、实，毛玻璃用于模块化信息卡和轻量 chrome。使用大圆角、柔和 blur、细亮边、克制高光和深色空间背景。避免手机 UI 复刻、大段透明正文、叠玻璃、低对比文字和截图 cosplay。

## Hard Rules

- Do not fake a status bar, notch, battery, Wi-Fi, carrier, or iPhone/iPad hardware shell.
- Do not mechanically recreate Apple screenshots, system apps, control center layouts, or lock-screen compositions.
- Do not turn the page into a phone app, settings screen, or bottom-tab navigation mockup.
- Do not place large paragraphs inside fully transparent glass.
- Do not turn every card into glass.
- Do not use `glass-on-glass`.
- Do not let glass become brighter or more attention-grabbing than the content itself.
- Do not use rainbow translucency, candy colors, or gamer-style neon glow.
- Do not hide important text over busy backgrounds without a solid or near-solid backing layer.
- Do not rely on UI module templates as fixed composition rules.
- Do not force a fixed section inventory or fixed screen taxonomy just to fit the style.
- Do not keep every scene centered, symmetrical, or identically framed just because the material system is consistent.

## Transferable Traits

- Translucent controls that react to surrounding color while keeping underlying content visible.
- Frosted modular cards that can hold diagrams, numbers, comparisons, and short labels.
- A clear separation between content plane and lightweight chrome.
- Rounded, fluid, connected module families rather than many disconnected floating ornaments.
- Fine highlights and soft optical depth, used sparingly.
- Content remains the focal plane; chrome exists to organize and guide.

## Layer Logic

### Layer 0: 内容层

承载：

- 主标题
- 主图 / 主结构图
- 这一页唯一想让观众记住的结论

规则：

- 用更稳、更深、更实体的面
- 不默认上纯玻璃
- 保证高对比和手机可读性

### Layer 1: 模块层

承载：

- 图解卡
- 数据卡
- 对照卡
- 标签
- 轻量控件 / 状态

规则：

- 可以使用轻毛玻璃
- 若承载文字，文字后面要有更实的底
- 永远比内容层更克制

### Layer 2: 临时解释层 / 轻 chrome

承载：

- 一句话类比
- 术语拆解
- caveat
- 对照提醒

规则：

- 只在需要时出现
- 讲完就退
- 不长期霸占主画面

## Remotion Adaptation Rules

- `remotion/src` 只提供最小 composition shell；真实场景结构应由 `shot_intents + content contracts` 生成。
- Remotion 负责 composition、动画、字幕、音频挂载、时间轴和渲染；不要回退到 HTML slide 截图链路。
- 毛玻璃的材质、层级和几何可以出现在场景代码里，但它们应该是 prompt 产物，不是 stock scaffold 类名。
- 优先把苹果感材料语言翻译成 token、层级和模块关系，不要翻译成固定的 sidebar / tabbar / hero 三件套。
- 如果一个场景主要靠复制前一页 UI 模板成立，而不是靠内容 contract 成立，这一页就应该重写。
- 如果把 blur 和玻璃减半，页面反而更清楚，说明层级方向通常是对的。

## Formula And Annotation Rendering

- 公式默认用 LaTeX / KaTeX / MathJax 或等价结构化渲染，保留 `formula_latex` 源。
- imagegen 不负责最终公式、变量、单位、尺寸、组件名或箭头标签。
- 爆炸图、机制图、航天器结构图可以用 imagegen 直接生成底图和短标注；所有精确标注必须由 visual QA 核对，不准把错误图硬塞进 Remotion。
- 每张非精确图都要在画面或旁白里说明 `示意`、`非按比例`、`概念结构` 或 `为便于观察已夸张`。
- 如果某个标注无法追溯到内容合同或来源，宁可删掉标注，不要让画面显得“像真的”。

## Acceptance Checks

- Can a viewer identify the page's main idea in one second?
- Does the frosted material support the page structure rather than turn the page into a phone UI?
- Is the page still readable on a phone screenshot?
- Does it feel Apple-informed without becoming Apple-cosplay?
- If the accent green is removed, does hierarchy still work?
- If the blur or transparency is reduced by half, does the page likely improve rather than collapse?
