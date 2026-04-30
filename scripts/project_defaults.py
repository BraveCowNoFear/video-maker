from __future__ import annotations

from copy import deepcopy
from pathlib import Path

DEFAULT_LOCAL_QWEN_PYTHON = Path(
    r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\.venv\Scripts\python.exe"
)
DEFAULT_LOCAL_QWEN_HELPER = Path(
    r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\scripts\generate_segments_qwen3.py"
)
DEFAULT_LOCAL_QWEN_MODEL = Path(
    r"C:\Users\Clr\Desktop\Video Maker\TTS\qwen3-tts-1.7b\models\Qwen3-TTS-12Hz-1.7B-CustomVoice"
)

DEFAULT_CONTENT_SUBAGENT_FLOW = [
    {
        "role": "content-strategist",
        "phase": "content-contracts",
        "must_run": True,
        "writes": [
            "content/problem_contract.json",
            "content/audience_contract.json",
            "content/opening_contract.json",
            "content/meaning_contract.json",
            "content/outline_plan.json",
            "content/depth_contract.json",
            "content/detail_weave.json",
            "content/evidence_map.json",
        ],
        "handoff_to": "script-writer",
    },
    {
        "role": "script-writer",
        "phase": "script-draft",
        "must_run": True,
        "reads": [
            "content/problem_contract.json",
            "content/audience_contract.json",
            "content/opening_contract.json",
            "content/meaning_contract.json",
            "content/outline_plan.json",
            "content/depth_contract.json",
            "content/detail_weave.json",
            "content/evidence_map.json",
        ],
        "writes": ["content/script_draft.json"],
        "handoff_to": "narration-polisher",
    },
    {
        "role": "narration-polisher",
        "phase": "narration-polish",
        "must_run": True,
        "reads": [
            "content/script_draft.json",
            "content/evidence_map.json",
        ],
        "writes": ["content/narration_polish.json"],
        "handoff_to": "coordinator",
    },
]
DEFAULT_SUPPORT_ROLES = [
    "visual-architect",
    "visual-qa-fixer",
    "production-engineer",
    "acceptance-reviewer",
]
DEFAULT_COORDINATOR_RULES = [
    "coordinator-only-orchestrates",
    "simple-commands-allowed",
    "delegate-content-visual-voice-assembly-and-review",
    "do-not-author-long-narration-remotion-cover-audio-strategy-or-review-report",
]
DEFAULT_CONTENT_ARTIFACTS = [
    "content/problem_contract.json",
    "content/audience_contract.json",
    "content/opening_contract.json",
    "content/meaning_contract.json",
    "content/outline_plan.json",
    "content/depth_contract.json",
    "content/detail_weave.json",
    "content/evidence_map.json",
    "content/script_draft.json",
    "content/narration_polish.json",
    "content/style_contract.json",
    "content/shot_intents.json",
    "content/visual_asset_plan.json",
    "content/segments.json",
    "content/screenshot_plan.json",
    "content/visual_qa_report.json",
    "content/acceptance_report.json",
]
DEFAULT_SCENE_COMPILER_CHAIN = [
    "content/style_contract.json",
    "content/shot_intents.json",
    "content/visual_asset_plan.json",
    "content/segments.json",
    "remotion/input-props.json",
]
DEFAULT_SHOT_ROLE_TAXONOMY = [
    "hook",
    "problem-frame",
    "thesis",
    "system-map",
    "mechanism",
    "formula",
    "exploded-view",
    "annotated-screenshot",
    "comparison",
    "tradeoff",
    "demo",
    "caveat",
    "takeaway",
    "scale-jump",
    "human-anchor",
]
DEFAULT_EXPLAINER_MODES = [
    "tool-workflow",
    "system-mechanism",
    "math-formula",
    "hardware-teardown",
    "concept-mental-model",
    "comparison-tradeoff",
]
DEFAULT_IMAGEGEN_ASSET_JOBS = [
    "tactile_anchor",
    "hero_silhouette",
    "mechanism_base",
    "scale_scene",
    "contrast_key_visual",
    "chapter_bumper",
    "cover_base",
    "texture_or_depth_plate",
]
DEFAULT_VISUAL_NARRATIVE_PATTERNS = [
    "wrong_model_vs_real_model",
    "inside_the_black_box",
    "scale_jump",
    "bottleneck_reveal",
    "counterfactual_pair",
    "evidence_cutaway",
    "memory_object",
]
DEFAULT_FRONTEND_DESIGN_SKILL = "web-design-engineer"
DEFAULT_RENDER_ENGINE = "remotion"
DEFAULT_REMOTION_COMPOSITION_ID = "VideoMaker"
DEFAULT_REMOTION_DIR = "remotion"
DEFAULT_VISUAL_THEME = "remotion + imagegen + quiet-glass-lab"
DEFAULT_VISUAL_THEME_ALIASES = {
    "",
    "web-design-engineer",
    "web-design-engineer-quiet-glass-lab",
    "quiet-glass-lab",
    "quiet-glass-lab-v3",
    "ios18-frosted-glass",
    "ios18-frosted-glass-black-green",
    "ios18-inspired-frosted-science-deck",
    "ios26-liquid-glass",
    "ios26-liquid-glass-black-green",
}
DEFAULT_STYLE_PROMPT_PACK = (
    "视觉实现默认使用 Remotion：先锁 palette / typography / spacing / radius / motion，"
    "再生成高质感 React composition。把场景做成黑绿、content-first 的 iOS 18-inspired frosted glass tech explainer。"
    "不是手机 App 模拟，也不是固定模板；版式、比例、动效和模块数量由内容决定。"
    "深色主阅读面保持高对比，玻璃只用于图解卡、数据卡、标签和短时解释层；"
    "避免廉价 AI 渐变/发光、假状态栏、设备壳、glass-on-glass 和透明正文。"
)
DEFAULT_GLASS_USAGE_RULES = [
    "正文层保持 solid / near-solid；图解卡、数据卡和对照卡可以使用半透明磨砂玻璃，但文字下面要有更实的承载层。",
    "使用大圆角模块、soft blur、细亮边和克制高光，不做厚重塑料质感或强折射特效。",
    "层级靠 typography、grouping、spacing、size 和稀疏 tint 建立，不靠到处发光。",
    "避免 glass-on-glass、长段透明正文、假状态栏、手机导航栏和 Apple App screenshot cosplay。",
]
DEFAULT_STYLE_INVARIANTS = [
    "prompt-driven-not-template",
    "motion-and-render-by-remotion",
    "layout-varies-by-content",
    "black-carbon-base-plus-acid-lime-emphasis",
    "ios18-inspired-frosted-modules",
    "one-visual-center-per-scene",
    "phone-readable-chinese-typography",
    "imagegen-direct-render-plus-visual-qa",
    "key-visual-reuse-across-cover-and-scenes",
]
DEFAULT_STYLE_AVOID = [
    "fixed-page-taxonomy",
    "cheap-ai-gradient-glow",
    "left-border-accent-card-cliche",
    "emoji-or-icon-spam",
    "fabricated-data",
    "copied-apple-screenshot-layouts",
    "phone-app-chrome-compositions",
    "full-screen-glass-content-panels",
    "rainbow-neon-translucency",
    "glass-used-as-main-reading-surface",
    "fake-cinematic-b-roll-without-evidence",
]
DEFAULT_FORBIDDEN_UI_ELEMENTS = [
    "fake_status_bar",
    "fake_device_shell",
    "bottom_tab_bar",
    "settings_screen_clone",
    "glass_paragraph_wall",
    "glass_on_glass",
]
DEFAULT_ACCEPTANCE_GATES = [
    "coverage_complete",
    "content_depth",
    "meaning_gain",
    "narration_naturalness",
    "voice_full_listening_passed",
    "ui_supports_content",
    "visual_screenshot_bug_review",
    "visual_qa_fix_pass",
    "remotion_content_authenticity",
    "content_authenticity",
    "formula_legibility",
    "diagram_annotation_truthfulness",
    "screenshot_traceability",
    "voice_consistency",
]
DEFAULT_BILIBILI_COVER_PATH = "publish/cover.png"
DEFAULT_BILIBILI_COVER_PROMPT_PATH = "publish/cover_prompt.md"
DEFAULT_BILIBILI_COVER_PROMPT_TEMPLATE = (
    "帮我设计一个视频封面，视频标题是“【标题】”，这是b站视频，"
    "你可以发挥你的设计审美，可以不需要原封不动的出现视频标题哦！"
    "极简风格，有视觉冲击力，主题色黑和荧光绿#【实际logo色号】"
)

