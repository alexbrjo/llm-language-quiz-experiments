# Fill-in-the-Blank Question Quality Across Frontier & Local Models

**Experiment:** e06 fill-in-the-blank model comparison
**Date:** 2026-03-25
**Author:** Claude Opus 4.6

---

## Abstract

This report evaluates open fill-in-the-blank (FITB) question generation across five models and three provider categories: OpenAI (GPT-4.1), Anthropic (Claude Sonnet 4.6, Claude Haiku 4.5), and local MLX (Qwen3.5-9B at 8-bit and 4-bit). This is the first experiment to test FITB questions (no multiple-choice options) and the first to include Anthropic models as generators. Ten German grammar topics were tested with 100 questions per model (500 total). A question is considered successful only if it passes all four evaluators (static, editor, student, and teacher). Claude Sonnet 4.6 achieved 98% all-pass — the highest score across any experiment — with 100% Teacher and 100% Editor approval individually. Claude Haiku 4.5 scored 89% all-pass and was the fastest API model at 4.2s/sample. GPT-4.1 scored 83% all-pass, with failures driven by Futur I structural issues and the recurring "sie" ambiguity. The Qwen local models scored 66% (8-bit) and 48% (4-bit) all-pass, with failures driven by incorrect declension endings, topic misalignment, and hint quality issues. Structured output mode (`schema`) eliminated all parse failures across every model — a major improvement over the trial's 10–30% parse failure rates for local models under `json_mode`. The dominant FITB-specific failure mode is answer ambiguity from underspecified subjects, replacing distractor quality as the primary concern from MCFIB experiments.

---

## 1. Introduction

Experiments e01–e05 established a comprehensive benchmark for multiple-choice fill-in-the-blank (MCFIB) German grammar questions, with GPT-5-mini as the cost-performance optimum at 97% Teacher approval ($0.0042/sample). E06 shifts to a fundamentally different question type: open fill-in-the-blank, where the learner must produce the correct word form without options.

This shift changes the generation challenge:

- **No distractors to generate** — eliminates MCFIB's most common failure mode (duplicate options, implausible distractors)
- **Higher clarity bar** — without options to anchor the learner, the sentence must unambiguously determine a single correct answer
- **New failure mode: ambiguity** — multiple valid forms may exist if the sentence context is insufficient

E06 also marks the first inclusion of Anthropic models (Claude Sonnet 4.6, Claude Haiku 4.5) as generators, enabling cross-provider comparison for the first time.

A trial (t06) of 6 models with 50 questions each was run to validate the pipeline. Key trial findings informed the experiment design: disabling Qwen's `enable_thinking` was critical (reduced parse failures from 90% to 10%), the "Sie" pronoun ambiguity was identified as the dominant failure mode, and Claude Sonnet 4.6 showed a perfect 100% Teacher score on 50 questions.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Collection            | Model                             | Provider      | Output Mode | Temp | Samples |
| --------------------- | --------------------------------- | ------------- | ----------- | ---- | ------- |
| e06 GPT-4.1           | gpt-4.1                           | OpenAI API    | schema      | 0.3  | 20/20   |
| e06 Claude Sonnet 4.6 | claude-sonnet-4-6                 | Anthropic API | schema      | —    | 20/20   |
| e06 Claude Haiku 4.5  | claude-haiku-4-5-20251001         | Anthropic API | schema      | —    | 20/20   |
| e06 Qwen3.5-9B-8bit   | NexVeridian/Qwen3.5-9B-8bit       | Local MLX     | schema      | 0.3  | 20/20   |
| e06 Qwen3.5-9B-4bit   | mlx-community/Qwen3.5-9B-MLX-4bit | Local MLX     | schema      | 0.3  | 20/20   |

Each model generated 20 samples (2 repeats × 10 topic presets, 5 questions each), yielding 100 questions per model, **500 questions total**. All models used structured output (`schema` mode) — OpenAI via `response_format: json_schema`, Anthropic via tool use, and local via outlines constrained generation. This eliminated all parse failures.

Local models ran with `{"enable_thinking": false}` in extra params and were preceded by 3 warmup samples to preload model weights before the timed run.

### 2.2 Grammar Topics

Ten topics, identical to e05:

