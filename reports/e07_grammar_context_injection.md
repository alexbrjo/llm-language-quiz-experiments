# E07: Grammar Context Injection for Question Generation

**Experiment:** e07
**Date:** 2026-04-02
**Model:** `mlx-community/Qwen3.5-9B-MLX-4bit` (local, MLX adapter)
**LLM Judge:** `gpt-4o` (temperature 0.1, json_mode)

---

## Abstract

This experiment held the generation model constant and varied the grammar knowledge injected into the prompt. Eight conditions spanned from a bare topic label (no-shot) to a full textbook compressed into the prompt. A total of 2,145 fill-in-the-blank questions were generated across all conditions and evaluated by a 4-evaluator pipeline (Static, Editor, Student, Teacher). The two best-performing conditions were **LLM-compressed full textbook (68.2% all-pass)** and **few-shot examples (67.0%)**, both substantially outperforming the no-shot baseline (28.2%). Surprisingly, section-level textbook context (conditions 4-6) did not clearly outperform a simple 1-shot example, while the full LLM-compressed textbook dramatically outperformed the full rule-compressed textbook (68.2% vs 47.4%). Notably, the best context injection condition (68.2%) exceeded the 4-bit model's e06 score of 48% by 20 points and approximately matched the 8-bit model's e06 score of 66%.

---

## 1. Experimental Setup

### 1.1 Model and Configuration

| Parameter              | Value                                         |
| ---------------------- | --------------------------------------------- |
| Model                  | `mlx-community/Qwen3.5-9B-MLX-4bit`          |
| Adapter                | MLX (local Apple Silicon inference)           |
| Output Mode            | `json_schema` (Outlines)                      |
| Max Tokens             | 1024                                          |
| Temperature            | default                                       |
| Questions per sample   | 5                                             |

### 1.2 Conditions

| # | Condition                   | Context Injected                                                    |
|---|----------------------------|---------------------------------------------------------------------|
| 1 | No-shot                    | Topic label only                                                    |
| 2 | 1-shot                     | Topic label + 1 example question with answer                        |
| 3 | Few-shot                   | Topic label + 3-5 example questions                                 |
| 4 | Raw textbook section       | Relevant chapter, unprocessed                                       |
| 5 | LLM-compressed section     | Chapter distilled by LLM into concise grammar rules                 |
| 6 | Rule-compressed section    | Chapter with exercises/dialogues stripped programmatically           |
| 7 | LLM-compressed full        | All grammar rules across all topics, LLM-distilled (~20k tokens)    |
| 8 | Rule-compressed full       | Full textbook with exercises/dialogues stripped (~100k tokens)       |

Conditions 1-6 used a shared prompt template with per-condition data files. Conditions 7-8 used dedicated prompt templates with the full textbook baked directly into the template text.

### 1.3 Sampling

- **Strategy:** Exhaustive (all topics per repeat)
- **Repeats:** 3
- **Topics:** Up to 20 per condition (topic coverage varied by data file)
- **Samples generated:** 60 per condition (480 total)

### 1.4 Evaluators

| Evaluator | Type     | Purpose                                                     |
|-----------|----------|-------------------------------------------------------------|
| Static    | Rules    | Structural validation (answer, explanation, blank present)  |
| Editor    | gpt-4o   | Grammatical correctness of the answered sentence            |
| Student   | gpt-4o   | Model attempts to produce the correct answer                |
| Teacher   | gpt-4o   | Model sees the entire question content                      |

A question passed the **all-pass** criterion only if it passed all four evaluators.

---

## 2. Results

### 2.1 Overall Results

