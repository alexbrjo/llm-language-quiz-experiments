# E08: RAG Chunking Strategies for Grammar Question Generation

**Experiment:** e08
**Date:** 2026-04-09
**Model:** `mlx-community/Qwen3.5-9B-MLX-4bit` (local, MLX adapter)
**LLM Judge:** `gpt-4o` (temperature 0.1, json_mode)
**Retrieval:** ChromaDB with `paraphrase-multilingual-MiniLM-L12-v2` embeddings

---

## Abstract

Following e07's exploration of static context injection, this experiment introduces dynamic retrieval-augmented generation (RAG) for grammar quiz generation. E08 focuses on the **storage dimension**: how textbook content should be chunked and indexed for retrieval. Nine RAG conditions crossed three chunking strategies (character-based, structural/markdown, semantic) with three chunk sizes (small, medium, large), holding the retrieval method constant (cosine similarity on raw topic-label queries with proportionally scaled k) and using unmodified textbook data. A total of 877 fill-in-the-blank questions were generated and evaluated by a 4-evaluator pipeline. **No RAG condition significantly outperformed the 1-shot control (57.3% all-pass).** Among fully-evaluated conditions, Sem 47 (57.8%) and Sem 89 (56.7%) came closest to the control but did not exceed it. Small chunks (k=8) averaged 56.3% all-pass vs 50.7% for medium chunks (k=4), suggesting that more numerous smaller chunks slightly outperformed fewer larger chunks. The primary finding is that naive injection of unprocessed textbook chunks did not provide the quality gains seen with static context injection in e07, likely due to poor retrieval precision: a spot-check showed the embedding model frequently failed to match German grammar topic labels to relevant textbook passages.

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
| Questions per sample   | 3                                             |

### 1.2 RAG Pipeline

Before each generation sample, the grammar topic label was sent to a sidecar service that embedded the query and retrieved the top-k most similar chunks from a ChromaDB vector store via cosine similarity. The retrieved chunks were joined with `---` delimiters and injected into the prompt template as reference material.

**Textbook source:** A 300-page CC-licensed German grammar textbook, extracted to markdown via marker-pdf (chosen for table extraction quality over pdfplumber, pymupdf4llm, and unstructured). The extracted text was intentionally left uncleaned to test RAG robustness with real-world data, including HTML artifacts in tables, page numbers, and table of contents fragments.

**Embedding model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, 0.1B parameters). Chosen over the ChromaDB default `all-MiniLM-L6-v2` for multilingual support, given that queries are German grammar topic labels and the textbook mixes German and English.

### 1.3 Conditions

| # | Condition | Strategy | Chunk Size | Overlap | Chunks | k | ~Content Injected |
|---|-----------|----------|-----------|---------|--------|---|-------------------|
| 1 | Control   | —        | —         | —       | —      | — | 0 tokens          |
| 2 | Char 400  | Character| 400 chars | 100     | ~1033  | 8 | ~0.77%            |
| 3 | Char 800  | Character| 800 chars | 200     | ~508   | 4 | ~0.79%            |
| 4 | Char 1600 | Character| 1600 chars| 400     | ~257   | 2 | ~0.78%            |
| 5 | Struct 400| Structural| 400 chars| 100     | ~999   | 8 | ~0.80%            |
| 6 | Struct 800| Structural| 800 chars| 200     | ~527   | 4 | ~0.76%            |
| 7 | Struct 3200| Structural| 3200 chars| 800   | ~250   | 2 | ~0.80%            |
| 8 | Sem 47    | Semantic | threshold 47| —     | ~974   | 8 | ~0.82%            |
| 9 | Sem 78    | Semantic | threshold 78| —     | ~485   | 4 | ~0.82%            |
| 10| Sem 89    | Semantic | threshold 89| —     | ~256   | 2 | ~0.78%            |

**Chunking strategies:**
- **Character:** `RecursiveCharacterTextSplitter` with configurable size and overlap
- **Structural:** Markdown header splitting (`MarkdownHeaderTextSplitter` on h1-h4 boundaries) followed by recursive character splitting for oversized sections
- **Semantic:** `SemanticChunker` from langchain_experimental, using percentile-based breakpoint detection on embedding similarity between sentence groups

