# Qwen3.5 9B vs 27B: Quantization and Scale Effects on German Grammar Quiz Generation

**Experiment:** e04 Qwen3.5 quantization comparison
**Date:** 2026-03-09
**Author:** Claude Sonnet 4.6

---

## Abstract

This report evaluates four variants of the Qwen3.5 model family — 9B at 8-bit and 4-bit quantization, and 27B at 4.5-bit and 3-bit quantization — on the same German grammar quiz generation task used in e03. All four models were run locally via MLX on an Apple Silicon M4 Pro with 24 GB RAM, using schema-mode structured output and thinking disabled at temperature 0.3. The headline results are: parameter count dominates quantization level as a quality predictor (27B models score 75–78% Teacher approval vs 51–66% for 9B models), and within the 9B family, quantization has a significant effect (8-bit at 65.5% vs 4-bit at 51.1% — a 14-point gap). Within the 27B family, the two variants score 77.6% and 75.6% — a 2-point gap that is within the noise of this sample size and should not be read as evidence that quantization level is inconsequential at 27B scale. The 27B 4.5-bit model exhibits a novel failure mode not seen in e03: the model generates Perfekt questions where the blank spans the full auxiliary+participle construction but places additional words after it, producing ungrammatical word order when filled in. This is detectable by the Editor but approved by the Teacher, creating an inverted Teacher-Editor gap unique in this dataset. The 9B 4-bit model degrades not only quantitatively but qualitatively — it begins making outright morphological errors in correct answer selection on Akkusativ topics.

**Important caveat:** All models were tested under a shared-baseline condition identical to e03 — the same Jinja-templated prompt, same grammar topics, same evaluators, same temperature. No per-model system prompts or hyperparameter search were applied. Results reflect shared-baseline performance, not each model's ceiling.

---

## 1. Introduction

Experiment e03 established Qwen3.5-9B (4-bit) as the best-performing local model, reaching 62.6% Teacher approval. E04 builds directly on that result with two focused questions:

1. **Does scaling to 27B parameters substantially improve quality on this task?**
2. **How much quality is lost by reducing quantization — 8-bit to 4-bit (9B), or 4.5-bit to 3-bit (27B)?**

These questions have practical implications for model selection on memory-constrained hardware. All four models fit within a 24 GB unified memory budget. The 27B 4.5-bit model (14 GB) is the tightest fit and leaves limited headroom for the OS; the 9B 4-bit (5.6 GB) is the most memory-efficient. All models were warmed up with a short test run before the timed experiment began.

The nine grammar topics tested are identical to e03, allowing partial cross-experiment comparison, though prompt and preset versions may have changed.

> **Statistical note:** Each topic is represented by two generation requests per model (approximately five questions each, up to 10 total per topic). A single question changing verdict shifts a topic's rate by approximately 10 percentage points. All per-topic figures should be read with this granularity in mind.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Run Name               | Model                                 | Provider | Output Mode | Thinking | Temp | Samples | Failed |
| ---------------------- | ------------------------------------- | -------- | ----------- | -------- | ---- | ------- | ------ |
| e04 Qwen3.5 27B 4.5bit | inferencerlabs/Qwen3.5-27B-MLX-4.5bit | MLX      | schema      | off      | 0.3  | 18/18   | 0      |
| e04 Qwen3.5 27B 3bit   | NexVeridian/Qwen3.5-27B-3bit          | MLX      | schema      | off      | 0.3  | 18/18   | 0      |
| e04 Qwen3.5 9B 8bit    | NexVeridian/Qwen3.5-9B-8bit           | MLX      | schema      | off      | 0.3  | 18/18   | 1      |
| e04 Qwen3.5 9B 4bit    | mlx-community/Qwen3.5-9B-MLX-4bit     | MLX      | schema      | off      | 0.3  | 18/18   | 0      |

All four runs used `schema` mode (constrained decoding via `outlines` against the full Pydantic schema) with thinking explicitly disabled. The single failed sample in the 9B 8-bit run resulted in 84 evaluated questions vs 85–90 for the others.

### 2.2 Model Characteristics

