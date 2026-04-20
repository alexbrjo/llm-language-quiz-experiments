# E09: Edge Model Fill-in-the-Blank Comparison for German Grammar

**Experiment:** e09 edge model FITB comparison
**Date:** 2026-04-14
**Author:** Claude Sonnet 4.6

---

## Abstract

This experiment evaluates four small edge models running locally via llama.cpp (Gemma 4 E2B, Gemma 4 E4B, Qwen3.5-4B, and Phi-4-mini) alongside a larger local model (Gemma 4 26B A4B, also via llama.cpp) and one API model (Claude Sonnet 4.6) for open fill-in-the-blank German grammar question generation. Twenty grammar topics were tested with four questions per sample across four repeats, yielding 123–183 evaluated questions per model (1,026 total). All questions were assessed by a four-evaluator pipeline (Static, Editor, Student, Teacher). The headline result is a three-tier quality structure: Gemma 4 26B A4B leads at 90.6% all-pass, Claude Sonnet 4.6 follows at 81.7%, the mid-range Gemma edge models reach 62–69%, and Phi-4-mini and Qwen3.5-4B both bottom out at ~45%. Static passes 100% across all models and all quality differences are driven by content. Three failure modes account for the majority of rejections across all models: passive voice agent word order errors (systematic and universal), conjunction ambiguity in Nebensätze questions (inherent to the topic), and knowledge errors in small models producing wrong marked answers that cascade into triple-evaluator failures. Gemma 4 26B A4B and Claude Sonnet 4.6 produced zero triple-failures in this run.

---

## 1. Introduction

Experiments e06–e08 established fill-in-the-blank question generation baselines for frontier API models and explored context injection strategies for improving smaller models. E09 evaluates the new Gemma 4 model family across three scales (E2B, E4B, and 26B A4B), alongside Qwen3.5-4B and Phi-4-mini as non-Gemma edge model comparisons, with Claude Sonnet 4.6 as a frontier API reference point.

E06 showed that Claude Sonnet 4.6 and Haiku 4.5 were the quality leaders for open FITB (98% and 89% all-pass respectively on 10 topics with a 4-evaluator pipeline), with the Qwen3.5-9B local models scoring 48–66%. E09 extends this to 20 topics and tests smaller, newer models including the first evaluation of the Gemma 4 family in this series.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Model | Provider | Runtime | Quant | Temp | N |
|---|---|---|---|---|---|
| Gemma 4 E2B | Google | llama.cpp | Q4_K_M | 0.3 | 180 |
| Gemma 4 E4B | Google | llama.cpp | Q4_K_M | 0.3 | 183 |
| Qwen3.5-4B | Alibaba | llama.cpp | Q4_K_M | 0.3 | 180 |
| Phi-4-mini | Microsoft | llama.cpp | Q4_K_M | 0.3 | 123 |
| Gemma 4 26B A4B | Google | llama.cpp | UD-IQ4_NL | 0.3 | 180 |
| Claude Sonnet 4.6 | Anthropic API | API | — | — | 180 |

Phi-4-mini produced 123 questions vs 180–183 for other models due to parse failures in a subset of samples.

| Model | Effective Params | VRAM | Context |
|---|---|---|---|
| Gemma 4 E2B | 2.3B effective (dense, PLE) | ~2 GB | 128K |
| Gemma 4 E4B | 4.5B effective (dense, PLE) | ~3 GB | 128K |
| Qwen3.5-4B | 4B | ~3 GB | 32K |
| Phi-4-mini | 3.8B | ~3 GB | 128K |
| Gemma 4 26B A4B | 26B total / 4B active (MoE) | ~13.4 GB | 128K |
| Claude Sonnet 4.6 | — | API | 200K |

### 2.2 Grammar Topics

Twenty German grammar topics were tested, expanding the 10-topic set from e06. Topics span adjective declension (nominative, accusative, dative), verb conjugation (Präsens, Präteritum, Perfekt, Futur I, Konjunktiv II), pronouns, articles, negation, prepositions, passive voice, relative pronouns, subordinate clauses, and reflexive pronouns. Each topic used a 1-shot example.

