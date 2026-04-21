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
        "role": "outline-researcher",
        "phase": "outline",
        "must_run": True,
        "writes": ["content/outline_plan.json"],
        "handoff_to": "depth-builder",
    },
    {
        "role": "depth-builder",
        "phase": "depth",
        "must_run": True,
        "reads": ["content/outline_plan.json"],
        "writes": ["content/depth_contract.json"],
        "handoff_to": "detail-filler",
    },
    {
        "role": "detail-filler",
        "phase": "detail",
        "must_run": True,
        "reads": ["content/outline_plan.json", "content/depth_contract.json"],
        "writes": ["content/detail_weave.json"],
        "handoff_to": "narration-polisher",
    },
    {
        "role": "narration-polisher",
        "phase": "narration-polish",
        "must_run": True,
        "reads": [
            "content/outline_plan.json",
            "content/depth_contract.json",
            "content/detail_weave.json",
        ],
        "writes": ["content/narration_polish.json"],
        "handoff_to": "chief-editor",
    },
]
DEFAULT_SUPPORT_ROLES = [
    "visual-architect",
    "voice-director",
    "acceptance-reviewer",
]
DEFAULT_CONTENT_ARTIFACTS = [
    "content/outline_plan.json",
    "content/depth_contract.json",
    "content/detail_weave.json",
    "content/narration_polish.json",
    "content/style_contract.json",
    "content/shot_intents.json",
    "content/segments.json",
]
DEFAULT_SCENE_COMPILER_CHAIN = [
    "content/style_contract.json",
    "content/shot_intents.json",
    "content/segments.json",
]
DEFAULT_SHOT_ROLE_TAXONOMY: list[str] = []
DEFAULT_VISUAL_THEME = "quiet-glass-lab"
DEFAULT_VISUAL_THEME_ALIASES = {
    "",
    "quiet-glass-lab",
    "quiet-glass-lab-v3",
    "ios18-frosted-glass",
    "ios18-frosted-glass-black-green",
    "ios18-inspired-frosted-science-deck",
    "ios26-liquid-glass",
    "ios26-liquid-glass-black-green",
}
DEFAULT_STYLE_PROMPT_PACK = (
    "把场景做成黑绿、content-first 的 iOS 18-inspired frosted glass tech explainer。"
    "不是手机 App 模拟，也不是固定模板；版式和模块数量由内容决定。"
    "深色主阅读面保持高对比，玻璃只用于图解卡、数据卡、标签和短时解释层；"
    "避免假状态栏、设备壳、glass-on-glass 和透明正文。"
)
DEFAULT_GLASS_USAGE_RULES = [
    "正文层保持 solid / near-solid；图解卡、数据卡和对照卡可以使用半透明磨砂玻璃，但文字下面要有更实的承载层。",
    "使用大圆角模块、soft blur、细亮边和克制高光，不做厚重塑料质感或强折射特效。",
    "层级靠 typography、grouping、spacing、size 和稀疏 tint 建立，不靠到处发光。",
    "避免 glass-on-glass、长段透明正文、假状态栏、手机导航栏和 Apple App screenshot cosplay。",
]
DEFAULT_STYLE_INVARIANTS = [
    "prompt-driven-not-template",
    "layout-varies-by-content",
    "black-carbon-base-plus-acid-lime-emphasis",
    "ios18-inspired-frosted-modules",
    "one-visual-center-per-scene",
    "phone-readable-chinese-typography",
]
DEFAULT_STYLE_AVOID = [
    "fixed-page-taxonomy",
    "copied-apple-screenshot-layouts",
    "phone-app-chrome-compositions",
    "full-screen-glass-content-panels",
    "rainbow-neon-translucency",
    "glass-used-as-main-reading-surface",
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
    "narration_naturalness",
    "ui_supports_content",
    "voice_consistency",
]