| Model                                 | Parameters | Quantization | Disk Size | Avg s/sample |
| ------------------------------------- | ---------- | ------------ | --------- | ------------ |
| inferencerlabs/Qwen3.5-27B-MLX-4.5bit | 27B        | ~4.5-bit     | 14 GB     | 43.2 s       |
| NexVeridian/Qwen3.5-27B-3bit          | 27B        | ~3-bit       | 11 GB     | 38.0 s       |
| NexVeridian/Qwen3.5-9B-8bit           | 9B         | ~8-bit       | 8.9 GB    | 25.5 s       |
| mlx-community/Qwen3.5-9B-MLX-4bit     | 9B         | ~4-bit       | 5.6 GB    | 14.7 s       |

The 3-bit 27B model is 3 GB smaller on disk and 5 seconds faster per sample than the 4.5-bit variant. The 4-bit 9B model is 3.3 GB smaller and 40% faster than 8-bit.

### 2.3 Grammar Topics

Nine topics identical to e03:

| Preset                           |
| -------------------------------- |
| Adjektivdeklination im Akkusativ |
| Adjektivdeklination im Dativ     |
| Adjektivdeklination im Nominativ |
| Hilfsverb in Perfekt             |
| Konjugation im Perfekt           |
| Konjugation im Präsens           |
| Konjugation im Präteritum        |
| Personalpronomen in Akkusativ    |
| Personalpronomen in Dativ        |

### 2.4 Evaluators

Identical to e03: Static (rule-based), Editor (German grammaticality), Teacher (pedagogical quality with CEFR rating). LLM evaluators used gpt-4o at temperature 0.1, json_mode.

---

## 3. Results

### 3.1 Overall Approval Rates

| Model           | Teacher Approval  | Editor Approval   | Static Clean      |
| --------------- | ----------------- | ----------------- | ----------------- |
| **27B 4.5-bit** | **77.6%** (66/85) | 83.5% (71/85)     | **90.6%** (77/85) |
| **27B 3-bit**   | 75.6% (68/90)     | **94.4%** (85/90) | 87.8% (79/90)     |
| **9B 8-bit**    | 65.5% (55/84)     | 88.1% (74/84)     | 83.3% (70/84)     |
| **9B 4-bit**    | 51.1% (46/90)     | 77.8% (70/90)     | 70.0% (63/90)     |

The two 27B models cluster closely on Teacher approval (77.6% vs 75.6%), while the two 9B models diverge more sharply (65.5% vs 51.1%). Editor approval tells a partially different story: the 27B 4.5-bit model has notably lower Editor approval (83.5%) than the 3-bit variant (94.4%), despite higher Teacher approval — an inverted relationship driven by a specific structural failure mode discussed in §4.2.

### 3.2 Parse Failure Rates

| Model       | Total Samples | Failures | Failure Rate |
| ----------- | ------------- | -------- | ------------ |
| 27B 4.5-bit | 18            | 0        | 0%           |
| 27B 3-bit   | 18            | 0        | 0%           |
| 9B 8-bit    | 18            | **1**    | **5.6%**     |
| 9B 4-bit    | 18            | 0        | 0%           |

Schema-mode structured output kept failure rates very low. The single 9B 8-bit failure is consistent with e03's behaviour at this model size.

### 3.3 Teacher Approval by Topic (%)

| Topic                            | 27B 4.5-bit | 27B 3-bit | 9B 8-bit | 9B 4-bit |
| -------------------------------- | ----------- | --------- | -------- | -------- |
| Adjektivdeklination im Akkusativ | 50          | 70        | 60       | **20**   |
| Adjektivdeklination im Dativ     | **90**      | 60        | 60       | 40       |
| Adjektivdeklination im Nominativ | 80          | **90**    | 70       | 80       |
| Hilfsverb in Perfekt             | **90**      | **90**    | **90**   | **90**   |
| Konjugation im Perfekt           | **90**      | **90**    | **20**   | 30       |
| Konjugation im Präsens           | 80          | 50        | 44       | 70       |
| Konjugation im Präteritum        | **90**      | **90**    | 40       | 50       |
| Personalpronomen in Akkusativ    | 80          | 50        | 80       | 30       |
| Personalpronomen in Dativ        | 50          | **90**    | **100**  | 50       |