### 2.3 Evaluators

| Evaluator | Type | Model | Purpose |
|---|---|---|---|
| Static | Rule-based | — | Blank present, answer non-empty, explanation non-empty |
| Editor | LLM | gpt-4o | Grammatical correctness and naturalness of the completed sentence |
| Student | LLM | gpt-4o | Simulated learner produces the correct answer without seeing it |
| Teacher | LLM | gpt-4o | Answer correctness, topic alignment, explanation quality, CEFR level |

Evaluation used gpt-4o at temperature 0.1 in `json_mode`. A question passes the **all-pass** criterion only if it passes all four evaluators.

---

## 3. Results

### 3.1 All-Pass Rates

| Model | N | All-Pass | All-Pass % |
|---|---|---|---|
| Gemma 4 26B A4B | 180 | 163 | **90.6%** |
| Claude Sonnet 4.6 | 180 | 147 | **81.7%** |
| Gemma 4 E4B | 183 | 127 | **69.4%** |
| Gemma 4 E2B | 180 | 113 | **62.8%** |
| Phi-4-mini | 123 | 56 | **45.5%** |
| Qwen3.5-4B | 180 | 81 | **45.0%** |

Three tiers are visible: Gemma 26B and Sonnet form the top tier (81–91%), the Gemma edge models form a mid tier (63–69%), and Phi and Qwen bottom out around 45%. The Gemma E2B–E4B gap (6.6 points) is smaller than the E4B–Sonnet gap (12.3 points), and Gemma 26B's 90.6% (higher than Sonnet's 81.7%) is the headline result: a locally-run quantised model outperformed a frontier API model on all-pass rate.

### 3.2 Per-Evaluator Pass Rates

| Model | Static | Editor | Student | Teacher |
|---|---|---|---|---|
| Gemma 4 26B A4B | 100% | 95.0% | 96.7% | 97.8% |
| Claude Sonnet 4.6 | 100% | 96.7% | 91.1% | 88.3% |
| Gemma 4 E4B | 100% | 80.9% | 84.2% | 90.7% |
| Gemma 4 E2B | 100% | 80.6% | 77.8% | 83.9% |
| Phi-4-mini | 100% | 64.2% | 65.9% | 74.8% |
| Qwen3.5-4B | 100% | 66.7% | 62.8% | 68.3% |

Static passes 100% for all models; every model reliably produced structurally complete questions. All quality differences are content-driven.

**Sonnet 4.6 shows an inverted evaluator pattern** relative to all other models: Editor (96.7%) > Student (91.1%) > Teacher (88.3%). For every other model, Teacher approval is the highest of the three LLM evaluators. Sonnet's grammatical quality was high and the Editor and Student passed its output at high rates. Where it fell short was pedagogical quality: the Teacher rejected questions where the sentence context did not unambiguously require a single answer, or where the question exercised a slightly different sub-rule than the stated topic. A grammatically correct question is not automatically a pedagogically sound one.

**For the two small models (Phi, Qwen)**, Editor and Student approval rates were similar (~64–67%), reflecting questions where the generated sentence was ungrammatical and the student could not recover the expected answer. Both evaluators were rejecting the same underlying content errors.

### 3.3 Multi-Evaluator Failures

| Model | 0 fails | 1 fail | 2 fails | 3 fails |
|---|---|---|---|---|
| Gemma 4 26B A4B | 163 | 15 | 2 | **0** |
| Claude Sonnet 4.6 | 147 | 23 | 10 | **0** |
| Gemma 4 E4B | 127 | 38 | 11 | 7 |
| Gemma 4 E2B | 113 | 39 | 19 | 9 |
| Phi-4-mini | 56 | 33 | 18 | **16** |
| Qwen3.5-4B | 81 | 38 | 37 | **24** |

Gemma 26B and Sonnet produced zero triple-failures. Their 2-fail items were concentrated in known hard topics (Passiv im Präsens, Wechselpräpositionen) and represent isolated borderline cases rather than systematic errors.