LOCAL_QWEN_BASE_INSTRUCT = (
    "请用同一个年轻中文女声稳定讲解科普内容。"
    "气质沉稳、大方、亲和，语速中速偏快且稳定，呼吸轻短，重点词轻微强调。"
    "开头必须直接用标准自然中文进入正文，不要出现乱码、拟声、外语、无意义音节或非中文热场。"
    "不要幼态、撒娇、夹子音、播音腔或突然兴奋。"
)


def _copy(value):
    return deepcopy(value)


def default_shot_role_for_index(index: int, total: int) -> str:
    return "content-derived"


def should_refresh_default_visual_contract(project: dict, ui_system: dict) -> bool:
    theme = str(ui_system.get("theme") or project.get("visual_style") or "").strip().lower()
    return theme in DEFAULT_VISUAL_THEME_ALIASES


def apply_default_visual_contract(project: dict, ui_system: dict) -> None:
    project["visual_style"] = DEFAULT_VISUAL_THEME
    ui_system["theme"] = DEFAULT_VISUAL_THEME
    ui_system["prompt_mode"] = "style-not-template"
    ui_system["render_engine"] = DEFAULT_RENDER_ENGINE
    ui_system["frontend_design_skill"] = DEFAULT_FRONTEND_DESIGN_SKILL
    ui_system["design_authority"] = "Remotion handles composition, animation, subtitles, audio mounting, timeline, and final rendering; imagegen handles production bitmap visuals; Quiet Glass Lab is only the brand constraint."
    ui_system["style_prompt_pack"] = DEFAULT_STYLE_PROMPT_PACK
    ui_system["visual_language"] = "remotion-quiet-glass-black-green"
    ui_system["palette"] = {"accent": "#D0F810", "ink": "#F7FAF4", "canvas": "#020302"}
    ui_system["style_invariants"] = _copy(DEFAULT_STYLE_INVARIANTS)
    ui_system["style_avoid"] = _copy(DEFAULT_STYLE_AVOID)
    ui_system["glass_usage_rules"] = _copy(DEFAULT_GLASS_USAGE_RULES)
    ui_system["mobile_readability"] = "required"
    ui_system["forbidden_ui_elements"] = _copy(DEFAULT_FORBIDDEN_UI_ELEMENTS)


