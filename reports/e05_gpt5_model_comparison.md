# GPT-5 Family vs GPT-4o for German Grammar Quiz Generation

**Experiment:** e05 GPT-5 model comparison
**Date:** 2026-03-11
**Author:** Claude Sonnet 4.6

---

## Abstract

This report evaluates OpenAI's GPT-5 and GPT-5-mini against the established GPT-4o baseline for German grammar quiz generation. Ten grammar topics were tested, each with ten questions (100 per model, 300 total). Three LLM-as-judge evaluators assessed each question. The headline result is convergence at the top: all three models achieve 95–97% Teacher approval and 96–99% Editor approval — a remarkably tight spread. GPT-5 edges GPT-4o on Teacher approval (97% vs 95%) and matches it on zero parse failures. GPT-5-mini ties GPT-5 at 97% Teacher approval while being 2.4× faster and 7.8× cheaper per sample than GPT-5 — and 42% cheaper than GPT-4o — making it the strongest cost-performance option. The quality gap between GPT-4o and the GPT-5 family is small — 2 percentage points on Teacher approval — and all three models are production-viable across all ten topics. The few failures that do occur are isolated and mechanistically distinct: GPT-4o's rejections concentrate on instruction-wording strictness and distractor plausibility; GPT-5's on two Präteritum conjugation errors for "ihr" forms; GPT-5-mini's on a single adjective declension error. This experiment also introduces Futur I as a tenth topic, which all three models handle at 100% Teacher approval.

**Note:** GPT-5 and GPT-5-mini were run at default temperature (no explicit temperature set), while GPT-4o was run at temperature 0.3 consistent with prior experiments.

---

## 1. Introduction

Experiments e01–e04 established GPT-4o as the quality ceiling for German grammar quiz generation and explored local model alternatives. E05 shifts focus upward: does OpenAI's GPT-5 family improve on GPT-4o's already-high quality, and does GPT-5-mini offer a viable cost-reduced alternative?

The experiment expands the topic set from 9 to 10, adding Futur I (future tense with "werden") alongside the 9 topics from prior experiments. All three models used the same prompt template ("exact answers small model v2"), the same data file ("german_mc_v2_presets"), and the same output mode (json_mode). Evaluation used gpt-4o as the LLM judge, consistent with prior experiments.

> **Statistical note:** Each topic is represented by 10 questions per model. A single question changing verdict shifts a topic's approval rate by 10 percentage points. All per-topic figures should be read with this granularity in mind.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Collection     | Model      | Provider   | Output Mode | Temp | Samples | Failed |
| -------------- | ---------- | ---------- | ----------- | ---- | ------- | ------ |
| e05 GPT-4o     | gpt-4o     | OpenAI API | json_mode   | 0.3  | 20/20   | 0      |
| e05 GPT-5      | gpt-5      | OpenAI API | json_mode   | —    | 20/20   | 0      |
| e05 GPT-5-mini | gpt-5-mini | OpenAI API | json_mode   | —    | 20/20   | 0      |

Each model generated 20 samples (2 repeats × 10 topic presets, 5 questions each), yielding 100 questions per model, 300 total. No parse failures occurred in any model.

### 2.2 Grammar Topics

Ten topics were tested — the nine from e03 plus Futur I:

| Preset                           | Example Question                                        | Example Answer |
| -------------------------------- | ------------------------------------------------------- | -------------- |
| Adjektivdeklination im Akkusativ | _Es gibt einen \_\_\_\_ (klein) Ort._                   | kleinen        |
| Adjektivdeklination im Dativ     | _Ich legte das Telefon auf den \_\_\_\_ (alt) Tisch._   | alten          |
| Adjektivdeklination im Nominativ | _Das ist eine \_\_\_\_ (klein) Stadt._                  | kleine         |
| **Futur I** (new)                | _Morgen \_\_\_\_ ich früh schlafen gehen._              | werde          |
| Hilfsverb in Perfekt             | _Er \_\_\_ (haben oder sein) nach Österreich gefahren._ | ist            |
| Konjugation im Perfekt           | _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._            | gearbeitet     |
| Konjugation im Präsens           | _\_\_\_\_ (sprechen) du Deutsch?_                       | Sprichst       |
| Konjugation im Präteritum        | _Er \_\_\_ (gehe) ins Kino._                            | ging           |
| Personalpronomen in Akkusativ    | _Kannst du \_\_\_ (ich) anrufen?_                       | mich           |
| Personalpronomen in Dativ        | _Kannst du \_\_\_ (ich) bitte helfen?_                  | mir            |