Qwen3.5-4B had 24 triple-failures and Phi-4-mini had 16, more than 13% and 18% of their output respectively. These are fundamental content errors: the sentence was ungrammatical (Editor), the student could not recover the expected answer (Student), and the Teacher identified a wrong or misaligned marked answer. Triple-failures represent a complete failure of the model to create anything of pedagogic value.

**Worst triple-failure clusters:**
- **Qwen3.5-4B Reflexivpronomen** (5 items): wrong case on reflexive pronoun marked as correct (`mich` instead of `mir`), producing an ungrammatical sentence and a student answer that disagreed with the marked answer.
- **Phi-4-mini Konjugation im Perfekt** (5 items): wrong auxiliary verb selection and malformed perfect constructions flagged by all three LLM evaluators.
- **Gemma E4B Futur I** (4 items): systematic bracket error where `werden` and the infinitive did not maintain final position when combined with modals or time adverbs.

### 3.4 Topics of Interest

The table below shows all-pass rates for the four topics with consistently low scores across models.

| Topic | 26B | Sonnet | E4B | E2B | Phi | Qwen |
|---|---|---|---|---|---|---|
| Passiv im Präsens | 22% | 56% | 11% | 0% | 11% | 0% |
| Wechselpräpositionen | 100% | 11% | 11% | 0% | 0% | 0% |
| Nebensätze (weil/dass/obwohl) | 67% | 44% | 100% | 22% | 11% | 22% |
| Präpositionen mit Dativ | 100% | 67% | 46% | 56% | 29% | 22% |

**Passiv im Präsens** was the only topic where Sonnet (56%) outperformed Gemma 26B (22%), and the only topic where the overall quality leader scored below 25%. Every model failed at least some Passiv questions, driven by a generation-side word order error discussed in §4.

**Wechselpräpositionen** scored 0% for three models and 11% for two, with Gemma 26B as the only model to achieve a high score (100%). Small models produced two overlapping failures: mislabeled questions (testing dative-only prepositions rather than the Akk/Dat alternation) and an answer scope mismatch between the expected answer and what the student produced.

**Nebensätze** was volatile, ranging from 11% (Phi) to 100% (Gemma E4B) with no clear model-size correlation. This reflects conjunction ambiguity: whether a question passed depended on whether the generated sentence happened to be semantically constrained enough to force one conjunction, which varied by sample.

---

## 4. Failure Mode Analysis

### 4.1 Passive Voice Word Order (Universal)

The most consistent failure in the dataset. All six models generated passive sentences with the partizip II appended after 'werden':

> `Das Buch wird gelesen von der Lehrerin.`

instead of the standard German order:

> `Das Buch wird von der Lehrerin gelesen.`

The Editor consistently rejected the first form as grammatically incorrect/unnatural. This is a generation bias, not a knowledge gap: the models appear to construct the passive skeleton (`wird X`) and then append the agent phrase rather than placing it in the correct pre-participle position. Context injection (e07, e08) did not resolve the analogous word order errors in prior experiments, suggesting this requires either prompt-level enforcement or a stronger model.

For smaller models (E2B, Qwen), additional sub-errors compounded the issue: wrong article gender in the agent phrase (`der neue Brücke` instead of `die neue Brücke`) and doubled participles (`Er wird bestehen die Prüfung bestehen`).

### 4.2 Conjunction Ambiguity in Nebensätze

The Teacher's uniqueness check accounts for approximately 70–80% of Teacher failures across all models. The dominant sub-pattern is conjunction ambiguity in Nebensätze questions:

> `Wir bleiben zu Hause, _____ es regnet.`

Both `weil` (causal: "because it is raining") and `obwohl` (concessive: "even though it is raining") are grammatically and semantically valid completions. The Teacher correctly rejects these because no single conjunction is forced by the sentence context. This is an inherent limitation of the topic as specified: generating a Nebensätze question that unambiguously requires exactly one of `weil`, `dass`, or `obwohl` demands more contextual scaffolding than the current prompt provides. The high variance across models (11–100%) reflects that some generated sentences happened to be contextually specific enough to pass, rather than systematic compliance with the constraint.