LOCAL_QWEN_BASE_INSTRUCT = (
    "请用同一个年轻中文女声稳定讲解科技内容。"
    "气质沉稳、大方、亲和，语速中速偏稳，呼吸轻短，重点词轻微强调。"
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
    ui_system["style_prompt_pack"] = DEFAULT_STYLE_PROMPT_PACK
    ui_system["visual_language"] = "ios18-frosted-glass-black-green"
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
    content_strategy.setdefault("main_agent_role", "chief-editor")
    content_strategy.setdefault("content_subagent_flow", _copy(DEFAULT_CONTENT_SUBAGENT_FLOW))
    content_strategy.setdefault("support_roles", _copy(DEFAULT_SUPPORT_ROLES))
    content_strategy.setdefault("artifacts", _copy(DEFAULT_CONTENT_ARTIFACTS))
    content_strategy.setdefault("scene_compiler_chain", _copy(DEFAULT_SCENE_COMPILER_CHAIN))
    content_strategy.setdefault("shot_role_taxonomy", _copy(DEFAULT_SHOT_ROLE_TAXONOMY))
    content_strategy.setdefault("structure_policy", "content-decides")
    content_strategy.setdefault(
        "scene_compiler_rule",
        "compile_style_contract_then_shot_intents_then_segments_without_using_fixed_page_templates",
    )
    content_strategy.setdefault(
        "delegation_fallback",
        "run_outline_then_depth_then_detail_then_narration_polish_locally_when_subagents_are_unavailable",
    )

    ui_system = project.setdefault("ui_system", {})
    if should_refresh_default_visual_contract(project, ui_system):
        apply_default_visual_contract(project, ui_system)
    else:
        project.setdefault("visual_style", DEFAULT_VISUAL_THEME)
        ui_system.setdefault("theme", DEFAULT_VISUAL_THEME)
        ui_system.setdefault("prompt_mode", "style-not-template")
        ui_system.setdefault("style_prompt_pack", DEFAULT_STYLE_PROMPT_PACK)
        ui_system.setdefault("visual_language", "ios18-frosted-glass-black-green")
        ui_system.setdefault("palette", {"accent": "#D0F810", "ink": "#F7FAF4", "canvas": "#020302"})
        ui_system.setdefault("style_invariants", _copy(DEFAULT_STYLE_INVARIANTS))
        ui_system.setdefault("style_avoid", _copy(DEFAULT_STYLE_AVOID))
        ui_system.setdefault("glass_usage_rules", _copy(DEFAULT_GLASS_USAGE_RULES))
        ui_system.setdefault("mobile_readability", "required")
        ui_system.setdefault("forbidden_ui_elements", _copy(DEFAULT_FORBIDDEN_UI_ELEMENTS))
    ui_system.setdefault("base_css_mode", "render-foundation-only")
    ui_system.setdefault("html_scaffold_mode", "neutral-render-shell")

    workflow = project.setdefault("voice_workflow", {})
    workflow["narration_mode"] = "master-track-preferred"
    workflow["timing_strategy"] = "master-audio-then-text-ratio"
    workflow.setdefault("spoken_text_strategy", "prefer_tts_text_then_voice")
    workflow.setdefault("text_normalization", "script-aware")
    workflow["publish_mode"] = "local-qwen-first"
    workflow.setdefault("accent_review_required", True)
    workflow.pop("web_manifest", None)

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
    voice_persona.setdefault("pace", "medium_steady")
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
    acceptance.setdefault("must_pass", _copy(DEFAULT_ACCEPTANCE_GATES))
    acceptance.setdefault("fail_action", "route_back_to_owner_and_regen")

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
    local_qwen.setdefault("trim_silence_ms", 18)
    local_qwen.setdefault("fade_ms", 12)

    return project


def build_project_data(topic: str, slug: str, voice_provider: str = "local-qwen") -> dict:
    project = {
        "topic": topic,
        "slug": slug,
        "output_name": f"{slug}.mp4",
        "audience": "想快速听懂概念、术语和实际取舍的 B 站技术观众。",
    }
    return apply_project_defaults(project, voice_provider=voice_provider)


def build_outline_plan_data(topic: str) -> dict:
    return {
        "version": "v3",
        "topic": topic,
        "outline_status": "needs_outline",
        "next_owner": "outline-researcher",
        "audience_problem": f"待定义：这期关于 {topic}，观众最容易卡住的误解是什么。",
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


def build_depth_contract_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_depth",
        "next_owner": "depth-builder",
        "based_on_outline": "content/outline_plan.json",
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
        "next_owner": "detail-filler",
        "source_contracts": {
            "outline_plan": "content/outline_plan.json",
            "depth_contract": "content/depth_contract.json",
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


def build_narration_polish_data() -> dict:
    return {
        "version": "v1",
        "status": "needs_narration_polish",
        "next_owner": "narration-polisher",
        "source_contracts": {
            "outline_plan": "content/outline_plan.json",
            "depth_contract": "content/depth_contract.json",
            "detail_weave": "content/detail_weave.json",
        },
        "constraints": {
            "beat_order_locked": True,
            "resolved_claim_locked": True,
            "no_new_facts_without_source": True,
            "spoken_chinese_required": True,
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
        "visual_language": "ios18-frosted-glass-black-green",
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
        "html_foundation_rule": "slides/base.css and scaffold HTML stay visually neutral; scene styling comes from prompt-generated HTML/CSS, not stock templates.",
    }


def build_shot_intents_data(topic: str) -> dict:
    return {
        "version": "v1",
        "topic": topic,
        "status": "needs_shot_intents",
        "next_owner": "chief-editor",
        "style_contract_ref": "content/style_contract.json",
        "beats": [],
    }


def build_segments_data() -> list[dict]:
    return []


def build_publish_notes(topic: str) -> str:
    return (
        f"# 发布备注\n\n"
        f"- 标题候选：\n"
        f"- 简介要点：\n"
        f"- 标签：\n"
        f"- 额外说明：\n\n"
        f"# 流程提醒\n\n"
        f"- 内容研究默认走 outline -> depth -> detail -> narration polish 四段串行\n"
        f"- narration-polisher 只修逻辑、语法、翻译腔和口播自然度，不改主线判断\n"
        f"- scene 编译默认走 style contract -> shot intent -> scene prompt，不直接套模板\n"
        f"- 不预建 scene HTML；先锁内容与 shot intent，再生成对应页面文件\n"
        f"- 风格只锁材质逻辑和层级，不锁固定模块\n"
        f"- slides/base.css 只保留渲染外壳；真实视觉完全由提示词与内容 contract 决定\n"
        f"- 配音优先整段单次合成；若失败优先修脚本、修文案或退回预览链路\n"
    )
