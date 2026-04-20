# Chinese Voice Rules

## Goal

把“能出声”升级成“中文观众听着不出戏”，并且让整条视频的多段音频保持同一个人设和同一种讲解气质。

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
- 基础提示词要明确写出：年轻、中文女声、沉稳、清晰、克制、语速稳定、不忽快忽慢、不要急躁、不要播音腔
- 一条视频从头到尾保持同一个 profile、同一个 speaker、同一条基础提示词
- 如果要加额外提示词，只能在统一基础提示词后面追加，不能每段单独换风格

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
- 统一生成后再试听样段，不要一边换 speaker 一边批量生成
- 听样后立刻更新 `record_voice_profile.py`
- 最后再运行 `quick_check.py`

不要把“voice 叫什么”和“听起来怎么样”只留在临时对话里。
