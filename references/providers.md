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
  "preview_voice_provider": "preview-edge-tts",
  "voice_settings": {
    "elevenlabs": {
      "voice_id": "",
      "voice_name": "",
      "model_id": "eleven_multilingual_v2",
      "output_format": "mp3_44100_128",
      "stability": 0.4,
      "similarity_boost": 0.8,
      "style": 0.15,
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
4. If provider is `auto` and the target language is Chinese, prefer `elevenlabs-web` first.
5. Only use `elevenlabs-api` for Chinese when the project already stores a reviewed API voice.
6. Otherwise fall back to Edge preview TTS and warn that the project is still on preview audio.

For a local deterministic pass, call `scripts/generate_tts_local_qwen.py`. It reuses the same profile, speaker, and detailed instruction for every segment.

## Tuning Notes

- If Chinese pronunciation sounds like a foreigner reading Chinese, reject the voice instead of tweaking tiny parameters.
- For Chinese, do not treat a generic English library voice as the default just because it sounds good in English.
- Keep sentences short in `segments.json`; voice models sound worse when one segment tries to carry too much text.
- Use `prepare_web_tts_manifest.py` before browser generation and `record_voice_profile.py` after you approve or reject a voice.
- For Qwen3 consistency, do not change `profile`, `speaker`, or the base `instruct` midway through one video.
- For deep parameter tuning, read `C:\Users\Clr\.agents\skills\text-to-speech\SKILL.md`.