| # | Condition                   |   N | All-Pass |  Rate | Static | Editor | Student | Teacher |
|---|----------------------------|----:|---------:|------:|-------:|-------:|--------:|--------:|
| 1 | No-shot                    | 255 |       72 | 28.2% | 100.0% |  67.1% |   52.5% |   51.8% |
| 2 | 1-shot                     | 240 |      120 | 50.0% | 100.0% |  82.5% |   70.0% |   65.0% |
| 3 | Few-shot                   | 285 |      191 | 67.0% | 100.0% |  82.1% |   81.1% |   76.1% |
| 4 | Raw textbook section       | 285 |      144 | 50.5% |  98.9% |  80.0% |   62.5% |   70.5% |
| 5 | LLM-compressed section     | 255 |       86 | 33.7% | 100.0% |  72.2% |   61.6% |   64.7% |
| 6 | Rule-compressed section    | 285 |      146 | 51.2% |  98.9% |  81.1% |   65.3% |   71.6% |
| 7 | LLM-compressed full        | 255 |      174 | 68.2% | 100.0% |  80.0% |   78.4% |   80.8% |
| 8 | Rule-compressed full       | 285 |      135 | 47.4% | 100.0% |  80.0% |   67.4% |   74.4% |

**Ranking by all-pass rate:**
1. Cond 7 — LLM-compressed full textbook: **68.2%**
2. Cond 3 — Few-shot: **67.0%**
3. Cond 6 — Rule-compressed section: **51.2%**
4. Cond 4 — Raw textbook section: **50.5%**
5. Cond 2 — 1-shot: **50.0%**
6. Cond 8 — Rule-compressed full: **47.4%**
7. Cond 5 — LLM-compressed section: **33.7%**
8. Cond 1 — No-shot: **28.2%**

### 2.2 Question Yield

Not all conditions produced the expected 300 questions (60 samples x 5 questions/sample). Some data files covered fewer than 20 topics, and some samples yielded fewer than 5 extractable questions.

| Condition | Expected | Actual | Yield  | Topics Covered |
|-----------|----------|--------|--------|----------------|
| 1         | 300      | 255    | 85.0%  | 17             |
| 2         | 300      | 240    | 80.0%  | 16             |
| 3         | 300      | 285    | 95.0%  | 19             |
| 4         | 300      | 285    | 95.0%  | 19             |
| 5         | 300      | 255    | 85.0%  | 17             |
| 6         | 300      | 285    | 95.0%  | 19             |
| 7         | 300      | 255    | 85.0%  | 17             |
| 8         | 300      | 285    | 95.0%  | 19             |

Total questions generated: **2,145** across all conditions.

---

## 3. Per-Topic Analysis

All-pass rates per topic, ordered by average performance. `--` indicates the topic was not present in that condition's data file.

| Topic                                    |   C1 |   C2 |   C3 |   C4 |   C5 |   C6 |   C7 |   C8 |
|------------------------------------------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| Personalpronomen in Akkusativ            |  33% | 100% | 100% | 100% |   -- | 100% |  80% |  67% |
| Adjektivdeklination im Nominativ         |  60% |  87% |  80% |  93% |  40% |  87% |  93% | 100% |
| Relativpronomen                          |  80% |  73% | 100% |  40% |  87% |  20% |  67% |  87% |
| Futur I                                  |   0% |  60% |  80% |  60% |  80% |  60% | 100% | 100% |
| Adjektivdeklination im Dativ             |   0% |  20% |  40% |  80% |  87% |  80% | 100% |  73% |
| Adjektivdeklination im Akkusativ         |  60% |  20% |  80% | 100% |  20% | 100% |  40% |  53% |
| Konjugation im Präsens                   |  60% |  60% |  60% |  60% |  60% |  60% | 100% |  80% |
| Nebensätze mit weil, dass, obwohl        |   7% |   -- |  53% |  47% |   -- |  60% | 100% |  60% |
| Konjugation im Präteritum                |  27% |  60% |  73% |  93% |  47% |  93% |  53% |  53% |
| Reflexivpronomen im Akkusativ und Dativ  |  60% |  20% |  80% |  40% |   0% |  40% |  20% |   -- |
| Personalpronomen in Dativ                |  27% |  60% |  67% |  40% |  40% |  40% | 100% |  40% |
| Hilfsverb in Perfekt                     |   -- |  60% |  80% |  40% |   7% |  40% |   -- |  33% |
| Negation mit "nicht" und "kein"          |  20% |  53% |  40% |   0% |  20% |   0% |  80% |   0% |
| Artikelbestimmung (der/die/das)          |   0% |   -- |  80% |  80% |   0% |  80% | 100% |   0% |
| Präpositionen mit Akkusativ              |   0% |   -- |  60% |  60% |  60% |  60% |  53% |  33% |
| Konjunktiv II (Höflichkeitsform)         |   0% |  40% |   -- |  20% |  13% |  20% |  47% |  33% |
| Konjugation im Perfekt                   |   -- |  20% |  80% |   7% |   7% |  20% |   -- |  20% |
| Passiv im Präsens                        |  20% |  47% |   0% |   -- |   7% |   -- |   -- |  40% |
| Wechselpräpositionen                     |  27% |  20% |  93% |   0% |   0% |   0% |   0% |   0% |
| Präpositionen mit Dativ                  |   -- |   -- |  27% |   0% |   -- |  13% |  27% |  27% |

