# Bilibili Tech Explainer Workflow

This is the default reusable workflow for Chinese Bilibili explainer videos bootstrapped by `video-maker`.

## Content-first start

Start by locking a coverage contract and a meaning contract.

Problem contract answers:

- what exact question drives the episode
- why this question is worth solving now
- what easy answer is tempting but wrong, shallow, or incomplete
- why the question is hard: hidden variable, wrong scale, missing evidence, false analogy, or tradeoff
- what would change the viewer's judgment
- what shape a satisfying answer should have: mechanism, proof, comparison, rule, workflow, or boundary

Audience contract answers:

- what the viewer can already understand without setup
- what terms must be defined before they can carry reasoning
- what everyday intuition will mislead the viewer
- what level of math, history, engineering, or domain context is allowed
- which details belong in the main line and which should be deferred

Opening contract answers:

- what false intuition the episode will overturn
- why the topic is weird, timely, useful, or consequential
- what concrete question the viewer is watching to resolve
- what route map the episode will follow
- what answer the opening implicitly promises not to dodge

Coverage contract answers:

- what the viewer currently misunderstands
- what the episode is really trying to explain
- what needs evidence, boundaries, or clarification

Meaning contract answers:

- why this episode is worth watching now
- what is at stake if the viewer keeps the old mental model
- what bigger map, system, or worldview this topic connects to
- what transferable tool the viewer should leave with
- what human anchor keeps the topic from becoming abstract sludge

Then let the serial content pipeline refine the beat plan.

## Explainer Mode Selection

Before outline, choose one primary `explainer_mode`:

- `tool-workflow`
- `system-mechanism`
- `math-formula`
- `hardware-teardown`
- `concept-mental-model`
- `comparison-tradeoff`

The mode decides what the viewer should gain: a workflow, a mechanism, a formula intuition, a component model, a mental model, or a tradeoff lens.

Each beat must declare:

- `target_misunderstanding`
- `why_people_misread`
- `scale_jump`
- `model_element`
- `evidence_carrier`
- `visual_job`
- `evidence_mode`
- `primary_representation`
- `analogy_boundary`
- `authenticity_note`

## Mode-specific story spines

Each mode needs a story spine before detailed beats. Use these as minimum shapes, not fixed templates.

- `system-mechanism`: visible symptom or event -> system boundary -> main actors and flows -> bottleneck or control loop -> failure/tradeoff -> reusable system map.
- `math-formula`: concrete intuition -> visual object or coordinate frame -> one variable change -> invariant or conservation idea -> formal LaTeX expression -> boundary where the formula stops helping.
- `hardware-teardown`: exterior recognition -> scale and constraints -> component map -> flow of force/heat/signal/material -> design tradeoff -> what the component model lets the viewer predict.
- `comparison-tradeoff`: common binary debate -> shared goal -> comparison axes -> where each option wins -> hidden cost -> decision rule.
- `concept-mental-model`: familiar wrong model -> contradiction or edge case -> better model -> consequences in 2-3 situations -> old model's limited use -> new seeing tool.
- `tool-workflow`: painful task -> target outcome -> minimal workflow map -> key operation -> failure modes -> reusable checklist.

If a proposed outline cannot be reduced to one of these spines, it is probably a topic list rather than an episode.

## Bilibili benchmark observations

Use this as creative pressure from sampled Bilibili science/technology videos, not as a mandate to copy their surface style.

- Strong episodes start with a social, visual, or counter-intuitive promise: "why is this not what you think?", "how does this process actually happen?", or "what rule decides the result?"
- The most useful shots are relationship shots: a system boundary, process arrow, coordinate frame, force/trajectory line, before/after comparison, or component callout.
- Large UPs often rely on real footage or lecture boards, but the transferable lesson is not the rough visual quality; it is that the viewer always knows what layer of the system they are looking at.
- A good explainer changes visual scale deliberately: object -> component -> mechanism -> consequence. Random detail jumps make the episode feel like trivia.
- Subtitles and captions work best as short conclusions, questions, or term locks; they should not become a full paragraph pasted over the image.
- Pacing target: roughly one small conclusion every 5-12 seconds, one question/turn every 15-30 seconds, and a visible layer change every 2-6 seconds when the scene is not a deliberate slow proof.
- Formula narration should not read symbols aloud. It should say what grows, what shrinks, what stays invariant, and what that pushes in the real object.
- Engineering, natural-science, medical, mathematical, social-science, and other domain episodes become weak when they only show topic footage or mood material. They need boundary, mechanism, variable/flow/causal paths, proof anchors, and tradeoff scenes.
- Manufacturing/process episodes work because they alternate macro process and local mechanism. Preserve that alternation when replacing factory footage with generated diagrams or animation.

## Coordinator Framing

Before assigning scene work, the coordinator should route three statements into the content pipeline and lock them only after subagent review:

- `audience_problem`
- `episode_thesis`
- `episode_scope`

And one constraint list:

- `what_not_to_overclaim`

