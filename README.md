# Video Maker

[English](./README.md) | [简体中文](./README.zh-CN.md)

`video-maker` is a Codex skill for end-to-end Bilibili explainer-video production on Windows.

## Repo map

- `SKILL.md`: entrypoint and operating rules
- `scripts/bootstrap_project.py`: full new-project scaffold plus runtime helper generation
- `scripts/bootstrap_video_project.py`: low-level content scaffold used by the full bootstrap wrapper
- `scripts/upgrade_project.py`: upgrade existing projects and rewrite runtime helpers
- `references/agent-orchestration.md`: simplified `content-strategist -> script-writer -> narration-polisher` content pipeline
- `references/bilibili-tech-explainer-workflow.md`: beat-driven explainer workflow
- `references/narration-polisher.md`: 口播润色 subagent 的职责和推荐提示词
- `remotion-best-practices` skill: default engine for video composition, animation, subtitles, audio mounting, timeline, and rendering
- `web-design-engineer` skill: optional visual-design support for layout and motion taste; production output stays in Remotion
- `references/quiet-glass-lab-v3.md`: iOS 18-inspired frosted glass brand prompt pack
- `references/quiet-glass-lab/base.css`: neutral render foundation only, not a visual theme or module template
- `references/chinese-voice-rules.md`: narration consistency rules
- `references/video-acceptance-rubric.md`: final QA gates including meaning-gain checks
- `publish/cover_prompt.md` in generated projects: imagegen-ready Bilibili cover prompt template
- `content/visual_qa_report.json` in generated projects: Remotion frame-sample and cover visual repair report
- `references/imagegen-2-visual-playbook.md`: GPT Image 2 / imagegen production rules for direct-rendered visuals with visual QA and regeneration
- `scripts/doctor.py`: environment checker

## Model

Default flow:

1. `coordinator` creates the project, runs simple commands, assigns subagent task packets, and makes final go / no-go decisions.
2. `content-strategist` writes problem, audience, opening, meaning, outline, depth, detail, and evidence contracts.
3. `script-writer` writes `content/script_draft.json`.
4. `narration-polisher` polishes the finished draft into natural Bilibili narration in `content/narration_polish.json`.
5. `coordinator` compiles shot intents and render-ready segments from the approved narration.
6. `visual-architect` designs Remotion scenes and uses `imagegen` for visual assets, exploded diagrams, animation assets, and the cover base.
7. `visual-qa-fixer` inspects Remotion frame samples and `publish/cover.png`, then fixes Remotion code/assets/cover text or regenerates imagegen outputs until visual blockers are gone.
8. `production-engineer` owns Qwen master-track audio, Remotion props, timeline, render, and export.
9. `acceptance-reviewer` checks many real screenshots, reads key Remotion code and content contracts, and listens to required audio samples.
10. Publish handoff runs only after video, cover, metadata, visual QA, and acceptance all pass.

Stable defaults:

- new projects do not use HTML slide rendering; Remotion scene code and props appear after content and shot intents are locked
- the main agent is a coordinator, not a maker; substantial content, visuals, voice, assembly, and review are delegated
- video composition, animation, subtitles, audio mounting, timeline, and rendering default to Remotion; the visual system is a brand prompt pack, not fixed scene templates
- visual assets and Bilibili covers default to `visual-architect` + `imagegen`, with final rendered-pixel repair owned by `visual-qa-fixer`
- visual production records benchmark and key visual inside `visual_asset_plan` so inspiration, cover promise, reusable key visual, imagegen assets, and QA stay connected without extra contract files
- Chinese narration prefers local Qwen first
- narration uses a single master-track path with a hard timeout and `voice_jobs/qwen_master_status.json` status manifest
- full-audio approval requires `voice_profile.full_audio_review_status = passed`; opening or midpoint spot checks are only supporting notes
- Chinese pace target is calibrated to the 2026-04-25 CUDA video: about 260 CJK chars/min, with duration mismatch treated as non-blocking when content and QA pass
- content planning now starts from `problem_contract`, then writes evidence-backed contracts before any render-ready segment exists
- finished content drafts are always sent through `narration-polisher` to remove AI machine-tone and lower ordinary viewer comprehension cost
- Bilibili cover generation happens after title lock and local QA, not during early content phases
- `prepare_publish_job.py` now emits `cover_path` and refuses publish handoff when the cover file is missing

For real Bilibili publishing, pair this skill with `desktop-control-for-windows`.

See [SKILL.md](./SKILL.md) for usage, [quiet-glass-lab-v3.md](./references/quiet-glass-lab-v3.md) for brand visual rules, and [chinese-voice-rules.md](./references/chinese-voice-rules.md) for voice rules. Remotion execution follows the companion `remotion-best-practices` skill.

## License

MIT
