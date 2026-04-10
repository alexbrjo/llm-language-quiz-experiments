# E07: Textbook Context Injection Strategies

**Experiment:** e07 (rerun)
**Date:** 2026-04-10
**Model:** `mlx-community/Qwen3.5-9B-MLX-4bit` (local, MLX adapter)
**LLM Judge:** `gpt-4o`

---

## Abstract

This experiment evaluates whether injecting textbook content into a 1-shot prompt improves fill-in-the-blank German grammar question quality on a small local model. Six conditions were tested, all sharing the same 1-shot example per topic, varying only in what additional textbook content was injected: none (control), raw textbook section, rule-compressed section, LLM-compressed section, rule-compressed full textbook (~100k tokens), and LLM-compressed full textbook (~20k tokens). A total of 1,528 questions were generated across all conditions and evaluated by a 4-evaluator pipeline. **No textbook injection condition meaningfully outperformed the 1-shot control (54.2% all-pass).** The best-performing condition, LLM-compressed section (58.0%), exceeded the control by 3.8 points — within the margin of statistical noise for these sample sizes. All five textbook conditions clustered in a tight 3.8-point range (54.5% to 58.0%), and both full-textbook conditions (55.3% and 56.1%) performed indistinguishably from their section-level counterparts despite injecting 5-40x more content. The primary finding is that unstructured or structurally-processed textbook content, regardless of scope or compression method, provides no detectable quality improvement over a single well-chosen example for this model. Failure modes were dominated by multi-word answer format mismatches, evaluator errors, and a handful of topics (Wechselpräpositionen, Passiv im Präsens, Konjugation im Perfekt) that the model struggled with regardless of injected context.

**Note on experimental history.** A previous run of e07 tested 8 conditions, several of which lacked the 1-shot example. The inconsistent baselines made the results difficult to interpret. This rerun holds the 1-shot example constant across all conditions so that differences reflect the value of textbook injection alone. A concurrent condition with hand-curated few-shot examples was also run and scored 70.6% all-pass; because few-shot examples introduce frontier-model-curated pedagogical content rather than raw textbook material, they represent a different experimental variable and are omitted from this report to keep the ablation clean. Section 5 briefly contextualizes the few-shot result.

---

## 1. Experimental Setup

### 1.1 Model and Configuration

| Parameter              | Value                                         |
| ---------------------- | --------------------------------------------- |
| Model                  | `mlx-community/Qwen3.5-9B-MLX-4bit`          |
| Adapter                | MLX (local Apple Silicon inference)           |
| Output Mode            | `json_schema` (Outlines)                      |
| Max Tokens             | 1024                                          |
| Temperature            | 0.3                                           |
| Thinking mode          | Disabled (`enable_thinking=False`)            |
| Questions per sample   | 5                                             |

### 1.2 Conditions

All conditions include an identical 1-shot example question per topic. They differ only in what additional textbook content is injected into the prompt.

| # | Condition | Textbook Content Injected |
|---|-----------|---------------------------|
| 1 | 1-shot control           | None                                                                |
| 2 | Raw section              | The relevant textbook section, unprocessed                          |
| 3 | Rule-compressed section  | The relevant section with exercise lines stripped programmatically  |
| 4 | LLM-compressed section   | The relevant section distilled by an LLM into concise grammar rules |
| 5 | Rule-compressed full     | The entire textbook with exercises stripped (~100k tokens)          |
| 6 | LLM-compressed full      | All grammar rules across all topics, LLM-distilled (~20k tokens)    |

Conditions 1-4 used a shared prompt template with per-condition data files. Conditions 5-6 used dedicated prompt templates with the full textbook baked directly into the template text and the 1-shot example injected via data file variables.

### 1.3 Textbook Source and Section Alignment

The source material was a 300-page CC-licensed German grammar textbook, extracted to markdown via marker-pdf. For section-level conditions (2-4), the correct textbook section had to be identified for each of the 20 grammar topics. Topics were mapped to sections manually, verified against the textbook's table of contents.