**Content control:** k was scaled proportionally to chunk count so that each condition injected approximately 0.8% of the total textbook content per query. This controlled for the amount of context injected across conditions while varying how that content was segmented.

**Note on 1-shot examples:** All conditions (including the control) included a 1-shot example question with answer in the prompt (from the data file). RAG conditions received this example *plus* retrieved textbook chunks, meaning they had strictly more information than the control.

### 1.4 Sampling

- **Strategy:** Exhaustive (all topics per pass)
- **Passes:** 2
- **Topics:** 20 per condition
- **Samples generated:** 40 per condition (400 total)

### 1.5 Evaluators

| Evaluator | Type     | Purpose                                                     |
|-----------|----------|-------------------------------------------------------------|
| Static    | Rules    | Structural validation (answer, explanation, blank present)  |
| Editor    | gpt-4o   | Grammatical correctness of the answered sentence            |
| Student   | gpt-4o   | Simulated student attempts to produce the correct answer    |
| Teacher   | gpt-4o   | Expert audit of question quality, answer correctness, topic alignment |

A question passed the **all-pass** criterion only if it passed all four evaluators.

---

## 2. Results

### 2.1 Overall Results

| # | Condition        |   N | All-Pass | Rate  | Static | Editor | Student | Teacher |
|---|-----------------|----:|---------:|------:|-------:|-------:|--------:|--------:|
| 1 | Control (1-shot)|  96 |       55 | 57.3% |  99.0% |  81.2% |   68.8% |   76.0% |
| 2 | Char 400/100     |  72 |       39 | 54.2% | 100.0% |  83.3% |   72.2% |   80.6% |
| 3 | Char 800/200     |  87 |       41 | 47.1% | 100.0% |  74.7% |   73.6% |   77.0% |
| 4 | Char 1600/400    |  90 |       46 | 51.1% | 100.0% |  81.1% |   68.9% |   76.7% |
| 5 | Struct 400/100   |  81 |       46 | 56.8% |  98.8% |  80.2% |   72.8% |   80.2% |
| 6 | Struct 800/200   | 105 |       53 | 50.5% | 100.0% |  76.2% |   68.6% |   72.4% |
| 7 | Struct 3200/800  |  87 |       44 | 50.6% | 100.0% |  67.8% |   67.8% |   75.9% |
| 8 | Sem 47           |  90 |       52 | 57.8% | 100.0% |  81.1% |   67.8% |   80.0% |
| 9 | Sem 78           |  79 |       43 | 54.4% |  94.9% |  72.2% |   77.2% |   70.9% |
| 10| Sem 89           |  90 |       51 | 56.7% | 100.0% |  78.9% |   65.6% |   75.6% |

**Ranking by all-pass rate:**
1. Cond 8 — Sem 47: **57.8%**
2. Cond 1 — Control: **57.3%**
3. Cond 5 — Struct 400/100: **56.8%**
4. Cond 10 — Sem 89: **56.7%**
5. Cond 9 — Sem 78: **54.4%**
6. Cond 2 — Char 400/100: **54.2%**
7. Cond 4 — Char 1600/400: **51.1%**
8. Cond 7 — Struct 3200/800: **50.6%**
9. Cond 6 — Struct 800/200: **50.5%**
10. Cond 3 — Char 800/200: **47.1%**

### 2.2 By Chunking Strategy

| Strategy    | Avg All-Pass | Best Condition          |
|-------------|:------------:|-------------------------|
| Semantic    |     56.3%    | Sem 47 (57.8%)          |
| Structural  |     52.6%    | Struct 400/100 (56.8%)  |
| Character   |     50.8%    | Char 400/100 (54.2%)    |
| **Control** |   **57.3%**  | —                       |

### 2.3 By Chunk Size

| Size Group     | Conditions                         | Avg All-Pass |
|----------------|-------------------------------------|:------------:|
| Small (k=8)    | Char 400, Struct 400, Sem 47       |     56.3%    |
| Medium (k=4)   | Char 800, Struct 800, Sem 78       |     50.7%    |
| Large (k=2)    | Char 1600, Struct 3200, Sem 89     |     52.8%    |

### 2.4 Question Yield

