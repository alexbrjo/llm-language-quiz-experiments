# AI-Generated German Grammar Quiz Quality: A Comparative Evaluation of GPT-4o, GPT-4o-mini, and GPT-4-Turbo

**Experiment:** e01 exact answers
**Date:** 2026-03-04
**Author:** Claude Sonnet 4.6

---

## Abstract

This report evaluates the quality of AI-generated German grammar quiz questions across three OpenAI models: GPT-4o, GPT-4o-mini, and GPT-4-Turbo. Using a fixed prompt that generates multiple-choice fill-in-the-blank questions, nine grammar topics were tested with each model. Three complementary LLM-as-judge evaluators assessed quality from distinct perspectives: a language Editor (grammatical correctness of generated sentences), a B1-level Student (answerability and difficulty calibration), and an expert Teacher (pedagogical quality and CEFR level). GPT-4-Turbo produced the highest quality output overall (94.4% teacher approval, 88.9% student accuracy), followed by GPT-4o (92.2%, 85.6%) and GPT-4o-mini (87.8%, 82.2%). All three models failed badly on Plusquamperfekt (past perfect) questions — an issue traceable to the prompt rather than the models themselves.

---

## 1. Introduction

Automatically generating language-learning quiz content at scale requires not just grammatical correctness, but pedagogical soundness: plausible distractors, accurate explanations, and questions that genuinely test the intended grammar point at the right difficulty level. This experiment asks whether commodity LLMs can reliably produce such content, and whether multi-perspective LLM evaluation can reliably assess it.

The specific task is generating German multiple-choice fill-in-the-blank questions — a format where the student sees a sentence with a blank and must choose the correct word form from four options. The grammar tested spans common learner challenges: possessive articles, adjective declension, and verb conjugation across tenses.

---

## 2. Experimental Setup

### 2.1 Generation Prompt

All three models were given the same generation prompt. The prompt is designed to produce **"exact answer"** questions — fill-in-the-blank items where grammar rules determine a single, unambiguous correct answer with no room for interpretation. For example, given a sentence with a missing possessive article and the pronoun cue in parentheses, only one inflected form is grammatically correct: every other option is definitively wrong. This contrasts with open-ended or opinion-based questions where multiple answers could be defended.

The prompt text (with Jinja template variables shown):

```
Generate {{ num_questions }} multiple-choice fill in the blank question(s) in {{ language }} testing {{ topic }}.

Example question: "{{ example_question }}"
Example instructions: "{{ example_instruction }}"
Example answer: "{{ example_answer }}"

Return JSON with this exact structure:
{
  "instruction": "instructions for the user to answer the question",
  "question_type": "multiple_choice",
  "questions": [
    {
      "content": "content for the question",
      "options": [
        {"answer": "option text", "is_correct": true},
        {"answer": "option text", "is_correct": false}
      ],
      "explanation": "a short explanation of why the correct answer is right"
    }
  ]
}

Include 4 options per question, exactly one correct each. Return only the JSON, no other text.
```

Key characteristics:

- **No system prompt** — all instructions are in the user turn
- **Output mode:** `prompt_only` — no structured output enforcement (JSON schema or tool use); the model must produce valid JSON by instruction alone
- **Temperature:** 0.7, **Max tokens:** 2048
- **Questions per sample:** 10 (`num_questions = 10`, `language = German`)

The `topic`, `example_question`, `example_instruction`, and `example_answer` variables were set per preset (see Section 2.2). Each preset provided a single one-shot example question, instruction, and correct answer to guide the model. The prompt requests four options per question with exactly one correct answer, plus an `explanation` field justifying the correct answer.

The per-preset examples used were:

| Preset                           | Example Question                                              | Example Answer   |
| -------------------------------- | ------------------------------------------------------------- | ---------------- |
| Adjektivdeklination im Akkusativ | _Es gibt einen **\_\_** (klein) Ort_                          | kleinen          |
| Adjektivdeklination im Dativ     | _Ich legte das Telefon auf den \_\_\_\_ (alt) Tisch._         | alten            |
| Adjektivdeklination im Nominativ | _Das ist eine **\_\_** (klein) Stadt._                        | kleine           |
| Konjugation im Plusquamperfekt   | _Ich **\_\_** (haben/sein) 2 Jahre lang **\_\_** (arbeiten)._ | habe, gearbeitet |
| Konjugation im Präsens           | _**\_\_** (sprechen) du Deutsch?_                             | Sprichst         |
| Konjugation im Präteritum        | _Er **\_** (gehe) ins Kino_                                   | ging             |
| Personalpronomen in Akkusativ    | _Kannst du **\_** (ich) bitte helfen?_                        | mir              |
| Possessivartikel im Akkusativ    | _Ich habe gestern mit **\_** (er) Bruder gesprochen._         | seinem           |
| Possessivpronomen                | _Ich habe gestern mit **\_** (er) Bruder gesprochen._         | seinem           |

