# Chinese Voice Rules

## Goal

把“能出声”升级成“中文观众听着不出戏”，并且让整条视频保持同一个人设和同一种讲解气质。

目标音色默认：

- 沉稳
- 大方
- 有亲和力
- 略带可爱感，但不能幼态化、撒娇化
- 像同一个人一次性录完，不像多个 scene clip 拼出来的人设漂移

## Hard Rules

- 不要把英文母语 voice 当成中文默认 voice。
- 中文讲解终版必须完整听完一次，再算通过。
- 如果任意位置出现乱码、火星语、外语、无意义音节、拟声热场、明显断裂或语速明显偏慢，直接判失败并重生。
- 如果当前 voice 听起来像外国人在念中文，直接判失败。
- 同一条视频里，不要频繁切换 speaker、profile 或基础风格提示词。

## Publish Order For Chinese

1. Local Qwen3-TTS + 固定 profile / speaker / instruct + 单一 `master-track`
2. Edge TTS only for preview / rough cut

## Master Track Rule

- 默认直接生成整条 `audio/master.*`
- 不保留 scene-level TTS 回退或拼接路径
- 视觉剪辑应该跟随已锁定的完整 narration，而不是为了配音切段去反向决定内容结构

## Pace Calibration

语速默认按 2026-04-25 已发布 CUDA 视频校准：最终口播 `2434` 个 CJK 汉字，成片 `560.37` 秒，约 `261` 中文字/分钟。

后续中文 tech explainer 默认：

- 目标：`260` 中文字/分钟
- 可接受区间：`240-285` 中文字/分钟
- 统计口径：优先统计 `segments[].tts_text`，没有则统计 `narration_text`；只数 CJK 汉字，英文缩写和数字另作人工听感判断
- 如果只是预期时长与最终时长不一致，但内容、中文听感和视觉 QA 都通过，时长本身不是发布 blocker
- 如果低于区间但听感仍自然、不拖沓，可作为 warning 直接发布；只有明显偏慢到影响观看节奏，或明显断裂/乱码/外语混入，才重生音频

## Local Qwen3 Consistency Rules

- 默认 profile 用 `young_calm_cn_female_explainer`
- 默认 speaker 用 `serena`
- 基础提示词要明确写出：年轻、中文女声、沉稳、大方、轻微可爱、清晰、克制、语速中速偏快且稳定、不忽快忽慢、不要急躁、不要播音腔
- 基础提示词必须明确要求：开头直接用标准自然中文进入正文，不要乱码、外语、无意义音节或非中文热场
- 一条视频从头到尾保持同一个 profile、同一个 speaker、同一条基础提示词
- 如果要加额外提示词，只能在统一基础提示词后面追加，不能每个 scene 单独换风格

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
- `single_pass_preferred`
- `fallback_master_track_policy`

## Spoken Text Contract

- 屏幕展示文案和配音文案不必永远一字不差。
- 如果屏幕上有 URL、命令、缩写、数字、型号、日期、英文产品名，优先在 segment 里单独写 `tts_text` / `spoken_text` / `voice_spoken` / `narration_text`。
- 这些字段存在时，TTS 应优先读它们，而不是硬读 `voice`。
- 原则是“观众听起来自然”，不是“让模型把所有字符都机械念出来”。

## Suggested Prompt Template

推荐把 prompt 写成“身份 + 节奏 + 禁止项 + 一致性要求”，而不是只堆气质形容词：

`请用同一位年轻中文女声完成整条科技讲解。声音沉稳、大方、友好，带一点自然可爱感，但不要幼态化。全程保持同一人设、同一情绪基线、同一语速和同一停顿习惯，优先像一次性录完。语速中速偏快且稳定，重点词只做轻微强调。开头直接用标准自然中文进入正文，不要乱码、外语、无意义音节或非中文热场。不要播音腔，不要客服腔，不要忽快忽慢，不要突然热情过头。`

## Drift Triggers

这些写法特别容易导致漂移：

- 每个 scene 单独追加不同风格词
- 同时塞进互相拉扯的标签
- 强行要求每段都更有情绪
- 一会强调速度，一会强调慢条斯理

宁可少写，也不要互相打架。

## Minimum Review Checklist

- 全片有没有明显外国人口音
- 全片是否都是自然中文，不能有火星语、乱码、外语或无意义音节
- 全片语速是否偏慢；慢到影响观看节奏就必须重生
- 中文停顿是否自然
- 英文产品名有没有被夸张误读
- 句尾语气是否像人在说话，而不是播报器
- 多段切换后，情绪基线是否一致
- 是否出现有时急躁、有时沉稳，或者有时很快、有时很慢的漂移

## Suggested Agent Behavior

- 先确认当前项目的单一 `master-track` 配置是否完整
- 如果走本地 Qwen3，先确认 `voice_settings.local_qwen` 里的 profile / speaker / instruct 是否符合当前视频定位
- 本地 Qwen3 master-track 生成必须记录 `voice_jobs/qwen_master_status.json`，并使用硬超时；默认 `voice_settings.local_qwen.synthesis_timeout_sec = 900`，长片可显式提高，但不能无限等待
- `voice_profile.full_audio_review_status = passed` 只在完整听完 master 后写入；`opening_review_status` 或中段抽听只能作为补充记录，不能替代完整听审
- 同时检查当前 `model_dir`、`instruct` 和整段讲稿长度是否适合一次性 master-track 合成
- 同时确认调用链真的把顶层 `voice_persona` / `voice_consistency` 注入 helper
- 中文讲解默认优先整段一次生成；只有模型本身明确无法完成时再修输入文本，而不是回退成 scene clips
- 先锁定 persona contract，再批量生成
- 听样后立刻更新 `record_voice_profile.py`
- 最后再运行 `quick_check.py`