### 2.3 Evaluators

Three evaluators were used (the static evaluator from e03 was not included in this run):

- **Editor:** German language editor assessing grammatical correctness of the answer-filled sentence
- **Student:** Simulated B1 learner attempting to answer the question
- **Teacher:** Expert auditing clarity, correctness, distractor quality, explanation accuracy, and CEFR level

Evaluation used **gpt-4o** at default settings in `json_mode`.

---

## 3. Results

### 3.1 Overall Approval Rates

| Model          | Teacher Approval   | Editor Approval    | Student Approval   |
| -------------- | ------------------ | ------------------ | ------------------ |
| **GPT-5**      | **97.0%** (97/100) | 96.0% (96/100)     | **98.0%** (98/100) |
| **GPT-5-mini** | **97.0%** (97/100) | **99.0%** (99/100) | 97.0% (97/100)     |
| GPT-4o         | 95.0% (95/100)     | 98.0% (98/100)     | 97.0% (97/100)     |

All three models exceed 95% across all evaluators. The differences are within the noise floor of 100-question samples — a single question flip changes any rate by 1 percentage point. The practical conclusion is that all three models are equivalently production-viable for this task.

### 3.2 Generation Performance

| Model      | Avg s/sample | Min s/sample | Max s/sample | Avg Completion Tokens | Avg Prompt Tokens | Cost/sample |
| ---------- | ------------ | ------------ | ------------ | --------------------- | ----------------- | ----------- |
| GPT-4o     | **8.6**      | 4.4          | 15.3         | 626                   | 375               | $0.0072     |
| GPT-5-mini | 26.2         | 18.8         | 35.7         | 2,038                 | 374               | **$0.0042** |
| GPT-5      | 62.8         | 43.9         | 98.3         | 3,224                 | 374               | $0.0327     |

*Costs calculated from OpenAI API pricing: gpt-4o ($2.50/$10.00 per 1M input/output tokens), gpt-5 ($1.25/$10.00), gpt-5-mini ($0.25/$2.00).*

GPT-5 is 7.3× slower than GPT-4o per sample and generates 5.2× more completion tokens. GPT-5-mini is 3.0× slower than GPT-4o and generates 3.3× more tokens. However, due to the GPT-5 family's lower per-token input pricing, GPT-5-mini is actually **42% cheaper** than GPT-4o per sample ($0.0042 vs $0.0072), while GPT-5 is 4.5× more expensive ($0.0327 vs $0.0072). The higher token counts for the GPT-5 family suggest these models produce more verbose output — likely longer explanations — for the same 5-question generation request. The extra tokens do not translate into measurably higher quality, but GPT-5-mini's lower pricing makes it the clear cost leader.

### 3.3 Teacher Approval by Topic (%)

| Topic                            | GPT-4o  | GPT-5   | GPT-5-mini |
| -------------------------------- | ------- | ------- | ---------- |
| Adjektivdeklination im Akkusativ | **100** | **100** | **100**    |
| Adjektivdeklination im Dativ     | **100** | 90      | **100**    |
| Adjektivdeklination im Nominativ | **100** | **100** | 90         |
| Futur I                          | **100** | **100** | **100**    |
| Hilfsverb in Perfekt             | 70      | **100** | 90         |
| Konjugation im Perfekt           | **100** | **100** | 90         |
| Konjugation im Präsens           | **100** | **100** | **100**    |
| Konjugation im Präteritum        | 80      | 80      | **100**    |
| Personalpronomen in Akkusativ    | **100** | **100** | **100**    |
| Personalpronomen in Dativ        | **100** | **100** | **100**    |

Each model achieves 100% on at least 7 of 10 topics. No model scores below 70% on any topic. The weakest results:

- **GPT-4o**: 70% on Hilfsverb in Perfekt (3 rejections), 80% on Konjugation im Präteritum (2 rejections)
- **GPT-5**: 80% on Konjugation im Präteritum (2 rejections), 90% on Adjektivdeklination im Dativ (1 rejection)
- **GPT-5-mini**: 90% on three topics (Nominativ, Hilfsverb, Perfekt) — 1 rejection each

GPT-5-mini's failures are the most evenly distributed (one per topic across three topics), while GPT-4o's concentrate in two topics. GPT-5's Präteritum weakness is shared with GPT-4o, suggesting a persistent difficulty with Präteritum "ihr" forms that persists across model generations.

### 3.4 Editor Approval by Topic (%)

| Topic                            | GPT-4o  | GPT-5   | GPT-5-mini |
| -------------------------------- | ------- | ------- | ---------- |
| Adjektivdeklination im Akkusativ | **100** | 90      | **100**    |
| Adjektivdeklination im Dativ     | **100** | **100** | **100**    |
| Adjektivdeklination im Nominativ | 90      | **100** | **100**    |
| Futur I                          | **100** | **100** | **100**    |
| Hilfsverb in Perfekt             | **100** | **100** | **100**    |
| Konjugation im Perfekt           | **100** | **100** | **100**    |
| Konjugation im Präsens           | **100** | **100** | **100**    |
| Konjugation im Präteritum        | **100** | 80      | **100**    |
| Personalpronomen in Akkusativ    | 90      | 90      | **100**    |
| Personalpronomen in Dativ        | **100** | **100** | 90         |

GPT-5-mini achieves 100% Editor on 9 of 10 topics — the cleanest grammatical output of any model. GPT-5's 80% Editor on Präteritum aligns with its Teacher failures on the same topic, confirming that its "ihr" conjugation errors are genuine grammatical mistakes, not just pedagogical shortcomings.

### 3.5 Student Approval by Topic (%)

| Topic                            | GPT-4o  | GPT-5   | GPT-5-mini |
| -------------------------------- | ------- | ------- | ---------- |
| Adjektivdeklination im Akkusativ | **100** | **100** | **100**    |
| Adjektivdeklination im Dativ     | 90      | **100** | **100**    |
| Adjektivdeklination im Nominativ | 90      | 90      | 90         |
| Futur I                          | **100** | **100** | 90         |
| Hilfsverb in Perfekt             | 90      | **100** | **100**    |
| Konjugation im Perfekt           | **100** | **100** | **100**    |
| Konjugation im Präsens           | **100** | **100** | **100**    |
| Konjugation im Präteritum        | **100** | 90      | **100**    |
| Personalpronomen in Akkusativ    | **100** | **100** | **100**    |
| Personalpronomen in Dativ        | **100** | **100** | 90         |

Student failures are sparse and do not strongly correlate with Teacher or Editor failures. The simulated student struggles with different questions than the expert evaluators, suggesting that question difficulty and question correctness are largely orthogonal at this quality level.

### 3.6 Items Failing Multiple Evaluators

Only 4 items across all 300 received 2+ evaluator rejections:

| Model      | Topic                            | Question                                                      | Fails / 3 |
| ---------- | -------------------------------- | ------------------------------------------------------------- | --------- |
| GPT-5      | Konjugation im Präteritum        | _Ihr \_\_\_\_ (lesen) das Buch bis spät in die Nacht._        | **3/3**   |
| GPT-4o     | Adjektivdeklination im Nominativ | _Das \_\_\_\_ (neu) Auto gehört meinem Vater._                | 2/3       |
| GPT-5      | Konjugation im Präteritum        | _Letztes Jahr \_\_\_\_ (fahren) ihr mit dem Zug nach Berlin._ | 2/3       |
| GPT-5-mini | Adjektivdeklination im Nominativ | _Der \_\_\_\_ (groß) Mann arbeitet hier._                     | 2/3       |