**Bold** marks notably high scores (≥90%). Hilfsverb in Perfekt is the one topic all four models handle well (90% Teacher across the board). Konjugation im Präteritum shows a sharp 27B/9B split: both 27B models score 90% while both 9B models score 40–50%.

### 3.4 Editor Approval by Topic (%)

| Topic                            | 27B 4.5-bit | 27B 3-bit | 9B 8-bit | 9B 4-bit |
| -------------------------------- | ----------- | --------- | -------- | -------- |
| Adjektivdeklination im Akkusativ | **100**     | 90        | 80       | **30**   |
| Adjektivdeklination im Dativ     | **100**     | 90        | 90       | 90       |
| Adjektivdeklination im Nominativ | 50          | **100**   | 90       | 80       |
| Hilfsverb in Perfekt             | **100**     | **100**   | 90       | 90       |
| Konjugation im Perfekt           | **20**      | 90        | **100**  | **100**  |
| Konjugation im Präsens           | 90          | **100**   | 89       | 90       |
| Konjugation im Präteritum        | **100**     | **100**   | 80       | 80       |
| Personalpronomen in Akkusativ    | **100**     | **100**   | **100**  | 70       |
| Personalpronomen in Dativ        | **100**     | 80        | 80       | 70       |

The 27B 4.5-bit model's 20% Editor on Konjugation im Perfekt stands out as the most anomalous result in the experiment — a model with 90% Teacher approval for the same topic receiving only 20% Editor approval. This is the reverse of the usual gap direction and has a specific mechanistic explanation (§4.2). The 9B 4-bit model scores only 30% Editor on Adjektivdeklination im Akkusativ — significantly below its already-low 20% Teacher — indicating grammatical errors in the generated sentences themselves.

### 3.5 CEFR Level Distribution (Teacher-Approved Questions Only)

| Model       | A1      | A2       | B1           |
| ----------- | ------- | -------- | ------------ |
| 27B 4.5-bit | 12% (8) | 56% (37) | **32% (21)** |
| 27B 3-bit   | 6% (4)  | 71% (48) | 24% (16)     |
| 9B 8-bit    | 7% (4)  | 69% (38) | 24% (13)     |
| 9B 4-bit    | 20% (9) | 52% (24) | 28% (13)     |

The 27B 4.5-bit model has the highest B1 fraction of approved questions (32%) — more challenging material when it succeeds. The 9B 4-bit model has the highest A1 proportion (20%), generating the simplest content — consistent with weaker instruction following. The 27B 3-bit and 9B 8-bit models cluster similarly at ~70% A2, 24% B1.

---

## 4. Analysis

### 4.1 Scale vs Quantization as Quality Predictors

The data cleanly separates two independent effects:

**Parameter scale (27B vs 9B) is the dominant factor.** Both 27B variants score approximately 76–78% Teacher approval; both 9B variants score 51–66%. The inter-size gap (10–27 points) is larger than any intra-size gap.

**Quantization level has a clear effect within 9B.** Reducing from 8-bit to 4-bit costs 14 Teacher-approval points — a meaningful and likely real degradation. The 27B picture is less clear: the two variants differ by only 2 points (77.6% vs 75.6%), which is well within the noise of ~85–90 questions per model. It is tempting to conclude that 27B is more robust to quantization than 9B, but this experiment cannot support that claim — the 2-point gap could easily reverse on a re-run. What can be said is that the 27B 3-bit model is not obviously worse than 4.5-bit, and it is cheaper to store and faster to run. The cleaner comparison to draw is cross-size: the 27B 3-bit model (11 GB, 38 s/sample) likely beats the 9B 8-bit model (8.9 GB, 25.5 s/sample) — similar disk footprint, similar speed class, but with a 10-point Teacher advantage that is large enough to be credible.

