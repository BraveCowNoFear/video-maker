# Agent Orchestration For AI Explainers

这份文档定义 `video-maker` 里推荐的主 agent / subagent 编排方式，目标不是把一期视频“写完”，而是把一期视频的内容方向、信息结构、UI 呈现和配音一致性一起拉齐。

## 总原则

- 主 agent 负责总论点、最终判断、内容拔高和最终成片一致性。
- subagent 只做独立侧任务，不抢关键路径决策。
- 一期视频至少要同时回答三件事：
  - 这是什么。
  - 为什么现在值得讲。
  - 观众看完之后该怎么判断或行动。

## 推荐角色

### 1. Main agent: `chief-editor`

主 agent 负责：

- 定义这期视频到底在帮观众澄清什么误解
- 设定一句能贯穿全片的中心判断
- 决定每一段只承担一个信息任务
- 把 subagent 的材料合并成一个统一视角
- 最后把“术语解释”拔高成“判断方法”

主 agent 产出：

- 一句话 thesis
- 一句话 higher-order takeaway
- 8 段 segment map
- 最终脚本与画面指令

### 2. Subagent: `research-scout`

负责：

- 查当前事实、定义、行业说法和容易混淆的相邻概念
- 给主 agent 提供可验证的资料点
- 找“观众最容易误会的地方”

不要负责：

- 直接决定整期视频的观点
- 自己写最终脚本

### 3. Subagent: `skeptic-elevator`

负责：

- 逼主 agent 回答“为什么这件事值得现在讲”
- 挑出过度简化、过度吹捧和逻辑跳步
- 提醒哪里需要把内容再拔高半层

典型问题：

- 这只是定义，还是判断？
- 这件事对观众的真实影响是什么？
- 如果只记住一句，应该记住哪一句？

### 4. Subagent: `visual-architect`

负责：

- 把每一段内容翻译成画面层级
- 决定什么信息是前景焦点，什么只是玻璃层里的辅助导航
- 保证 UI 是辅助内容，不是喧宾夺主

输出要回答：

- 这页的视觉中心是什么
- 哪些信息必须被玻璃承载
- 哪些信息应该直接裸露在内容层，不要再包一层卡片

### 5. Subagent: `voice-director`

负责：

- 定义整条视频唯一的 voice persona
- 检查每段的口气、节奏、停顿和情绪基线是否一致
- 防止因为逐段生成导致人设漂移

### 6. Subagent: `acceptance-reviewer`

负责：

- 专门验收 `内容深度`
- 专门验收 `UI 是否在服务内容`
- 专门验收 `配音 persona / 节奏 / 音色一致性`
- 明确指出要打回给谁，而不是只说“这里不太好”

一旦发现问题，reviewer 只做两件事：

- 标出失败项
- 把任务路由回对应 owner 重做

不要自己偷偷补一小块然后宣称通过。

## 标准流程

1. 主 agent 先写 `topic memo`
   - audience problem
   - thesis
   - higher-order takeaway
   - what not to overclaim
2. 并行启动 subagents
   - `research-scout`
   - `skeptic-elevator`
   - `visual-architect`
   - `voice-director`
3. 主 agent 合并材料
   - 删除重复事实
   - 保留最能支撑判断的例子
   - 让 UI 和 voice 为同一个节奏服务
4. 生成 segment map
   - 每段只做一件事
   - 每段都有清晰的页面焦点
5. 进入专门验收
   - `acceptance-reviewer` 只看通过 / 不通过
   - 不通过就打回对应 agent
6. 最后统一做两轮复核
   - 文字和页面是不是一个节奏
   - 配音和页面是不是一个人设

## Acceptance loop

推荐固定三项 gate：

- `content_depth`
- `ui_supports_content`
- `voice_consistency`

推荐打回路由：

- `content_depth` 失败 -> `chief-editor` + `skeptic-elevator`
- `ui_supports_content` 失败 -> `visual-architect`
- `voice_consistency` 失败 -> `voice-director`

每次打回之后都要补一条简短复盘：

- 问题是什么
- 为什么会出现
- 下一次默认怎么避免

如果这个复盘具有复用价值，就写回 skill 文档或项目默认规则。

## Segment map 写法

每段都建议写成四格：

- `segment goal`
- `viewer confusion`
- `visual focus`
- `takeaway line`

这样做的好处是：

- 内容不会散
- UI 不会空转
- 主 agent 更容易控制节奏

## 内容拔高规则

不是每段都拔高，而是在三个位置拔高：

- `01-hook`：先给“为什么现在值得讲”
- `05-deep dive` 或 `06-contrast`：给“为什么大家会长期讲混”
- `08-choice`：给“看完以后应该怎么判断”

如果一整期视频只有解释，没有判断，就还不够。
