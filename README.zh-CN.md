# Video Maker

[English](./README.md) | [简体中文](./README.zh-CN.md)

`video-maker` 是一个面向 Codex 的 skill，用于在 Windows 上端到端制作 B 站讲解类视频。

## 仓库地图

- `SKILL.md`：skill 入口和操作规则
- `scripts/bootstrap_project.py`：新项目完整脚手架和运行时 helper 生成
- `scripts/bootstrap_video_project.py`：完整初始化包装器使用的底层内容脚手架
- `scripts/upgrade_project.py`：升级旧项目并重写运行时 helper
- `references/agent-orchestration.md`：简化后的 `content-strategist -> script-writer -> narration-polisher` 内容流水线
- `references/bilibili-tech-explainer-workflow.md`：按叙事 beat 组织的讲解视频工作流
- `references/narration-polisher.md`：口播润色 subagent 的职责和推荐提示词
- `references/quiet-glass-lab-v3.md`：iOS 18 inspired 的磨砂玻璃品牌提示词包
- `references/quiet-glass-lab/base.css`：中性渲染基础，不再作为视觉主题或模块模板
- `references/chinese-voice-rules.md`：中文旁白一致性规则
- `references/video-acceptance-rubric.md`：包含意义增量检查的最终 QA 闸门
- `references/imagegen-2-visual-playbook.md`：GPT Image 2 / imagegen 直接成图、视觉 QA 和重生规则
- `scripts/doctor.py`：环境检查器

## 模型

默认流程：

1. `coordinator` 创建项目、运行简单命令、分配 subagent 任务包，并做最终 go / no-go 决策。
2. `content-strategist` 写问题、观众、开头、意义、提纲、深度、细节和证据合同。
3. `script-writer` 写 `content/script_draft.json`。
4. `narration-polisher` 把完成稿润色成自然 B 站口播，输出 `content/narration_polish.json`。
5. `coordinator` 基于通过的口播编译 shot intents 和可渲染 segments。
6. `visual-architect` 设计 Remotion scenes，并用 `imagegen` 生成视觉资产、爆炸图、动画素材和封面底图。
7. `visual-qa-fixer` 检查 Remotion frame samples 和 `publish/cover.png`，修复代码、资产、封面文字或重生 imagegen 输出，直到没有视觉阻塞。
8. `production-engineer` 负责 Qwen master-track、Remotion props、时间线、渲染和导出。
9. `acceptance-reviewer` 检查多张真实截图、关键 Remotion 代码、内容合同，并听审必要音频。
10. 只有视频、封面、元数据、视觉 QA 和验收都通过后，才进入发布交接。

稳定默认：

- 新项目不再使用 HTML slide 渲染；内容和 shot intents 锁定后才生成 Remotion scene 代码和 props
- 主 agent 是 coordinator，不是全能制作者；内容、视觉、语音、装配和 review 默认委派
- 视频 composition、动画、字幕、音频挂载、时间线和渲染默认走 Remotion；视觉系统是品牌提示词包，不是固定 scene 模板
- 视觉资产和 B 站封面默认由 `visual-architect` + `imagegen` 生成，最终像素级修复归 `visual-qa-fixer`
- 视觉生产把 benchmark 和 key visual 记录进 `visual_asset_plan`，避免额外合同文件
- 中文旁白优先本地 Qwen
- 旁白使用单一 master-track 路径，带硬超时和 `voice_jobs/qwen_master_status.json` 状态 manifest
- 完整音频通过必须写入 `voice_profile.full_audio_review_status = passed`；开头或中段抽听只能作为辅助
- 中文语速按 2026-04-25 CUDA 视频校准：约 260 CJK 字/分钟；内容和 QA 通过时，时长不一致本身不阻塞
- 内容规划从 `problem_contract` 开始，再写有证据支撑的合同，之后才出现可渲染 segment
- 完成稿必须经过 `narration-polisher`，去掉 AI 机味并降低普通观众理解成本
- B 站封面在标题锁定和本地 QA 之后生成，不放在早期内容阶段
- `prepare_publish_job.py` 现在输出 `cover_path`，并在封面文件缺失时拒绝发布交接

真实发布到 B 站时，需要搭配 `desktop-control-for-windows`。

使用方式见 [SKILL.md](./SKILL.md)，品牌视觉规则见 [quiet-glass-lab-v3.md](./references/quiet-glass-lab-v3.md)，语音规则见 [chinese-voice-rules.md](./references/chinese-voice-rules.md)。Remotion 执行遵循配套的 `remotion-best-practices` skill。

## 许可证

MIT