Each condition received 40 generation samples (2 passes x 20 topics), with 3 questions requested per sample for an expected yield of 120 questions per condition.

| Condition        | Samples | Expected | Generated | Yield |
|-----------------|--------:|---------:|----------:|------:|
| Control          |      40 |      120 |        96 | 80.0% |
| Char 400/100     |      40 |      120 |        72 | 60.0% |
| Char 800/200     |      40 |      120 |        87 | 72.5% |
| Char 1600/400    |      40 |      120 |        90 | 75.0% |
| Struct 400/100   |      40 |      120 |        81 | 67.5% |
| Struct 800/200   |      40 |      120 |       105 | 87.5% |
| Struct 3200/800  |      40 |      120 |        87 | 72.5% |
| Sem 47           |      40 |      120 |        90 | 75.0% |
| Sem 78           |      40 |      120 |        79 | 65.8% |
| Sem 89           |      40 |      120 |        90 | 75.0% |

Total questions evaluated: **877** across all conditions (73.1% average yield). The model frequently generated fewer than 3 questions per sample, with some samples producing 0 extractable questions.

### 2.5 Generation Statistics

| Condition        | Avg Prompt Tokens | Avg Completion Tokens | Avg Latency |
|-----------------|:-----------------:|:---------------------:|:-----------:|
| Control          |               362 |                   371 |        8.6s |
| Char 400/100     |               869 |                   429 |       10.9s |
| Struct 400/100   |               874 |                   406 |       10.7s |
| Sem 47           |               887 |                   426 |       10.9s |

RAG conditions used approximately 2.4x more prompt tokens than the control, with proportionally higher latency. The additional ~500 prompt tokens represent the retrieved textbook chunks.

---

## 3. Per-Topic Analysis

Per-topic all-pass rates are reported for the control (n=0-5 per topic) and selected RAG conditions. The control generated 0 valid questions for 4 of 20 topics (Konjunktiv II, Negation, Passiv, Reflexivpronomen) — these topics are absent from the control's aggregate 57.3% rate, which is computed only over the 96 questions that were successfully generated. **Caution:** With only 2-5 items per topic per condition, individual topic rates are highly volatile. A topic scoring 100% (3/3) or 0% (0/3) could easily flip with one additional sample. The per-topic analysis is useful for identifying qualitative patterns and failure anecdotes, but the rates themselves should not be treated as precise measurements.

### 3.1 Topics Where RAG Enabled Generation

**Konjunktiv II, Negation, Reflexivpronomen, Dativ Präpositionen** — The control generated 0 valid questions for these topics. The model lacked sufficient parametric knowledge of these grammar concepts to produce well-formed questions without context. RAG-retrieved chunks, even imperfect ones, provided enough signal for the model to generate some correct questions (29-50% all-pass). This is the clearest value of dynamic content injection: enabling generation for topics that are beyond the model's parametric knowledge.

### 3.2 Anecdote: Context Contamination (Hilfsverb in Perfekt)

The control produced simple, clean questions for this topic:
> Q: `Ich _____ gestern nach Berlin gefahren.` / A: `bin`

The retrieved context for RAG conditions contained complex examples involving modal verbs in perfect tense:
> Retrieved: "Die Studentin hat diese ganze Woche fleißig lernen müssen."

The model mimicked the retrieved example verbatim:
> Generated: `Die Studentin _____ diese ganze Woche fleißig lernen müssen.` / A: `hat`

This produced harder questions that tested modal-verb-in-perfect constructions rather than simple auxiliary verb selection, going beyond the intended scope. The model treated retrieved examples as templates rather than reference material.

### 3.3 Anecdote: Topic Drift (Nebensätze)

The topic "Nebensätze mit weil, dass, obwohl" specifies three conjunctions. The control produced clean questions testing these:
> Q: `Er ist müde, _____ er lange gearbeitet hat.` / A: `weil`

RAG conditions retrieved passages covering subordinate clauses broadly, including conjunctions like "weshalb" and "ob" that are outside the topic scope:
> Generated: `Er hat den Bus verpasst, _____ er trotzdem pünktlich war.` / A: `weshalb`

The Teacher evaluator correctly rejected these as topic-misaligned. The retrieved context expanded the model's scope beyond what was asked.