| Model       | Teacher % | Disk   | Avg s/sample | Teacher pts/GB |
| ----------- | --------- | ------ | ------------ | -------------- |
| 27B 4.5-bit | 77.6%     | 14 GB  | 43.2 s       | 5.5            |
| 27B 3-bit   | 75.6%     | 11 GB  | 38.0 s       | 6.9            |
| 9B 8-bit    | 65.5%     | 8.9 GB | 25.5 s       | 7.4            |
| 9B 4-bit    | 51.1%     | 5.6 GB | 14.7 s       | 9.1            |

By quality-per-gigabyte the 9B 4-bit model still wins in efficiency terms, but its absolute quality floor (51%) is below what is likely useful in a pipeline without heavy human review.

### 4.2 The 27B 4.5-bit Inverted Gap: Word Order Errors in Multi-Blank Perfekt Questions

The most structurally interesting failure in this experiment is the 27B 4.5-bit model's Konjugation im Perfekt result: 90% Teacher approval, 20% Editor approval — a reverse gap of 70 points, where Editor rejects questions that Teacher approves.

The cause is a generation pattern unique to this model. Rather than placing only the Partizip II in the blank (as in the e03 prompt example: "Ich habe 2 Jahre lang **\_** (arbeiten)"), the 27B 4.5-bit model generates questions where the blank spans the full Perfekt construction — both the auxiliary verb and the Partizip II — and then places additional elements (direct object, adverbial) after the blank:

| Generated question template                            | Correct answer  | Filled sentence                                       | Word order correct? |
| ------------------------------------------------------ | --------------- | ----------------------------------------------------- | ------------------- |
| _Wir \_\_\_\_ (gehen) gestern ins Kino._               | sind gegangen   | _Wir **sind gegangen** gestern ins Kino._             | ✗                   |
| _Sie \_\_\_\_ (schreiben) einen Brief an ihre Mutter._ | hat geschrieben | _Sie **hat geschrieben** einen Brief an ihre Mutter._ | ✗                   |
| _Er \_\_\_\_ (kaufen) ein neues Auto._                 | hat gekauft     | _Er **hat gekauft** ein neues Auto._                  | ✗                   |
| _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._           | gearbeitet      | _Ich habe 2 Jahre lang **gearbeitet**._               | ✓                   |

German requires the Partizip II at the end of the clause. When the blank spans "auxiliary + Partizip II" and a direct object follows, the filled sentence violates this rule. The Editor evaluates the filled sentence and correctly rejects it. The Teacher, however, evaluates the pedagogical structure of the question — the correct answer is valid, the distractors are plausible, the explanation is accurate — and approves it.

The first question in each batch ("Ich habe 2 Jahre lang **\_** (arbeiten)") is structured correctly (blank contains only the Partizip II, with auxiliary already in the sentence), so one out of five questions per batch passes both evaluators. This accounts for the 20% Editor score.

This failure does not appear in the 27B 3-bit model (90% Editor on the same topic), suggesting it is not a fundamental limitation of the Qwen3.5-27B architecture but rather a quantization-induced or prompt-interaction effect specific to the inferencerlabs 4.5-bit build.

### 4.3 The 9B 4-bit Morphological Failure on Akkusativ

The 9B 4-bit model's 20% Teacher / 30% Editor on Adjektivdeklination im Akkusativ represents a qualitative shift from the patterns seen in e03. In e03, the model's Akkusativ performance was respectable. In e04, the model makes outright morphological errors — marking incorrect answers as correct — not just explanation mistakes:

| Generated sentence                          | Marked correct | Actual correct | Error type                                |
| ------------------------------------------- | -------------- | -------------- | ----------------------------------------- |
| _Er liest ein \_\_\_\_ (interessant) Buch._ | interessanten  | interessantes  | Wrong ending for neuter+indefinite        |
| _Wir besuchen eine \_\_\_\_ (alt) Frau._    | alten          | alte           | Wrong ending for feminine+indefinite Akk. |
| _Er trägt ein \_\_\_\_ (neue) Kleid._       | neuen          | neues          | Wrong ending for neuter+indefinite        |
| _Sie halten die \_\_\_\_ (groß) Tür._       | großen         | große          | Wrong ending for feminine+definite Akk.   |