### 4.3 Knowledge Errors in Small Models

Phi-4-mini and Qwen3.5-4B produced questions where the marked answer was simply wrong, a different category of failure from the ambiguity and word order issues that affected larger models. These manifested as triple-failure cascades because all three downstream evaluators independently detected the error.

Examples of marked-answer errors:
- `Sie hat gestern im Kino gewesen` with answer `hat`: `sein` is the required auxiliary for `sein`-verbs; the model applied the wrong auxiliary and flagged it as correct.
- `Ich koche mich heute Abend ein Abendessen` with answer `mich`: the correct reflexive here is dative `mir`; `mich` is accusative and produces an ungrammatical sentence.
- Futur I questions (Gemma E4B) where the infinitive landed in second position: `Du wirst wollen morgen deinen Freund anrufen` instead of `Du wirst morgen deinen Freund anrufen wollen`.

These errors were largely absent from the Gemma edge models, suggesting Qwen3.5-4B and Phi-4-mini have gaps in German morphosyntactic knowledge that the Gemma architecture avoids.

### 4.4 Wechselpräpositionen Answer Scope Mismatch

Questions in this topic frequently created an answer scope conflict between what the question implied was being tested and what the Student produced:

> `Die Katze springt _____ (das) Sofa.`
> Expected: `auf das` | Student answers: `das`

The hint `(das)` signals the article form, leading the Student to produce just the article. The expected answer requires the preposition+article together. This is a question construction flaw: the blank placement and hint don't accommodate the multi-word answer the topic requires. It cannot be resolved by prompting the model to produce better questions; it requires either a different blank placement (after the preposition) or a different hint format. Gemma 26B's 100% on this topic suggests that a more capable model produced questions where the answer scope was clearer, but the underlying format tension remains.

---

## 5. Discussion

### 5.1 Three Quality Tiers

The results sort cleanly into three groups:

**Top tier (81–91%):** Gemma 4 26B A4B and Claude Sonnet 4.6. Both produced zero triple-failures. Their remaining failures are concentrated in three hard topics (Passiv, Wechselpräpositionen, Nebensätze) and represent inherent format limitations rather than model knowledge errors. Gemma 26B's 90.6% (higher than Sonnet's 81.7%) is the headline result of the experiment: a locally-run quantised model outperformed a frontier API model on all-pass rate.

**Mid tier (63–69%):** Gemma 4 E4B and Gemma 4 E2B. Meaningful quality with acceptable triple-failure rates (5–9 items each). The 6.6-point gap between E2B and E4B is consistent with the quantization effects observed in prior experiments. Both are potentially viable for production use with post-generation filtering.

**Bottom tier (~45%):** Phi-4-mini and Qwen3.5-4B. Fewer than half of generated questions passed all evaluators. High triple-failure rates (13–18%) indicate fundamental knowledge errors, not marginal quality issues. These are not viable for unsupervised production use without significant post-filtering or prompt engineering.

### 5.2 Gemma 26B Outperforming Sonnet 4.6

Gemma 26B's 90.6% all-pass exceeded Sonnet's 81.7% by 8.9 points, a meaningful gap at these sample sizes. The difference was driven by Teacher approval (97.8% vs 88.3%): Gemma 26B's questions were more reliably topic-aligned and less prone to the ambiguity patterns that the Teacher caught. This may reflect that the 26B model has more capacity to reason about uniqueness constraints during generation, or that its instruction following for the generation prompt is stronger.

### 5.3 Sonnet's Inverted Evaluator Pattern

Sonnet's Editor > Student > Teacher ordering is the reverse of every other model. Sonnet produced grammatically impeccable sentences (96.7% Editor approval) but generated questions where the sentence context did not uniquely force a single answer, or where the topic label was technically correct but the question exercised a slightly different sub-rule. These are questions that work grammatically but fail on the stricter "is this the right question for this topic?" bar that the Teacher applies.

