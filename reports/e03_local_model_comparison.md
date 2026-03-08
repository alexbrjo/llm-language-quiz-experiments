# Local MLX Models vs. GPT-4o for German Grammar Quiz Generation

**Experiment:** e03 local model comparison
**Date:** 2026-03-08
**Author:** Claude Sonnet 4.6

---

## Abstract

This report evaluates five quantised local models — EuroLLM-22B, Llama-3.2-3B, Qwen2.5-7B, Qwen3.5-9B, and SmolLM3-3B, all run via MLX on Apple Silicon — against a GPT-4o baseline for German grammar quiz generation. Nine grammar topics were tested, each with two generation batches of approximately five questions (≈90 questions per model, 540 total). Three LLM-as-judge evaluators assessed each question. The headline result is a large quality gap: GPT-4o achieves 87.8% Teacher approval and 98.9% Editor approval; the best local model (Qwen3.5-9B at 4-bit) reaches 62.6% and 85.7% respectively. Below Qwen3.5 the quality deteriorates sharply, with SmolLM3-3B effectively unusable (1.4% Teacher approval, 4 parse failures out of 18 samples). More instructive than the aggregate numbers are the failure modes: each weaker model exhibits a distinct and consistent pattern of breakdown — all-identical options, task confusion, case misidentification, and degenerate repetition — that reveals different categories of instruction-following capability. Parameter count is not a reliable predictor: EuroLLM-22B (22B parameters, 52 seconds per sample) scores 24.4% Teacher approval, worse than Qwen3.5-9B (9B parameters, 16 seconds per sample) at 62.6%.

**Important caveat:** All models were tested with the same prompt — a Jinja-templated instruction set that included additional guidance designed to help smaller models follow the task structure — without further model-specific tuning. This is a shared-baseline experiment, not an optimized comparison. No per-model system prompts, hyperparameter search, or fine-tuning were performed. The scores reflect what each model produces under a common, reasonably well-specified prompt; they do not reflect the ceiling achievable through model-specific optimization.

---

## 1. Introduction

Experiments e01 and e02 established a GPT-4o baseline for the German grammar quiz generation pipeline and identified that output mode has no meaningful effect on pedagogical quality. E03 shifts focus: can capable local models replace the API call? The motivation is latency control, offline operation, and cost elimination. All five local models are 4-bit quantised MLX variants run on an Apple Silicon Mac and were warmed up before the timed experiment began. GPT-4o is included as a held-out control at the same temperature (0.3) and output mode (json_mode) as in prior experiments.

The 9 grammar topics tested are a subset of the e02 set, dropping Possessivartikel deklination im Akkusativ and Possessivpronomen (the two topics with the most persistent e02 prompt defects) and retaining the nine that showed consistent behaviour in e02.

**Scope and limitations.** This experiment measures _shared-baseline_ performance: all models were run with the same prompt — a Jinja-templated instruction set that already includes additional guidance aimed at helping smaller models follow the task format — without further per-model modification. No model-specific system prompts, additional few-shot examples, or hyperparameter search were applied. No fine-tuning was performed. The experiment answers the question: _what does each model produce under a common, reasonably well-specified prompt?_ It does not answer what each model could produce with model-specific prompt engineering, output mode tuning, or fine-tuning on the task. The results are a practical shared-baseline, not a ceiling on what is achievable.

> **Statistical note:** Each topic is represented by two generation requests per model (approximately 5 questions each, 10 total per topic). A single question changing verdict shifts a topic's approval rate by 10 percentage points. All per-topic figures should be read with this granularity in mind. Sample sizes are small; findings should be treated as directional rather than conclusive.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Run Name           | Model                                            | Provider   | Output Mode | Temp | Samples | Failed |
| ------------------ | ------------------------------------------------ | ---------- | ----------- | ---- | ------- | ------ |
| e03 control gpt-4o | gpt-4o                                           | OpenAI API | json_mode   | 0.3  | 18/18   | 0      |
| e03 EuroLLM-22B    | mlx-community/EuroLLM-22B-Instruct-2512-mlx-4bit | MLX        | prompt_only | 0.3  | 18/18   | 0      |
| e03 Qwen3.5-9B     | mlx-community/Qwen3.5-9B-MLX-4bit                | MLX        | schema      | 0.3  | 18/18   | 0      |
| e03 Qwen2.5-7B     | mlx-community/Qwen2.5-7B-Instruct-4bit           | MLX        | prompt_only | 0.3  | 17/18   | 1      |
| e03 Llama-3.2-3B   | mlx-community/Llama-3.2-3B-Instruct-4bit         | MLX        | prompt_only | 0.3  | 18/18   | 0      |
| e03 SmolLM3-3B     | mlx-community/SmolLM3-3B-4bit                    | MLX        | prompt_only | 0.3  | 14/18   | 4      |