| Preset                           | Example Question                                   | Example Answer |
| -------------------------------- | -------------------------------------------------- | -------------- |
| Adjektivdeklination im Akkusativ | Es gibt einen `_____` (klein) Ort.                 | kleinen        |
| Adjektivdeklination im Dativ     | Ich legte das Telefon auf den `_____` (alt) Tisch. | alten          |
| Adjektivdeklination im Nominativ | Das ist eine `_____` (klein) Stadt.                | kleine         |
| Futur I                          | Morgen `_____` ich schlafen gehen.                 | werde          |
| Hilfsverb in Perfekt             | Er `_____` nach Österreich gefahren.               | ist            |
| Konjugation im Perfekt           | Ich habe 2 Jahre lang `_____` (arbeiten).          | gearbeitet     |
| Konjugation im Präsens           | `_____` (sprechen) du Deutsch?                     | Sprichst       |
| Konjugation im Präteritum        | Er `_____` (gehen) ins Kino.                       | ging           |
| Personalpronomen in Akkusativ    | Kannst du `_____` (ich) anrufen?                   | mich           |
| Personalpronomen in Dativ        | Kannst du `_____` (ich) bitte helfen?              | mir            |

### 2.3 Evaluators

| Evaluator | Type                 | Model  | Purpose                                                    |
| --------- | -------------------- | ------ | ---------------------------------------------------------- |
| Static    | Pass condition only  | —      | Structural validation (answer, explanation, blank present) |
| Editor    | LLM + pass condition | gpt-4o | Grammatical correctness of `answered_sentence`             |
| Student   | LLM + pass condition | gpt-4o | Expert student attempts to produce the correct answer      |
| Teacher   | LLM + pass condition | gpt-4o | Expert audit: uniqueness, correctness, CEFR rating         |

Evaluation used **gpt-4o** at temperature 0.1 in `json_mode`.

---

## 3. Results

### 3.1 Overall Results

A question is considered successful only if it passes **all four evaluators** (static, editor, student, teacher). This is a stricter metric than reporting per-evaluator rates, which can obscure the true usable output rate.

| Model                 | All-Pass | Static | Editor | Student | Teacher |
| --------------------- | -------- | ------ | ------ | ------- | ------- |
| **Claude Sonnet 4.6** | **98%**  | 100%   | 100%   | 98%     | 100%    |
| Claude Haiku 4.5      | 89%      | 100%   | 100%   | 90%     | 99%     |
| GPT-4.1               | 83%      | 100%   | 94%    | 86%     | 98%     |
| Qwen3.5-9B-8bit       | 66%      | 100%   | 86%    | 77%     | 87%     |
| Qwen3.5-9B-4bit       | 48%      | 100%   | 72%    | 81%     | 73%     |

Claude Sonnet 4.6 achieves 98% all-pass — 98 of 100 questions pass every evaluator. Its 2 failures come from the student evaluator only (the teacher and editor approved all 100). Claude Haiku 4.5 scores 89% all-pass, with most failures from the student evaluator (10 failures) and 1 teacher rejection on a borderline topic alignment case (Dativ vs Akkusativ in a sentence using "auf den").

GPT-4.1's 83% all-pass is notably lower than its 98% Teacher rate — the gap is driven by 14 student failures and 6 editor failures on questions the teacher approved. Many of these are "sie" ambiguity questions where the teacher was lenient but the student chose the alternative valid interpretation.

Structured output mode achieved 100% Static pass across all models — no missing blanks, no empty answers or explanations.

### 3.2 Generation Performance

| Model             | Avg s/sample | Median s/sample | Min  | Max  | Avg Prompt Tok | Avg Comp Tok |
| ----------------- | ------------ | --------------- | ---- | ---- | -------------- | ------------ |
| Claude Haiku 4.5  | **4.2**      | 4.0             | 3.3  | 7.3  | 1,233          | 645          |
| GPT-4.1           | 5.8          | 5.5             | 3.2  | 8.5  | 349            | 382          |
| Claude Sonnet 4.6 | 10.0         | 9.9             | 8.0  | 14.2 | 1,234          | 678          |
| Qwen3.5-9B-4bit   | 43.9         | 47.6            | 12.4 | 52.6 | —              | —            |
| Qwen3.5-9B-8bit   | 71.8         | 81.6            | 15.5 | 88.7 | —              | —            |

Claude Haiku 4.5 is the fastest model at 4.2s/sample, slightly ahead of GPT-4.1 (5.8s). The Anthropic models report higher prompt token counts (1,233–1,234 vs 349 for GPT-4.1) — the difference may reflect how each provider counts tokens in schema mode.

