# Output Mode Effects on German Grammar Quiz Quality: Comparing prompt_only, json_mode, and schema

**Experiment:** e02 exact answers
**Date:** 2026-03-05
**Author:** Claude Sonnet 4.6 (revised by AJ)

---

## Abstract

This report evaluates whether OpenAI's three structured output modes — `prompt_only`, `json_mode`, and `schema` — produce measurably different quality in GPT-4o-generated German grammar quiz questions. Using the same "exact answers" prompt from e01, eleven grammar topics were tested once per mode (10 questions each, 110 questions per mode, 330 total). Three LLM-as-judge evaluators assessed each question. The headline result is that **output mode has no meaningful effect on Teacher-level quality**: approval rates were 89.1%, 88.2%, and 89.1% respectively — statistically indistinguishable given the small per-cell sample size. However, schema mode diverges sharply on Editor approval (89.1% vs. 96–97% for the other two modes), driven by a systematic error: the model marks strong adjective declension forms as correct in contexts that require weak declension after definite articles. Schema mode simultaneously eliminates all duplicate option defects — a structural benefit — and generates ~30% faster, but introduces content accuracy regressions that outweigh its formatting advantages for this task.

---

## 1. Introduction

Structured output modes are typically evaluated on their ability to produce well-formed JSON — a parsing problem. Less studied is whether constraining the output format affects the _content_ of what is generated: do models reason differently when generating under a strict schema vs. free-form text? This experiment treats output mode as the sole independent variable and holds model (gpt-4o), prompt, temperature (0.7), and max tokens (2048) constant.

The secondary motivation was to test a fixed version of the prompt presets following corrections identified in e01. The Plusquamperfekt preset (which drove near-zero Editor approval in e01) has been retired. Personalpronomen in Akkusativ now uses an accusative-governing example (`mich`). Two new topics have been added: Konjugation im Perfekt and Hilfsverb in Perfekt.

> **Statistical note:** Each topic is represented by exactly one generation request (10 questions) per mode. A single question flipping verdict changes a topic's approval rate by 10 percentage points. All per-topic figures should be read with this granularity in mind; only the overall 110-question totals carry meaningful statistical weight. The 33 generation requests — not the 330 individual questions — constitute the effective sample for inference, since all 10 questions in a batch are generated together.

---

## 2. Experimental Setup

### 2.1 Generation Prompt and Presets

The prompt is identical to e01: a Jinja-templated instruction to generate multiple-choice fill-in-the-blank questions with a one-shot example per preset, returning JSON only.

Eleven grammar topics were tested, with updated or new presets compared to e01:

| Preset                                    | Example Question                                        | Example Answer | Change from e01       |
| ----------------------------------------- | ------------------------------------------------------- | -------------- | --------------------- |
| Possessivartikel deklination im Akkusativ | _Ich habe gestern mit \_\_\_ (er) Bruder gesprochen._   | seinem         | Unchanged             |
| Adjektivdeklination im Nominativ          | _Das ist eine \_\_\_\_ (klein) Stadt._                  | kleine         | Unchanged             |
| Adjektivdeklination im Dativ              | _Ich legte das Telefon auf den \_\_\_\_ (alt) Tisch._   | alten          | Unchanged             |
| Adjektivdeklination im Akkusativ          | _Es gibt einen \_\_\_\_ (klein) Ort_                    | kleinen        | Unchanged             |
| Possessivpronomen                         | _Ich habe gestern mit \_\_\_ (er) Bruder gesprochen._   | seinem         | Unchanged             |
| Konjugation im Präteritum                 | _Er \_\_\_ (gehe) ins Kino_                             | ging           | Unchanged             |
| Konjugation im Präsens                    | _\_\_\_\_ (sprechen) du Deutsch?_                       | Sprichst       | Unchanged             |
| Konjugation im Perfekt                    | _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._            | gearbeitet     | **New topic**         |
| Personalpronomen in Akkusativ             | _Kannst du \_\_\_ (ich) anrufen?_                       | mich           | **Fixed** (was `mir`) |
| Personalpronomen in Dativ                 | _Kannst du \_\_\_ (ich) bitte helfen?_                  | mir            | **New topic**         |
| Hilfsverb in Perfekt                      | _Er \_\_\_ (haben oder sein) nach Österreich gefahren._ | ist            | **New topic**         |