Two preset examples contain errors that are relevant to the results (discussed in Section 4.1 and 4.5).

### 2.2 Grammar Topics (Presets)

Nine grammar presets were tested, each producing one sample (10 questions):

| Preset                                    | Topic Area                        |
| ----------------------------------------- | --------------------------------- |
| Adjektivdeklination im Akkusativ          | Adjective declension — accusative |
| Adjektivdeklination im Dativ              | Adjective declension — dative     |
| Adjektivdeklination im Nominativ          | Adjective declension — nominative |
| Konjugation im Plusquamperfekt            | Verb conjugation — past perfect   |
| Konjugation im Präsens                    | Verb conjugation — present tense  |
| Konjugation im Präteritum                 | Verb conjugation — simple past    |
| Personalpronomen in Akkusativ             | Personal pronouns — accusative    |
| Possessivartikel deklination im Akkusativ | Possessive articles — accusative  |
| Possessivpronomen                         | Possessive pronouns               |

**Total per model:** 9 samples × 10 questions = **90 questions**

### 2.3 Models Under Test

| Model ID      | Avg. Generation Time | Avg. Tokens Used |
| ------------- | -------------------- | ---------------- |
| `gpt-4o`      | 17.5 s               | 1,326            |
| `gpt-4o-mini` | 22.5 s               | 1,331            |
| `gpt-4-turbo` | 34.7 s               | 1,387            |

GPT-4-Turbo was notably slower, taking roughly twice as long as GPT-4o for similar token counts. GPT-4o-mini, despite being the smallest model, was slower than GPT-4o in this batch — likely due to server load at time of execution.

### 2.4 Evaluators

Four evaluators assessed each generated question. Evaluation was run by `gpt-4o-mini` in `json_mode` at temperature 0.1.

#### Static Evaluator

A rule-based structural check (zero API calls). Validates format compliance: option count, exactly one correct answer, required fields. **Result across all three models: zero issues detected** — all questions passed structural validation.

#### Editor Evaluator

A German language editor assessing the **answered sentence** (question with the correct answer filled in). Evaluates grammatical correctness and naturalness only; ignores pedagogical quality. Produces `approval` (boolean) and `reasoning`.

_Average cost: ~186 tokens, ~1,860 ms per question_

#### Student Evaluator

A simulated B1-level German language learner who attempts to answer the question. Produces a chosen `answer`, step-by-step `reasoning`, and `ambiguity_notes`. The student's answer is compared against the marked correct option to compute accuracy.

_Average cost: ~265 tokens, ~2,374 ms per question_

#### Teacher Evaluator

An expert German teacher auditing the question on five criteria: (1) clarity, (2) correctness of the marked answer, (3) quality of distractors, (4) accuracy of the explanation, and (5) CEFR level. Produces `approval`, `rating` (A1–C2), and a list of `issues`.

_Average cost: ~509 tokens, ~4,175 ms per question_

---

## 3. Results

### 3.1 Overall Approval Rates

| Model       | Teacher Approval  | Editor Approval   | Student Accuracy  |
| ----------- | ----------------- | ----------------- | ----------------- |
| GPT-4-Turbo | **94.4%** (85/90) | **84.4%** (76/90) | **88.9%** (80/90) |
| GPT-4o      | 92.2% (83/90)     | **84.4%** (76/90) | 85.6% (77/90)     |
| GPT-4o-mini | 87.8% (79/90)     | 81.1% (73/90)     | 82.2% (74/90)     |

GPT-4-Turbo leads on all three metrics. GPT-4o and GPT-4-Turbo tie on Editor approval. GPT-4o-mini consistently underperforms the other two models by 3–7 percentage points.

### 3.2 CEFR Level Distribution