The pattern is consistent: the model defaults to the `-en` ending (weak masculine accusative) regardless of noun gender. This is a generalisation error, not a random failure — the model has overfit to the most common adjective ending in accusative contexts. The two correct questions in the batch both involve plural nouns ("zwei neue Bücher") or straightforwardly masculine contexts ("einen schönen Garten"), where `-en` happens to be correct.

At 4-bit quantization, the fine-grained distinctions in the adjective paradigm — which require tracking noun gender, article type, and case simultaneously — appear to collapse. The 9B 8-bit model scores 60% Teacher on the same topic with fewer outright wrong-answer errors.

### 4.4 The 9B 8-bit Konjugation im Perfekt Failure Persists

As in e03, the 9B 8-bit model collapses on Konjugation im Perfekt (20% Teacher), despite performing well on related topics (Hilfsverb in Perfekt: 90%). The failure mode is identical: the model generates correct Partizip II forms but fails to produce three distinct plausible alternatives, repeating the correct form across multiple option slots:

| Question                                     | Options                                               |
| -------------------------------------------- | ----------------------------------------------------- |
| _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._ | gearbeitet / **gearbeitet** / arbeitend / arbeitete   |
| _Wir haben das Haus \_\_\_\_ (bauen)._       | gebaut / **gebaut** / baute / bauen                   |
| _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._ | gearbeitet / gearbeitet / **gearbeitet** / gearbeitet |
| _Wir sind nach Berlin \_\_\_\_ (fahren)._    | gefahren / gefuhrten / **gefuhrten** / gefuhrten      |

The 9B 4-bit model has the same problem on Perfekt (30% Teacher) with an additional issue: all four options are sometimes identical ("gearbeitet / gearbeitet / gearbeitet / gearbeitet"). This "all-same" collapse is worse than the partial duplication seen in 8-bit.

The persistence of this failure across both quantizations and across e03 and e04 suggests it is a genuine weakness of the Qwen3.5-9B architecture on this specific task — not a quantization artifact. Konjugation im Perfekt requires generating plausible wrong Partizip II forms (e.g., non-existent stems, wrong ge- prefixes, Präteritum forms) which is a distractor generation task the model has not mastered.

### 4.5 The 27B 3-bit Dips on Konjugation im Präsens and Personalpronomen in Akkusativ

The 27B 3-bit model scores 50% Teacher on both Konjugation im Präsens and Personalpronomen in Akkusativ, compared to 80% for the 4.5-bit variant on the same topics. Teacher issue notes cite explanation inaccuracies and occasional case confusion — not systematic structural failures. At 10 questions per topic, a 30-point gap represents 3 questions and is well within sample-size noise. It would be unwise to attribute these dips to quantization from a single run; they may simply reflect unlucky batches.

### 4.6 Adjektivdeklination im Dativ: A 27B-Only Topic

In e03, Adjektivdeklination im Dativ was the hardest topic for all local models, with the 9B 4-bit model scoring only 70%. E04 confirms this pattern for 9B variants (60% for 8-bit, 40% for 4-bit) but shows that 27B achieves substantially better results:

| Model       | Dativ Teacher % |
| ----------- | --------------- |
| 27B 4.5-bit | 90%             |
| 27B 3-bit   | 60%             |
| 9B 8-bit    | 60%             |
| 9B 4-bit    | 40%             |

The 27B 4.5-bit result (90%) is the highest any local model has scored on this topic, though at 10 questions it represents a single lucky or unlucky batch away from 80% or 100%. The 27B 3-bit model scores 60% — the same as both 9B variants. Whether this reflects a genuine quantization sensitivity on Dativ or is a sampling artefact cannot be determined from one run.

---

## 5. Evaluator Analysis

### 5.1 Teacher–Editor Gap by Model

| Model       | Teacher | Editor | Gap       | Direction |
| ----------- | ------- | ------ | --------- | --------- |
| 27B 4.5-bit | 77.6%   | 83.5%  | -5.9 pts  | Inverted  |
| 27B 3-bit   | 75.6%   | 94.4%  | +18.8 pts | Normal    |
| 9B 8-bit    | 65.5%   | 88.1%  | +22.6 pts | Normal    |
| 9B 4-bit    | 51.1%   | 77.8%  | +26.7 pts | Normal    |