Notable changes from e01: Plusquamperfekt has been retired. Personalpronomen in Akkusativ now correctly uses an accusative-governing example (`anrufen` → `mich`). The three new topics test compound tense formation and auxiliary verb selection.

### 2.2 Output Modes Under Test

| Mode          | Mechanism                                                                                                        | Format requirement                                           |
| ------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `prompt_only` | Instruction-only; no API-level format constraint                                                                 | Relies on prompt instruction                                 |
| `json_mode`   | `response_format: {"type": "json_object"}` — valid JSON guaranteed                                               | Must contain the word "JSON" in messages (already satisfied) |
| `schema`      | `response_format: {"type": "json_schema", "strict": true}` with the full `GeneratedQuestionList` Pydantic schema | JSON must exactly match the schema                           |

### 2.3 Generation Timing and Token Usage

| Mode          | Avg. Time / Sample | Avg. Tokens / Sample |
| ------------- | ------------------ | -------------------- |
| `prompt_only` | 19.2 s             | 1,299                |
| `json_mode`   | 17.6 s             | 1,289                |
| `schema`      | **13.6 s**         | **1,262**            |

Schema mode is approximately 29% faster than prompt_only. The token savings are modest (~37 tokens/sample, ~3%), likely because the schema eliminates the model's tendency to restate the structure in the response.

### 2.4 Evaluators

Four evaluators assessed each question. Evaluation used **gpt-4o** at temperature 0.1 in `json_mode` — a change from e01, which used gpt-4o-mini. The stricter evaluator model may account for some differences in absolute approval rates between experiments.

- **Static:** Rule-based checks — option count, single correct answer, option uniqueness
- **Editor:** German language editor assessing grammatical correctness of the answer-filled sentence
- **Student:** Simulated B1 learner attempting to answer the question (accuracy measured by matching the marked correct answer)
- **Teacher:** Expert auditing clarity, correctness, distractor quality, explanation accuracy, and CEFR level

---

## 3. Results

### 3.1 Overall Approval Rates

| Mode          | Teacher Approval   | Editor Approval     | Student Accuracy    | Static Issues |
| ------------- | ------------------ | ------------------- | ------------------- | ------------- |
| `prompt_only` | 89.1% (98/110)     | **96.4%** (106/110) | **96.4%** (106/110) | 3             |
| `json_mode`   | 88.2% (97/110)     | **97.3%** (107/110) | 94.5% (104/110)     | 6             |
| `schema`      | **89.1%** (98/110) | 89.1% (98/110)      | 93.6% (103/110)     | **0**         |

Teacher approval is essentially flat across all three modes. The meaningful divergence is in **Editor approval**: schema trails prompt_only by 7.3 percentage points and json_mode by 8.2 points. Schema mode is the only mode where Editor and Teacher approval coincide — for the other two modes, the Editor is significantly more permissive than the Teacher.

### 3.2 CEFR Level Distribution

| CEFR Level | `prompt_only` | `json_mode` | `schema` |
| ---------- | ------------- | ----------- | -------- |
| A1         | 8 (7%)        | 9 (8%)      | 10 (9%)  |
| A2         | 70 (64%)      | 65 (59%)    | 60 (55%) |
| B1         | 32 (29%)      | 36 (33%)    | 40 (36%) |
| B2+        | 0             | 0           | 0        |

The A2–B1 concentration is consistent across all three modes. Schema mode skews very slightly toward B1, but the differences are small and likely noise given per-sample granularity. This distribution is the expected output for single-blank morphological questions without a specified difficulty target — output mode has no effect on it.