GPT-5's "Ihr last das Buch" (marked answer: "last") is the only item rejected by all three evaluators — a triple fail. The teacher flagged the conjugation as incorrect, the editor rejected the grammar, and the student could not answer it. This is a genuine verb conjugation error: the Präteritum of "lesen" for "ihr" is "last" — which is actually correct, but rare enough that even the gpt-4o judge flagged it as wrong. This highlights a limitation of LLM-as-judge evaluation: the judge itself can be wrong on edge cases of German grammar.

The GPT-5-mini Nominativ failure ("Der große Mann") presents a similar evaluator-error pattern: "große" is correct after the definite article "der" (weak declension: _der große Mann_), but the teacher evaluator incorrectly claimed it should be "großer" (strong declension without an article). This is a false negative from the evaluation pipeline, not a model error.

### 3.7 CEFR Level Distribution (Teacher-Approved Questions)

| Model      | A1     | A2       | B1       |
| ---------- | ------ | -------- | -------- |
| GPT-4o     | 9% (9) | 60% (57) | 31% (29) |
| GPT-5      | 7% (7) | 53% (51) | 40% (39) |
| GPT-5-mini | 8% (8) | 56% (54) | 36% (35) |

GPT-5 generates the highest proportion of B1-level questions (40%), continuing the pattern observed with Qwen3.5-9B in e03. The GPT-5 family skews slightly harder than GPT-4o, with 9 fewer A2 questions shifted toward B1. This is a positive signal for content diversity — harder questions are more valuable for intermediate learners.

---

## 4. Analysis

### 4.1 Failure Mode Analysis

The failures in e05 are qualitatively different from e03. In e03, failures were structural — duplicate options, task substitution, case confusion, degenerate repetition. In e05, all failures are isolated content errors on individual questions. No model exhibits a systematic failure pattern.

**GPT-4o's Hilfsverb in Perfekt rejections (3/10).** The Teacher rejected three questions not for wrong answers but for instruction wording: the prompt's instruction template "Wählen Sie das richtige Konjugation im haben oder sein aus" contains a grammatical error in the instruction itself ("Konjugation" should be "Konjugation von" or "konjugierte Form"). The Teacher penalized all three on this basis, plus flagged weak distractors ("wäre" is not plausible for a Perfekt auxiliary question). This is a prompt-level issue, not a model-level one — the same instruction template is used by all models, but the GPT-4o-as-judge evaluator was inconsistently strict about it across models.

**GPT-5's Präteritum failures (2/10).** Two questions used the "ihr" form of strong verbs in Präteritum: "Ihr last" (lesen) and "Letztes Jahr fuhrt ihr" (fahren). Both forms are grammatically defensible — "ihr last" and "ihr fuhrt" are the historically correct Präteritum forms — but they are archaic and rarely encountered in modern usage. The evaluator rejected them as incorrect. This is an edge case where model and evaluator disagree on acceptable German, and the evaluator's stricter standard is arguably appropriate for A2/B1 learners.

**GPT-5's Dativ rejection (1/10).** "Er schrieb den Brief mit blauer Tinte" — the teacher evaluator confused itself in its reasoning, initially saying "blauer" was wrong, then contradicting itself. The answer "blauer" is correct: "mit" governs dative, "Tinte" is feminine, and without an article the strong declension ending for feminine dative is "-er". This is another evaluator false negative.

**GPT-5-mini's Nominativ rejection (1/10).** "Der große Mann arbeitet hier" — as discussed in §3.6, the model is correct and the evaluator is wrong. After the definite article "der", weak declension applies: "der große Mann", not "der großer Mann".

### 4.2 Evaluator Reliability at High Quality Levels

A pattern emerges from §4.1: at 95%+ model quality, a meaningful fraction of "failures" are evaluator errors rather than model errors. Of the 11 total Teacher rejections across all three models:

- ~3 are instruction-wording strictness (GPT-4o Hilfsverb) — a prompt issue
- ~2 are evaluator false negatives (GPT-5 Dativ, GPT-5-mini Nominativ) — evaluator errors
- ~2 are genuine but debatable (GPT-5 Präteritum "ihr" forms) — edge cases
- ~4 are genuine quality issues (GPT-4o Präteritum, GPT-5-mini Hilfsverb/Perfekt)