**Local model latency drift:** Both Qwen models show a large gap between min and max latency (e.g., 15.5s → 88.7s for 8-bit). This is caused by MLX's Metal buffer cache accumulating GPU memory buffers across requests without releasing them, leading to increasing memory pressure and swap usage over successive requests. This is a [known MLX issue](https://github.com/ml-explore/mlx/pull/390) with a potential mitigation via `mlx.core.metal.set_cache_enabled(False)`, which trades a small throughput hit for stable memory usage. Median latency is more representative than mean for local models.

### 3.3 All-Pass Rate by Topic (%)

| Topic                            | GPT-4.1 | Sonnet 4.6 | Haiku 4.5 | Qwen 8-bit | Qwen 4-bit |
| -------------------------------- | ------- | ---------- | --------- | ---------- | ---------- |
| Adjektivdeklination im Akkusativ | **100** | **100**    | **100**   | 90         | **100**    |
| Adjektivdeklination im Dativ     | 90      | **100**    | 90        | 60         | 0          |
| Adjektivdeklination im Nominativ | 90      | 90         | 80        | 70         | 70         |
| Futur I                          | 50      | **100**    | 80        | **100**    | 20         |
| Hilfsverb in Perfekt             | 80      | **100**    | 80        | 80         | 0          |
| Konjugation im Perfekt           | **100** | **100**    | **100**   | 10         | 80         |
| Konjugation im Präsens           | 90      | **100**    | 90        | 80         | 80         |
| Konjugation im Präteritum        | 70      | **100**    | 80        | 40         | 40         |
| Personalpronomen in Akkusativ    | **100** | **100**    | **100**   | 80         | 60         |
| Personalpronomen in Dativ        | 60      | 90         | 90        | 50         | 30         |

Claude Sonnet 4.6 achieves 100% on 8 of 10 topics. Its two 90% scores (Adjektivdeklination im Nominativ, Personalpronomen in Dativ) are from student evaluator failures, not teacher or editor rejections.

GPT-4.1 drops sharply on Futur I (50%) — the model omitted subjects from some Futur I sentences, causing editor and student failures even though the teacher approved. Personalpronomen in Dativ (60%) and Konjugation im Präteritum (70%) are also weak, driven by the "sie" ambiguity and archaic conjugation patterns seen in prior experiments.

**Qwen3.5-9B-4bit scores 0% all-pass on two topics** — Adjektivdeklination im Dativ and Hilfsverb in Perfekt. Every question in these topics failed at least one evaluator. Futur I (20%) is also near-total failure: all 8 rejected questions (consistent across both repeats) share the same cause — the model's explanation incorrectly describes Futur I as formed with "Konjunktiv II" instead of the present tense of "werden". The grammar and answers are correct; only the explanation is wrong. The 8-bit model handles Futur I perfectly (100%).

**Konjugation im Perfekt is catastrophic for Qwen3.5-9B-8bit (10%)** — only 1 of 10 questions passes all evaluators, despite 70% Teacher approval. The gap reflects editor and student failures on questions the teacher accepted.

### 3.4 Editor Approval by Topic (%)

GPT-4.1 has 6 Editor failures, concentrated in Futur I (3 failures where the model omitted the subject from the answered sentence — e.g., "In zwei Stunden wird nach Hause kommen") and Konjugation im Präteritum (1 failure on the archaic "fuhrt" form).

Qwen3.5-9B-8bit has 14 Editor failures driven by incorrect adjective endings ("das schönen Spielzeug" instead of "das schöne Spielzeug") and tense confusion (generating Perfekt sentences in Präteritum presets).

Qwen3.5-9B-4bit has 28 Editor failures — the highest of any model — with systematic issues in dative constructions (missing articles, wrong endings) and topic misalignment.

### 3.5 Student Accuracy

| Model             | Student Accuracy | Failures |
| ----------------- | ---------------- | -------- |
| Claude Sonnet 4.6 | **98%**          | 2        |
| Claude Haiku 4.5  | 90%              | 10       |
| GPT-4.1           | 86%              | 14       |
| Qwen3.5-9B-4bit   | 81%              | 19       |
| Qwen3.5-9B-8bit   | 77%              | 23       |

Claude Sonnet's 2 student failures: the expert student answered "neue" instead of "neuen" for weak plural nominative, and "sie" instead of "ihnen" for dative plural. Both are cases where the student evaluator made a grammatical error on a genuinely challenging question.

GPT-4.1's 14 student failures are largely driven by ambiguity in the generated questions themselves. At least 6 failures involve "sie" sentences where the student chose a different but arguably valid interpretation (e.g., plural "gehen" instead of singular "geht", "lasen" instead of "las", "haben" instead of "hat"). The remaining failures are on dative/accusative adjective declension and Futur I questions where the student used present tense instead of "werden".