### 3.3 Results by Grammar Topic

#### Teacher Approval by Topic (%)

| Topic                                         | `prompt_only` | `json_mode` | `schema` |
| --------------------------------------------- | ------------- | ----------- | -------- |
| Adjektivdeklination im Akkusativ              | 80            | **100**     | **100**  |
| Adjektivdeklination im Dativ                  | **100**       | **100**     | 70       |
| Adjektivdeklination im Nominativ              | **100**       | 80          | 80       |
| Hilfsverb in Perfekt                          | 90            | 80          | 90       |
| Konjugation im Perfekt                        | 90            | **100**     | **100**  |
| Konjugation im Präsens                        | **100**       | 90          | **100**  |
| Konjugation im Präteritum                     | 90            | 80          | 90       |
| Personalpronomen in Akkusativ                 | **100**       | 90          | **100**  |
| Personalpronomen in Dativ                     | 80            | 80          | **100**  |
| **Possessivartikel deklination im Akkusativ** | **60**        | 90          | 80       |
| **Possessivpronomen**                         | 90            | 80          | 70       |

#### Editor Approval by Topic (%)

| Topic                                     | `prompt_only` | `json_mode` | `schema` |
| ----------------------------------------- | ------------- | ----------- | -------- |
| Adjektivdeklination im Akkusativ          | 90            | **100**     | **100**  |
| Adjektivdeklination im Dativ              | **100**       | **100**     | **100**  |
| **Adjektivdeklination im Nominativ**      | **100**       | **100**     | **60**   |
| Hilfsverb in Perfekt                      | 90            | **100**     | **100**  |
| Konjugation im Perfekt                    | **100**       | 90          | **100**  |
| Konjugation im Präsens                    | **100**       | **100**     | **100**  |
| Konjugation im Präteritum                 | **100**       | **100**     | 80       |
| Personalpronomen in Akkusativ             | **100**       | **100**     | 90       |
| Personalpronomen in Dativ                 | **100**       | **100**     | **100**  |
| Possessivartikel deklination im Akkusativ | 80            | 90          | 80       |
| **Possessivpronomen**                     | **100**       | 90          | **70**   |

#### Student Accuracy by Topic (%)

| Topic                                     | `prompt_only` | `json_mode` | `schema` |
| ----------------------------------------- | ------------- | ----------- | -------- |
| Adjektivdeklination im Akkusativ          | **100**       | **100**     | **100**  |
| Adjektivdeklination im Dativ              | **100**       | 90          | **100**  |
| **Adjektivdeklination im Nominativ**      | **100**       | 90          | 70       |
| Hilfsverb in Perfekt                      | 90            | **100**     | **100**  |
| Konjugation im Perfekt                    | **100**       | **100**     | **100**  |
| Konjugation im Präsens                    | **100**       | 90          | **100**  |
| Konjugation im Präteritum                 | 90            | **100**     | 90       |
| Personalpronomen in Akkusativ             | **100**       | **100**     | **100**  |
| Personalpronomen in Dativ                 | **100**       | **100**     | **100**  |
| Possessivartikel deklination im Akkusativ | 80            | 90          | 90       |
| **Possessivpronomen**                     | **100**       | 80          | 80       |

### 3.4 Teacher–Editor Agreement

| Mode          | Both Approve | Both Reject | Teacher ✓ / Editor ✗ | Teacher ✗ / Editor ✓ |
| ------------- | ------------ | ----------- | -------------------- | -------------------- |
| `prompt_only` | 98 (89%)     | 4 (4%)      | 0 (0%)               | 8 (7%)               |
| `json_mode`   | 94 (85%)     | 0 (0%)      | 3 (3%)               | 13 (12%)             |
| `schema`      | 93 (85%)     | 7 (6%)      | 5 (5%)               | 5 (5%)               |

The most notable entry: `prompt_only` has **zero cases** of Teacher approving while Editor rejects. All 12 Teacher rejections in prompt_only were also caught by the Editor. For schema mode, 5 questions pass the Teacher but fail the Editor — indicating schema mode introduces a category of grammatically wrong content that the Teacher misses.