This suggests the true Teacher approval rate for all three models may be closer to 98–99% after correcting for evaluator errors. It also suggests that at this quality level, the LLM-as-judge evaluation methodology is approaching its reliability ceiling — the judge introduces as much noise as the models being judged.

### 4.3 The Speed–Quality–Cost Tradeoff

| Model      | Teacher % | Avg s/sample | Cost/sample | Relative Cost |
| ---------- | --------- | ------------ | ----------- | ------------- |
| GPT-4o     | 95%       | **8.6 s**    | $0.0072     | 1.7×          |
| GPT-5-mini | 97%       | 26.2 s       | **$0.0042** | **1.0×**      |
| GPT-5      | 97%       | 62.8 s       | $0.0327     | 7.8×          |

GPT-5-mini is the cheapest model tested — 42% less than GPT-4o per sample — while also achieving the highest Teacher approval (tied with GPT-5 at 97%). This inverts the token-based cost assumption: although GPT-5-mini generates 3.3× more tokens than GPT-4o, its per-token pricing is low enough to more than offset the extra volume.

GPT-4o remains the fastest option (8.6s vs 26.2s per sample) while being only 2 points below the GPT-5 family on Teacher approval. For latency-sensitive pipelines, GPT-4o is still the best choice.

GPT-5 is 7.8× more expensive than GPT-5-mini with identical Teacher approval (97%) and 2.4× slower, making it strictly inferior for this task. The only scenario where GPT-5 might be preferred is if the longer explanations it generates provide additional value — but this experiment does not measure explanation quality independently.

### 4.4 Comparison with E03 Local Models

For context, here are the e05 results alongside the e03 local model tier structure:

| Model                | Teacher % | Avg s/sample | Source     |
| -------------------- | --------- | ------------ | ---------- |
| **GPT-5** (e05)      | **97.0%** | 62.8         | OpenAI API |
| **GPT-5-mini** (e05) | **97.0%** | 26.2         | OpenAI API |
| **GPT-4o** (e05)     | **95.0%** | 8.6          | OpenAI API |
| GPT-4o (e03)         | 87.8%     | 5.5          | OpenAI API |
| Qwen3.5-9B (e03)     | 62.6%     | 15.7         | Local MLX  |
| Qwen2.5-7B (e03)     | 42.4%     | 14.3         | Local MLX  |
| EuroLLM-22B (e03)    | 24.4%     | 52.4         | Local MLX  |
| Llama-3.2-3B (e03)   | 17.8%     | 7.0          | Local MLX  |
| SmolLM3-3B (e03)     | 1.4%      | 6.9          | Local MLX  |

GPT-4o's e05 score (95.0%) is higher than its e03 score (87.8%). This is not an apples-to-apples comparison — e05 uses 10 questions per topic (vs ~10 in e03) and includes the new Futur I topic — but it suggests that the 87.8% e03 figure may have been slightly pessimistic, or that run-to-run variation at this quality level is meaningful.

The quality gap between the best API model (GPT-5, 97%) and the best local model (Qwen3.5-9B, 62.6%) remains at 34 percentage points. The GPT-5 family does not change the fundamental conclusion from e03: local models are not yet viable replacements for API models on this task.

### 4.5 Futur I: A Clean Topic

Futur I (future tense with "werden") was added in e05 and all three models achieve 100% Teacher approval on it. This is unsurprising — Futur I is morphologically simple (conjugate "werden", keep the main verb as infinitive) and does not involve the distractor-generation challenges that make Adjektivdeklination im Dativ difficult. It serves as a useful control topic confirming that all models handle straightforward grammar constructions reliably.

---

## 5. Discussion

### 5.1 Diminishing Returns at the Quality Frontier

The central finding of e05 is that GPT-5-mini is the new Pareto optimum for German grammar quiz generation. The 2-point Teacher approval gain over GPT-4o (95% → 97%) comes at *lower* cost: GPT-5-mini is 42% cheaper per sample ($0.0042 vs $0.0072) despite generating 3.3× more tokens, thanks to its lower per-token pricing. The tradeoff is latency — GPT-5-mini is 3.0× slower than GPT-4o. GPT-5, by contrast, offers no advantage over GPT-5-mini: identical quality, 2.4× slower, 7.8× more expensive.