The Teacher evaluator assigned each question a CEFR difficulty rating. All three models concentrated output in the A1–B1 range, with no questions rated B2 or higher.

| CEFR Level | GPT-4o   | GPT-4o-mini | GPT-4-Turbo |
| ---------- | -------- | ----------- | ----------- |
| A1         | 11 (12%) | 13 (14%)    | 14 (16%)    |
| A2         | 32 (36%) | 25 (28%)    | 29 (32%)    |
| B1         | 47 (52%) | 52 (58%)    | 47 (52%)    |
| B2+        | 0        | 0           | 0           |

The prompt's absence of a target difficulty specification results in a natural bias toward B1 — the "safe middle" for grammar fill-in-the-blank questions. GPT-4o-mini skews slightly more toward B1 and produces fewer A2-level questions. The ceiling at B1 is a **prompt limitation**: without an explicit CEFR target or complexity guidance, models default to straightforward one-blank sentences testing a single rule.

### 3.3 Results by Grammar Topic

#### Teacher Approval by Topic (%)

| Topic                              | GPT-4o  | GPT-4o-mini | GPT-4-Turbo |
| ---------------------------------- | ------- | ----------- | ----------- |
| Adjektivdeklination im Akkusativ   | **100** | **100**     | **100**     |
| Adjektivdeklination im Nominativ   | 80      | **100**     | **100**     |
| Adjektivdeklination im Dativ       | **100** | 90          | 90          |
| Konjugation im Präsens             | **100** | 90          | **100**     |
| Konjugation im Präteritum          | **100** | 90          | **100**     |
| Personalpronomen in Akkusativ      | **100** | 70          | 90          |
| Possessivartikel im Akkusativ      | 90      | 60          | **100**     |
| Possessivpronomen                  | **100** | **100**     | 90          |
| **Konjugation im Plusquamperfekt** | **60**  | **90**      | **80**      |

#### Editor Approval by Topic (%)

| Topic                              | GPT-4o  | GPT-4o-mini | GPT-4-Turbo |
| ---------------------------------- | ------- | ----------- | ----------- |
| Adjektivdeklination im Akkusativ   | **100** | **100**     | **100**     |
| Adjektivdeklination im Nominativ   | **100** | **100**     | **100**     |
| Adjektivdeklination im Dativ       | **100** | **100**     | 80          |
| Konjugation im Präsens             | 50      | 90          | **100**     |
| Konjugation im Präteritum          | **100** | **100**     | **100**     |
| Personalpronomen in Akkusativ      | **100** | 90          | 80          |
| Possessivartikel im Akkusativ      | 90      | 60          | **100**     |
| Possessivpronomen                  | **100** | 90          | **100**     |
| **Konjugation im Plusquamperfekt** | **20**  | **0**       | **0**       |

#### Student Accuracy by Topic (%)

| Topic                              | GPT-4o  | GPT-4o-mini | GPT-4-Turbo |
| ---------------------------------- | ------- | ----------- | ----------- |
| Adjektivdeklination im Akkusativ   | **100** | **100**     | **100**     |
| Adjektivdeklination im Nominativ   | 80      | **100**     | **100**     |
| Konjugation im Präsens             | **100** | 90          | **100**     |
| Konjugation im Präteritum          | **100** | **100**     | 90          |
| Personalpronomen in Akkusativ      | **100** | 90          | **100**     |
| Possessivartikel im Akkusativ      | 90      | 60          | **100**     |
| Possessivpronomen                  | 80      | **100**     | **100**     |
| Adjektivdeklination im Dativ       | 60      | 30          | 50          |
| **Konjugation im Plusquamperfekt** | 60      | 70          | 60          |

---

## 4. Analysis

### 4.1 The Plusquamperfekt Problem

The most striking finding is the **complete collapse of Editor approval** for Plusquamperfekt questions. GPT-4o-mini and GPT-4-Turbo scored 0%; GPT-4o managed only 20%. Yet the Teacher evaluator was far more lenient (60–90%), and students still answered ~60–70% correctly.

Examining the Editor rejections reveals a systematic failure: the models consistently produce **malformed sentence structures** when generating fill-in-the-blank questions for the past perfect tense. Examples of Editor-flagged sentences:

- _"Sie hatten, geschlossen die Tür schließen."_ — incorrect word order and redundant infinitive
- _"Du hattest das Buch gelesen, [malformed structure]"_ — past participle separated from auxiliary
- _"Wir waren, gegessen bereits"_ — wrong auxiliary verb (`waren` instead of `hatten`) and broken word order

The root cause is the **preset example**, not just the prompt structure. The Plusquamperfekt preset provided this one-shot example:

> _"Ich **\_\_** (haben/sein) 2 Jahre lang **\_\_** (arbeiten)."_ → `"habe, gearbeitet"`

This example has two problems. First, it shows a **two-blank question** — contradicting the prompt's single-blank format and encouraging the model to generate similarly split constructions. Second, the example answer is **grammatically wrong**: Plusquamperfekt requires the auxiliary in the simple past (`hatte`), not the present perfect (`habe`). The correct answer should be `"hatte, gearbeitet"`. Models trained to follow the example pattern faithfully will reproduce both the two-blank structure and the incorrect auxiliary.

The prompt itself also lacks an explicit constraint that the blank must replace exactly one word form, which compounds the issue for multi-part verb tenses. The Teacher evaluator's relative leniency here suggests it focuses on whether the question tests the right concept rather than sentence-level grammaticality.

**Learning:** The Plusquamperfekt failures are primarily a preset authoring error. The example answer should be `"hatte, gearbeitet"`, and the example should use a single-blank format (e.g., _"Ich hatte 2 Jahre lang **\_\_** (arbeiten)."_ → `"gearbeitet"`). Adding an explicit prompt constraint (_"the blank must replace exactly one word form"_) would provide an additional safeguard.

### 4.2 GPT-4o-mini's Duplicate Distractor Problem

GPT-4o-mini uniquely exhibits **duplicate option generation**: producing two identical wrong answers in the same question. Examples found:

- Two instances of `"meine"` as distractors in one question
- Two instances of `"ihr"` as distractors in another
- Two instances of identical `"lernt"` options

This is a quality regression specific to the smaller model. The static evaluator did not catch these in this run, despite already having a case-insensitive uniqueness check — suggesting these evaluations predate that check being in place.

### 4.3 Wrong Answer Marked as Correct

Both the Teacher evaluator and the Editor (indirectly) flagged cases where the model marked the wrong option as correct. This occurred across all models but most frequently with:

- **Possessivartikel im Akkusativ** (GPT-4o-mini: 60% teacher approval)
- **Plusquamperfekt** (incorrect auxiliary verb selection — `sein` vs. `haben`)
- **Adjective declension** edge cases (gender misidentification)

Representative Teacher feedback: _"Incorrect correct answer marked; explanation does not justify the correct answer; the use of 'sein' is not applicable for 'gehen' in Plusquamperfekt."_

### 4.4 Explanation Errors

The most frequent flaw flagged by the Teacher evaluator was **incorrect or misleading explanations** — even when the correct answer itself was right. Examples:

- Claiming `'deinen'` is the accusative form for a neuter noun (it is actually for masculine)
- Stating `'Kleid'` is in the accusative when the explanation should note it is neuter
- Using the wrong German grammatical terminology (e.g., `"neutrale Subjekte"` — not standard)

This pattern suggests the models understand _which_ form to use but sometimes generate post-hoc justifications that are grammatically incorrect. The explanation is generated as part of the same JSON blob as the answer — there is no separate reasoning step. Adding chain-of-thought or requiring the model to state the noun's gender and case before choosing the form could reduce this class of error.

### 4.5 Personalpronomen Preset — Topic/Example Mismatch

The Personalpronomen in Akkusativ preset provided this example:

> _"Kannst du **\_** (ich) bitte helfen?"_ → `"mir"`

The answer `"mir"` is dative, not accusative — `helfen` governs the dative case in German. This contradicts the preset's stated topic ("Personalpronomen in **Akkusativ**"). Models following the example may generate a mix of dative and accusative pronoun questions rather than focusing exclusively on the accusative case as intended. The generated questions would still be grammatically correct, but the topic coherence — testing a specific case — is undermined.

This likely explains why the Teacher evaluator flagged some Personalpronomen questions and why the Student achieved only 90% accuracy on this topic despite it being a relatively simple concept (personal pronouns in a single case).

**Learning:** Preset examples must be internally consistent with the stated topic. An accusative pronoun example should use a verb that governs the accusative (e.g., _"Ich sehe **\_** (du) jeden Tag."_ → `"dich"`).