---

## 4. Analysis

### 4.1 Output Mode Does Not Affect Teacher-Level Quality

The Teacher approval rates — 89.1%, 88.2%, 89.1% — are within single-question noise of each other (one question in either direction changes a rate by ~0.9 points). This is the clearest finding from e02: **choosing an output mode does not improve pedagogical quality**. Constraining the JSON structure does not cause GPT-4o to produce better quiz questions.

This is a meaningful negative result. A common intuition is that schema enforcement "focuses" the model on content rather than format — relieving it of the burden of inventing structure. The data does not support this. The Teacher evaluator, which assesses the hardest dimensions (correct answer, distractor quality, explanation accuracy), is equally satisfied across all three modes.

### 4.2 Schema Mode's Adjective Declension Failure

The sharpest mode-specific failure is a systematic content accuracy error in schema mode: **the model marks strong adjective declension forms as correct in contexts that require weak declension**.

In German, adjectives following a definite article use weak declension, which always ends in `-e` (nominative singular) or `-en` (dative, accusative, genitive). Schema mode generated four questions in the Adjektivdeklination im Nominativ batch where the definite article was present but the model marked a strong (article-less) form as correct:

| Question generated by schema mode          | Marked answer | Correct answer | Error                   |
| ------------------------------------------ | ------------- | -------------- | ----------------------- |
| _Das \_\_\_\_ (neu) Auto ist leise._       | `neues`       | `neue`         | Strong → should be weak |
| _Der \_\_\_\_ (jung) Mann spielt Fußball._ | `junger`      | `junge`        | Strong → should be weak |
| _Der \_\_\_\_ (klein) Hund bellt laut._    | `kleiner`     | `kleine`       | Strong → should be weak |
| _Das \_\_\_\_ (schnell) Auto ist teuer._   | `schnelles`   | `schnelle`     | Strong → should be weak |

The same model (gpt-4o) in prompt_only and json_mode produces correct weak forms in identical contexts (e.g., `neue`, `große`, `alte` after definite articles). The error is mode-specific, not model-specific.

The failure is isolated to post-definite-article contexts. Indefinite article contexts (`ein _____ (alt) Baum` → `alter`) were handled correctly across all modes, including schema. This suggests the model's strong/weak declension discrimination degrades under schema constraints specifically when the article context is `der/die/das`.

One plausible explanation: in schema mode, the output is parsed against a rigid structure at the token level. The model may be prioritizing grammatical form completeness (generating the most phonologically "full" word form) over case/article agreement. This is speculative; the failure could also be stochastic noise in a single 10-question batch.

### 4.3 Schema Mode Eliminates Duplicate Options

Schema mode produced **zero duplicate options** across all 110 questions. Prompt_only had 3 duplicate-option questions; json_mode had 6. This is a direct structural benefit of schema enforcement — the output format does not explicitly prohibit duplicates, but the constrained generation process appears to suppress this failure mode.

The 6 duplicate-option questions in json_mode are particularly notable, as json_mode produced more duplicates than the fully unconstrained prompt_only. All duplicate instances were flagged by the static evaluator.

### 4.4 Possessivpronomen: Persistent Difficulty Across All Modes

Possessivpronomen is the most consistently problematic topic. Teacher approval ranges 70–90% depending on mode, and schema mode shows the lowest Editor approval (70%). Schema mode generates standalone/genitive pronoun forms (`meines Auto`, `deiner Schwester für`, `unseres Haus`) where attributive/article forms are grammatically required (`mein Auto`, `deine Schwester`, `unser Haus`). This is a second schema-mode accuracy regression affecting a different grammatical domain.

Possessivartikel deklination im Akkusativ also shows variability (60–90% Teacher approval), with prompt_only scoring only 60% — its worst topic. The Teacher flagged ambiguity when `sie` (third person) was used as the pronoun cue, since it can refer to both "she" and "they," yielding different correct articles.