def apply_project_defaults(project: dict, voice_provider: str | None = None) -> dict:
    voice_language = str(project.get("voice_language") or "zh-CN")

    if voice_provider:
        project["voice_provider"] = voice_provider
    else:
        project.setdefault("voice_provider", "local-qwen")

    project["voice_language"] = voice_language
    project.setdefault("preview_voice_provider", "preview-edge-tts")
    project.setdefault("voice_quality_bar", "publish_requires_reviewed_natural_voice_for_chinese")
    project.setdefault("canvas_ratio", "16:9")

    content_strategy = project.setdefault("content_strategy", {})
    content_strategy.pop("series_goal", None)
    content_strategy.pop("episode_goal", None)
    content_strategy.pop("segment_count_policy", None)
    content_strategy.pop("duration_policy", None)
    if str(content_strategy.get("main_agent_role") or "").strip().lower() in {"", "chief-editor", "chief_editor"}:
        content_strategy["main_agent_role"] = "coordinator"
    content_strategy.setdefault("coordinator_rules", _copy(DEFAULT_COORDINATOR_RULES))
    subagent_flow = content_strategy.setdefault("content_subagent_flow", _copy(DEFAULT_CONTENT_SUBAGENT_FLOW))
    if isinstance(subagent_flow, list):
        flow_roles = {str(item.get("role") or "") for item in subagent_flow if isinstance(item, dict)}
        legacy_roles = {"outline-researcher", "depth-builder", "detail-filler"}
        if legacy_roles & flow_roles or "script-writer" not in flow_roles:
            content_strategy["content_subagent_flow"] = _copy(DEFAULT_CONTENT_SUBAGENT_FLOW)
        else:
            for item in subagent_flow:
                if (
                    isinstance(item, dict)
                    and item.get("role") == "narration-polisher"
                    and item.get("handoff_to") in {"chief-editor", "chief_editor"}
                ):
                    item["handoff_to"] = "coordinator"
    support_roles = content_strategy.setdefault("support_roles", _copy(DEFAULT_SUPPORT_ROLES))
    if isinstance(support_roles, list):
        content_strategy["support_roles"] = [
            "production-engineer" if role == "voice-director" else role
            for role in support_roles
            if role != "cover-designer"
        ]
        for role in DEFAULT_SUPPORT_ROLES:
            if role not in content_strategy["support_roles"]:
                content_strategy["support_roles"].append(role)
    artifacts = content_strategy.setdefault("artifacts", _copy(DEFAULT_CONTENT_ARTIFACTS))
    if isinstance(artifacts, list):
        for artifact in DEFAULT_CONTENT_ARTIFACTS:
            if artifact not in artifacts:
                artifacts.append(artifact)
    content_strategy.setdefault("scene_compiler_chain", _copy(DEFAULT_SCENE_COMPILER_CHAIN))
    content_strategy.setdefault("shot_role_taxonomy", _copy(DEFAULT_SHOT_ROLE_TAXONOMY))
    content_strategy.setdefault("explainer_modes", _copy(DEFAULT_EXPLAINER_MODES))
    content_strategy.setdefault("visual_narrative_patterns", _copy(DEFAULT_VISUAL_NARRATIVE_PATTERNS))
    content_strategy.setdefault("explainer_mode_policy", "choose_mode_before_outline_then_route_visual_representation_per_beat")
    content_strategy.setdefault(
        "representation_policy",
        {
            "imagegen": "final visual rendering, including Chinese text, formulas, labels, numbers, UI-like states, and cover copy; visual-qa-fixer must inspect and regenerate if inaccurate",
            "remotion": "single path for video composition, animation, subtitles, audio mounting, timeline, frame sampling, and final render",
            "react_css": "Remotion scene implementation layer for layout, motion, crop-safe surfaces, and non-imagegen utility UI only when the beat truly needs code-native layout",
            "latex": "formula source-of-truth for review, but final formula visuals may be rendered by imagegen and must be visually checked",
            "animation": "Remotion-driven state changes, feedback loops, phase transitions, propagation, iteration, accumulated error",
            "hybrid": "imagegen direct render plus Remotion motion shell when needed; regenerate imagegen output when text or symbols are wrong",
        },
    )
    content_strategy.setdefault("structure_policy", "content-decides")
    content_strategy.setdefault(
        "scene_compiler_rule",
        "compile_style_contract_then_shot_intents_then_segments_without_using_fixed_page_templates",
    )
    content_strategy.setdefault(
        "delegation_fallback",
        "prepare_task_packets_and_pause_or_request_authorization_when_subagents_are_unavailable",
    )
    if content_strategy.get("delegation_fallback") == "run_outline_then_depth_then_detail_then_narration_polish_locally_when_subagents_are_unavailable":
        content_strategy["delegation_fallback"] = "prepare_task_packets_and_pause_or_request_authorization_when_subagents_are_unavailable"

    ui_system = project.setdefault("ui_system", {})
    if should_refresh_default_visual_contract(project, ui_system):
        apply_default_visual_contract(project, ui_system)
    else:
        project.setdefault("visual_style", DEFAULT_VISUAL_THEME)
        ui_system.setdefault("theme", DEFAULT_VISUAL_THEME)
        ui_system.setdefault("prompt_mode", "style-not-template")
        ui_system.setdefault("render_engine", DEFAULT_RENDER_ENGINE)
        ui_system.setdefault("frontend_design_skill", DEFAULT_FRONTEND_DESIGN_SKILL)
        ui_system.setdefault("design_authority", "Remotion handles composition, animation, subtitles, audio mounting, timeline, and final rendering; imagegen handles production bitmap visuals; Quiet Glass Lab is only the brand constraint.")
        ui_system.setdefault("style_prompt_pack", DEFAULT_STYLE_PROMPT_PACK)
        ui_system.setdefault("visual_language", "remotion-quiet-glass-black-green")
        ui_system.setdefault("palette", {"accent": "#D0F810", "ink": "#F7FAF4", "canvas": "#020302"})
        ui_system.setdefault("style_invariants", _copy(DEFAULT_STYLE_INVARIANTS))
        ui_system.setdefault("style_avoid", _copy(DEFAULT_STYLE_AVOID))
        ui_system.setdefault("glass_usage_rules", _copy(DEFAULT_GLASS_USAGE_RULES))
        ui_system.setdefault("mobile_readability", "required")
        ui_system.setdefault("forbidden_ui_elements", _copy(DEFAULT_FORBIDDEN_UI_ELEMENTS))
    ui_system.setdefault("remotion_dir", DEFAULT_REMOTION_DIR)
    ui_system.setdefault("remotion_composition_id", DEFAULT_REMOTION_COMPOSITION_ID)
    ui_system.setdefault("base_css_mode", "legacy-only")
    ui_system.setdefault("html_scaffold_mode", "legacy-only")
    ui_system.setdefault("visual_owner", "visual-architect")
    ui_system.setdefault("imagegen_owner", "visual-architect")
    ui_system.setdefault("visual_qa_owner", "visual-qa-fixer")
    ui_system.setdefault("imagegen_model_preference", "gpt-image-2 via imagegen skill for production bitmap bases")
    ui_system.setdefault("imagegen_playbook", "references/imagegen-2-visual-playbook.md")
    ui_system.setdefault("imagegen_asset_jobs", _copy(DEFAULT_IMAGEGEN_ASSET_JOBS))
    ui_system.setdefault(
        "visual_qa_rule",
        "visual-qa-fixer must inspect Remotion-rendered frame samples and cover pixels, then fix Remotion code/assets/cover before production handoff.",
    )
    ui_system.setdefault(
        "imagegen_scope",
        ["visual_design_assets", "exploded_diagrams", "mechanism_diagrams", "animation_assets", "cover"],
    )

    workflow = project.setdefault("voice_workflow", {})
    workflow["narration_mode"] = "master-track-preferred"
    workflow["timing_strategy"] = "master-audio-then-text-ratio"
    workflow.setdefault("spoken_text_strategy", "prefer_tts_text_then_voice")
    workflow.setdefault("text_normalization", "script-aware")
    workflow["publish_mode"] = "local-qwen-first"
    workflow.setdefault("accent_review_required", True)
    workflow.pop("web_manifest", None)

    render_pipeline = project.setdefault("render_pipeline", {})
    render_pipeline["engine"] = DEFAULT_RENDER_ENGINE
    render_pipeline.setdefault("remotion_dir", DEFAULT_REMOTION_DIR)
    render_pipeline.setdefault("composition_id", DEFAULT_REMOTION_COMPOSITION_ID)
    render_pipeline.setdefault("props_path", "remotion/input-props.json")
    render_pipeline.setdefault("public_audio_dir", "remotion/public/audio")
    render_pipeline.setdefault("public_asset_dir", "remotion/public/assets")
    render_pipeline.setdefault("frame_sample_dir", "remotion_frames")
    render_pipeline.setdefault(
        "ownership",
        "Remotion owns composition, animation, subtitles, audio mounting, timeline, frame sampling, and final render; imagegen owns production bitmap assets and cover.",
    )

    publish = project.setdefault("publish", {})
    publish.setdefault("platform", "bilibili")
    publish.setdefault("cover_required", True)
    publish.setdefault("cover_path", DEFAULT_BILIBILI_COVER_PATH)
    publish.setdefault("cover_prompt_path", DEFAULT_BILIBILI_COVER_PROMPT_PATH)
    publish.setdefault("browser_preference", "microsoft-edge-stable")
    publish.setdefault("browser_channel", "stable")
    publish.setdefault("browser_channel_avoid", ["edge-dev"])
    publish.setdefault(
        "browser_login_requirement",
        "open bilibili in the already signed-in Microsoft Edge stable window, not Edge Dev",
    )
    if str(publish.get("cover_generation_owner") or "").strip().lower() in {"", "chief-editor", "chief_editor", "cover-designer"}:
        publish["cover_generation_owner"] = "visual-architect"
    if str(publish.get("cover_generation_mode") or "").strip().lower() in {"", "main-agent-imagegen-first"}:
        publish["cover_generation_mode"] = "visual-architect-imagegen"
    publish.setdefault("cover_visual_qa_owner", "visual-qa-fixer")
    publish.setdefault(
        "cover_text_accuracy_rule",
        "exact Chinese cover text should be generated directly by imagegen; visual-qa-fixer must inspect it and regenerate until it is correct.",
    )
    publish.setdefault(
        "cover_generation_stage",
        "after-local-qa-and-title-lock-before-prepare-publish-job",
    )
    publish.setdefault("cover_upload_verification_required", True)
    publish.setdefault(
        "cover_upload_verification_rule",
        "after uploading cover_path, verify the Bilibili form visibly shows the custom cover before final publish",
    )
    publish.setdefault(
        "duration_mismatch_policy",
        "duration mismatch is not a publish blocker when content, voice, visual QA, cover, and metadata pass",
    )
    if str(publish.get("cover_delegation_policy") or "").strip().lower() in {
        "",
        "allow-at-most-one-sidecar-subagent-for-variant-exploration-only",
    }:
        publish["cover_delegation_policy"] = "no-separate-cover-designer-role"

    voice_profile = project.setdefault("voice_profile", {})
    voice_profile.setdefault("provider", "")
    voice_profile.setdefault("voice_name", "")
    voice_profile.setdefault("locale", "")
    voice_profile.setdefault("source_type", "")
    voice_profile.setdefault("review_status", "unreviewed")
    voice_profile.setdefault("review_notes", [])
    voice_profile.pop("mode", None)
    voice_profile.pop("voice_id", None)

    voice_persona = project.setdefault("voice_persona", {})
    voice_persona.setdefault("id", "cn_female_steady_graceful_cute_v1")
    voice_persona.setdefault("display_name", "沉稳大方可爱女声")
    voice_persona.setdefault("identity", "熟悉 AI 和工具工作流、表达克制但友好的年轻中文女生。")
    voice_persona.setdefault("core_traits", ["沉稳", "大方", "亲和", "轻微可爱"])
    voice_persona.setdefault("forbidden_traits", ["幼态", "撒娇", "夹子音", "播音腔", "突然兴奋"])
    voice_persona.setdefault("baseline_emotion", "calm_friendly")
    voice_persona.setdefault("pace", "medium_fast_steady")
    voice_persona.setdefault("breath", "light_short_controlled")
    voice_persona.setdefault("emphasis", "light_keyword_only")
    voice_persona.setdefault("qwen_base_instruct", LOCAL_QWEN_BASE_INSTRUCT)

    voice_consistency = project.setdefault("voice_consistency", {})
    voice_consistency["strategy"] = "master-track-preferred"
    voice_consistency["lock_fields"] = ["profile", "speaker", "language", "model_dir", "base_instruct"]
    voice_consistency["fallback_mode"] = "fix-master-pass-or-preview-edge"
    voice_consistency.setdefault("emotion_variance", "low")
    voice_consistency.setdefault("pace_variance", "low")
    voice_consistency.setdefault("breath_variance", "low")

    acceptance = project.setdefault("acceptance", {})
    acceptance.setdefault("reviewer", "acceptance-reviewer")
    must_pass = acceptance.setdefault("must_pass", _copy(DEFAULT_ACCEPTANCE_GATES))
    if isinstance(must_pass, list):
        for index, gate in enumerate(list(must_pass)):
            if gate == "html_content_authenticity":
                must_pass[index] = "remotion_content_authenticity"
        for gate in DEFAULT_ACCEPTANCE_GATES:
            if gate not in must_pass:
                must_pass.append(gate)
    acceptance.setdefault("fail_action", "route_back_to_owner_and_regen")
    acceptance.setdefault("screenshot_review_required", True)
    acceptance.setdefault("screenshot_review_minimum", "many_actual_video_screenshots_or_remotion_frame_samples")
    acceptance.setdefault("remotion_review_required", True)
    acceptance.pop("html_review_required", None)
    acceptance.setdefault("content_authenticity_review_required", True)

    settings = project.setdefault("voice_settings", {})
    settings.pop("elevenlabs", None)
    edge = settings.setdefault("edge_preview", {})
    edge.setdefault("voice", "zh-CN-XiaoxiaoNeural")
    edge.setdefault("rate", "+2%")
    edge.setdefault("pitch", "+0Hz")

    local_qwen = settings.setdefault("local_qwen", {})
    local_qwen.setdefault("enabled", True)
    local_qwen.setdefault("profile", "young_calm_cn_female_explainer")
    local_qwen.setdefault("speaker", "serena")
    local_qwen.setdefault("language", "Chinese")
    local_qwen.setdefault("instruct", LOCAL_QWEN_BASE_INSTRUCT)
    local_qwen.setdefault("model_dir", str(DEFAULT_LOCAL_QWEN_MODEL))
    local_qwen.setdefault("helper_script", str(DEFAULT_LOCAL_QWEN_HELPER))
    local_qwen.setdefault("python_executable", str(DEFAULT_LOCAL_QWEN_PYTHON))
    local_qwen.setdefault("format", "wav")
    local_qwen.setdefault("attn_implementation", "sdpa")
    local_qwen.setdefault("dtype", "bfloat16")
    local_qwen.setdefault("long_form_supported", True)
    local_qwen.setdefault("target_cjk_chars_per_minute", 260)
    local_qwen.setdefault("acceptable_cjk_chars_per_minute_min", 240)
    local_qwen.setdefault("acceptable_cjk_chars_per_minute_max", 285)
    local_qwen.setdefault("pace_reference", "CUDA 2026-04-25 published video: 2434 CJK chars / 560.37 sec = 261 CJK chars per minute")
    local_qwen.setdefault("full_audio_review_required", True)
    local_qwen.setdefault("synthesis_timeout_sec", 900)
    local_qwen.setdefault("status_manifest", "voice_jobs/qwen_master_status.json")
    local_qwen.pop("must_pass_opening_chinese_review_sec", None)
    local_qwen.setdefault("trim_silence_ms", 18)
    local_qwen.setdefault("fade_ms", 12)

    return project