### 3.1 Key Observations by Topic

**Consistently easy topics** (>60% across most conditions):
- **Personalpronomen in Akkusativ** — Straightforward substitution pattern. Reached 100% in most conditions with any context.
- **Adjektivdeklination im Nominativ** — Common grammar pattern that the model handled well even without context.

**Topics where context helps most** (large gap between C1 and best):
- **Futur I** — 0% no-shot to 100% with full LLM-compressed context. The no-shot model produced multi-word answers ("werde kaufen") but placed them incorrectly in the sentence, creating word-order failures.
- **Adjektivdeklination im Dativ** — 0% no-shot to 100% in C7. The model struggled with dative adjective endings without explicit paradigm tables.
- **Nebensätze** — 7% no-shot to 100% in C7. Word order in subordinate clauses is a complex rule that benefited from explicit reference.

**Topics that remain hard across all conditions:**
- **Wechselpräpositionen** — 93% in few-shot (C3) but 0% in all textbook conditions (C4-C8). The textbook context may have confused the model with competing rules for accusative vs. dative.
- **Konjugation im Perfekt** — Below 20% in most conditions except few-shot (80%). The model frequently produced incorrect past participles.
- **Präpositionen mit Dativ** — Below 30% everywhere. Complex preposition-case mappings were poorly handled even with explicit rules.

---

## 4. Failure Mode Analysis

### 4.1 Failure Patterns

A question could fail one or more of the three LLM evaluators (Static passed at 98.9-100% and was not a significant failure source). The failure pattern distribution:

| Pattern                        | Count | % of Failures | Description |
|--------------------------------|------:|:-------------:|-------------|
| Student only                   |   305 |         28.3% | Question was correct, but the simulated student gave a different answer |
| Editor + Student + Teacher     |   231 |         21.4% | Fundamental correctness issue — wrong answer, wrong grammar, wrong word order |
| Teacher only                   |   198 |         18.4% | Question was grammatically correct but Teacher flagged topic mismatch or explanation quality |
| Editor + Teacher               |   122 |         11.3% | Answer was grammatically wrong, Teacher also flagged it |
| Student + Teacher              |   101 |          9.4% | Teacher and Student both disagreed with the provided answer |
| Editor + Student               |    62 |          5.8% | Grammar error that prevented the student from arriving at the expected answer |
| Editor only                    |    52 |          4.8% | Minor grammar issue (e.g., preposition choice) but Student and Teacher still passed |
| Static only                    |     6 |          0.6% | Structural issue (missing field) |

**Total failures:** 1,077 / 2,145 questions (50.2%)

**Note on evaluator reliability:** The evaluators used gpt-4o, which is not ground truth. Some failures — particularly Student-only and Teacher-only rejections — may have been evaluator errors rather than genuine generation defects. E05 found that at high quality levels, a meaningful fraction of Teacher rejections were false negatives. The triple-failure pattern (Editor + Student + Teacher) is the most reliable indicator of genuine correctness issues, as three independent evaluators agreeing on failure is unlikely to be coincidental.

### 4.2 Failure Category: Genuine Correctness Errors (Triple Failures)