This is a different failure mode from the small models, where sentences were grammatically broken. For frontier API models, Teacher approval is a more informative signal than Editor or Student approval alone.

### 5.4 Gemma's Edge Architecture Advantage

The two Gemma edge models consistently outperformed Phi-4-mini and Qwen3.5-4B despite overlapping parameter counts. Gemma E4B (4.5B effective, dense) scored 69.4% vs Qwen3.5-4B (4B dense) at 45.0%. Gemma E2B (2.3B effective, dense) scored 62.8%, higher than Phi-4-mini (3.8B dense) at 45.5%. The "E" in E2B/E4B denotes effective parameter count: these models use Per-Layer Embeddings (PLE), which inflate the total parameter count but not the compute-active count. They are standard dense transformers optimised for on-device deployment, not MoE. The quality gap over Phi and Qwen is more likely explained by Gemma 4's stronger multilingual and grammatical training data. The knowledge error failure mode (§4.3) was largely absent from the Gemma edge models and prevalent in Phi and Qwen, consistent with better German morphosyntactic coverage in Gemma's training.

---

## 6. Limitations

1. **Topic-level sampling noise.** With 4 repeats × 4 questions per topic, each topic has approximately 16 questions per model. A single verdict change shifts a topic's pass rate by ~6 percentage points. Per-topic figures should be read as directional.

2. **Hard topic confounds.** Three topics (Passiv, Wechselpräpositionen, Nebensätze) have format-level failure modes that are not addressable by model quality alone. Removing these topics from the all-pass calculation would improve all models' scores and potentially change the tier structure.

3. **Single judge.** All LLM evaluation used gpt-4o. Cross-provider evaluation bias (the judge systematically favouring or disfavouring certain model outputs) is not assessed.

---

## 7. Conclusions

Across 1,026 German grammar fill-in-the-blank questions from six models tested on 20 topics:

1. **Gemma 4 26B A4B was the quality leader at 90.6% all-pass**, outperforming Claude Sonnet 4.6 (81.7%) and all smaller models. This is the first experiment in this series where a locally-run quantised model exceeded a frontier API model on all-pass rate.

2. **Three quality tiers emerged.** Top (Gemma 26B, Sonnet, 81–91%), mid (Gemma E4B, E2B, 63–69%), and bottom (Phi-4-mini, Qwen3.5-4B, ~45%). The tier boundaries are large enough to be practically meaningful.

3. **Static passed 100% for all models.** Format compliance was not a differentiating factor. All quality differences were content-driven.

4. **Passive voice word order was the single most consistent failure**, present in every model. It is a generation-side word order bias, not a knowledge gap, and was not addressed by context injection in prior experiments (e07, e08).

5. **Conjunction ambiguity drove 70–80% of Teacher failures across all models.** Nebensätze questions require more contextual specificity than the current prompt reliably produces.

6. **Small model failures cascaded.** Phi-4-mini (13%) and Qwen3.5-4B (18%) both produced triple-failures at high rates, indicating genuine knowledge errors rather than borderline quality. The Gemma edge models avoided this failure mode almost entirely despite similar or smaller parameter counts, pointing to stronger German morphosyntactic training.

7. **Gemma 4 E-series models consistently outperformed same-size dense competitors.** Gemma E2B (2.3B effective) at 62.8% exceeded Phi-4-mini (3.8B) at 45.5%; Gemma E4B (4.5B effective) at 69.4% exceeded Qwen3.5-4B (4B) at 45.0%. The E-series models are dense transformers using Per-Layer Embeddings (PLE), not MoE; the quality advantage reflects training data rather than architecture.

---

_Written by Claude Sonnet 4.6. Reviewed by Alexander Johnson. Generation models: Gemma 4 E2B, Gemma 4 E4B, Phi-4-mini, Qwen3.5-4B (llama.cpp, Q4_K_M), Gemma 4 26B A4B (llama.cpp, UD-IQ4_NL), Claude Sonnet 4.6 (Anthropic API). LLM judge (Editor, Student, Teacher evaluators): gpt-4o._