def build_project_data(topic: str, slug: str, voice_provider: str = "local-qwen") -> dict:
    project = {
        "topic": topic,
        "slug": slug,
        "output_name": f"{slug}.mp4",
        "audience": "聪明但可能带着错误直觉的 B 站科普观众。",
    }
    return apply_project_defaults(project, voice_provider=voice_provider)


def build_problem_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_problem_contract",
        "next_owner": "content-strategist",
        "root_question": f"待定义：这期关于 {topic} 真正要解决的唯一主问题。",
        "why_this_question_matters": "待定义：为什么观众现在值得看这个问题。",
        "false_easy_answer": "待定义：观众或普通内容最容易给出的浅答案。",
        "why_it_is_hard": "待定义：这个问题真正难在什么隐藏变量、尺度、证据或权衡。",
        "difficulty_source": "to-be-selected",
        "what_would_change_the_viewer_judgment": "待定义：看完后观众哪一个判断会被改变。",
        "answer_shape": "to-be-selected",
        "primary_evidence_carrier": "to-be-selected",
        "supporting_evidence_carrier": "to-be-selected",
        "sub_questions": [],
        "non_questions": [],
        "minimum_satisfying_answer": "待定义：少于什么就不算真正回答了问题。",
    }


def build_audience_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_audience_contract",
        "next_owner": "content-strategist",
        "viewer_baseline": "待定义：普通 B 站用户已经知道什么。",
        "likely_misreadings": [],
        "term_budget": {
            "max_new_terms_per_minute": 2,
            "must_define_before_use": True,
        },
        "must_define_terms": [],
        "dangerous_intuitions": [],
        "allowed_context_level": "plain-language-first",
        "plain_language_targets": [
            "先用生活直觉或可见关系解释，再给术语。",
            "每个抽象判断都要落到可观察对象、关系或代价上。",
        ],
    }