Note: Qwen3.5-9B used `schema` mode (structured output with the full Pydantic schema) while all other local models used `prompt_only`. The control gpt-4o used `json_mode` consistent with e01/e02.

### 2.2 Grammar Topics

Nine topics were tested:

| Preset                           | Example Question                                        | Example Answer |
| -------------------------------- | ------------------------------------------------------- | -------------- |
| Adjektivdeklination im Akkusativ | _Es gibt einen \_\_\_\_ (klein) Ort._                   | kleinen        |
| Adjektivdeklination im Dativ     | _Ich legte das Telefon auf den \_\_\_\_ (alt) Tisch._   | alten          |
| Adjektivdeklination im Nominativ | _Das ist eine \_\_\_\_ (klein) Stadt._                  | kleine         |
| Hilfsverb in Perfekt             | _Er \_\_\_ (haben oder sein) nach Österreich gefahren._ | ist            |
| Konjugation im Perfekt           | _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._            | gearbeitet     |
| Konjugation im Präsens           | _\_\_\_\_ (sprechen) du Deutsch?_                       | Sprichst       |
| Konjugation im Präteritum        | _Er \_\_\_ (gehe) ins Kino._                            | ging           |
| Personalpronomen in Akkusativ    | _Kannst du \_\_\_ (ich) anrufen?_                       | mich           |
| Personalpronomen in Dativ        | _Kannst du \_\_\_ (ich) bitte helfen?_                  | mir            |

### 2.3 Model Characteristics

| Model                     | Developer          | Released  | Training cutoff | Parameters  | Disk (4-bit) | Avg s/sample |
| ------------------------- | ------------------ | --------- | --------------- | ----------- | ------------ | ------------ |
| gpt-4o                    | OpenAI             | May 2024  | Apr 2024        | undisclosed | API only     | **5.5 s**    |
| Llama-3.2-3B-Instruct     | Meta               | Sep 2024  | Dec 2023        | 3.2B        | 1.7 GB       | 7.0 s        |
| Qwen2.5-7B-Instruct       | Alibaba            | Sep 2024  | ~late 2023      | 7.6B        | 4.0 GB       | 14.3 s       |
| SmolLM3-3B                | HuggingFace        | Jul 2025  | ~Jun 2025       | 3.0B        | 1.6 GB       | 6.9 s        |
| EuroLLM-22B-Instruct-2512 | utter-project (EU) | Dec 2025  | not published   | 22.6B       | **12 GB**    | 52.4 s       |
| Qwen3.5-9B                | Alibaba            | Mar 2026¹ | ~late 2024      | 9.0B        | 5.6 GB       | 15.7 s       |

> ¹ Qwen3.5-9B was released on March 2, 2026 — six days before this experiment ran. EuroLLM's "2512" suffix is a YYMM date stamp (December 2025).

The disk sizes above are for 4-bit MLX quantised versions downloaded from `mlx-community` on Hugging Face. The effective bits-per-weight is roughly 4.5–5 including non-quantised layers. At full precision, models would be 6–8× larger.

### 2.4 Evaluators

The same four evaluators from e02 were used:

- **Static:** Rule-based checks — option count, single correct answer, option uniqueness, non-empty explanation
- **Editor:** German language editor assessing grammatical correctness of the answer-filled sentence
- **Student:** Simulated B1 learner attempting to answer the question
- **Teacher:** Expert auditing clarity, correctness, distractor quality, explanation accuracy, and CEFR level

Evaluation used **gpt-4o** at temperature 0.1 in `json_mode`, consistent with e02.

---

## 3. Results

### 3.1 Overall Approval Rates

| Model                | Teacher Approval  | Editor Approval   | Static Clean      |
| -------------------- | ----------------- | ----------------- | ----------------- |
| **gpt-4o (control)** | **87.8%** (79/90) | **98.9%** (89/90) | **93.3%** (84/90) |
| Qwen3.5-9B           | 62.6% (57/91)     | 85.7% (78/91)     | 72.5% (66/91)     |
| Qwen2.5-7B           | 42.4% (36/85)     | 63.5% (54/85)     | 77.6% (66/85)     |
| EuroLLM-22B          | 24.4% (22/90)     | 86.7% (78/90)     | 46.7% (42/90)     |
| Llama-3.2-3B         | 17.8% (16/90)     | 67.8% (61/90)     | 67.8% (61/90)     |
| SmolLM3-3B           | 1.4% (1/70)       | 25.7% (18/70)     | 10.0% (7/70)      |

