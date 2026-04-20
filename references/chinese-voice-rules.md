# Chinese Voice Rules

## Goal

把“能出声”升级成“中文观众听着不出戏”，并且让整条视频的多段音频保持同一个人设和同一种讲解气质。

目标音色默认更新为：

- 沉稳
- 大方
- 有亲和力
- 略带可爱感，但不能幼态化、撒娇化
- 像同一个人一次性录完，不像八段各自生成

## Hard Rules

- 不要把英文母语 voice 当成中文默认 voice。
- 中文讲解终版必须过一次短听感验收，再算通过。
- 如果当前 voice 听起来像外国人在念中文，直接判失败，不要靠微调参数硬撑。
- 同一条视频里，不要频繁切换 speaker、profile 或基础风格提示词。

## Publish Order For Chinese

1. ElevenLabs web workflow + 已试听通过的中文 voice
2. ElevenLabs API + 已试听通过的中文 API voice
3. Local Qwen3-TTS + 固定 profile / speaker / instruct 的稳定批量生成
4. Edge TTS only for preview / rough cut

## Why Web-First Exists

在当前环境里，中文项目走 ElevenLabs API 常见两个问题：

- 免费账户对 library voices 走 API 可能直接返回 402
- 就算 API 可调，随便挑一个英文 voice 也很容易出现外国人口音

所以中文项目默认走 `elevenlabs-web-first` 更稳。它允许先在网页里试听 voice，再批量生成。

## Local Qwen3 Consistency Rules

- 默认 profile 用 `young_calm_cn_female_explainer`
- 默认 speaker 用 `serena`
- 基础提示词要明确写出：年轻、中文女声、沉稳、大方、轻微可爱、清晰、克制、语速稳定、不忽快忽慢、不要急躁、不要播音腔
- 一条视频从头到尾保持同一个 profile、同一个 speaker、同一条基础提示词
- 如果要加额外提示词，只能在统一基础提示词后面追加，不能每段单独换风格

## Persona Contract

建议在项目里显式保存一份 voice persona contract，而不是只靠一句 `instruct`。

最少应包含：

- `persona_name`
- `age_feel`
- `temperament`
- `delivery`
- `emotion_floor`
- `emotion_ceiling`
- `forbidden_traits`

推荐默认：

- `persona_name`: `calm_graceful_cute_cn_female`
- `age_feel`: `25-30`
- `temperament`: `沉稳、大方、友好、略带可爱感`
- `delivery`: `中速偏稳、句间停顿自然、强调克制`
- `emotion_floor`: `平静`
- `emotion_ceiling`: `轻微兴奋，不外放`
- `forbidden_traits`: `播音腔、甜妹腔、客服腔、过度元气、逐字段落感`

## Suggested Prompt Template

推荐把 prompt 写成“身份 + 节奏 + 禁止项 + 一致性要求”，而不是只堆气质形容词：

`请用同一位年轻中文女声完成整条科技讲解。声音沉稳、大方、友好，带一点自然可爱感，但不要幼态化。全程保持同一人设、同一情绪基线、同一语速和同一停顿习惯，像一个表达很稳的女生在耐心讲解复杂问题。语速中速偏稳，重点词只做轻微强调。不要播音腔，不要客服腔，不要忽快忽慢，不要突然热情过头，也不要句句都像结论。`

## Drift Triggers

这些写法特别容易导致分段漂移：

- 每段单独追加不同风格词
- 同时塞进“可爱、活泼、温柔、专业、御姐、俏皮”这类互相拉扯的标签
- 强行要求每段都“更有情绪”
- 一段强调速度，一段强调慢条斯理
- 一段强调亲切，一段强调高冷克制

宁可少写，也不要互相打架。

## Minimum Review Checklist

至少检查这些点：

- 前 20 到 30 秒有没有明显外国人口音
- 中文停顿是否自然
- 英文产品名有没有被夸张误读
- 句尾语气是否像人在说话，而不是播报器
- 多段切换后，情绪基线是否一致
- 是否出现有时急躁、有时沉稳，或者有时很快、有时很慢的漂移

只要有一项明显不对，就把该 voice 记为失败。

## Project Metadata To Keep Updated

用 `record_voice_profile.py` 把结果写回：

- `provider`
- `mode`
- `voice_name`
- `locale`
- `source_type`
- `review_status`
- `review_notes`

推荐写法：

- 通过：`review_status=passed`
- 失败：`review_status=failed`，备注里写清原因，例如 `foreign accent on Chinese narration`

## Suggested Agent Behavior

- 先决定当前项目走网页中文 voice 还是本地 Qwen3
- 如果走网页，先运行 `prepare_web_tts_manifest.py`
- 如果走本地 Qwen3，先确认 `voice_settings.local_qwen` 里的 profile / speaker / instruct 是否符合当前视频定位
- 同时确认调用链真的把顶层 `voice_persona` / `voice_consistency` 注入 helper；如果只是写在 `project.json` 里但执行时没传进去，验收时应判为“配音一致性未落实”
- 先锁定 persona contract，再批量生成，不要先生成后补设定
- 统一生成后再试听样段，不要一边换 speaker 一边批量生成
- 听样后立刻更新 `record_voice_profile.py`
- 最后再运行 `quick_check.py`

不要把“voice 叫什么”和“听起来怎么样”只留在临时对话里。