def build_opening_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_opening_contract",
        "next_owner": "content-strategist",
        "false_intuition": "待定义：观众最自然但不够准确的直觉。",
        "why_it_feels_plausible": "待定义：这个直觉为什么看起来合理。",
        "where_it_breaks": "待定义：它在哪个条件、尺度、证据或边界上失效。",
        "opening_question": "待定义：开头承诺要解决的具体问题。",
        "thesis": "待定义：这期会交付的更强看法。",
        "route_map": [],
        "promised_answer": "待定义：开头承诺不会回避的答案。",
    }


def build_outline_plan_data(topic: str) -> dict:
    return {
        "version": "v3",
        "topic": topic,
        "outline_status": "needs_outline",
        "next_owner": "content-strategist",
        "based_on_problem_contract": "content/problem_contract.json",
        "based_on_audience_contract": "content/audience_contract.json",
        "based_on_opening_contract": "content/opening_contract.json",
        "audience_problem": f"待定义：这期关于 {topic}，观众最容易卡住的误解是什么。",
        "audience_baseline": "待定义：普通 B 站用户理解这期需要的起点。",
        "term_budget": {"max_new_terms_per_minute": 2, "must_define_before_use": True},
        "opening_contract": "content/opening_contract.json",
        "episode_thesis": f"待定义：这期关于 {topic} 的核心命题是什么。",
        "episode_scope": "待定义：这期需要覆盖到什么范围、边界或重点。",
        "story_shape": "to-be-decided",
        "pacing_strategy": "to-be-decided",
        "coverage_contract": {
            "must_answer": [],
            "what_not_to_overclaim": [],
            "question_policy": "content-decides",
        },
        "open_questions": [],
        "beats": [],
    }