The most striking entry is EuroLLM-22B: 86.7% Editor approval alongside 24.4% Teacher approval — a 62-point gap. This divergence has a specific structural cause (see §4.2). In all other models Editor and Teacher track more closely; a high Editor-low Teacher gap signals that sentences are grammatically valid but questions are pedagogically broken.

### 3.2 Parse Failure Rates

| Model        | Total Samples | Failures | Failure Rate |
| ------------ | ------------- | -------- | ------------ |
| gpt-4o       | 18            | 0        | 0%           |
| EuroLLM-22B  | 18            | 0        | 0%           |
| Qwen3.5-9B   | 18            | 0        | 0%           |
| Qwen2.5-7B   | 18            | 1        | 5.6%         |
| Llama-3.2-3B | 18            | 0        | 0%           |
| SmolLM3-3B   | 18            | **4**    | **22.2%**    |

SmolLM3-3B's 22% sample failure rate is operationally significant — more than 1-in-5 generation requests produce unparseable output. The failures are caused by degenerate repetition loops (see §4.6).

### 3.3 Teacher Approval by Topic (%)

| Topic                            | EuroLLM | Llama | Qwen2.5 | Qwen3.5 | SmolLM3 | gpt-4o  |
| -------------------------------- | ------- | ----- | ------- | ------- | ------- | ------- |
| Adjektivdeklination im Akkusativ | 50      | 10    | **100** | 60      | 0       | **100** |
| **Adjektivdeklination im Dativ** | **0**   | **0** | **0**   | 70      | **0**   | **100** |
| Adjektivdeklination im Nominativ | **100** | 10    | 30      | 80      | 0       | 90      |
| Hilfsverb in Perfekt             | **0**   | **0** | 10      | 80      | **0**   | 90      |
| Konjugation im Perfekt           | **0**   | 40    | 80      | **10**  | **0**   | 60      |
| Konjugation im Präsens           | **0**   | 10    | **0**   | 60      | **0**   | 90      |
| Konjugation im Präteritum        | 10      | 40    | 40      | 50      | —       | 70      |
| Personalpronomen in Akkusativ    | **0**   | 30    | 40      | 73      | **0**   | **100** |
| Personalpronomen in Dativ        | 60      | 20    | 80      | 80      | 10      | 90      |

Bold entries mark notable outliers (unexpectedly high or low). SmolLM3 Präteritum is omitted because the two batches both failed to parse.

Adjektivdeklination im Dativ is the hardest topic: only Qwen3.5 (70%) and gpt-4o (100%) pass it with any regularity. All three smaller models score 0%. This is not coincidence — it is a consistent and mechanistically distinct failure for each model (see §4).

Konjugation im Perfekt is anomalous for Qwen3.5-9B (10% Teacher, 100% Editor). This is explained in §4.4.

### 3.4 Editor Approval by Topic (%)

| Topic                            | EuroLLM | Llama | Qwen2.5 | Qwen3.5 | SmolLM3 | gpt-4o  |
| -------------------------------- | ------- | ----- | ------- | ------- | ------- | ------- |
| Adjektivdeklination im Akkusativ | 80      | 60    | 60      | 80      | 0       | **100** |
| Adjektivdeklination im Dativ     | 70      | 70    | 60      | **100** | 10      | **100** |
| Adjektivdeklination im Nominativ | **100** | 80    | 60      | 80      | 10      | **100** |
| Hilfsverb in Perfekt             | 60      | 70    | 40      | 90      | 0       | **100** |
| Konjugation im Perfekt           | 90      | 60    | 80      | **100** | 60      | **100** |
| Konjugation im Präsens           | **100** | 90    | 30      | 70      | 30      | **100** |
| Konjugation im Präteritum        | **100** | 60    | 80      | 70      | —       | **100** |
| Personalpronomen in Akkusativ    | 90      | 50    | 80      | 91      | 40      | 90      |
| Personalpronomen in Dativ        | 90      | 70    | 90      | 90      | 30      | **100** |

EuroLLM-22B achieves 100% Editor on Konjugation im Präteritum and Konjugation im Präsens — perfect grammaticality — while scoring 10% and 0% Teacher approval respectively. The sentences are correct; the questions are not.

### 3.5 CEFR Level Distribution (Approved Questions Only)

| Model        | A1      | A2       | B1           |
| ------------ | ------- | -------- | ------------ |
| gpt-4o       | 8% (6)  | 57% (45) | 35% (28)     |
| Qwen3.5-9B   | 11% (6) | 47% (27) | **42% (24)** |
| Qwen2.5-7B   | 3% (1)  | 72% (26) | 25% (9)      |
| EuroLLM-22B  | 14% (3) | 82% (18) | 5% (1)       |
| Llama-3.2-3B | 13% (2) | 63% (10) | 25% (4)      |
| SmolLM3-3B   | 0%      | 100% (1) | 0%           |