### 3.6 Items Failing Multiple Evaluators

| Model             | Items with 2+ fails | Triple fails |
| ----------------- | ------------------- | ------------ |
| GPT-4.1           | 4                   | 1            |
| Qwen3.5-9B-8bit   | 14                  | 2            |
| Qwen3.5-9B-4bit   | 16                  | 2            |
| Claude Sonnet 4.6 | 0                   | 0            |
| Claude Haiku 4.5  | 0                   | 0            |

GPT-4.1's triple fail: "Ihr **\_** (fahren) im Sommer nach Italien." with answer "fuhrt" — all three evaluators rejected it (Editor: incorrect conjugation, Student: couldn't produce it, Teacher: ambiguous).

Qwen3.5-9B-8bit's triple fails are both on "Gestern **\_** (ich) nach Hause gegangen" with answer "bin" — the model generated a Perfekt sentence for a Präteritum preset, a topic misalignment.

### 3.7 CEFR Level Distribution (Teacher-Approved Questions)

| Model             | A1       | A2       | B1           |
| ----------------- | -------- | -------- | ------------ |
| Claude Sonnet 4.6 | 6% (6)   | 39% (39) | **55% (55)** |
| Claude Haiku 4.5  | 3% (3)   | 57% (56) | 40% (40)     |
| GPT-4.1           | 8% (8)   | 57% (56) | 35% (34)     |
| Qwen3.5-9B-8bit   | 14% (12) | 47% (41) | 39% (34)     |
| Qwen3.5-9B-4bit   | 15% (11) | 48% (35) | 37% (27)     |

Claude Sonnet 4.6 generates the most challenging content — 55% of its approved questions target B1, significantly higher than all other models. This mirrors the pattern seen with GPT-5 in e05 (40% B1) and suggests that more capable models naturally produce harder, more contextually rich sentences.

The local models generate the highest proportion of A1 questions (14–15%), indicating simpler sentence structures.

---

## 4. Analysis

### 4.1 Failure Mode Analysis

The failure modes in FITB are qualitatively different from MCFIB (e01–e05). In MCFIB, the dominant failures were distractor-related: duplicate options, implausible distractors, and incorrect option counts. In FITB, three new failure modes dominate:

**1. Subject ambiguity (GPT-4.1, Qwen).** Sentences using "sie" without sufficient context to disambiguate singular from plural. GPT-4.1 generated "Jeden Morgen **\_** (gehen) sie zur Arbeit" — both "geht" (she) and "gehen" (they) are valid. This was the single most common failure for GPT-4.1, identical to the pattern seen in the t06 trial despite the strengthened uniqueness rule in the prompt.

**2. Incorrect grammar (Qwen).** The local models produce wrong declension endings — "eine neuen Schule" instead of "eine neue Schule", "das schönen Spielzeug" instead of "das schöne Spielzeug". These are genuine grammatical errors in the generated content, not ambiguity. The 4-bit model has roughly twice the rate of the 8-bit model (28 vs 14 editor failures).

**3. Topic misalignment (Qwen).** The most severe failure: generating questions that test the wrong grammar point. Qwen3.5-9B-8bit generated Perfekt sentences in a Präteritum preset ("Gestern bin nach Hause gegangen" — Perfekt with "bin" instead of Präteritum "ging"). Qwen3.5-9B-4bit placed dative-governing verbs in accusative presets and generated reflexive pronouns ("sich") where personal pronouns were expected.

**4. Structural incompleteness (GPT-4.1).** Three Futur I questions had missing subjects in the answered sentence — the model generated the blank and hint but the transform stripped the hint parenthetical and left an incomplete sentence (e.g., "In zwei Stunden wird nach Hause kommen"). This is a prompt/transform interaction issue: the model used the hint parenthetical as the subject marker.

### 4.2 Claude Models: A New Quality Tier

The headline finding is that both Claude models outperform GPT-4.1 on FITB generation:

| Model             | All-Pass | Teacher | Editor | Student | Multi-fail items |
| ----------------- | -------- | ------- | ------ | ------- | ---------------- |
| Claude Sonnet 4.6 | **98%**  | 100%    | 100%   | 98%     | 0                |
| Claude Haiku 4.5  | **89%**  | 99%     | 100%   | 90%     | 0                |
| GPT-4.1           | **83%**  | 98%     | 94%    | 86%     | 4                |