231 questions (21.4% of failures) failed all three LLM evaluators, indicating fundamentally incorrect output. These fell into three subcategories:

**A. Word order errors (Futur I, Nebensätze)**
The model generated multi-word answers (e.g., "werde kaufen") that, when inserted into the blank, produced incorrect word order. In German, the infinitive in Futur I must go to the end of the clause, but the model's answered sentence placed it in the middle:

> Q: `Ich _____ (kaufen) morgen ein neues Buch.`
> A: `werde kaufen`
> Answered: `Ich werde kaufen morgen ein neues Buch.` (wrong)
> Correct: `Ich werde morgen ein neues Buch kaufen.`

This is a structural problem with FITB format for multi-word answers — the blank position cannot accommodate verb-final word order.

**B. Wrong declension/conjugation**
The model provided an incorrect grammatical form as the answer, with the correct form as the hint (ideally the hint is the base form):

> Q: `Das Kind trinkt das _____ (kalte) Wasser.`
> A: `kalten` (wrong — should be `kalte` for accusative neuter with definite article)

> Q: `Der Lehrer liest _____ (alte) Geschichten den Kindern vor.`
> A: `alten` (wrong — `Geschichten` is accusative plural, needs `alte`)

**C. Topic-misaligned questions**
Questions that tested a different grammar point than the stated topic:

> Topic: Adjektivdeklination im Nominativ
> Q: `Ich habe einen _____ (rot) Ball gekauft.`
> A: `roten`
> (Actually tested accusative, not nominative)

### 4.3 Failure Category: Student Disagreements (305 cases)

The largest failure category: the Student evaluator produced a different answer than expected. Two subcategories:

**A. Student evaluator errors**
The Student evaluator (which did not see the topic label) sometimes gave an incorrect answer, producing a false negative. For example:

> Q: `Die _____ (schön) Blumen duften stark.`
> Expected: `schönen` | Student answered: `schöne`

`schönen` is unambiguously correct — plural nominative with definite article requires the weak ending -en. The Student's answer was wrong, making this an evaluator error rather than a generation defect.

**B. Poorly-constructed blanks**
Some questions, especially for Artikelbestimmung, placed the wrong word in the blank:

> Q: `Der _____ (Hund) bellt laut auf dem Hof.`
> Expected: `Hund` | Student answered: `der`

The model produced a question where the blank was the noun itself (already visible in the hint), not the article. The student reasonably filled in the article instead. This pattern accounted for most Artikelbestimmung failures.

### 4.4 Failure Category: Teacher-Only Rejections (198 cases)

Questions that passed Editor and Student but were rejected by Teacher, usually for:

- **Explanation quality:** The answer was correct but the explanation cited the wrong rule
- **Topic mismatch:** The question tested a valid grammar point but not the one specified
- **Contextual awkwardness:** The sentence was grammatically correct but pragmatically odd ("Ich sehe mich jeden Tag" — syntactically valid but semantically unusual)

---

## 5. Comparison to E06 Baseline

E06 tested Qwen3.5-9B-MLX-4bit under a 1-shot prompt and measured 48% all-pass. E07's Condition 2 (1-shot) scored 50.0%. These were broadly consistent, though not directly comparable — the prompt template, data files, topic set, and sample size differed between experiments. The comparison is directional, not exact.

E06 concluded that the 4-bit model's "local model quality ceiling is 66%" (the 8-bit score) and that 48% "is not viable for production use." E07 challenged both claims:

| Configuration                     | All-Pass | Source |
|-----------------------------------|---------|--------|
| Qwen3.5-9B-4bit, 1-shot (e06)    |    48%  | e06    |
| Qwen3.5-9B-8bit, 1-shot (e06)    |    66%  | e06    |
| Qwen3.5-9B-4bit, 1-shot (e07 C2) |    50%  | e07    |
| Qwen3.5-9B-4bit, few-shot (e07 C3) |  67%  | e07    |
| Qwen3.5-9B-4bit, LLM-full (e07 C7) | 68%  | e07    |