Qwen3.5-9B's approved questions skew notably toward B1 (42%) — the highest B1 fraction of any model, including gpt-4o. This is a meaningful finding: among questions that pass quality review, Qwen3.5 generates the most challenging material. The other local models cluster heavily at A2.

---

## 4. Analysis

### 4.1 The Quality Tier Structure

The six models fall into three distinct tiers based on Teacher approval:

- **Tier 1 (viable):** gpt-4o (87.8%)
- **Tier 2 (partially viable):** Qwen3.5-9B (62.6%), Qwen2.5-7B (42.4%)
- **Tier 3 (not viable):** EuroLLM-22B (24.4%), Llama-3.2-3B (17.8%), SmolLM3-3B (1.4%)

Tier 2 models produce useful output for some topics but fail badly on others — particularly on the declension topics (Dativ, Nominativ) and the compound-tense topics (Präsens, Hilfsverb). For a production pipeline, selective use of Tier 2 models on easier topics (Personalpronomen, Präteritum) while routing harder topics to gpt-4o is theoretically possible, but this is speculative given the sample size.

### 4.2 EuroLLM-22B: The All-Identical Options Failure

The most startling single-model failure is EuroLLM-22B's behaviour on Adjektivdeklination im Dativ: the model generates all four answer choices as the same word. Every question in the batch has the structure:

| Content                                                | Options                           | Correct |
| ------------------------------------------------------ | --------------------------------- | ------- |
| _Ich legte das Telefon auf den \_\_\_\_ (alt) Tisch._  | alten / alten / alten / alten     | alten   |
| _Sie gab dem \_\_\_\_ (groß) Kind ein Geschenk._       | großen / großen / großen / großen | großen  |
| _Er schenkte dem \_\_\_\_ (neu) Auto einen Aufkleber._ | neuen / neuen / neuen / neuen     | neuen   |

The correct adjective form is always right, but the question is trivially answerable regardless — any selection is correct. The static evaluator catches all of these (duplicate option issues on 10 out of 10 Dativ questions). The Editor still passes 70% because checking only the correct-answer-filled sentence ("Ich legte das Telefon auf den alten Tisch.") finds no grammatical error. The Teacher rejects 100% because no learning can occur from a question with four identical options.

This explains most of the EuroLLM Teacher-Editor gap. The model appears to "know" the right adjective form but cannot generate distractors — it collapses to producing the correct answer in all four option slots.

A second Dativ defect compounds the problem: many EuroLLM Dativ sentences use accusative prepositions instead of dative ones. _"Sie bewunderte das \_\_\_\_ (alt) Gemälde"_ uses _bewundern_ (accusative), not a dative-governing verb. The Teacher flags this even in the few questions that escape the duplicate-option trap.

Paradoxically, EuroLLM-22B achieves 100% Teacher approval on Adjektivdeklination im Nominativ — the same grammatical domain, just a different case. The collapse is case-specific, not a general limitation on German adjective declension.

### 4.3 Llama-3.2-3B: Task Substitution

Llama-3.2-3B misunderstands the task at a fundamental level for adjective declension topics. Instead of generating fill-in-the-blank questions that test a specific morphological form, the model generates predicate-adjective questions where no declension is required:

| Generated question                          | Marked answer | What it actually tests                         |
| ------------------------------------------- | ------------- | ---------------------------------------------- |
| _Die Frau ist \_\_\_\_ (hoch) und singt._   | hoch          | vocabulary (predicate adjective, undeclined)   |
| _Der Mann ist \_\_\_\_ (arm) und arbeitet._ | arm           | vocabulary (predicate adjective, undeclined)   |
| _Sie haben einen \_\_\_\_ (bunt) Ball._     | bunter        | wrong strong declension (was: klein → kleiner) |
| _Es gibt einen \_\_\_\_ (klein) Ort._       | groøÖ         | garbled Unicode characters                     |

The Teacher rejects these because they do not test the stated topic. The Editor is more permissive — "Die Frau ist hoch und singt" is grammatically acceptable — producing the characteristic Editor-yes / Teacher-no disagreement pattern for this model.

The garbled character output ("groøÖ") in at least one sample suggests the model is also generating token-level artifacts, likely from mishandled multi-byte Unicode in the MLX inference stack.

### 4.4 Qwen3.5-9B: Near-Miss on Konjugation im Perfekt

Qwen3.5-9B is the only local model with a plausible production use case, but its Konjugation im Perfekt performance is anomalous: 10% Teacher, 100% Editor. The failure mode is identical to EuroLLM's Dativ problem: the model generates 3–4 duplicate options, all containing the correct past participle:

| Content                                      | Options                                           |
| -------------------------------------------- | ------------------------------------------------- |
| _Ich habe 2 Jahre lang \_\_\_\_ (arbeiten)._ | gearbeitet / gearbeitet / gearbeitet / gearbeitet |
| _Wir sind nach Hause \_\_\_\_ (gehen)._      | gegangen / gegangen / ging / gehen                |
| _Er hat einen Brief \_\_\_\_ (schreiben)._   | geschrieben / schrieb / schreiben / geschrieben   |

The static evaluator caught 9 of the 10 questions in this topic for duplicate option issues. The Teacher additionally flagged missing explanations on several questions — Qwen3.5 in schema mode appears to sometimes omit the explanation field entirely (3 "explanation is empty" static issues logged).

For all other topics, Qwen3.5-9B's duplicate rate is low. Konjugation im Perfekt appears to be a specific degenerate case where the model can produce the correct Partizip II form but cannot generate three plausible wrong alternatives, so it fills the remaining slots with the correct answer.

### 4.5 Qwen2.5-7B: Systematic Case Confusion

Qwen2.5-7B achieves 100% Teacher approval on Adjektivdeklination im Akkusativ — its best topic and one of the few perfect scores in the experiment outside gpt-4o. But it scores 0% on Adjektivdeklination im Dativ. The failure is not random — the Teacher consistently identifies the same error: the model generates accusative-case sentence structures when testing the dative case.

A dative context requires prepositions or verbs that govern dative (e.g., _auf dem Tisch_, _mit dem Hund_, _geben + Dativobjekt_). Qwen2.5-7B generates sentences with _auf den_ (accusative), _in den_ (accusative direction), or _sah_ (_sehen_, accusative). It then correctly applies the adjective endings for the case it actually generated — accusative — and marks the accusative form as the correct answer, while the instruction labels the topic as Dativ. This produces a question that is internally consistent but topically wrong.

This finding suggests Qwen2.5-7B has adequate adjective morphology knowledge but unreliable case-preposition knowledge. The same model that marks `kleinen` correctly after `einen` (masculine accusative) cannot reliably construct a sentence where the preposition governs dative.

### 4.6 SmolLM3-3B: Degenerate Repetition

SmolLM3-3B's most distinctive failure mode is infinite-loop generation in explanation text. Two of its four parse failures contain the same sentence repeated dozens of times until the generation hits the token limit:

> _"Da der Akkusativ hier fehlt, wird 'klein' als Adjektiv im Dativ verwendet, der dann zu 'kleinem' wird, wenn er im Dativ steht. Da der Akkusativ hier fehlt, wird 'klein' als Adjektiv im Dativ verwendet..."_ [× 50+ repetitions]

The raw response exceeds the context limit and the JSON is truncated, producing "Could not extract question set from LLM response". Even in successfully parsed samples, SmolLM3 shows the same all-identical-options pattern as EuroLLM but more severely: options such as ["schlank", "schlank", "schlank", "schlank"] appear across topics, not just in Dativ. The model's sole Teacher-approved question — a Personalpronomen in Dativ question — appears to be a near-verbatim copy of the one-shot example in the prompt (_"Kannst du mir bitte helfen?"_). This raises the question of whether SmolLM3 is capable of task-relevant generation at all, or is simply retrieving from its context window.

### 4.7 Neither Parameter Count, Model Age, nor Training Recency Predict Quality

The ranking by Teacher approval (Qwen3.5-9B > Qwen2.5-7B > EuroLLM-22B > Llama-3.2-3B > SmolLM3-3B) violates every intuitive proxy for model capability:

**Parameter count:** EuroLLM-22B at 22B parameters scores 24.4% — below Qwen3.5-9B at 9B (62.6%) and Qwen2.5-7B at 7B (42.4%). The largest local model is the worst performer by Teacher approval. It is also 3.3× slower per sample than Qwen3.5-9B and consumes 2.1× the disk space (12 GB vs 5.6 GB).

**Model recency:** Sorting by release date:

| Model        | Released | Months old at experiment | Teacher % |
| ------------ | -------- | ------------------------ | --------- |
| Qwen3.5-9B   | Mar 2026 | **<1**                   | **62.6%** |
| EuroLLM-22B  | Dec 2025 | 3                        | 24.4%     |
| SmolLM3-3B   | Jul 2025 | 8                        | 1.4%      |
| Llama-3.2-3B | Sep 2024 | 18                       | 17.8%     |
| Qwen2.5-7B   | Sep 2024 | 18                       | 42.4%     |

The newest model (Qwen3.5-9B, released six days before the experiment) is the best local performer. But the second-newest (EuroLLM-22B) is the worst local performer. SmolLM3-3B, released eight months prior, is effectively unusable despite being the most recently trained model by knowledge cutoff (~June 2025). Model age alone explains nothing.