This pattern is consistent with broader trends in LLM development: as models approach human-level performance on a task, each generation brings smaller absolute improvements. For this task, GPT-4o already operates above the 90% threshold where the remaining errors are edge cases, evaluator disagreements, and prompt-level issues rather than systematic model limitations.

### 5.2 Implications for Pipeline Design

The practical implications are:

1. **GPT-5-mini is the new default recommendation.** It achieves the highest Teacher approval (97%, tied with GPT-5), is 42% cheaper than GPT-4o per sample ($0.0042 vs $0.0072), and is 7.8× cheaper than GPT-5. The only tradeoff is latency (26.2s vs 8.6s per sample).

2. **GPT-4o remains the best choice for latency-sensitive pipelines.** At 8.6s per sample (3× faster than GPT-5-mini), it is the fastest option while still achieving 95% Teacher approval.

3. **GPT-5 offers no advantage over GPT-5-mini.** Identical Teacher approval, 2.4× slower, 7.8× more expensive. There is no scenario in this data where GPT-5 outperforms GPT-5-mini.

3. **The evaluation pipeline needs calibration.** At 95%+ model quality, evaluator false negatives become a significant fraction of total failures. Consider either (a) using GPT-5 as the judge model, (b) adding a second-pass review for rejected items, or (c) accepting that 95% measured approval implies ~98% true approval.

4. **The static evaluator was not used in e05.** Adding it back would catch any residual duplicate-option or structural issues, though at these quality levels such issues appear to be absent.

### 5.3 Limitations

- **No explicit temperature for GPT-5/5-mini.** The GPT-5 family was run at default temperature while GPT-4o used 0.3. This may slightly inflate GPT-5 family scores if default temperature is lower, or deflate them if higher.
- **Single evaluation run.** Each question was evaluated once. Run-to-run evaluation variance is unknown but likely non-trivial given the evaluator errors identified in §4.1.
- **Same evaluator model as one of the generators.** GPT-4o was used both as a generator and as the evaluation judge. This could introduce a self-preference bias, though GPT-4o's slightly lower scores suggest this effect, if present, is small.
- **No prompt caching factored in.** Costs are calculated at standard (non-cached) input rates. With prompt caching, input costs would drop significantly for all models, further favoring GPT-5-mini which already has the lowest input cost.

---

## 6. Conclusions

Across 300 German grammar questions from three OpenAI models testing ten topics:

1. **GPT-5 and GPT-5-mini achieve 97% Teacher approval**, a 2-point improvement over GPT-4o's 95%. All three models are production-viable with zero parse failures and no systematic failure modes.

2. **GPT-5-mini is strictly preferable to GPT-5.** Identical Teacher approval (97%), 2.4× faster generation, 7.8× cheaper per sample ($0.0042 vs $0.0327). GPT-5 offers no measurable advantage for this task.

3. **GPT-5-mini is the new cost-performance optimum.** At 97% Teacher approval and $0.0042 per sample, it is both the highest-quality and cheapest model tested — 42% cheaper than GPT-4o ($0.0072). GPT-4o retains the latency advantage (8.6s vs 26.2s per sample).

4. **At 95%+ quality, evaluator noise becomes the dominant signal.** Approximately half of the Teacher rejections in e05 are attributable to evaluator errors, instruction-wording strictness, or debatable edge cases rather than genuine model failures. The true quality of all three models is likely 98–99%.

5. **The GPT-5 family generates harder questions.** GPT-5's approved questions have the highest B1 proportion (40%) vs GPT-4o's 31%. For building challenging quiz content, the GPT-5 family produces more advanced material.

6. **Futur I is a clean topic.** All models achieve 100% Teacher approval on the newly added Futur I topic.

7. **The API vs local model gap remains large.** GPT-5's 97% Teacher approval vs Qwen3.5-9B's 62.6% (e03) represents a 34-point gap that has not closed from the model consumer side.

---

_Written by Claude Sonnet 4.6 using data generated by TurboContentForge. Generation models: gpt-4o, gpt-5, gpt-5-mini (all OpenAI API). LLM judge model (Editor, Student, Teacher evaluators): gpt-4o._