Context injection appeared to recover quality in a similar range to what quantization lost, though the cross-experiment comparison is approximate (different prompts, data files, and sample sizes). The directional finding — that prompt-side knowledge augmentation can partially compensate for model capacity — holds, but the exact magnitude should not be over-interpreted.

E06 identified three failure modes specific to the 4-bit model: incorrect declension endings, topic misalignment, and hint quality issues. Context injection partially addressed these:
- **Declension errors** were reduced in C3 and C7 (paradigm tables in context helped the model pick correct endings)
- **Topic misalignment** persisted — some questions still tested the wrong grammar point regardless of context
- **Hint quality** (using inflected forms instead of base forms as hints) was not systematically measured in e07 but appeared less frequently in manual spot-checks of C7 output

---

## 6. Condition Comparison (Within E07)

### 6.1 Example-Based vs. Textbook-Based Context

| Approach                | Best Condition      | All-Pass |
|-------------------------|--------------------|---------:|
| Example-based (C1-C3)   | Few-shot (C3)      |    67.0% |
| Section textbook (C4-C6)| Rule-compressed (C6)|   51.2% |
| Full textbook (C7-C8)   | LLM-compressed (C7)|   68.2% |

Few-shot examples and the full LLM-compressed textbook tied for best performance, both roughly doubling the no-shot baseline. Paradoxically, section-level textbook context (the focused, topic-specific approach) did not outperform a simple 1-shot example. This contradicted the intuition that focused context should be more useful than either broad context or few examples.

### 6.2 LLM Compression vs. Rule Compression

| Scope   | LLM-Compressed | Rule-Compressed | Delta |
|---------|---------------:|----------------:|------:|
| Section | 33.7% (C5)     | 51.2% (C6)      | -17.5 |
| Full    | 68.2% (C7)     | 47.4% (C8)      | +20.8 |

LLM compression produced opposite effects at different scales:
- **Section level:** LLM compression *hurt* — C5 (33.7%) was worse than C6 (51.2%) and even worse than C1 no-shot for some topics. The LLM may have over-compressed single-chapter content, losing critical paradigm tables.
- **Full textbook level:** LLM compression *helped dramatically* — C7 (68.2%) was 20.8 points above C8 (47.4%). At full-textbook scale, the LLM effectively synthesized cross-chapter rules into a coherent reference, while the rule-compressed full textbook (~100k tokens) may have overwhelmed the model's attention.

### 6.3 Context Volume vs. Quality

The relationship between prompt context size and quality was non-monotonic:

| Context Size   | Condition(s)     | All-Pass |
|----------------|------------------|---------:|
| ~10 tokens     | C1 (no-shot)     |    28.2% |
| ~80 tokens     | C2 (1-shot)      |    50.0% |
| ~250-400 tokens| C3 (few-shot)    |    67.0% |
| ~500-1.5k      | C5 (LLM section) |    33.7% |
| ~1-3k          | C6 (rule section)|    51.2% |
| ~2-5k          | C4 (raw section) |    50.5% |
| ~20k           | C7 (LLM full)    |    68.2% |
| ~100k          | C8 (rule full)   |    47.4% |

Quality peaked at two points: (1) at ~250-400 tokens with well-crafted few-shot examples, and (2) at ~20k tokens with LLM-compressed full-textbook context. Larger raw context (~100k) degraded performance relative to the LLM-compressed version, suggesting that for this model, context quality mattered more than volume.

---

## 7. Hypothesis Evaluation

| # | Hypothesis | Result |
|---|-----------|--------|
| H1 | 1-shot significantly outperforms no-shot | **Confirmed.** 50.0% vs 28.2% (+21.8 points) |
| H2 | Few-shot outperforms 1-shot with diminishing returns | **Confirmed.** 67.0% vs 50.0% (+17.0 points) |
| H3 | LLM-compressed section matches or beats raw section | **Rejected.** LLM-compressed section (33.7%) was the worst non-baseline condition. Over-compression at section level. |
| H4 | Section-level context outperforms full-textbook context | **Rejected.** Full LLM-compressed (68.2%) beat all section-level conditions. Broad context won over focused context. |
| H5 | Context injection shows larger gains on harder topics | **Mixed.** Some hard topics (Futur I, Nebensätze) showed large gains; others (Wechselpräpositionen, Präpositionen mit Dativ) remained hard regardless. |
| H6 | No condition significantly reduces ambiguity failures | **Confirmed.** Student-only failures were the largest category across all conditions. |
| H7 | LLM-compressed section is the optimal cost-quality tradeoff | **Rejected.** Few-shot (C3) achieved similar quality with much less preparation cost. |