**Training data recency:** SmolLM3-3B has the most recent training cutoff of any model in the experiment (~June 2025), yet it is the worst performer. Llama-3.2-3B's training data cuts off in December 2023 — over two years before this experiment — yet it outperforms SmolLM3 by a factor of 13 on Teacher approval (17.8% vs 1.4%). The amount of recent data in the training corpus does not translate to instruction-following capability for structured generation tasks.

**Disk size vs. quality:**

| Model        | Disk (4-bit) | Teacher % | Quality / GB   |
| ------------ | ------------ | --------- | -------------- |
| gpt-4o       | API          | 87.8%     | N/A            |
| Qwen3.5-9B   | 5.6 GB       | 62.6%     | 11.2 pts/GB    |
| Qwen2.5-7B   | 4.0 GB       | 42.4%     | 10.6 pts/GB    |
| Llama-3.2-3B | 1.7 GB       | 17.8%     | 10.5 pts/GB    |
| SmolLM3-3B   | 1.6 GB       | 1.4%      | 0.9 pts/GB     |
| EuroLLM-22B  | 12 GB        | 24.4%     | **2.0 pts/GB** |

Qwen3.5-9B and Qwen2.5-7B deliver roughly equivalent quality-per-gigabyte (~11 pts/GB). EuroLLM-22B at 2.0 pts/GB is the worst ratio of any model; it costs more disk space and more inference time per unit of quality than any alternative. SmolLM3-3B at 0.9 pts/GB is even lower in absolute terms but at least is cheap to store and fast to run.

Two confounds limit causal claims: (1) Qwen3.5-9B used schema-mode structured output while all other local models used prompt_only — schema mode may confer a formatting advantage independent of model capability. (2) EuroLLM is explicitly optimised for multilingual European language coverage across all 24 EU languages, not for instruction-following performance on structured generation tasks. Its German fluency may be high while its JSON generation capability is low.

### 4.8 gpt-4o's Konjugation im Perfekt Underperformance

GPT-4o scores only 60% Teacher on Konjugation im Perfekt — its worst topic, and lower than Qwen2.5-7B's 80% on the same topic. The Teacher rejections cite explanation inaccuracies rather than wrong answers: the correct Partizip II is usually marked, but the explanatory text contains errors such as referring to _gehen_ as a "modal verb" or stating that "gg is required" in _gegessen_. This is an explanation-quality failure, not a content failure — the question could still teach the right form if the learner ignores the explanation.

---

## 5. Evaluator Analysis

### 5.1 The Teacher–Editor Gap as a Diagnostic Signal

The Teacher-Editor approval gap is a useful diagnostic:

| Model           | Teacher | Editor    | Gap          |
| --------------- | ------- | --------- | ------------ |
| gpt-4o          | 87.8%   | 98.9%     | 11.1 pts     |
| Qwen3.5-9B      | 62.6%   | 85.7%     | 23.1 pts     |
| Qwen2.5-7B      | 42.4%   | 63.5%     | 21.1 pts     |
| **EuroLLM-22B** | 24.4%   | **86.7%** | **62.3 pts** |
| Llama-3.2-3B    | 17.8%   | 67.8%     | 50.0 pts     |
| SmolLM3-3B      | 1.4%    | 25.7%     | 24.3 pts     |

A large gap indicates the model produces grammatically valid sentences but pedagogically broken questions. EuroLLM-22B's 62-point gap is the extreme case: the model's one-answer-duplicated-four-times output is always grammatically correct once the correct option is substituted into the sentence, but is pedagogically worthless as a quiz question. Llama-3.2-3B's 50-point gap reflects a similar pattern: predicative adjective questions are grammatically valid but do not test adjective declension.

A small gap is not inherently good — SmolLM3's 24-point gap coexists with near-zero absolute quality. A small gap at high absolute values (gpt-4o: 11 points at 87.8%) is the target profile.

### 5.2 Static Evaluator as an Early Filter

The static evaluator (option uniqueness, correct-answer presence, non-empty explanation) is a cheap and useful pre-filter. Its clean rate correlates roughly with overall quality:

| Model        | Static Clean | Teacher Approval |
| ------------ | ------------ | ---------------- |
| gpt-4o       | 93.3%        | 87.8%            |
| Qwen2.5-7B   | 77.6%        | 42.4%            |
| Qwen3.5-9B   | 72.5%        | 62.6%            |
| Llama-3.2-3B | 67.8%        | 17.8%            |
| EuroLLM-22B  | 46.7%        | 24.4%            |
| SmolLM3-3B   | 10.0%        | 1.4%             |