def build_meaning_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_meaning_contract",
        "next_owner": "content-strategist",
        "viewer_before": "待定义：观众看这期之前通常卡在哪里。",
        "viewer_after": "待定义：观众看完后会多一种什么判断方式或行动能力。",
        "core_judgment": "待定义：这期最终要交给观众的核心判断。",
        "why_watch_now": "待定义：为什么这个主题现在值得看。",
        "explainer_mode": "to-be-selected",
        "domain_type": "to-be-selected",
        "target_misunderstandings": [],
        "scale_jumps": [],
        "representation_decisions": [],
        "must_not_be": [
            "知识点堆叠",
            "只解释名词",
            "为了显得完整而扩写无关内容",
            "用好看的图冒充事实",
        ],
        "beats": [],
    }


def build_depth_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_depth",
        "next_owner": "content-strategist",
        "based_on_outline": "content/outline_plan.json",
        "based_on_problem_contract": "content/problem_contract.json",
        "episode_depth_goal": {
            "context_note": "待定义：这期与上下文、背景或使用场景的关系。",
            "confusion_knot": "待定义：这期最容易长期讲混的核心结在哪里。",
            "resolution_note": "待定义：这期最终要收束到什么理解或结论。",
        },
        "beats": [],
        "routing": {
            "needs_outline_rework": [],
            "ready_for_detail": [],
        },
    }


def build_detail_weave_data() -> dict:
    return {
        "version": "v1",
        "detail_status": "needs_detail",
        "next_owner": "script-writer",
        "source_contracts": {
            "problem_contract": "content/problem_contract.json",
            "outline_plan": "content/outline_plan.json",
            "depth_contract": "content/depth_contract.json",
            "evidence_map": "content/evidence_map.json",
        },
        "locks": {
            "coverage_shape_locked": True,
            "beat_order_locked": True,
            "claims_locked": True,
        },
        "beats": [],
        "sources": [],
        "deferred_details": [],
    }


def build_evidence_map_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_evidence_map",
        "next_owner": "script-writer",
        "claims": [],
        "source_refs": [],
        "known_unknowns": [],
        "disagreement_notes": [],
        "deferred_but_important_questions": [],
    }


def build_script_draft_data() -> dict:
    return {
        "version": "v1",
        "status": "needs_script_draft",
        "next_owner": "script-writer",
        "source_contracts": {
            "problem_contract": "content/problem_contract.json",
            "audience_contract": "content/audience_contract.json",
            "opening_contract": "content/opening_contract.json",
            "meaning_contract": "content/meaning_contract.json",
            "outline_plan": "content/outline_plan.json",
            "depth_contract": "content/depth_contract.json",
            "detail_weave": "content/detail_weave.json",
            "evidence_map": "content/evidence_map.json",
        },
        "constraints": {
            "beat_order_locked": True,
            "no_new_facts_without_evidence_map": True,
            "plain_bilibili_audience_required": True,
        },
        "beats": [],
    }


def build_narration_polish_data() -> dict:
    return {
        "version": "v2",
        "status": "needs_narration_polish",
        "next_owner": "narration-polisher",
        "source_contracts": {
            "script_draft": "content/script_draft.json",
            "evidence_map": "content/evidence_map.json",
        },
        "constraints": {
            "beat_order_locked": True,
            "resolved_claim_locked": True,
            "no_new_facts_without_source": True,
            "spoken_chinese_required": True,
            "plain_bilibili_audience_required": True,
        },
        "beats": [],
        "global_avoid": [
            "营销腔",
            "为了显得聪明而堆术语",
            "一句里塞太多转折",
            "像模型解释模型一样的自我指涉",
        ],
    }