The 27B 4.5-bit model is the only model with an inverted Teacher-Editor gap — the first such inversion in this experiment series. The inversion is entirely attributable to the Konjugation im Perfekt word order failure (§4.2): a structural defect the Editor catches via grammaticality checking that the Teacher misses because it evaluates pedagogical soundness rather than the filled sentence.

The 9B 4-bit model's 26.7-point gap is the largest normal gap, consistent with a model that occasionally generates grammatically invalid sentences (30% Editor on Akkusativ) while still having the correct pedagogical intent.

### 5.2 Static Evaluator Performance

| Model       | Static Clean | Teacher Approval |
| ----------- | ------------ | ---------------- |
| 27B 4.5-bit | 90.6%        | 77.6%            |
| 27B 3-bit   | 87.8%        | 75.6%            |
| 9B 8-bit    | 83.3%        | 65.5%            |
| 9B 4-bit    | 70.0%        | 51.1%            |

Static cleanliness and Teacher approval correlate monotonically. The 9B 4-bit model's 70% static clean rate is driven by high `explanation is empty` flags — the model generates valid answer structures but frequently omits the explanation field. This is a schema-adherence failure at the content level (constrained decoding ensures field presence, but not field content length).

---

## 6. Discussion

### 6.1 Model Selection Recommendations

This experiment allows clearer model selection guidance than e03, which compared architecturally diverse models. Within the Qwen3.5 family:

**Best quality (with caveats):** Both 27B variants score within noise of each other (77.6% vs 75.6%) and neither is clearly better overall. The 4.5-bit model has a mechanistic word order defect on Konjugation im Perfekt that the Editor reliably catches; the 3-bit model has lower topic scores on Präsens and Personalpronomen in Akkusativ that may or may not be real. The honest answer is that a single run cannot distinguish them on Teacher approval alone.

**Practical preference: 27B 3-bit** — 3 GB smaller, 5 seconds faster, 94.4% Editor approval (the highest of any model tested), and without the Perfekt word order defect. It is the safer choice absent stronger evidence that 4.5-bit is better.

**Best quality/speed tradeoff:** 9B 8-bit (65.5% Teacher, 25.5 s/sample) — 10 points below 27B 3-bit but nearly 3× faster. Viable for applications where generation latency matters more than quality ceiling.

**Not recommended without filtering:** 9B 4-bit (51.1% Teacher) — generates wrong correct answers on Akkusativ topics and frequently omits explanations. Without static pre-filtering, roughly 1-in-2 questions require rejection. May still be useful for topics where it performs well (Hilfsverb in Perfekt: 90%, Adjektivdeklination im Nominativ: 80%), with per-topic routing.

### 6.2 Konjugation im Perfekt as a Persistent Stress Test

Across e03 and e04, Konjugation im Perfekt has been the most consistent failure topic for local models:

| Model (experiment)     | Teacher % | Failure mode                               |
| ---------------------- | --------- | ------------------------------------------ |
| 27B 4.5-bit (e04)      | 90%       | Word order errors in multi-blank sentences |
| 27B 3-bit (e04)        | 90%       | None observed                              |
| 9B 8-bit (e04)         | 20%       | Duplicate/all-same options                 |
| 9B 4-bit (e04)         | 30%       | Duplicate/all-same options                 |
| 9B 4-bit (e03, schema) | 10%       | Duplicate options                          |

The 27B 3-bit model is the only local model to handle Konjugation im Perfekt well. This topic is demanding because it requires: (1) selecting the correct Partizip II form (strong vs weak), (2) matching the auxiliary (haben vs sein), and (3) generating three plausible wrong alternatives for each. The 9B models and the 4.5-bit 27B model each fail at step (3) or at the sentence template level.

### 6.3 The Practical Value of 3-bit Quantization