The correlation is imperfect: Qwen2.5-7B has higher static cleanliness than Qwen3.5-9B (77.6% vs 72.5%) but lower Teacher approval (42.4% vs 62.6%). Static issues are necessary but not sufficient — a question can have unique, valid-looking options and still contain a wrong correct answer or a case-confusion error that only the Teacher catches.

---

## 6. Discussion

### 6.1 Qwen3.5-9B as the Only Viable Local Model

Of the five local models, only Qwen3.5-9B approaches a quality level that could be useful in practice. Its 62.6% Teacher approval still represents a significant regression from gpt-4o's 87.8%, but the B1-rich CEFR distribution of its approved questions (42% vs gpt-4o's 35%) is an interesting counterpoint — the model generates harder questions when it generates correct ones.

Whether 62.6% Teacher approval is "good enough" depends on pipeline design. If generated questions undergo human review before publication, a 37% rejection rate may be acceptable. If the output is used directly (no review), it is not: 37 out of every 100 questions contain a wrong correct answer, broken distractors, or a pedagogically broken structure.

Qwen3.5-9B's Konjugation im Perfekt failure (10% Teacher) is its most actionable weakness. This specific topic collapses due to duplicate options, which the static evaluator catches. A pipeline that filters on static cleanliness would automatically reject these questions, effectively raising the usable yield from the model — though at the cost of discarding most Perfekt questions.

### 6.2 What Harder Topics Reveal

The adjective declension topics — particularly Dativ — function as stress tests that separate the models clearly. The Dativ topic requires:

1. Constructing a sentence with a dative-governing element
2. Generating the correct weak/mixed adjective ending for the dative case
3. Generating three plausible but incorrect alternatives (strong forms, accusative forms, wrong gender)

GPT-4o handles all three. Qwen3.5 handles 1 and 2 but fails at 3 (duplicate distractors). Qwen2.5 fails at 1 (uses accusative prepositions). EuroLLM fails at 3 (all-identical options). Llama and SmolLM3 fail at 1 (generate predicative or undeclined forms).

This decomposition suggests the bottleneck for smaller models is distractor generation, not morphology. The models know the correct form but cannot generate plausible wrong forms — they either copy the correct form into all slots or produce nonsensical distractors. Prompt engineering specifically targeting distractor diversity may help, but this is untested.

### 6.3 The Speed-Quality Tradeoff

| Model        | Quality (Teacher %) | Speed (s/sample) | Quality per second |
| ------------ | ------------------- | ---------------- | ------------------ |
| gpt-4o       | 87.8%               | 5.5              | 16.0               |
| Qwen3.5-9B   | 62.6%               | 15.7             | 4.0                |
| Qwen2.5-7B   | 42.4%               | 14.3             | 3.0                |
| Llama-3.2-3B | 17.8%               | 7.0              | 2.5                |
| EuroLLM-22B  | 24.4%               | 52.4             | 0.5                |
| SmolLM3-3B   | 1.4%                | 6.9              | 0.2                |

GPT-4o dominates on quality-per-second. EuroLLM-22B is the worst local option by this metric despite being the largest model. For offline use where total generation time matters (e.g., generating a large question bank overnight), Qwen3.5-9B at 4.0 quality-per-second is a reasonable choice if the lower quality ceiling is acceptable.

### 6.4 Failure Modes Suggest Instruction-Following Gaps, Not Knowledge Gaps

A recurring pattern across the weaker models is that they understand the subject matter but fail at the task structure. The distinction matters because the two failure types have different remedies.

**EuroLLM-22B** achieves 86.7% Editor approval — the model generates grammatically correct German sentences most of the time. It correctly produces weak adjective forms after definite articles (100% Teacher on Nominativ). Its failure is at the level of question construction: it cannot generate three distinct wrong alternatives, filling all four option slots with the correct answer. This is not a German grammar problem. Given that the prompt already includes instructions aimed at smaller models and this still occurs, the collapse likely reflects a deeper mismatch: EuroLLM was primarily trained for language fluency tasks (translation, multilingual generation) rather than structured pedagogical output. Distractor generation is simply not a task type it has learned.

**Llama-3.2-3B** similarly demonstrates German vocabulary knowledge — the predicative adjectives it generates ("hoch", "arm", "schlank") are real German words used correctly. It fails at understanding what the task is: fill-in-the-blank declension testing, not adjective vocabulary selection. Despite the prompt's structural guidance, the model substitutes a simpler, more familiar task. This suggests it may lack exposure to this type of structured quiz output in its pretraining, making prompt-level instruction insufficient on its own.

**Qwen2.5-7B** gets the adjective morphology right for the case it actually generates — it just consistently generates the wrong case. Its accusative sentences for dative topics are internally consistent. This is a topic-specification failure: the model does not reliably translate "Adjektivdeklination im Dativ" into sentence structures that actually require dative. This is the most tractable failure in the set — it may be addressable at the preset level by changing the one-shot example to a more explicit dative construction.