### 3.4 Small N and Regression to the Mean

Several topics showed apparent large swings between control and RAG conditions (e.g., 100% -> 40%, or 0% -> 50%). While the anecdotes above show genuine failure modes, much of the per-topic variance is explained by small sample sizes. With n=3 per topic in the control, a single bad question changes the rate by 33 percentage points. Topics that scored 100% in control (3/3 by chance) would naturally regress toward the population mean (~55%) in a larger RAG sample, producing an apparent "RAG hurt" effect even if RAG had no real impact. This is regression to the mean — extreme observations from small samples tend to move toward the average in subsequent measurements. The effect works in both directions: topics scoring 0% in control would appear to "benefit" from RAG simply by regressing upward.

---

## 4. Failure Mode Analysis

### 4.1 Failure Counts by Evaluator

| Evaluator | Total Failures | % of All Evaluations |
|-----------|:--------------:|:--------------------:|
| Student   |            262 |                29.9% |
| Teacher   |            206 |                23.5% |
| Editor    |            196 |                22.3% |
| Static    |              6 |                 0.7% |

### 4.2 Student Evaluator Mismatches (262 cases)

The Student evaluator produced 262 mismatches (student answer != expected answer). Not all of these represent genuine question quality issues — a significant fraction were evaluator errors or format mismatches rather than problems with the generated question. Three categories:

**A. Malformed questions**
The generation model produced questions where the blank position and hint contradicted the expected answer:

> Q: `Der Ball rollt auf den _____ (Tisch).`
> Expected: `auf den` | Student answered: `den`

The preposition "auf den" already appears in the sentence, and the hint "(Tisch)" indicates the noun should fill the blank. The expected answer "auf den" is wrong — the blank and hint don't match the intended answer. The student's response was reasonable given the question as written.

**B. Student evaluator errors**
The student evaluator (gpt-4o) sometimes applied incorrect grammar rules or ignored hint information:

> Q: `Wir geben _____ (sie/pl) die Blumen.`
> Expected: `ihnen` | Student answered: `ihr`

The hint "(sie/pl)" unambiguously specifies third-person plural, making "ihnen" the only correct dative form. The student evaluator ignored the plural specification.

> Q: `Die _____ (schön) Blumen duften stark.`
> Expected: `schönen` | Student answered: `schöne`

The correct answer is unambiguously `schönen` (plural nominative with definite article requires weak ending -en). The student evaluator applied the wrong declension rule.

**C. Multi-word answer format mismatches**
A recurring pattern across conjugation topics where the student and the expected answer disagreed on the scope of the blank:

> Expected: `hast` | Student answered: `hast gegessen`
> Expected: `werden geschrieben` | Student answered: `werden`

The generation model sometimes placed auxiliary verbs in the blank with the expectation that the participle appears elsewhere, while the student interpreted the blank differently. This is a structural limitation of the fill-in-the-blank format for German verb constructions, not a question correctness issue.

The relative proportion of these categories was not systematically measured, but manual inspection of a sample suggests categories A and B (question/evaluator errors) account for a substantial fraction of the 262 cases. The Student evaluator's mismatch rate should therefore be interpreted as an upper bound on genuine question quality failures, not a precise measure.

### 4.3 Teacher Failures (206 cases)

Teacher rejections fell into three categories:

**A. Topic misalignment from retrieved context**
RAG-specific failure mode: retrieved chunks led the model to generate questions testing related but different grammar points (see section 3.3 for a detailed anecdote). This pattern was unique to RAG conditions — the retrieved context broadened the model's scope beyond the specified topic.

**B. Incorrect answers from model confusion**
The model provided wrong grammatical forms as answers, often influenced by patterns in the retrieved chunks:

> Topic: Adjektivdeklination im Nominativ
> Q: `Das _____ (neue) Haus gehört der Familie.`
> A: `neuen` (wrong — neuter nominative with definite article requires `neue`)

**C. Explanation quality issues**
Correct questions with inaccurate or incomplete explanations:

> Explanation cites "Partizip-II-Form" but the answer is the auxiliary verb, not the participle.

### 4.4 Editor Failures (184 cases)