Claude Sonnet 4.6 is the clear quality leader with 98% all-pass. Claude Haiku 4.5 is 2.4× faster than Sonnet and the fastest API model overall, with 89% all-pass.

GPT-4.1's 83% all-pass is significantly lower than its 98% Teacher rate — the gap reveals that many teacher-approved questions still fail the editor or student. This is driven by structural issues in Futur I (subject omission) and the persistent "sie" ambiguity.

### 4.3 Structured Output: Parse Failures Eliminated

Switching from `json_mode` (trial) to `schema` mode (experiment) had a dramatic effect on local models:

| Model           | json_mode (t06) | schema (e06) |
| --------------- | --------------- | ------------ |
| Qwen3.5-9B-8bit | 10% parse fail  | **0%**       |
| Qwen3.5-9B-4bit | 30% parse fail  | **0%**       |

Structured output via outlines constrained generation completely eliminated parse failures, yielding 100 questions from each local model versus ~45 and ~35 in the trial. However, the all-pass rates (66% and 48%) show that structural validity alone does not guarantee usable output — most Qwen failures are content quality issues, not format issues.

### 4.4 Quantization Effect

The 8-bit vs 4-bit comparison confirms the finding from e04 that quantization significantly impacts quality:

| Metric   | 8-bit | 4-bit | Delta |
| -------- | ----- | ----- | ----- |
| All-Pass | 66%   | 48%   | -18pp |
| Teacher  | 87%   | 73%   | -14pp |
| Editor   | 86%   | 72%   | -14pp |
| Student  | 77%   | 81%   | +4pp  |

The 18-point all-pass gap is wider than the 14-point Teacher gap, showing that the 4-bit model's failures compound across evaluators. The 4-bit model's higher Student accuracy (81% vs 77%) is paradoxical — it likely reflects the 4-bit model generating simpler questions that the student can answer more easily, rather than higher quality.

### 4.5 Manual Curation of Qwen Samples (Anecdotal)

A small manual curation of Qwen outputs revealed failure modes that the automated evaluators did not fully catch:

**Hint quality issues.** The 8-bit model used already-declined forms as hints instead of base forms — e.g., `_____ (ihr)` where "ihr" is itself the dative form, making the hint useless for a learner who needs to derive the answer from the base. The 4-bit model went further, using inflected forms like "(neuer)" instead of "(neu)". These pass the static evaluator (which checks for a blank and an answer) but are pedagogically broken.

**Sentence structure errors.** The 8-bit model placed the hint on the wrong sentence element — "Gestern **\_** (ich) ins Kino gehen" uses the subject "ich" as the hint instead of the verb, producing a malformed FITB question. The resulting `answered_sentence` ("Gestern ging ins Kino gehen") is also ungrammatical.

**Unnatural sentences.** The 4-bit model generated sentences that are grammatically parseable but not how a native speaker would express the idea — e.g., "Wir brauchen uns Hilfe" and "Er hilft dem Mann schweren Arbeit". The editor evaluator caught some of these but not all.

**"Sie" ambiguity.** Both models produced "sie" ambiguity ("Sie **\_** das Haus bauen" — werden or wird; "Sie lernt sehr fleißig" — lernt or lernen), confirming the automated teacher findings.

These observations suggest that the automated evaluators undercount defects in local model output — particularly around hint quality and sentence naturalness, which are FITB-specific concerns not present in MCFIB evaluation.

### 4.6 The "sie" Ambiguity Persists

Despite strengthening the uniqueness rule in the prompt ("The sentence must provide enough context... that only one word form is grammatically correct"), GPT-4.1 still generated ambiguous "sie" sentences. The prompt improvement was language-agnostic by design, and GPT-4.1 appears to not internalize the constraint for German-specific pronoun ambiguity.

Claude models did not produce any "sie" ambiguity failures, suggesting they are better at the self-verification step implied by the strengthened rule.

---

## 5. Discussion

### 5.1 Claude Sonnet 4.6 as the New Quality Leader

Claude Sonnet 4.6's perfect 100% across Teacher and Editor at 100 questions is remarkable. For context, the best prior result was GPT-5-mini and GPT-5 at 97% Teacher on MCFIB (e05). FITB is arguably a harder task (no distractors to generate, but stricter uniqueness requirements), making this result even more impressive.

The 55% B1 content rate — the highest of any model — suggests Sonnet generates more contextually rich and challenging sentences rather than defaulting to simple A2 constructions. This is valuable for producing content aimed at intermediate learners.