**SmolLM3-3B**'s repetition loop is a generation stability failure that the current prompt does not prevent. The model enters an infinite loop in the explanation field, producing the same sentence dozens of times until hitting the token limit.

The pattern across the four models is: _German grammar knowledge is partially intact; the structural failure is in producing well-formed question output._ The failures likely require more than further prompt wording to resolve:

| Failure type                             | Likeliest remedy                                                                               | Estimated effort    |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------- |
| Distractor generation collapse (EuroLLM) | Task-specific fine-tuning; richer few-shot examples showing diverse wrong answers              | High                |
| Task substitution (Llama)                | Fine-tuning or task-decomposition (generate sentence separately, then options)                 | High                |
| Case confusion (Qwen2.5)                 | Preset-level change: replace dative one-shot example with a clearer dative preposition context | Low — preset edit   |
| Generation instability (SmolLM3)         | Schema mode; reduced max tokens; constrained decoding                                          | Low — config change |
| Duplicate distractors (Qwen3.5)          | Explicit negative constraint in prompt; schema with enum uniqueness                            | Low–medium          |
| Explanation inaccuracies (Qwen3.5)       | Separate explanation generation step; chain-of-thought prompting                               | Medium              |

EuroLLM-22B's German grammar competence makes it the most interesting candidate for a follow-up experiment. A model that correctly declines adjectives and generates grammatically valid sentences at near-gpt-4o Editor rates has the underlying German knowledge the task requires — it simply has not learned to produce quiz question structure. Whether that is recoverable through fine-tuning on a small set of well-formed examples is an open question worth testing.

---

## 7. Conclusions

Across approximately 540 German grammar questions from six models testing nine topics, the following findings emerge:

1. **GPT-4o remains the quality ceiling.** 87.8% Teacher approval, 98.9% Editor approval, zero parse failures — no local model approaches this in the e03 setup.

2. **Qwen3.5-9B is the only local model with partial viability.** At 62.6% Teacher approval it is 25 points below gpt-4o, but its approved questions have the richest B1 distribution of any model. It requires static filtering to remove duplicate-option batches.

3. **No standard proxy predicts quality.** Parameter count, model age, training data recency, and disk size all fail as predictors. EuroLLM-22B (22B parameters, 3 months old, 12 GB) scores 24.4% — worse than Qwen3.5-9B (9B parameters, released 6 days before the experiment, 5.6 GB) at 62.6%. SmolLM3-3B has the most recent training cutoff (~June 2025) and the worst performance. Qwen3.5-9B delivers ~11× better quality-per-gigabyte than EuroLLM-22B.

4. **Each weak model fails in a distinct and mechanistically informative way.** EuroLLM collapses distractor generation into all-identical options. Llama-3.2 substitutes predicative adjective vocabulary questions for morphological ones. Qwen2.5-7B confuses accusative and dative case contexts. SmolLM3-3B enters degenerate repetition loops.

5. **Adjektivdeklination im Dativ is the hardest topic for local models.** Five out of five local models score 0–70% Teacher approval on it; gpt-4o scores 100%. Distractor generation for inflected forms is the specific bottleneck.

6. **The Teacher–Editor gap quantifies pedagogical failure independent of grammaticality.** EuroLLM-22B's 62-point gap is the clearest example in the dataset: grammatically valid output, pedagogically broken questions.

7. **SmolLM3-3B is not usable for this task as configured.** One Teacher-approved question out of 70 evaluated (1.4%), four parse failures out of 18 samples (22%), and a degenerate repetition failure mode that produces output longer than the context window. Constrained decoding or a much simpler prompt may change this outcome.

8. **These scores reflect a shared-baseline condition, not each model's ceiling.** The prompt used in e03 was designed with smaller models in mind and represents a genuine effort at a well-specified common instruction. However, no per-model system prompts, hyperparameter search, or fine-tuning were applied. The failure modes — particularly EuroLLM's distractor collapse and Qwen2.5's case confusion — have identifiable structural causes that targeted intervention could address. E03 establishes what the models produce under a common, reasonable prompt; it does not establish what they are capable of with model-specific optimization.

---

_Written by Claude Sonnet 4.6 using data generated by SprachlernSandbox. Generation models: gpt-4o (OpenAI API), EuroLLM-22B-Instruct-2512-mlx-4bit, Llama-3.2-3B-Instruct-4bit, Qwen2.5-7B-Instruct-4bit, Qwen3.5-9B-MLX-4bit, SmolLM3-3B-4bit (all local MLX). LLM judge model (Editor, Student, Teacher evaluators): gpt-4o._