---

## 8. Limitations

1. **Unequal topic coverage.** Not all 20 topics appeared in every condition's data file (topic coverage ranged from 16 to 19). This made direct per-topic comparisons across conditions imperfect for topics with missing conditions.

2. **Question yield varied.** Conditions produced 240-285 questions instead of the expected 300, due to incomplete topic coverage and some samples producing fewer than 5 extractable questions.

3. **Multi-word answer problem.** The FITB format inherently struggles with answers that are multi-word (e.g., "werde kaufen" for Futur I), because simple blank substitution breaks German word order. This disproportionately penalized conditions that produced more multi-word answers.

4. **Student evaluator without topic.** The Student evaluator did not see the grammar topic being tested. This made it a stronger test of question quality (a good question should be answerable without knowing the topic), but also meant correct questions with subtle grammar points could fail if the student applied a different rule.

5. **Evaluator false negatives.** As noted in e05, at moderate-to-high quality levels, a meaningful fraction of Teacher rejections were evaluator errors rather than genuine model failures. Some Teacher-only rejections (198 cases) likely included false negatives.

6. **Single model.** Results are specific to Qwen3.5-9B-MLX-4bit. A more capable model might show different sensitivity to context injection. Conversely, a weaker model might benefit more from explicit context.

---

## 9. Conclusions

1. **Context injection worked, but the form mattered more than the volume.** The two best conditions — few-shot examples (67.0%) and LLM-compressed full textbook (68.2%) — used very different amounts of context but both presented grammar knowledge in a well-structured, directly actionable format. Raw or programmatically-stripped textbook content at any scale performed worse.

2. **Few-shot examples were the best cost-quality tradeoff.** At 67.0% all-pass with ~250-400 tokens of context, few-shot provided nearly the same quality as the LLM-compressed full textbook (68.2% at ~20k tokens) with far less preparation effort and faster inference.

3. **LLM compression scaled well but not down.** At full-textbook scale, LLM compression produced the best single condition. At section scale, it produced the second-worst condition. The LLM appeared to be better at synthesizing broad knowledge than at summarizing narrow content.

4. **Many failures were reasoning problems, not knowledge problems.** Multi-word answers with broken word order, topic-misaligned blanks, and ambiguous sentences accounted for a large share of failures. These required the model to reason about German syntax and self-verify its output — capabilities that context injection alone cannot provide. A more capable model (as e06 showed with Claude Sonnet at 98%) handled these cases correctly, suggesting that the remaining 30% failure rate was bounded by the model's reasoning capacity rather than by what was in the prompt.

5. **Context injection may partially compensate for quantization.** The 4-bit model with few-shot or LLM-compressed full context (67-68% all-pass) reached a similar range to the 8-bit model's e06 baseline (66%), though the experiments were not directly comparable (different prompts, data, sample sizes). The directional finding suggests that with the right prompt, the 4-bit model can be competitive with the 8-bit model at lower memory cost.

6. **Recommended local model configuration:** Few-shot (Condition 3) with 3-5 hand-crafted examples per topic. If full-textbook context is available and latency is acceptable, LLM-compressed full textbook (Condition 7) provided a marginal additional benefit. Note that even the best local model configuration (68.2%) remained far below API models — Claude Sonnet 4.6 achieved 98% all-pass in e06 with 1-shot prompting.

---

_Written by Claude Opus 4.6 using data generated by LLMContentForge. Generation model: Qwen3.5-9B-MLX-4bit (local). LLM judge model (Editor, Student, Teacher evaluators): gpt-4o._