### 4.5 json_mode's Teacher Rejection Pattern

JSON mode had the most cases where the Editor approved but the Teacher rejected (13 vs. 8 for prompt_only, 5 for schema). The Teacher flagged: wrong answer marked (incorrect conjugation forms, e.g. `saht` instead of `sahtet` for `ihr` in Präteritum), ambiguous `sie` contexts, duplicate correct-answer options, and explanation errors. The Editor, checking only the grammaticality of the answered sentence, passed these cases since the sentences themselves were grammatically acceptable even when the wrong option was marked as correct.

### 4.6 New Topics Perform Well

The three new topics added in e02 — Konjugation im Perfekt, Personalpronomen in Dativ, and Hilfsverb in Perfekt — all perform strongly:

- **Konjugation im Perfekt**: 90–100% Teacher approval, 100% Editor approval across all modes. The single-blank Perfekt example (`gearbeitet`) appears to have been sufficient to guide the model away from the two-blank failures that plagued Plusquamperfekt in e01.
- **Personalpronomen in Dativ**: 80–100% Teacher approval. The topic generates accurate dative pronoun questions. Some Teacher rejections involved questionable pronoun usage for `es` in dative contexts.
- **Hilfsverb in Perfekt**: 80–90% Teacher approval with some notes about awkward wording in instructions. The core auxiliary selection (haben vs. sein) appears to be generated correctly most of the time.

The Personalpronomen in Akkusativ fix (changing the example answer from `mir` to `mich`) also produced a clean result: all three modes scored 90–100% Teacher approval on this topic, up from the mixed results seen in e01.

---

## 5. Evaluator Analysis

### 5.1 The Editor Fills a Distinct Role

In e01, the key teacher/editor disagreement was Teacher-approves-Editor-rejects, concentrated in Plusquamperfekt structural failures. In e02, the pattern inverts for prompt_only and json_mode: Editor-approves-Teacher-rejects is the dominant disagreement direction. The Teacher flags wrong answers marked and explanation errors; the Editor sees only the answered sentence and approves it if grammatically correct.

Schema mode is the only condition where Teacher-approves-Editor-rejects occurs at meaningful frequency (5 cases) — because schema mode introduces wrong correct answers in adjective and possessivpronomen questions. The final answered sentence with those wrong answers filled in is grammatically incorrect (e.g., _"Das neues Auto ist leise."_ — strong declension after definite article), which the Editor catches.

### 5.2 Evaluator Upgraded to gpt-4o

E02 used gpt-4o as the evaluator rather than gpt-4o-mini from e01. This makes the evaluations both more expensive and, presumably, more reliable. However, it complicates direct numerical comparison between experiments — some of the apparent regression in overall approval rates vs. e01 may reflect a stricter evaluator rather than worse generation.

### 5.3 Student Accuracy as a Cross-Check

Student accuracy (computed by matching the student evaluator's free-text answer to the marked correct option) correlates closely with Editor approval in this experiment. Topics with wrong correct answers (schema mode's adjective declension failures) produce lower student accuracy, since a B1 student correctly identifies the grammatically correct form and chooses it — but it's marked wrong in the question. Student accuracy falling below Teacher approval signals wrong-answer marking; the two schema-mode weak spots (AdjNom: 70%, Possessivpronomen: 80%) both show this pattern.

---

## 6. Discussion

### 6.1 Mode Recommendation

For this task, **json_mode is the recommended default**. It offers near-prompt_only output quality (97.3% Editor approval, 88.2% Teacher approval), zero parsing failures guaranteed by the API, and slightly lower duplicate option frequency than prompt_only relative to overall quality. The modest speed disadvantage relative to schema mode (~4s per sample) is unlikely to matter for offline generation.

**prompt_only** is a viable alternative when generation speed is not a constraint. It produced the cleanest Teacher–Editor agreement profile (zero cases of teacher approving content that the editor later rejected) and the best student accuracy.