### 5.2 Claude Haiku 4.5: The New Cost-Performance Optimum

Claude Haiku 4.5 offers a compelling combination:

- 99% Teacher approval (1 borderline rejection)
- 100% Editor approval
- Fastest API model at 4.2s/sample
- Cost-effective Anthropic pricing tier

For latency-sensitive FITB generation, Haiku is strictly preferable to GPT-4.1 (faster, 89% vs 83% all-pass, better grammar).

### 5.3 Local Models: Quality Ceiling and Practical Viability

Qwen3.5-9B-8bit at 66% all-pass (87% Teacher) is an improvement over its e03 MCFIB score (62.6% Teacher), though the all-pass metric shows the gap with API models is larger than Teacher alone suggests. Three factors contribute to the improvement:

1. **Structured output** eliminated parse failures (was 10% of samples)
2. **Thinking disabled** prevented the model from consuming its token budget on internal reasoning before producing output
3. **FITB format** is simpler than MCFIB (no distractors to generate)

However, 66% all-pass is still 17–32 points below the API models. The failures are qualitatively different — not ambiguity or edge cases, but genuine grammatical errors, topic misalignment, and hint quality issues that indicate the model lacks deep grammatical competence. At 71.8s/sample (median 81.6s), the latency is also 17× slower than Haiku.

The 4-bit model at 48% all-pass is not viable for production use — fewer than half its questions pass all evaluators. The 18-point all-pass gap from 8-bit confirms quantization as a significant quality predictor for this task.

### 5.4 Limitations

- **Small sample per topic.** Each topic has 10 questions per model (2 repeats × 5 questions). A single verdict change shifts a topic's approval rate by 10 percentage points.
- **Same judge for all models.** GPT-4o evaluated all models, including GPT-4.1 from the same provider. Cross-provider bias is possible and not evaluated in this experiment.
- **Local model latency is noisy.** MLX Metal buffer cache growth causes logarithmic latency increase over a session ([ml-explore/mlx#390](https://github.com/ml-explore/mlx/pull/390)). Median latency is reported alongside mean, but true steady-state throughput would require cache management.
- **Haiku's single rejection may be an evaluator error.** The teacher rejected a sentence testing accusative after "auf den" in a Dativ preset — the sentence is correct for the Akkusativ reading of "auf", making this a borderline case. True Teacher approval may be 100%.

---

## 6. Conclusions

Across 500 German grammar fill-in-the-blank questions from five models testing ten topics:

1. **Claude Sonnet 4.6 is the quality leader** with 98% all-pass (100% Teacher, 100% Editor). It generates the most challenging content (55% B1) with only 2 student failures across 100 questions.

2. **Claude Haiku 4.5 is the new cost-performance optimum** for FITB: 89% all-pass, 99% Teacher, 100% Editor, and the fastest API model at 4.2s/sample. It is faster and higher quality than GPT-4.1.

3. **GPT-4.1 scores 83% all-pass** (98% Teacher), revealing that Teacher approval alone overstates usable output. The gap is driven by structural issues (subject omission in Futur I), the persistent "sie" ambiguity, and editor failures that the teacher overlooked.

4. **Structured output eliminates parse failures.** Switching from `json_mode` to `schema` mode reduced local model parse failures from 10–30% to 0%, yielding 100 structurally valid questions per model. However, structural validity does not guarantee quality — Qwen all-pass rates are 66% and 48%.

5. **FITB reshuffles the failure taxonomy.** Distractor quality (MCFIB's dominant failure) is replaced by answer ambiguity and topic misalignment. The strengthened uniqueness rule helped Claude models avoid ambiguity entirely but did not prevent it in GPT-4.1.

6. **The local model quality ceiling is 66% all-pass** (Qwen3.5-9B-8bit). Failures are genuine grammatical errors, topic misalignment, and hint quality issues — not ambiguity or edge cases.

7. **Quantization matters: 8-bit vs 4-bit is an 18-point all-pass gap** (66% vs 48%), consistent with e04 findings. The 4-bit model has baked-in knowledge errors (Konjunktiv II for Futur I) not present in the 8-bit model.

---

_Written by Claude Opus 4.6 using data generated by TurboContentForge. Generation models: gpt-4.1 (OpenAI API), claude-sonnet-4-6, claude-haiku-4-5-20251001 (Anthropic API), NexVeridian/Qwen3.5-9B-8bit, mlx-community/Qwen3.5-9B-MLX-4bit (Local MLX). LLM judge model (Editor, Student, Teacher evaluators): gpt-4o._