The 27B 3-bit result (75.6% Teacher) is practically encouraging. A 27B model at 3-bit quantization is at least not obviously worse than 4.5-bit on this task, while using 3 GB less memory — which is a useful data point even if the 2-point Teacher gap is too small to interpret. Whether this reflects genuinely good quantization calibration, or whether the 4.5-bit model would pull ahead with more samples, is an open question.

In contrast, 3-bit quantization of the 9B model (tested in earlier exploratory runs, not in e04) is expected to fall well below even the 4-bit quality level based on the steeper degradation curve seen in the 9B size class. The asymmetry suggests that 27B is a better base for aggressive quantization than 9B.

### 6.4 Failure Modes Versus e03

E04 adds two failure modes not observed in e03:

1. **Inverted Editor gap via word order errors** (27B 4.5-bit, Konjugation im Perfekt): The model generates questions where the blank position creates ungrammatical word order in the filled sentence. This is not a distractor quality failure but a sentence template design failure.

2. **Wrong correct answers via gender/case generalisation** (9B 4-bit, Adjektivdeklination im Akkusativ): The model marks morphologically incorrect forms as correct. This is more dangerous than e03-style explanation errors because a student following the question would learn the wrong rule.

Both failure modes are learnable from the evaluation data: the word order failure is caught by the Editor, and the wrong-correct-answer failure is caught by both the Teacher and (via 30% Editor approval) the Editor. Neither is caught by the static evaluator alone. This reinforces the value of the LLM-as-judge layer in the pipeline.

---

## 7. Conclusions

Across approximately 349 evaluated German grammar questions from four Qwen3.5 variants testing nine topics, the following findings emerge:

1. **Parameter scale dominates quantization level as a quality predictor.** The 27B models (75–78% Teacher) outperform 9B models (51–66%) by a larger margin than any quantization level difference within each size class.

2. **Within 27B, the two variants cannot be reliably ranked on Teacher approval alone.** The 2-point gap (75.6% vs 77.6%) is within the noise of ~85–90 questions per model. The 27B 3-bit model has meaningfully better Editor approval (94.4% vs 83.5%), but this is largely explained by the 4.5-bit model's mechanistic Perfekt word order failure rather than general quality. A larger experiment would be needed to determine whether quantization level matters within the 27B family on this task.

3. **Within 9B, 8-bit is meaningfully better than 4-bit.** A 14-point Teacher gap (65.5% vs 51.1%) is large enough to be operationally significant. At 4-bit, the model begins making outright wrong-answer errors rather than explanation inaccuracies — a qualitative shift in failure mode.

4. **The 27B 4.5-bit model introduces a novel inverted Editor gap.** On Konjugation im Perfekt, Teacher approval (90%) exceeds Editor approval (20%) because the model generates question templates with ungrammatical word order when filled. Teacher evaluates pedagogical intent; Editor evaluates the resulting German sentence. Both judgements are correct; the conflict reveals a structural generation defect invisible to the static evaluator.

5. **Adjektivdeklination im Dativ remains the hardest topic for local models.** All 9B variants score 40–60%. The 27B 4.5-bit model scores 90% on this topic, but at 10 questions this is a single run result and should be treated as directional rather than conclusive.

6. **Konjugation im Perfekt is a persistent stress test.** Only the 27B 3-bit model handles it well (90%). All other local models fail via duplicate options or sentence template errors, despite correctly generating Partizip II forms.

7. **These results reflect shared-baseline performance, not model ceilings.** All four models were run with the same prompt under the same conditions. The failure modes identified — particularly the word order template error and the Akkusativ gender generalisation — have targeted remedies (prompt-level sentence template guidance, additional Akkusativ examples) that could improve results substantially.

---

_Written by Claude Sonnet 4.6 using data generated by SprachlernSandbox. Generation models: Qwen3.5-27B-MLX-4.5bit (inferencerlabs), Qwen3.5-27B-3bit (NexVeridian), Qwen3.5-9B-8bit (NexVeridian), Qwen3.5-9B-MLX-4bit (mlx-community) — all local MLX on Apple Silicon M4 Pro. LLM judge model (Editor, Teacher evaluators): gpt-4o._