Of the 20 topics, 19 have dedicated or clearly-aligned sections in the textbook. **Negation mit "nicht" und "kein"** has no dedicated section; the closest available content (the "Ein-Words" section, which covers "kein" as an indefinite article variant) was used but does not address "nicht" placement. Several topics share sections because the textbook doesn't separate them: all three Adjektivdeklination cases share the "Adjective Endings" section, both Personalpronomen topics share "Pronouns (All Cases)", and both case-specific Präpositionen topics share the "Prepositions" section. These imperfections were left in place as a best-effort test of how content injection behaves with realistic, imperfect source data — the kind practitioners would actually encounter when pointing RAG or static injection at an existing corpus.

### 1.4 Sampling

- **Strategy:** Exhaustive (all topics per pass)
- **Passes:** 3
- **Topics:** 20 per condition
- **Samples generated:** 60 per condition (360 total)

### 1.5 Evaluators

| Evaluator | Type     | Purpose                                                              |
|-----------|----------|----------------------------------------------------------------------|
| Static    | Rules    | Structural validation (answer, explanation, blank present)           |
| Editor    | gpt-4o   | Grammatical correctness of the answered sentence                     |
| Student   | gpt-4o   | Simulated student attempts to produce the correct answer             |
| Teacher   | gpt-4o   | Expert audit of question quality, answer correctness, topic alignment|

A question passed the **all-pass** criterion only if it passed all four evaluators.

---

## 2. Results

### 2.1 Overall Results

| # | Condition               |   N | All-Pass |  Rate | Static | Editor | Student | Teacher |
|---|-------------------------|----:|---------:|------:|-------:|-------:|--------:|--------:|
| 1 | 1-shot control          | 225 |      122 | 54.2% |  99.6% |  76.9% |   67.1% |   79.1% |
| 2 | Raw section             | 233 |      127 | 54.5% |  99.6% |  76.4% |   73.4% |   78.1% |
| 3 | Rule-compressed section | 260 |      144 | 55.4% |  99.6% |  71.9% |   71.5% |   82.3% |
| 4 | LLM-compressed section  | 250 |      145 | 58.0% | 100.0% |  79.6% |   73.6% |   85.6% |
| 5 | Rule-compressed full    | 285 |      160 | 56.1% |  96.5% |  71.6% |   76.1% |   84.6% |
| 6 | LLM-compressed full     | 275 |      152 | 55.3% |  96.4% |  78.2% |   71.3% |   82.2% |

**Ranking by all-pass rate:**
1. LLM-compressed section: **58.0%**
2. Rule-compressed full: **56.1%**
3. Rule-compressed section: **55.4%**
4. LLM-compressed full: **55.3%**
5. Raw section: **54.5%**
6. 1-shot control: **54.2%**

The entire range from best to worst spans 3.8 percentage points. The 95% confidence intervals on the individual rates and on the between-condition differences are both wide enough to contain zero:

| Condition                | Rate  | 95% CI |
|--------------------------|:-----:|:------:|
| 1-shot control           | 54.2% |  ±6.5  |
| Raw section              | 54.5% |  ±6.4  |
| Rule-compressed section  | 55.4% |  ±6.0  |
| LLM-compressed section   | 58.0% |  ±6.1  |
| Rule-compressed full     | 56.1% |  ±5.8  |
| LLM-compressed full      | 55.3% |  ±5.9  |

Individual CIs are computed as `1.96 * sqrt(p*(1-p)/n)`. For the largest observed gap (LLM-compressed section 58.0% vs 1-shot control 54.2%, +3.8 points), the 95% CI of the difference is `1.96 * sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2) = ±8.9` points, which easily contains zero. A two-proportion z-test gives z = 0.83, p ≈ 0.41 — nowhere near significance. No condition is statistically distinguishable from the control or from any other condition.

### 2.2 By Scope

| Scope      | Conditions                                    | Avg All-Pass |
|------------|-----------------------------------------------|:------------:|
| No textbook| 1-shot control                                |   54.2%      |
| Section    | Raw, rule-compressed, LLM-compressed section  |   56.0%      |
| Full text  | Rule-compressed full, LLM-compressed full     |   55.7%      |

Section-level and full-textbook injection produced essentially identical averages, despite full-textbook conditions injecting 5-40x more content. This suggests the additional content in the full-textbook conditions provided no useful signal that wasn't already available in the focused section.

### 2.3 By Compression Method

Holding scope constant, compare LLM-compression vs rule-compression:

| Scope   | LLM-Compressed | Rule-Compressed | Delta |
|---------|---------------:|----------------:|------:|
| Section | 58.0%          | 55.4%           | +2.6  |
| Full    | 55.3%          | 56.1%           | -0.8  |

LLM compression did not consistently outperform rule compression. At section scope, LLM compression was slightly ahead (+2.6 points, 95% CI of difference ±8.6). At full-textbook scope, LLM compression was slightly behind (-0.8 points, 95% CI of difference ±8.2). Both observed differences are well within the noise floor.

### 2.4 Question Yield

Each condition ran 60 samples (3 passes × 20 topics) requesting 5 questions per sample, for an expected yield of 300 questions per condition.

| Condition               | Samples | Expected | Generated | Yield |
|-------------------------|--------:|---------:|----------:|------:|
| 1-shot control          |      60 |      300 |       225 | 75.0% |
| Raw section             |      60 |      300 |       233 | 77.7% |
| Rule-compressed section |      60 |      300 |       260 | 86.7% |
| LLM-compressed section  |      60 |      300 |       250 | 83.3% |
| Rule-compressed full    |      60 |      300 |       285 | 95.0% |
| LLM-compressed full     |      60 |      300 |       275 | 91.7% |

Total questions evaluated: **1,528**.

Full-textbook conditions had noticeably higher yield (91.7-95.0%) than the control (75.0%). This is a confound worth flagging: higher-yield conditions may include lower-quality marginal questions that raise N without raising the pass count proportionally. If the full-textbook conditions had the same yield as the control, their all-pass rates might look slightly better in absolute terms — but since they underperform even at inflated N, the conclusion holds.

### 2.5 Generation Statistics

| Condition               | Avg Prompt Tokens | Avg Latency |
|-------------------------|------------------:|------------:|
| 1-shot control          |               413 |       12.6s |
| Raw section             |             1,563 |       15.0s |
| Rule-compressed section |             1,439 |       14.9s |
| LLM-compressed section  |             1,163 |       14.1s |
| LLM-compressed full     |             7,579 |       29.9s |
| Rule-compressed full    |            46,421 |      140.1s |

Rule-compressed full textbook conditions used ~112x more prompt tokens and were ~11x slower than the control, for zero quality improvement. The latency numbers reflect uncached prompts — in a production setting, the full-textbook portion of the prompt would be static across samples and could be served from a prompt cache (KV cache on local inference, or provider-side caching on hosted APIs), dramatically reducing per-sample latency after the first call. Token counts are unaffected by caching, but compute/latency costs can be amortized. Even with prompt caching, however, the quality remains unchanged — the injected content is not useful signal regardless of how cheaply it can be served.

---

## 3. Per-Topic Analysis

All-pass rates by topic and condition. With n=5-15 per topic per condition, individual cells are noisy; focus on patterns across rows.

| Topic                                              | Ctrl | Raw  | Rule-S | LLM-S | Rule-F | LLM-F |
|----------------------------------------------------|-----:|-----:|-------:|------:|-------:|------:|
| Adjektivdeklination im Nominativ                   |  80% |  70% |    53% |   87% |    73% |   67% |
| Adjektivdeklination im Akkusativ                   |  53% |  70% |    67% |   80% |    40% |   73% |
| Adjektivdeklination im Dativ                       |  67% |  62% |    87% |   53% |    93% |   87% |
| Artikelbestimmung (der/die/das)                    | 100% |  80% |    73% |   67% |    67% |   20% |
| Futur I                                            |  67% |  67% |    80% |   80% |    93% |   67% |
| Hilfsverb in Perfekt                               |  80% |  60% |    47% |   53% |    60% |   50% |
| Konjugation im Perfekt                             |  20% |   0% |     7% |    0% |    10% |   20% |
| Konjugation im Präsens                             |  90% |  87% |    87% |  100% |    80% |   93% |
| Konjugation im Präteritum                          |  53% |  60% |    87% |   87% |    60% |   67% |
| Konjunktiv II (Höflichkeitsform)                   |  60% |  47% |    40% |   40% |    20% |   53% |
| Nebensätze mit "weil", "dass", "obwohl"            |  20% |   -- |    70% |   80% |    53% |   60% |
| Negation mit "nicht" und "kein"                    |  80% |   7% |     0% |   30% |   100% |  100% |
| Passiv im Präsens                                  |  20% |   0% |     0% |   20% |     0% |    0% |
| Personalpronomen in Akkusativ                      |  53% |  73% |    87% |   50% |    67% |   87% |
| Personalpronomen in Dativ                          |  67% |  73% |    40% |   47% |    40% |   47% |
| Präpositionen mit Akkusativ                        |  20% |  80% |   100% |   73% |    67% |   33% |
| Präpositionen mit Dativ                            |   -- |  20% |    60% |   80% |    40% |   27% |
| Reflexivpronomen im Akkusativ und Dativ            |  40% |  53% |    40% |   60% |    33% |   50% |
| Relativpronomen                                    |  87% |  73% |    67% |   80% |    93% |   53% |
| Wechselpräpositionen (Akkusativ vs. Dativ)         |   0% |   7% |     0% |    0% |     0% |    0% |