And one meaning layer:

- `why_now`
- `stakes_if_ignored`
- `worldview_delta`
- `transferable_tool`
- `human_anchor`

Without these items, do not move to final `segments.json`.

## Required content artifacts

1. `content/problem_contract.json`
   - root question
   - false easy answer
   - difficulty source
   - judgment change target
   - answer shape
2. `content/audience_contract.json`
   - viewer baseline
   - likely misreadings
   - term budget
   - plain-language targets
3. `content/opening_contract.json`
   - false intuition
   - where it breaks
   - opening question
   - route map
   - promised answer
4. `content/meaning_contract.json`
   - why-now framing
   - stakes
   - worldview delta
   - transferable takeaway
   - human anchor
5. `content/outline_plan.json`
   - flexible beat map
   - pacing strategy
   - `provisional_claim`
   - beat-by-beat visual focus and bridge
   - beat-by-beat reason to exist
6. `content/depth_contract.json`
   - `resolved_claim`
   - `beat_progression`
   - `context_role`
   - `overclaim_boundary`
   - `required_support`
   - scale jump and meaning gain
7. `content/detail_weave.json`
   - examples
   - misconceptions
   - adjacent concepts
   - edge cases
   - source-backed constraints
   - human anchors and deferred details
8. `content/evidence_map.json`
   - claim support
   - confidence and boundary
   - source refs
   - annotation dependencies
9. `content/script_draft.json`
   - first complete narration draft
   - source claim refs
   - visual cues and terms to define
10. `content/narration_polish.json`
   - polished spoken Chinese
   - plain-language cleanup
   - translationese / machine-tone cleanup
11. `content/style_contract.json`
   - visual invariants
   - style-not-template rules
   - chrome/content/layer constraints
12. `content/shot_intents.json`
   - beat-by-beat shot role
   - narrative job
   - visual goal
   - must show / must avoid
   - meaning-carrying visual emphasis
13. `content/visual_asset_plan.json`
   - imagegen / remotion / react-css / latex / real-screenshot asset responsibilities
   - benchmark pattern, key visual, provenance, text/symbol targets and QA risk
14. `content/segments.json`
   - final render-ready scene list
15. `content/visual_qa_report.json`
   - rendered Remotion frame and cover pixel checks
   - fixes applied and unresolved blockers

`segments.json` should be treated as the compiled artifact, not the brainstorming surface.

## Content flow

1. `coordinator` runs simple commands, assigns subagent task packets, and locks handoffs
2. `content-strategist` locks problem, audience, opening, meaning, outline, depth, detail, and evidence contracts
3. `script-writer` turns the locked contracts into `content/script_draft.json`
4. `narration-polisher` polishes the finished draft into natural spoken Chinese without changing claims
5. `coordinator` reviews the approved narration and routes it into shot intents without authoring the scene content directly
6. `visual-architect` records benchmark and key visual inside `visual_asset_plan`, then translates `style_contract + shot_intents` into Remotion scene code and uses `imagegen` for visual assets / diagrams / animation assets / cover
7. `visual-qa-fixer` inspects actual rendered Remotion frame samples and cover pixels, fixes Remotion code/assets/cover bugs, and writes `content/visual_qa_report.json`
8. `production-engineer` handles Qwen master-track audio, Remotion props, timeline, subtitles, audio mounting, rendering, and export
9. `acceptance-reviewer` checks real screenshots, Remotion code, `visual_qa_report`, content authenticity, and audio samples before final handoff

If delegation is not available, prepare task packets and pause or request authorization; do not let the coordinator silently become every specialist.

## Meaning rules

The episode should not merely explain. It should also change how the viewer looks at something.

At the episode level, confirm:

- the topic has a concrete reason to matter now
- the viewer's old mental model is explicitly insufficient
- the episode earns one non-forced scale jump
- the ending leaves a reusable way of thinking, not just a conclusion sentence

If these are absent, the project may still be clear, but it is not yet meaningful enough.

Default story order should change the viewer's judgment, not just list topics:

1. `false_easy_answer`: what the viewer is tempted to believe.
2. `contradiction`: the observation that breaks that answer.
3. `mechanism_model`: the variables or process that actually explain it.
4. `proof_anchor`: screenshot, data, formula, source, test result, or concrete artifact.
5. `boundary`: where the model stops working.
6. `transfer_rule`: how the viewer should judge a similar case next time.

## Beat rules

Each beat should do one thing well.

When a beat exists, it should usually answer:

- `purpose`
- `shot_role`
- `viewer_question`
- `provisional_claim`
- `visual_focus`
- `bridge_out`
- `why_this_beat_exists`
- `what_new_way_of_seeing_is_gained`

If one beat is doing too many jobs, split it.
If two adjacent beats are doing the same job, merge them.

## Depth rules

Each beat should also answer:

- what changes or advances here
- how this beat connects to neighboring beats
- what misconception it is breaking
- where the overclaim boundary is
- what support detail is still required
- whether this beat completes a necessary `scale_jump`
- whether this beat increases the viewer's judgment, not just their vocabulary