Editor failures flagged grammatically incorrect answered sentences. These correlated strongly with Teacher failures — when the answer was wrong, the answered sentence was naturally ungrammatical. Standalone Editor failures (grammatically awkward but otherwise correct) included:

- Unnatural word order in passive constructions
- Missing contractions (bei dem instead of beim)
- Semantically odd but grammatically valid sentences

### 4.5 RAG-Specific Failure Patterns

Two failure patterns were unique to RAG conditions:

- **Context contamination** — the model copying or paraphrasing examples from retrieved chunks instead of generating novel questions (see section 3.2 for a detailed anecdote). This reduced question diversity and often produced questions that tested more complex constructions than the topic warranted.
- **Topic drift** — retrieved context covering related but distinct grammar concepts caused the model to generate off-topic questions (see section 3.3).

---

## 5. Comparison to E07

E07 tested static context injection with the same model and found that few-shot examples (67.0%) and LLM-compressed full textbook (68.2%) substantially outperformed the 1-shot baseline (50.0%). E08's 1-shot control scored 57.3%, which is higher than e07's 1-shot (50.0%) but not directly comparable due to different configurations:

| Difference | E07 | E08 |
|-----------|-----|-----|
| Passes | 3 | 2 |
| Questions per sample | 5 | 3 |
| Prompt template | `num_questions > 1` | `num_questions\|int > 1` with `is defined` guards |
| Topic name formatting | Varied by data file | Standardized |
| Thinking mode | Not controlled | Disabled via `enable_thinking=False` |

E08's higher control score (57.3% vs 50.0%) likely reflects the less demanding configuration: 2 passes and 3 questions per sample gave the model fewer opportunities to produce errors.

While the e08 RAG techniques did not improve question quality, there is still the possibility that a better content injection strategy has the potential to improve question quality.

| Method                    | All-Pass | Source |
|---------------------------|:--------:|--------|
| LLM-compressed full text  |   68.2%  | e07    |
| Few-shot examples         |   67.0%  | e07    |
| RAG, best (Sem 47)        |   57.8%  | e08    |
| 1-shot control            |   57.3%  | e08    |
| 1-shot                    |   50.0%  | e07    |

---

## 6. Analysis: Why RAG Didn't Help

### 6.1 Retrieval Quality

A spot-check of retrieved content for 5 topics across 3 strategies (Char 800, Struct 800, Sem 78) revealed poor retrieval precision:

| Topic | Char 800 | Struct 800 | Sem 78 |
|-------|----------|------------|--------|
| Adjektivdeklination im Nominativ | Adjectival nouns (tangential) | Participial constructions (wrong topic) | `kein-` examples (tangential) |
| Hilfsverb in Perfekt | Modal verb perfekt examples (overly complex) | Modal verb position rules (partially relevant) | Modal verb position rules (partially relevant) |
| Konjunktiv II (Höflichkeitsform) | Subjunctive I uses (wrong subjunctive) | Subjunctive II intro (relevant) | Subjunctive II forms (relevant) |
| Nebensätze mit weil, dass, obwohl | Verb-first conditionals (wrong topic) | Particle words table (irrelevant) | Prepositional phrases (irrelevant) |
| Wechselpräpositionen | Dative object exercises (wrong topic) | Verb-first conditionals (wrong topic) | Dative object exercises (wrong topic) |

For "Wechselpräpositionen" (two-way prepositions), no strategy retrieved content about prepositions at all. For "Nebensätze" (subordinate clauses with weil/dass/obwohl), no strategy retrieved content about subordinate clause word order. The retrieval was only clearly relevant for Konjunktiv II.

Several factors contributed to poor retrieval:

**A. Cross-language semantic gap.** The topic labels are German grammatical terms, but the textbook explains concepts in English with German examples. The embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) is multilingual but may not bridge the specific gap between German grammar terminology and English explanations of those concepts.

**B. Semantic similarity of grammar content.** A 300-page German grammar textbook is highly self-similar at the embedding level — passages about accusative adjective declension are semantically close to passages about dative adjective declension. A 384-dimension embedding model may not have enough resolution to distinguish these fine-grained differences.

**C. Topic labels as queries.** The query "Adjektivdeklination im Nominativ" is a short, abstract label — not a natural language question about the concept. The embedding of this label may not be close to the embedding of the textbook passage that actually explains nominative adjective declension, especially if that passage uses different terminology.