### 3.1 Topics Where the Model Struggles Regardless of Context

Three topics scored consistently low across all conditions, indicating topic-specific failure modes unrelated to the model's grammatical knowledge:

- **Wechselpräpositionen (Akkusativ vs. Dativ):** 0-7% across all conditions. The model generates reasonable-looking questions with the correct case reasoning in the explanation, but the student evaluator consistently answers with just the article instead of the preposition+article contraction expected by the answer key (e.g., expects "im", student says "den"). This is a format mismatch between how the question model produces multi-word answers and how the student model parses them.
- **Passiv im Präsens:** 0-20% across all conditions. The Editor evaluator frequently flags the answered sentences for unnatural word order. German passive voice with a prepositional agent phrase ("Das Haus wird gebaut von den Arbeitern") tends to be ungrammatical in the placement the model generates — the agent phrase should typically come before the participle or the sentence should be restructured.
- **Konjugation im Perfekt:** 0-20% across all conditions. The model frequently generates questions where the auxiliary verb is in the blank but the expected answer is ambiguous between including or excluding the participle. Similar multi-word answer issue to Wechselpräpositionen.

These are topic-specific failure modes that context injection does not address. They represent inherent limitations of the fill-in-the-blank format for certain German grammar constructions rather than knowledge gaps.

### 3.2 Topics Where Context Injection Showed Movement

- **Negation mit "nicht" und "kein":** Highly variable (0-100%) across conditions. Raw and rule-compressed section both scored ~0-7% because the aligned section ("Ein-Words") covers "kein" as an indefinite article variant but does not address "nicht" placement — the model, following the retrieved content, generated "kein"-focused questions when "nicht" questions were expected. Full-textbook conditions reached 100% because they had access to content from elsewhere in the textbook covering "nicht" usage. This topic illustrates the cost of incomplete textbook coverage.
- **Präpositionen mit Dativ:** The control had no valid items for this topic (model failed to produce extractable questions without explicit case lists), while section conditions scored 20-80%. The raw/rule-compressed section included the full preposition table, which gave the model the necessary reference to generate case-appropriate questions.
- **Nebensätze mit weil, dass, obwohl:** Jumped from 20% (control) to 70-80% (section conditions). The control produced broken questions that mixed conjunction choice with word-order rules. Section conditions included the "Conjunctions" textbook section with clear rules, which helped the model produce focused questions.

These three topics are where textbook injection showed a meaningful, interpretable benefit. In each case, the model's baseline knowledge was weakest and the textbook content filled a specific gap.

### 3.3 Regression to the Mean in Per-Topic Data

Most apparent topic-level differences across conditions are within the range expected from sampling noise. With n=5-15 per topic, a shift of 20-30 percentage points can occur by chance. Topics that scored unusually high or low in one condition tend to regress toward the population mean in other conditions. The patterns in sections 3.1 and 3.2 were identified as real because they appear consistently across multiple conditions, not because a single cell differs from another.

---

## 4. Failure Mode Analysis

### 4.1 Failure Pattern Distribution

A question could fail one or more of the four evaluators. Across all 1,528 questions, 678 (44.4%) failed at least one evaluator. The pattern distribution:

| Pattern                          | Count | % of Failures |
|----------------------------------|------:|:-------------:|
| Student only                     |   131 |     19.3%     |
| Editor only                      |   128 |     18.9%     |
| Editor + Student                 |   127 |     18.7%     |
| Teacher only                     |    96 |     14.2%     |
| Editor + Student + Teacher       |    90 |     13.3%     |
| Student + Teacher                |    60 |      8.8%     |
| Editor + Teacher                 |    23 |      3.4%     |
| Static + Student                 |    11 |      1.6%     |
| Static only                      |     5 |      0.7%     |
| Other combinations               |     7 |      1.0%     |

**Interpretation:**
- **Student-only failures (19.3%)** are usually evaluator-side format mismatches (the student's answer differs from the expected answer in scope or form, not correctness).
- **Editor-only failures (18.9%)** flag grammatically awkward sentences that still have a correct answer.
- **Editor + Student failures (18.7%)** catch answers that are wrong — the sentence is ungrammatical and the student arrives at a different answer.
- **Triple failures (Editor + Student + Teacher, 13.3%)** are the most reliable indicator of fundamentally incorrect output.

### 4.2 Malformed Questions with Multi-Word Answers

A large fraction of Student failures trace back to questions where the blank position and hint do not cleanly match the expected multi-word answer. Examples:

> Topic: Wechselpräpositionen
> Q: `Ich suche meine Schlüssel _____ (der) Schrank.`
> Expected: `im` | Student answered: `den`

The blank sits directly before the noun and the hint is "(der)", which reads as asking for an article. The expected answer, however, is the preposition+article contraction "im" (= "in dem"). The student reasonably interpreted the blank as an article slot and produced "den". The question is malformed — the blank position and hint don't accommodate the intended answer.

> Topic: Passiv im Präsens
> Q: `Der Brief _____ (schreiben) vom Lehrer.`
> Expected: `wird geschrieben` | Student answered: `werden`

The hint "(schreiben)" is the infinitive of the main verb, but the expected answer is the full passive construction (auxiliary + participle). The student produced the auxiliary "werden" because that's the only word form the blank could plausibly hold given the hint. Again, the question construction doesn't support its own expected answer.

These are question-generation failures, not evaluator errors or knowledge gaps. The model is producing questions for multi-word German constructions where the standard fill-in-the-blank format (single blank + single-word hint) can't encode the intended answer. They would be addressed by format changes (explicit multi-word blanks, separate slots for auxiliary and participle, multiple choice) rather than more context.

### 4.3 Passive Voice Word Order

Passive voice conditions produced consistent Editor failures for sentences like:

> `Das Haus wird gebaut von den Arbeitern.`

The Editor evaluator flagged these as grammatically correct but with unnatural word order. The preferred German construction places the agent phrase before the participle:

> `Das Haus wird von den Arbeitern gebaut.`

The model consistently generated the less natural word order regardless of injected context. This is a generation quality issue, not an evaluator error.

### 4.4 Topic Drift from Misaligned Sections

The Negation topic illustrates what happens when the aligned textbook section doesn't match the topic label. The best available section was "Ein-Words" (covering "kein" as a possessive/indefinite article variant), which has no content on "nicht" placement. In raw and rule-compressed section conditions, the model produced questions focused on "kein" when "nicht" was the intended test. Full-textbook conditions, which had access to incidental "nicht" usage from other sections, scored dramatically better (100%) on this topic. The result is counterintuitive: injecting more (and less targeted) content helped more than injecting focused (but narrow) content, because the "focused" content was missing the relevant information.

---

## 5. Context on the Few-Shot Condition

A condition using 6 hand-curated few-shot examples per topic (generated by Claude Opus) was run alongside the textbook conditions. It scored **70.6% all-pass** — a 16-point improvement over the 1-shot control. This result is excluded from the main analysis because few-shot examples represent a different experimental variable (high-quality pedagogical content curated by a frontier model) rather than a variant of textbook processing. Including it would conflate "does textbook injection help?" with "does curated example content help?" — two questions with different answers that should be tested separately.

The directional finding is: curated pedagogical content from a stronger model helps substantially, while unstructured textbook content from the source material does not. This is consistent with the broader pattern observed in e08 (RAG with retrieved textbook chunks also failed to improve over the 1-shot control).

---

## 6. Cost Analysis

Given that no textbook injection condition meaningfully improved quality, the cost differences between conditions become purely overhead:

| Condition               | Avg Prompt Tokens | Latency | Cost Ratio (vs control) |
|-------------------------|------------------:|--------:|:-----------------------:|
| 1-shot control          |               413 |   12.6s | 1.0x                    |
| LLM-compressed section  |             1,163 |   14.1s | 2.8x                    |
| Rule-compressed section |             1,439 |   14.9s | 3.5x                    |
| Raw section             |             1,563 |   15.0s | 3.8x                    |
| LLM-compressed full     |             7,579 |   29.9s | 18.4x                   |
| Rule-compressed full    |            46,421 |  140.1s | 112.4x                  |

The rule-compressed full textbook condition used over 100x the tokens of the control for the same quality. Section-level conditions used 3-4x more tokens for no measurable benefit. In production, none of these tradeoffs would be justified.

---

## 7. Limitations

1. **Single model.** Results are specific to Qwen3.5-9B-MLX-4bit. A weaker model might benefit more from explicit context; a stronger model might already handle most cases without needing it.

2. **Limited sample size per topic.** With n=5-15 per topic per condition, individual topic rates are noisy and most cross-condition differences within a topic are within sampling variance.

3. **Textbook coverage gaps.** One topic (Negation mit nicht und kein) has no dedicated section in the source textbook. This affects section-level conditions' coverage of that topic but not the control or full-textbook conditions.

4. **Shared sections across topics.** The experiment's topics don't map exactly to chapters in the source textbook (e.g., all three Adjektivdeklination cases share one section, both Personalpronomen topics share one section). This means some topic pairs retrieved identical content for section-level conditions, reducing the effective number of independent comparisons.

5. **Evaluator false negatives.** The Student evaluator produced format mismatches that were counted as failures even when the student's reasoning was correct. This penalizes all conditions equally but inflates the absolute failure rate. True quality rates are likely higher than the reported all-pass numbers.

6. **Yield variance.** Full-textbook conditions generated more questions per sample than the control (91-95% vs 75%), which may mean they included lower-quality marginal questions that wouldn't have been generated in lower-yield conditions. This would tend to depress their all-pass rates relative to a yield-matched comparison.

7. **Fill-in-the-blank format limitation.** The FITB format struggles with multi-word German answers (verb-infinitive pairs in Futur I, preposition+article contractions in Wechselpräpositionen, auxiliary+participle in passive voice). Addressing these would require either prompting the model to avoid multi-word answers, reworking the output format to support multi-word blanks, or using a more capable model that can reason about blank placement and answer scope consistently.

---

## 8. Conclusions

1. **Textbook content injection did not improve over a 1-shot example for this model.** All six conditions (1-shot control and five textbook variants) clustered in a 3.8-point range (54.2% to 58.0%), which is within sampling noise.

2. **Compression method (LLM vs rule) did not matter.** At both section and full-textbook scope, LLM-compressed and rule-compressed variants performed equivalently. The LLM compression work done to prepare these files added no measurable value.

3. **Scope (section vs full) did not matter.** Full-textbook conditions, despite injecting 5-40x more content, performed no better than section-level conditions. More context was not more useful context.

4. **The largest-context condition was the worst cost-quality tradeoff.** Rule-compressed full textbook used ~112x more tokens and ~11x more latency than the control for zero quality improvement.

5. **Topic-specific failure modes dominate.** Three topics (Wechselpräpositionen, Passiv im Präsens, Konjugation im Perfekt) scored consistently low across all conditions due to format limitations of fill-in-the-blank questions for multi-word German answers. These failure modes are not addressable by context injection.

6. **Textbook coverage matters more than retrieval or compression strategy.** The one case where full-textbook conditions dramatically outperformed section conditions (Negation, 100% vs 0-30%) was driven by a topic that had no dedicated section in the textbook. This suggests that ensuring source material actually covers the target topics is more important than how the content is segmented or compressed.

7. **Directional observation on curated examples.** The concurrent few-shot condition (70.6% with 6 hand-curated examples), while excluded from this experiment's main analysis, points to curated example content as a lever worth investigating separately. Unprocessed textbook content and frontier-model-curated examples are two distinct interventions; this experiment rules out the former but does not assess the latter.

---

_Written by Claude Opus 4.6. Reviewed by Alexander Johnson and Claude Opus 4.6. Generation model: Qwen3.5-9B-MLX-4bit (local). LLM judge (Editor, Student, Teacher evaluators): gpt-4o._