def build_style_contract_data() -> dict:
    return {
        "version": "v1",
        "status": "active",
        "prompt_mode": "style-not-template",
        "theme": DEFAULT_VISUAL_THEME,
        "render_engine": DEFAULT_RENDER_ENGINE,
        "remotion_dir": DEFAULT_REMOTION_DIR,
        "remotion_composition_id": DEFAULT_REMOTION_COMPOSITION_ID,
        "frontend_design_skill": DEFAULT_FRONTEND_DESIGN_SKILL,
        "imagegen_owner": "visual-architect",
        "imagegen_model_preference": "gpt-image-2 via imagegen skill for production bitmap bases",
        "imagegen_playbook": "references/imagegen-2-visual-playbook.md",
        "imagegen_scope": ["visual_design_assets", "exploded_diagrams", "mechanism_diagrams", "animation_assets", "cover"],
        "imagegen_asset_jobs": _copy(DEFAULT_IMAGEGEN_ASSET_JOBS),
        "design_authority": "Use Remotion for composition, animation, subtitles, audio mounting, timeline, and final rendering; use imagegen for production bitmap visuals; use Quiet Glass Lab only as the brand constraint.",
        "visual_language": "remotion-quiet-glass-black-green",
        "style_prompt_pack": DEFAULT_STYLE_PROMPT_PACK,
        "style_invariants": _copy(DEFAULT_STYLE_INVARIANTS),
        "style_avoid": _copy(DEFAULT_STYLE_AVOID),
        "glass_usage_rules": _copy(DEFAULT_GLASS_USAGE_RULES),
        "forbidden_ui_elements": _copy(DEFAULT_FORBIDDEN_UI_ELEMENTS),
        "shot_compilation_rule": "vary_layout_by_content_but_keep_material_hierarchy_consistent",
        "shot_prompt_layers": {
            "content_plane": "near-solid dark plane carrying the page's single main idea with large readable typography",
            "functional_chrome": "restrained frosted modules and chrome for controls, labels, data points, and lightweight structure",
            "temporary_explainer": "small transient clarifier layer that can use frosted glass but should not dominate the page",
        },
        "design_workflow_rule": "When style_contract and shot_intents are already clear, continue without pausing for user confirmation; record design decisions in Remotion code comments or project notes.",
        "remotion_foundation_rule": "Remotion is the only render path for scenes, animation, subtitles, audio, timeline, and final video. Legacy slides/base.css and scaffold HTML are not production paths.",
    }


def build_shot_intents_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_shot_intents",
        "next_owner": "visual-architect",
        "style_contract_ref": "content/style_contract.json",
        "representation_options": ["imagegen", "remotion", "react-css", "latex", "animation", "hybrid", "real-screenshot"],
        "required_fields_to_consider": [
            "story_turn",
            "viewer_question",
            "base_visual_kind",
            "imagegen_text_required",
            "imagegen_text_exactness_check",
            "proof_anchor_ref",
            "boundary_label",
        ],
        "beats": [],
    }


def build_visual_asset_plan_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_visual_asset_plan",
        "next_owner": "visual-architect",
        "source_contracts": {
            "meaning_contract": "content/meaning_contract.json",
            "style_contract": "content/style_contract.json",
            "shot_intents": "content/shot_intents.json",
        },
        "visual_benchmark": {
            "reference_family": "",
            "borrowed_pattern": "",
            "not_to_copy": [],
            "evidence_carrier": "",
            "qa_risk": [],
            "notes": "Borrow the thinking pattern, not the look.",
        },
        "key_visual": {
            "main_object": "",
            "visual_question": "",
            "thumbnail_promise": "",
            "cover_text_candidates": [],
            "base_visual_prompt": "",
            "reuse_plan": {"opening": "", "chapter_bumpers": "", "ending": ""},
            "mobile_readability_check": "pending",
        },
        "asset_rules": {
            "imagegen_model_preference": "gpt-image-2 via imagegen skill for production bitmap bases",
            "imagegen_allowed_for": [
                "base illustration",
                "exploded view",
                "mechanism diagram background",
                "concept visual",
                "animation texture or key visual",
                "bilibili cover",
                "exact Chinese text",
                "formulas",
                "code snippets",
                "labels",
                "numbers",
                "source marks",
                "UI states",
            ],
            "must_render_directly_with_imagegen": ["Chinese text", "formulas", "code", "labels", "numbers", "source marks", "UI states"],
            "truth_labels": ["exact", "schematic", "metaphor", "not-to-scale", "exaggerated-for-visibility"],
            "asset_jobs": _copy(DEFAULT_IMAGEGEN_ASSET_JOBS),
            "default_stack": ["imagegen_direct_render", "visual_qa", "regenerate_if_text_or_symbols_fail"],
            "regeneration_policy": "If generated Chinese text, formulas, code, labels, numbers, sources, or UI states are wrong, regenerate the image.",
            "do_not_use_imagegen_for": ["fake UI passed off as real", "fake measurements", "fake source evidence", "unverified data"],
        },
        "assets": [],
    }


def build_segments_data() -> list[dict]:
    return []


def build_screenshot_plan_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_screenshot_plan",
        "next_owner": "production-engineer",
        "required_samples": ["opening", "middle", "ending", "dense-information", "all-formula-scenes", "all-real-screenshot-scenes"],
        "minimum_interval_seconds": 10,
        "manifest_path": "content/screenshot_manifest.json",
        "samples": [],
    }