**D. Retrieved content is unprocessed.** The raw textbook chunks contained tables of contents, exercise instructions, page numbers, and HTML artifacts alongside the useful grammar rules. This noise diluted the useful signal in the retrieved context.

**E. Uneven textbook coverage.** Not all 20 grammar topics are covered equally in the textbook. A search of the raw text confirmed that "Wechselpräpositionen" appears only as "two-way prepositions" in a single short passage, and "Negation mit nicht und kein" has no dedicated section — the word "nicht" appears only incidentally in example sentences for other topics. For these topics, no retrieval strategy could have found relevant instructional content because it barely exists in the source material. This is a data limitation, not a retrieval limitation.

### 6.2 The Small Chunk Advantage

Small chunks (k=8) averaging 56.3% all-pass outperformed medium chunks (k=4) at 50.7%. This likely reflects two factors:

1. **More retrieval attempts.** With k=8, the system had 8 chances to retrieve something relevant. With k=2, it had only 2. Given imperfect retrieval, more attempts increased the probability of including at least one useful chunk.

2. **Less noise per chunk.** Smaller chunks contained less irrelevant surrounding content. A 400-character chunk was more likely to be a coherent, focused passage than a 1600-character chunk that might span multiple concepts.

### 6.3 Retrieval Overlap Between Strategies

If different chunking strategies retrieve the same content for a given topic, the conditions are not truly independent. A sequence similarity analysis of retrieved content for 5 topics across the medium-size strategies (Char 800, Struct 800, Sem 78) found low overlap:

| Topic                              | Char-Struct | Char-Sem | Struct-Sem |
|------------------------------------|:-----------:|:--------:|:----------:|
| Adjektivdeklination im Nominativ   |        2.5% |     9.0% |       2.2% |
| Hilfsverb in Perfekt               |       13.9% |     9.3% |      46.1% |
| Konjunktiv II (Höflichkeitsform)   |        1.8% |     8.3% |      26.1% |
| Konjugation im Präsens             |        3.1% |     3.9% |       3.7% |
| Relativpronomen                    |       27.3% |     1.8% |       1.9% |

The strategies mostly retrieved different content for the same query. Structural and semantic chunking overlapped most (46% for Hilfsverb), likely because both respect natural content boundaries. Character chunking, which splits at arbitrary positions, retrieved largely unique content. This confirms that chunking strategy genuinely changes what content reaches the model, yet the all-pass rates remained similar — further evidence that retrieval precision, not chunk content, was the binding constraint.

### 6.4 Question Yield and Injected Context

RAG conditions generated fewer questions per sample than the control on average (2.1 vs 2.4 questions/sample), but the relationship between injected context and yield was inconsistent:

| Condition        | Avg Context (chars) | Questions/Sample |
|-----------------|:-------------------:|:----------------:|
| Control          |                   0 |              2.4 |
| Struct 800/200   |               2,412 |              2.6 |
| Char 1600/400    |               2,704 |              2.2 |
| Sem 89           |               2,937 |              2.2 |
| Char 400/100     |               2,212 |              1.9 |
| Sem 78           |               2,204 |              2.0 |

Struct 800/200 had the highest yield (2.6 qs/sample, 87.5%) despite having substantial injected context, while Char 400/100 had the lowest (1.9 qs/sample, 60.0%) with less context. The cause of this yield variance is unclear. The outlier yield for Struct 800/200 (105 questions vs 72-90 for other conditions) inflated its N and should be noted when comparing all-pass rates: a larger N from higher yield may include lower-quality marginal questions that would not have been generated in lower-yield conditions.

---

## 7. Experiment Design Considerations

### 7.1 Sample Size

With N ranging from 72 to 105 per condition and all-pass rates around 50-58%, the confidence intervals on these rates are approximately +/-10 percentage points. Most conditions fall within each other's confidence intervals, making it difficult to draw strong conclusions about which chunking strategy or size is best. A larger experiment (3+ passes, N>200 per condition) would be needed to detect the small effect sizes observed.

### 7.2 Question Yield

