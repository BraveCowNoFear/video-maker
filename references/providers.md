# Providers

## Goal

Keep the old Bilibili explainer project structure unchanged and only upgrade the voice layer.

## Default Recommendation

### Publish path

- Provider: ElevenLabs web workflow first for Chinese
- Model: `eleven_multilingual_v2` when API path is explicitly approved
- Use for: Chinese final narration that needs more natural pauses and emphasis

### Preview path

- Provider: Edge TTS
- Voice: `zh-CN-XiaoxiaoNeural`
- Use for: timing, rough cut, and quick early review

### Local open-source path

- Provider: local Qwen3-TTS
- Default profile: `young_calm_cn_female_explainer`
- Default speaker: `serena`
- Use for: stable Chinese female narration with consistent tone across many segments

## Environment Variables

- `ELEVENLABS_API_KEY`: enable ElevenLabs final voice generation
- `ELEVENLABS_VOICE_ID`: optional global default when the project does not set a voice id

## Project JSON Fields Added By This Skill

```json
{
  "voice_provider": "auto-natural-tts",
  "voice_language": "zh-CN",
  "voice_workflow": {
    "publish_mode": "elevenlabs-web-first",
    "web_manifest": "voice_jobs/web_tts_manifest.json",
    "accent_review_required": true
  },
  "voice_profile": {
    "provider": "",
    "mode": "",
    "voice_name": "",
    "voice_id": "",
    "locale": "",
    "source_type": "",
    "review_status": "unreviewed",
    "review_notes": []
  },
  "voice_persona": {
    "id": "cn_female_steady_graceful_cute_v1",
    "display_name": "沉稳大方可爱女声",
    "identity": "熟悉技术、友好克制的年轻中文女生",
    "core_traits": ["沉稳", "大方", "亲和", "轻微可爱"],
    "forbidden_traits": ["幼态", "撒娇", "夹子音", "播音腔", "突然兴奋"],
    "baseline_emotion": "calm_friendly",
    "pace": "medium_steady",
    "breath": "light_short_controlled",
    "emphasis": "light_keyword_only",
    "qwen_base_instruct": "请用年轻中文女声做 AI 科普讲解。整体气质沉稳、大方、清晰、友好，带一点自然可爱的亲和感，但不要幼态，不要撒娇，不要夹子音。全程保持同一个人设、同一种情绪基线和同一套说话习惯。语速中速偏稳，节奏统一，不忽快忽慢。句间停顿自然，呼吸轻、短、克制，句尾收得干净。重点词只做轻微强调，不要夸张，不要播音腔，不要突然兴奋，也不要突然压低情绪。像熟悉 AI 工具和工作流的年轻女生，在冷静而友好地解释复杂概念。"
  },
  "voice_consistency": {
    "anchor_segment_id": "01",
    "locked_fields": ["profile", "speaker", "language", "voice_id", "model_id", "base_instruct"],
    "emotion_variance": "low",
    "pace_variance": "low",
    "breath_variance": "low",
    "regen_policy": "regen_outliers_only"
  },
  "preview_voice_provider": "preview-edge-tts",
  "voice_settings": {
    "elevenlabs": {
      "voice_id": "",
      "voice_name": "",
      "model_id": "eleven_multilingual_v2",
      "output_format": "mp3_44100_128",
      "stability": 0.72,
      "similarity_boost": 0.8,
      "style": 0.05,
      "use_speaker_boost": true,
      "language_code": "zh"
    },
    "edge_preview": {
      "voice": "zh-CN-XiaoxiaoNeural",
      "rate": "+2%",
      "pitch": "+0Hz"
    },
    "local_qwen": {
      "enabled": true,
      "profile": "young_calm_cn_female_explainer",
      "speaker": "serena",
      "language": "Chinese",
      "instruct": "",
      "model_dir": "C:\\Users\\Clr\\Desktop\\Video Maker\\TTS\\qwen3-tts-1.7b\\models\\Qwen3-TTS-12Hz-1.7B-CustomVoice",
      "helper_script": "C:\\Users\\Clr\\Desktop\\Video Maker\\TTS\\qwen3-tts-1.7b\\scripts\\generate_segments_qwen3.py",
      "python_executable": "C:\\Users\\Clr\\Desktop\\Video Maker\\TTS\\qwen3-tts-1.7b\\.venv\\Scripts\\python.exe",
      "format": "wav",
      "attn_implementation": "sdpa",
      "dtype": "bfloat16"
    }
  }
}
```

## Selection Logic

1. If the command explicitly passes `--provider elevenlabs-api`, require `ELEVENLABS_API_KEY`.
2. If the command explicitly passes `--provider elevenlabs-web`, require existing reviewed web-generated files or prepare a manifest.
3. If the command explicitly passes `--provider edge-preview`, always use Edge preview TTS.
4. If provider is `auto` and the target language is Chinese, prefer `local-qwen` first when the local helper is ready.
5. Only use `elevenlabs-api` for Chinese when the project already stores a reviewed API voice.
6. If reviewed web-generated audio already exists, allow explicit `elevenlabs-web`.
7. Otherwise fall back to Edge preview TTS and warn that the project is still on preview audio.

For a local deterministic pass, call `scripts/generate_tts_local_qwen.py`. It reuses the same profile, speaker, and detailed instruction for every segment, and also materializes the top-level `voice_persona` / `voice_consistency` fields into one explicit voice-lock prompt before calling the helper.

## Tuning Notes

- If Chinese pronunciation sounds like a foreigner reading Chinese, reject the voice instead of tweaking tiny parameters.
- For Chinese, do not treat a generic English library voice as the default just because it sounds good in English.
- Keep sentences short in `segments.json`; voice models sound worse when one segment tries to carry too much text.
- Use `prepare_web_tts_manifest.py` before browser generation and `record_voice_profile.py` after you approve or reject a voice.
- For Qwen3 consistency, do not change `profile`, `speaker`, or the base `instruct` midway through one video.
- If `voice_persona` and `voice_consistency` exist in `project.json`, the wrapper must inject them into the helper call; storing them as metadata only is not enough for acceptance.
- For deep parameter tuning, read `C:\Users\Clr\.agents\skills\text-to-speech\SKILL.md`.