def build_visual_qa_report_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_visual_qa",
        "next_owner": "visual-qa-fixer",
        "source_artifacts": {
            "remotion_code": "remotion/src/**/*",
            "frame_samples": "remotion_frames/*.png",
            "remotion_props": "remotion/input-props.json",
            "segments": "content/segments.json",
            "shot_intents": "content/shot_intents.json",
            "visual_asset_plan": "content/visual_asset_plan.json",
            "cover": "publish/cover.png",
            "cover_prompt": "publish/cover_prompt.md",
        },
        "must_check": [
            "remotion_frame_pixels",
            "cover_pixels",
            "exact_chinese_text",
            "mojibake_or_question_marks",
            "missing_characters",
            "text_overlap_or_clipping",
            "white_bars_or_bad_crop",
            "wrong_or_stale_cover_file",
            "unreadable_labels_or_formulas",
            "thumbnail_mobile_legibility",
            "imagegen_text_exactness",
            "imagegen_formula_code_label_exactness",
            "source_claim_traceable",
            "same_layout_repetition_count",
        ],
        "fix_permissions": [
            "edit_remotion_react_css",
            "edit_or_regenerate_visual_assets",
            "rerun_imagegen_for_cover_or_assets",
            "regenerate_imagegen_until_text_symbols_and_labels_pass",
            "rerender_remotion_frame_samples_after_fixes",
        ],
        "constraints": {
            "do_not_change_facts_or_narration": True,
            "must_inspect_rendered_pixels_not_source_only": True,
            "blocking_findings_must_be_fixed_before_production": True,
        },
        "checks": [],
        "fixes_applied": [],
        "unresolved_blockers": [],
        "go_no_go": "pending",
    }


def build_acceptance_report_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_acceptance_review",
        "next_owner": "acceptance-reviewer",
        "source_contracts": {
            "meaning_contract": "content/meaning_contract.json",
            "visual_asset_plan": "content/visual_asset_plan.json",
            "screenshot_plan": "content/screenshot_plan.json",
            "visual_qa_report": "content/visual_qa_report.json",
            "segments": "content/segments.json",
        },
        "must_pass": _copy(DEFAULT_ACCEPTANCE_GATES),
        "findings": [],
        "go_no_go": "pending",
    }


def build_cover_prompt(topic: str) -> str:
    return (
        "# B 站封面提示词\n\n"
        "在执行前，把 `【标题】` 换成最终发布标题，把 `【实际logo色号】` 换成当前品牌荧光绿，例如 `D0F810`；标题可以不逐字照搬到画面里。\n\n"
        f"- 当前选题：{topic}\n"
        f"- 默认输出：`{DEFAULT_BILIBILI_COVER_PATH}`\n"
        "- 推荐时机：本地 QA 通过、标题候选锁定之后，执行 `prepare_publish_job.py` 之前\n"
        "- 默认 owner：`visual-architect`\n"
        "- 默认策略：`visual-architect` 调用 `imagegen` 直接生成封面文字和画面；`visual-qa-fixer` 负责逐字看图，不对就重生\n"
        "- 发布到 B 站前必须准备好这张封面\n\n"
        "```text\n"
        f"{DEFAULT_BILIBILI_COVER_PROMPT_TEMPLATE}\n"
        "```\n"
    )


def build_publish_notes(topic: str) -> str:
    return (
        f"# 发布备注\n\n"
        f"- 标题候选：\n"
        f"- 简介要点：\n"
        f"- 标签：\n"
        f"- 封面主标题/钩子：\n"
        f"- 封面必须保留的识别元素：\n"
        f"- 封面文件：{DEFAULT_BILIBILI_COVER_PATH}\n"
        f"- 上传浏览器：Microsoft Edge 正式版（不是 Edge Dev）\n"
        f"- 额外说明：\n\n"
        f"# 流程提醒\n\n"
        f"- 内容默认走 content-strategist -> script-writer -> narration-polisher 三段串行\n"
        f"- 主 agent 是 coordinator，只负责统筹、简单命令、合并和最终决策；内容、视觉、音频、装配和验收都交给 subagent\n"
        f"- script-writer 先生成 content/script_draft.json；narration-polisher 再去掉 AI 人机味、翻译腔和过硬书面语，不改主线判断\n"
        f"- scene 编译默认走 style contract -> shot intent -> Remotion React composition，不再走 HTML slide 渲染路径\n"
        f"- visual-architect 在 visual_asset_plan 内记录 benchmark 和 key_visual：借鉴认知模式，不复制画风；封面、片头、章节和结尾共享一个主视觉记忆点\n"
        f"- 不预建 HTML scene；先锁内容与 shot intent，再生成对应 Remotion scene 代码和 imagegen 资产\n"
        f"- 风格只锁材质逻辑和层级，不锁固定模块；视频 composition、动画、字幕、音频、时间轴和渲染默认交给 Remotion\n"
        f"- visual-architect 可调用 imagegen 生成视觉设计、爆炸图、机制图、动画素材和 B 站封面\n"
        f"- imagegen 负责高质量成图，包含中文大字、公式、标签、数字、代码和 UI 状态；visual-qa-fixer 逐字/逐项核对，不对就重生 imagegen 图\n"
        f"- visual-qa-fixer 必须读取实际 Remotion frame samples 和封面图，发现错字、缺字、乱码、重叠、白边、坏裁切或过期封面就重生图片或修 Remotion 代码并重渲染\n"
        f"- production-engineer 合并配音和装配职责：优先整段单次合成，负责 Remotion props、渲染和导出\n"
        f"- 中文语速按上期 CUDA 成片校准：目标约 260 中文字/分钟，可接受区间 240-285；时长不匹配但内容和 QA 通过时不阻塞发布\n"
        f"- acceptance-reviewer 必须看多张实际截图、读 Remotion 代码和内容合同，并完整听完 master 音频\n"
        f"- 封面默认在本地 QA 通过且标题锁定后由 visual-architect 生成，再由 visual-qa-fixer 看图修正；输出到 `{DEFAULT_BILIBILI_COVER_PATH}`\n"
        f"- 最终交给 UI worker 上传 B 站时，默认打开已登录的 Microsoft Edge 正式版，不要用 Edge Dev\n"
    )