If a beat cannot answer these without breaking the outline, route it back to the outline phase.

## Evidence And Uncertainty Discipline

Every core claim should have a `claim_id` in `content/evidence_map.json`.

Each claim should declare:

- `support_type`: `first-principles` / `empirical` / `historical` / `consensus` / `primary-source` / `informed-analogy`
- `confidence_level`: `high` / `medium` / `low`
- `proof_anchor_scene`: the beat or visual where the viewer can see why the claim is plausible
- `source_refs`: local notes, links, screenshots, papers, official pages, or sampled video references
- `known_unknowns`
- `controversy_status`
- `overclaim_boundary`

Rules:

- If a claim drives the thesis, it needs either a proof anchor or an explicit limitation.
- If a visual annotation includes a number, dimension, component name, arrow direction, formula, or phase order, it must map back to an evidence-map claim.
- If a claim is only an analogy, mark it as analogy and say where the analogy breaks.
- Do not let a smooth narration pass hide weak evidence. A beautiful sentence with weak support is still a weak beat.

## Detail rules

`content-strategist` may add support material only inside `detail_weave`:

- examples
- source-backed facts
- misconception cleanup
- term unpacking
- boundary cases
- human anchors
- transferable heuristics
- deferred material that should stay out of the main line

It may not rewrite `resolved_claim`.
It may not stuff the episode with extra facts that do not increase understanding.

## Visual system

Default render engine: `remotion`.

Default brand constraint: `Quiet Glass Lab`.

What is fixed:

- `16:9` horizontal output
- content-first hierarchy
- black-carbon base with sparse acid-lime emphasis
- restrained iOS 18-inspired frosted glass modules and chrome
- concentric rounded shapes, subtle lensing, soft refraction
- phone-readable Chinese typography
- no fake status bars, Apple hardware shells, or screenshot cosplay
- no cheap AI-style visual cliches: purple-pink-blue gradient wash, meaningless glow, left-border accent cards, emoji/icon spam, fabricated data

What is not fixed:

- page naming
- module inventory
- one mandatory demo page
- any single recurring layout skeleton

Optional shot-role vocabulary:

- `hook`
- `problem-frame`
- `thesis`
- `system-map`
- `mechanism`
- `comparison`
- `tradeoff`
- `demo`
- `caveat`
- `takeaway`
- `scale-jump`
- `human-anchor`

Use `remotion-best-practices` for composition, layout, typography, motion, subtitles, audio mounting, timeline, and rendering. See `quiet-glass-lab-v3.md` for the black-green frosted-glass brand prompt pack.
Use `imagegen` through `visual-architect` for bitmap visual assets, exploded diagrams, mechanism diagrams, animation assets, and the final Bilibili cover base. Then route rendered Remotion frame samples and cover to `visual-qa-fixer`; exact Chinese cover text, verified labels, and formulas must be checked visually and regenerated when imagegen is unreliable.

Read `imagegen-2-visual-playbook.md` before creating visual assets. The default pattern is direct imagegen rendering plus visual QA: imagegen should generate the key visual, short Chinese text, formulas, labels, numbers, code snippets and UI-like states directly. If the rendered pixels are wrong, regenerate the image instead of patching failed text with separate rendered layers.

## Real Screenshot vs Schematic vs Formula

- `real-screenshot`: use when the claim depends on an actual UI, experiment, video frame, or visible state. Must preserve screenshot provenance.
- `schematic`: use when the real object is too cluttered, hidden, microscopic, huge, or unavailable. Must label as schematic / not-to-scale when relevant.
- `formula`: use when the explanation depends on symbol correctness. Must preserve LaTeX source and render formulas structurally.
- `hybrid`: use only when a complex object, system, structure, process, or mathematical relation needs imagegen plus Remotion motion shell or real screenshot composition; text and formulas still default to imagegen direct rendering.

Never accept imagegen text, formulas, dimensions, labels, or component names without visual QA. If they are wrong, regenerate the imagegen output.

## Narration rules

- Default to short Chinese sentences.
- Explain the intuition first, terminology second.
- Let the viewer feel the stake or weirdness before naming the abstraction.
- Say the downside directly; do not oversell.
- Run one narration-polish pass before final `segments.json`.
- Use one continuous master narration track.
- Keep one persona lock across the full narration pass; do not fall back to scene-level stitching.
- `production-engineer` owns TTS generation and Remotion rendering together, so voice fixes and render/export fixes stay in one engineering loop.

## Demo guidance

- Tool or workflow explainers often benefit from a demo.
- Concept-first explainers do not need a demo by default.
- Demo is a content choice, not a mandatory fixed slot.
- If a demo beat exists but the real capture is missing, use the beat's Remotion scene as a temporary placeholder.

## Publish notes

Each project should keep:

- title candidates
- short description bullets
- tags
- style reminders
- the one-sentence `why_now` promise