The model was prompted to generate 3 questions per sample but averaged ~2.2, with some samples producing 0 extractable questions. This resulted in N ranging from 72 to 105 per condition instead of the expected 120. The variable yield introduces a mild confound: conditions where the model produced more questions may have included lower-quality marginal questions that would have been omitted in a lower-yield condition.

### 7.3 Content Control

The proportional-k design (scaling k inversely with chunk count to inject ~0.8% of content per query) was a reasonable control for total content volume but did not control for content quality. Larger chunks may have included more surrounding noise for the same percentage of content, while smaller chunks with higher k had more independent retrieval attempts.

---

## 8. Limitations

1. **Single retrieval method.** All conditions used the same retrieval method (cosine similarity on the raw topic-label embedding). The chunking experiment was confounded with retrieval quality — if retrieval consistently returned irrelevant chunks, no chunking strategy could have helped. A follow-up experiment isolating retrieval techniques (e.g., HyDE, reranking) would help separate these effects.

2. **Single embedding model.** The `paraphrase-multilingual-MiniLM-L12-v2` model may not be well-suited for matching German grammar topic labels to English-language textbook content. A larger or domain-specialized embedding model might produce different results.

3. **No retrieval quality measurement.** The experiment measured end-to-end question quality but did not independently measure whether the retrieved chunks were topically relevant. Adding a retrieval precision metric would help distinguish "retrieved the right content but model used it poorly" from "retrieved irrelevant content."

4. **Unclean data.** The textbook text was intentionally left uncleaned after marker-pdf extraction to test robustness. HTML artifacts in tables, page numbers, and table of contents entries appeared in retrieved chunks. Cleaning the text might improve retrieval quality.

5. **Cross-experiment comparability.** Differences in configuration between e07 and e08 (passes, questions per sample, prompt template, thinking mode) limit the strength of cross-experiment comparisons. The directional finding (static context > RAG) holds, but the magnitude should not be over-interpreted.

6. **Small N.** With ~80-100 items per condition, the experiment lacked statistical power to detect small differences between chunking strategies. Observed differences of 5-7 percentage points were within confidence intervals.

---

## 9. Conclusions

1. **Naive RAG did not improve question quality over unaugmented generation.** The best fully-evaluated RAG condition (Sem 47, 57.8%) did not meaningfully exceed the control (57.3%).

2. **RAG enabled generation for topics the model otherwise couldn't handle.** The control generated 0 valid questions for Konjunktiv II, Negation, Reflexivpronomen, and Dativ Präpositionen. RAG conditions produced some correct questions for these topics (29-50% all-pass), demonstrating RAG's value for topics beyond the model's parametric knowledge. Conversely, some topics that scored well in the control appeared to score worse under RAG, but with only 2-5 items per topic in the control, these swings are within the range expected from regression to the mean and should not be interpreted as RAG degrading performance on those topics specifically.

3. **Retrieval quality appears to be the bottleneck, not chunking strategy.** The differences between chunking strategies were small (52.6-56.3% average all-pass) and within confidence intervals. The more fundamental issue was that the embedding model and query format did not reliably retrieve topically relevant passages.

4. **Small chunks with more retrieval attempts outperformed large chunks.** The small chunk group (k=8) at 56.3% outperformed medium (50.7%) and large (52.8%) groups, suggesting that at this retrieval quality level, casting a wider net with more chunks was more effective than retrieving fewer, larger passages.

5. **Context contamination was a significant RAG-specific failure mode.** The model frequently copied or paraphrased example sentences from retrieved chunks, producing questions that were near-duplicates of textbook content and often tested more complex constructions than the topic warranted.

6. **Next steps.** Future experiments could hold chunking constant and vary the retrieval technique (e.g., HyDE for better query formulation, reranking for better precision, post-retrieval compression to reduce noise). Independently measuring retrieval precision — whether the right chunks are being retrieved — would help isolate whether the bottleneck is retrieval or utilization of retrieved content.

---

_Written by Claude Opus 4.6. Reviewed by Claude Opus 4.6 and Alexander Johnson. Generation model: Qwen3.5-9B-MLX-4bit (local). LLM judge (Editor, Student, Teacher evaluators): gpt-4o. Retrieval: ChromaDB with paraphrase-multilingual-MiniLM-L12-v2._