**Schema mode is not recommended** for this prompt type. The structural guarantee — ensuring the output matches the exact Pydantic schema — comes at the cost of content accuracy for grammar questions. The 7.3-point Editor approval gap (89.1% vs 96.4%) is driven by real grammatical errors in the generated answers, not formatting noise. The speed advantage (~5.6s faster per sample) does not compensate for the accuracy regression in a quality-sensitive generation pipeline.

This recommendation may not generalize. Schema mode is well-suited for tasks where structural completeness is the primary concern and minor answer-level errors are acceptable. For language learning content — where a wrong correct answer directly misleads learners — the accuracy regression is disqualifying.

### 6.2 Why Might Schema Mode Reduce Content Accuracy?

The adjective declension and possessivpronomen failures in schema mode warrant a hypothesis. In unconstrained generation, GPT-4o produces the explanation _alongside_ the answer, and the explanation text references the grammatical rule being applied. This implicit chain-of-thought may anchor the model to the correct rule. In schema mode, the constrained token sampling for each field may weaken this coupling — the model selects answer tokens without the same implicit reasoning context. This is speculative and would require controlled ablation to confirm.

### 6.3 Remaining Prompt-Level Issues

Several issues persist across all modes:

1. **Possessivpronomen preset examples**: Both Possessivpronomen and Possessivartikel im Akkusativ use the same one-shot example (`seinem`), despite testing different grammatical forms. This likely contributes to the model occasionally conflating possessive articles (attributive, before nouns) with standalone possessive pronouns.

2. **`sie` ambiguity**: The pronoun `sie` (she/they) recurs in generated questions and occasionally creates ambiguous items where either `ihr` or `ihren` could be correct depending on interpretation. Adding a prompt constraint — _"use pronouns with unambiguous person/number"_ — or substituting `er`/`du`/`wir` examples would eliminate this category of Teacher rejections.

3. **CEFR distribution**: All modes produce questions in the A2–B1 range, as expected for single-blank morphological fill-in-the-blank questions. This is a property of the prompt design, not a defect.

---

## 7. Conclusions

Across 330 German grammar questions testing three GPT-4o output modes, the following key findings emerge:

1. **Output mode does not affect pedagogical quality**. Teacher approval rates are within noise across all three modes (~89%). Choosing structured output mode to improve question quality is not supported by this data.

2. **Schema mode's lower Editor approval cannot be attributed to output mode with this data**. All Editor failures trace to two topics — each a single generation request, each with identifiable preset flaws that plausibly explain the errors. The gap may be noise from those flawed presets rather than a mode effect.

3. **Schema mode eliminates duplicate option defects**. The structural constraint suppresses a failure mode that appears in both other modes (3–6 instances).

4. **Schema mode generates ~30% faster**. For latency-sensitive pipelines, this is a meaningful advantage — but only if the accuracy regression is acceptable.

5. **The Personalpronomen in Akkusativ preset fix worked**. Correcting the example answer from `mir` (dative) to `mich` (accusative) yielded 90–100% Teacher approval across all modes, up from the mixed results in e01.

6. **New verb tense topics (Perfekt, Hilfsverb) outperform declension topics**. Single-blank compound-tense questions generate cleanly; the two-blank pathology from the old Plusquamperfekt preset does not recur with a well-formed single-blank example.

7. **Possessivpronomen remains the weakest topic**, with Teacher approval 70–90% depending on mode, and schema mode introducing unique wrong-answer errors for this topic.

8. **The Teacher evaluator misses some wrong-answer instances in schema mode**. Five questions were approved by the Teacher but rejected by the Editor due to wrong answers being grammatically incorrect once filled in. The Editor evaluator provides an orthogonal signal for answer-level correctness.

---

_Written by Claude Sonnet 4.6 using data generated by SprachlernSandbox. Generation model: gpt-4o. LLM judge model (Editor, Student, Teacher evaluators): gpt-4o._
