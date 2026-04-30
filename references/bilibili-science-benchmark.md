# Bilibili Science Benchmark

This reference condenses sampled Bilibili science and technology videos into reusable creative pressure for `video-maker`.

Local research corpus from this improvement pass:

- `C:\Users\Clr\Desktop\Video Maker\research\bilibili-followings`
- `C:\Users\Clr\Desktop\Video Maker\research\bilibili-inspiration-corpus`
- `C:\Users\Clr\Desktop\Video Maker\research\bilibili-top20-science-20260424`

Sampled channels included:

- 张朝阳的物理课
- 毕导
- 一切的流程
- 思维实验室
- ASPT-航天科普小组
- 环球科学
- plus a later 20-channel follower-ranked corpus covering natural history, classroom math, hardware review, engineering demos, institutional physics, geography, biology, AI education, and math visualization.

The later corpus contains 60 videos, 3612 ten-second screenshots, and 142 downloaded platform subtitle files. Some channels do not expose Bilibili subtitle tracks; missing subtitle files are recorded in the local manifest and should not be silently invented.

The goal is not to copy their surface style. The goal is to learn what makes their explanations legible.

## Shared Pattern

Strong science videos usually follow:

1. Counter-intuitive hook or concrete curiosity.
2. Explicit misconception or viewer question.
3. A visible model: board, diagram, map, process, experiment, object, or formula.
4. Two to four progressive explanation blocks.
5. Return to the opening question.
6. Transferable rule, judgment, or way of seeing.

If an episode cannot say what new way of seeing the viewer gets, it is not ready.

## Transferable Principles From The 20-Channel Corpus

- Every strong channel has a preferred `evidence carrier`. Examples: live organism/object, field footage, classroom board, animated theorem, benchmark chart, product teardown, paper/source screenshot, institutional diagram, physical test rig, or real interface.
- The evidence carrier decides pacing. Board proof can be slow; product testing and scientific news need faster proof/caption cycles; field/nature footage needs location and species/context anchors.
- The visual style is less important than layer awareness. Viewers should know whether they are seeing an object, component, mechanism, proof, source, analogy, or takeaway.
- Large creators often use rough footage, but the lesson is not roughness. The reusable lesson is provenance: the viewer can see where the claim comes from.
- Short-form-heavy channels are useful for hooks and rhythm, but they are weak references for complete episode structure. Use them as micro-pattern samples, not full workflow templates.
- Product/technology reviews show a useful pattern: `object -> test condition -> metric -> comparison -> tradeoff -> buying/usage implication`. This can generalize to non-product science as `object -> condition -> measurement -> comparison -> principle`.
- Math visualization channels show that formulas become watchable when each symbol is tied to a visible geometric or dynamic object.
- Natural science channels show that identification, scale, habitat, and behavior are separate explanation layers; mixing them without labels makes the video feel like a nature montage.
- Institutional science accounts often win with one small diagram and one precise claim. This is a useful antidote to overproduced scenes.

## Shot Lessons

- 张朝阳的物理课: board and formula scenes work because they are proof anchors. The visual may be plain, but the viewer sees the actual reasoning surface.
- 毕导: hook strength comes from everyday objects, experiments, and playful misdirection, but the strong parts are still measurements, comparisons, and visible tests.
- 一切的流程: process videos work by alternating macro flow and local mechanism. The viewer always knows where they are in the production chain.
- ASPT: aerospace videos need real mission footage, phase labels, trajectory/attitude/timeline layers, and clear boundaries between confirmed fact and live interpretation.
- 思维实验室: archive-heavy explainers need maps, time jumps, and causal arrows; otherwise footage becomes mood rather than explanation.
- 环球科学: paper/news explainers need source shots, simplified diagrams, and short conclusion captions; screenshots of papers are proof anchors, not final explanation.

## Pacing Lessons

- A small conclusion every 5-12 seconds keeps the viewer oriented.
- A turn, question, or tension update every 15-30 seconds prevents list-like exposition.
- Visual layer changes every 2-6 seconds help dense material, unless the scene is intentionally slow proof.
- Captions should be one or two lines. Use them for claims, questions, labels, and term locks, not paragraph transcription.
- Formula narration should explain direction, invariants, and consequences rather than reading symbols aloud.

## Visual Translation For Video Maker

`video-maker` should improve on human samples by using generated and structured visuals where humans often rely on rough footage.

- Replace rough board-only explanations with LaTeX + animated coordinate frames + board-like proof anchors when exactness matters.
- Replace inaccessible interiors, hidden mechanisms, tiny structures, abstract systems, or hard-to-film scenes with direct imagegen visuals that include dimensions, components, arrows, and uncertainty labels, then verify the rendered pixels visually.
- Replace generic footage montages with process maps, timelines, force/flow arrows, and state-transition animation.
- Use real screenshots or source shots when the claim depends on provenance.
- Use imagegen for clean hero visuals, exploded views, section diagrams, mechanism bases, and covers, but never for final readable formulas, dimensions, or verified labels.

## Evidence Carrier Selection

Before designing scenes, choose one primary evidence carrier and one supporting carrier:

- `board_or_formula`: theorem, derivation, math intuition, physics relation.
- `physical_experiment`: test, measurement, everyday object, controlled comparison.
- `field_or_real_object`: organism, landscape, artifact, machine, product, material.
- `source_document`: paper, official page, dataset, map, archive, news primary source.
- `instrument_or_interface`: benchmark, telemetry, software UI, lab instrument, diagnostic screen.
- `generated_schematic`: hidden mechanism, conceptual relation, interior structure, scale comparison.
- `animated_model`: changing variable, process, trajectory, feedback loop, state transition.

If no evidence carrier is selected, the project is likely to become narration over decoration.

## Minimal Aesthetic Direction

- One screen, one judgment.
- Structure before decoration.
- Black/white/gray plus one functional accent is enough.
- The accent color should mark active variable, direction, current phase, selected component, or final takeaway.
- Leave breathing room around Chinese titles and labels.
- Keep proof, schematic, and analogy visually distinct.
- Extreme polish is welcome only when it increases clarity.

## Anti-patterns

- Opening with 20-30 seconds of background before posing a question.
- Consecutive scenes that are only narration plus wallpaper.
- Engineering or aerospace news without mechanism, boundary, or tradeoff.
- Formula walls where variables never map back to objects.
- Generated diagrams that imply exact internal structure without evidence.
- Full-screen fake UI, fake status bars, fake data dashboards, or Apple cosplay.
- Clickbait hook that the ending never answers.