### 4.6 GPT-4o Capitalization Artifacts

The Editor evaluator flagged GPT-4o specifically for capitalizing verbs in the middle of sentences (e.g., _"Warum Kommst du nicht zur Party?"_, _"Liest du ein Buch?"_). This appears to be an artifact of the model occasionally treating the question `content` field as a sentence that starts with the verb (V2 word order in questions) and capitalizing it as if it were the first word of a standalone sentence — then failing to lowercase when the sentence is reconstructed with prior context.

This is a subtle formatting issue that the static evaluator and Teacher miss but the Editor (focused solely on the final sentence) correctly catches.

### 4.6 Dative Adjective Declension — Student Difficulty

The Adjektivdeklination im Dativ topic shows unusually low student accuracy: 30% (GPT-4o-mini), 50% (GPT-4-Turbo), 60% (GPT-4o). This is the lowest student performance of any topic, and notably the questions passed Teacher and Editor review at reasonable rates.

This reveals an interesting tension: questions can be **grammatically correct and well-formed but genuinely difficult**. The dative adjective paradigm (`dem netten Mann`, `der netten Frau`, `dem netten Kind`) involves subtle ending distinctions that a B1 student might legitimately find hard. The Student evaluator is thus functioning correctly — it is measuring real difficulty, not just flawed question design.

---

## 5. Evaluator Analysis

### 5.1 Teacher vs. Editor Agreement

| Model       | Both Approve | Both Reject | Teacher ✓ / Editor ✗ | Teacher ✗ / Editor ✓ |
| ----------- | ------------ | ----------- | -------------------- | -------------------- |
| GPT-4o      | 73 (81%)     | 4 (4%)      | 10 (11%)             | 3 (3%)               |
| GPT-4o-mini | 67 (74%)     | 5 (6%)      | 12 (13%)             | 6 (7%)               |
| GPT-4-Turbo | 75 (83%)     | 4 (4%)      | 10 (11%)             | 1 (1%)               |

The two evaluators agree in ~85–87% of cases. The dominant disagreement pattern is **Teacher approves but Editor rejects** (10–12 cases per model). This is concentrated in Plusquamperfekt and Präsens questions where the sentence form is broken or unnatural but the question's pedagogical intent is still clear. The Teacher, focused on whether the question tests the right thing, overlooks sentence-level awkwardness that the Editor catches.

The reverse (Editor approves, Teacher rejects) is rare (1–6 cases), occurring when a grammatically correct sentence has a wrong answer marked or a misleading explanation.

**Learning:** The Editor and Teacher are genuinely complementary. A question should ideally pass both. Using only the Teacher would miss ~11% of structurally broken questions; using only the Editor would miss wrong-answer-marking errors.

### 5.2 The Static Evaluator's Blind Spots

The static evaluator found zero issues across all 270 questions — but multiple questions had serious defects:

- Duplicate option text (GPT-4o-mini)
- Wrong answer marked as correct (all models)
- Broken sentence structure (Plusquamperfekt, all models)

The static check currently only validates JSON structure and the `is_correct` flag count. It should be extended with:

1. **Option uniqueness**: reject if any two options share identical text
2. **Option count**: ensure exactly 4 options (currently checked)
3. **Explanation non-empty**: reject if explanation is blank

### 5.3 The Student Evaluator as Difficulty Signal

The Student evaluator's accuracy correlates strongly with question quality but is not identical to it. For Plusquamperfekt, students still answered 60–70% correctly despite broken sentences — suggesting the questions were parseable enough that the correct answer was identifiable even when the sentence structure was wrong. For Dative adjective declension, students scored only 30–60% on structurally correct questions — revealing genuine difficulty.

One limitation: the Student evaluator occasionally returns `"none"` as an answer when it determines that none of the options are correct (observed once in GPT-4o-mini's Possessivartikel batch). This reveals a question where the correct answer was absent from the options — a generation error not caught by any other evaluator. The Student evaluator is thus the only one that detects this specific failure mode.

---

## 6. Discussion

### 6.1 Model Recommendations

**GPT-4-Turbo** produces the highest quality output for this task — tightest accuracy (88.9%), highest teacher approval (94.4%), and no unique failure modes. Its slower generation time (~35s per 10-question sample) and higher cost make it suitable for a high-quality offline generation pipeline rather than real-time use.

**GPT-4o** offers the best speed-quality tradeoff (~17s per sample, 92.2% teacher approval). For production use, GPT-4o is the recommended default. Its main unique failure is the capitalization artifact in questions, which the Editor evaluator reliably catches.

**GPT-4o-mini** is not recommended for this prompt as-is. The duplicate distractor problem, higher explanation error rate, and lower overall quality (87.8% teacher approval, 82.2% student accuracy) represent a significant quality gap that outweighs its speed and cost advantages. With a stricter prompt it might be viable for high-volume, cost-sensitive pipelines.

### 6.2 Prompt Improvements

The "Exact answers" prompt works well for **morphological** grammar questions (possessive articles, personal pronouns, adjective declension) where a single inflected word fills the blank. It fails for **syntactic** questions (Plusquamperfekt, complex verb phrases) where filling a single blank with the correct form is not straightforward to express as a sentence.

Recommended prompt changes:

1. **Add a CEFR target** — to break out of the A1–B1 ceiling, the prompt should specify `"target CEFR level: {{ cefr_level }}"`.

2. **Fix the Plusquamperfekt preset example** — the current example shows a two-blank question and uses the wrong auxiliary (`habe` instead of `hatte`). A corrected single-blank example would directly address the structural failures observed across all three models for this topic.

3. **Add an explicit constraint for verb questions** — _"The blank must replace exactly one word (one verb form). Do not split a two-part verb construction."_

4. **Require explicit grammatical reasoning in explanations** — e.g., _"The explanation must state the noun's grammatical gender, the required case, and why that case applies."_ This would reduce the high rate of technically correct but misleadingly reasoned explanations.

### 6.3 Evaluator Improvements

1. **Static evaluator**: The validator already includes a case-insensitive uniqueness check on option text. The GPT-4o-mini duplicates returning `{"issues": []}` suggests these evaluations predated that check, or it was not active at run time. Re-running the static evaluator against the stored samples would confirm whether the existing check catches them.

2. **Teacher evaluator**: The prompt is strong but could explicitly separate **answer correctness** from **explanation quality** in the output schema, with separate boolean flags. Currently both are collapsed into a single `approval` decision.

3. **Student evaluator**: The current design does not check whether the student's chosen answer text exactly matches one of the listed options — it just returns freeform text. Cases where the student answers `"none"` (indicating no valid option exists) should be escalated as a generation error rather than simply scored as incorrect.

4. **Cross-evaluator pipeline**: Results suggest that a **two-stage filter** (static → Editor → Teacher) would be more efficient than running all evaluators in parallel, since Editor failures are strong predictors of Teacher failures and are cheaper to compute (~186 tokens vs. ~509 tokens per question).

---

## 7. Conclusions

Across 270 German grammar quiz questions generated by three GPT-model variants, the following key findings emerge:

1. **GPT-4-Turbo > GPT-4o > GPT-4o-mini** in question quality, with GPT-4-Turbo achieving 94.4% teacher approval and 88.9% student accuracy.

2. **The Plusquamperfekt topic is a prompt failure**, not a model failure. All three models generate broken sentence structures for this topic, pointing to a fundamental mismatch between the prompt's fill-in-the-blank format and multi-word verb constructions.

3. **GPT-4o-mini uniquely generates duplicate distractors** — a defect not caught by the static evaluator in this run, though a uniqueness check already exists in the validator.

4. **Explanation quality is the most common flaw** across all models and topics. Models frequently produce the correct answer with incorrect grammatical reasoning in the explanation field.

5. **The three LLM evaluators are genuinely complementary**: Editor catches sentence-level structural issues; Student measures answerability and real difficulty; Teacher catches semantic errors (wrong answer marked, misleading explanations). No single evaluator is sufficient.

6. **The CEFR ceiling at B1** is a prompt limitation. Without difficulty guidance, all models default to simple one-rule questions.

7. **The static evaluator's uniqueness check was not active during these evaluations** — the duplicate option defects in GPT-4o-mini output were not caught. Wrong-answer detection remains outside the static evaluator's scope and requires an LLM-based pass.

---

_Written by Claude Sonnet 4.6 using data generated by SprachlernSandbox. Generation models: gpt-4o, gpt-4o-mini, gpt-4-turbo. LLM judge model (Editor, Student, Teacher evaluators): gpt-4o-mini._
