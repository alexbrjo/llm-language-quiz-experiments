# E10: Edge Model German Verb Card Generation

**Experiment:** e10 edge model verb card comparison
**Date:** 2026-04-30
**Author:** Claude Opus 4.7, Alexander Johnson

---

## Abstract

This experiment evaluates five edge models (Bonsai 8B, Qwen3.5 4B, Ministral 3 3B, Nemotron 3 Nano 4B, and Gemma 4 E2B) on the task of generating structured German verb flashcards (infinitive, English translation, separability tag, past participle, and irregular form notes) for 100 common German verbs. Claude Haiku 4.5 is included as a frontier API ceiling and Claude Sonnet 4.6 serves as the judge. Translation is essentially solved by every model tested (94–100% pass) but the grammar fields are more challenging: among edge models, per-field pass rates range from 16% (Bonsai 8B's past participle) to 95% (Qwen3.5 4B's past participle), and the all-pass metric ranges from 3% (Bonsai 8B) to 44% (Qwen3.5 4B). Failure modes are model-specific and distinct; these are discussed in section 4.

---

## 1. Introduction

Experiments e06 and e09 evaluated open fill-in-the-blank question generation across model classes. This experiment turns to a different content type: flash cards. Flash cards are the simplest LLM-generated learning artifact and bring some advantages: latency matters less (cards are static and persistent), the per-card token cost is short, and the output is deterministic. If small local models can produce dependable cards, an entire class of vocabulary-acquisition workflows becomes deployable on consumer hardware.

The verb is a demanding part of speech in German. The perfect flash card captures the word, a translation, separability behaviour, the past participle (and auxiliary verb `hat` or `ist`), and irregular conjugations. These are five distinct knowledge demands on the model, each with distinct ways to fail.

E10 measures (a) how each model performs on each of the four judged fields independently, and (b) what the dominant failure modes look like, with concrete examples.

---

## 2. Experimental Setup

### 2.1 Models Under Test

| Model | Provider | Params | Quant | Size | Runtime | Temp | Role |
|---|---|---|---|---|---|---|---|
| Bonsai 8B | Prism ML | 8.2B | 1-bit (native) | 1.2 GB | local (LM Studio) | 0.1 | edge |
| Qwen3.5 4B | Alibaba | 4B | Q4_K_M | 3.4 GB | local (LM Studio) | 0.1 | edge |
| Ministral 3 3B | Mistral | 3B | Q4_K_M | 3.0 GB | local (LM Studio) | 0.1 | edge |
| Nemotron 3 Nano 4B | NVIDIA | 4.0B | Q4_K_M | 2.8 GB | local (LM Studio) | 0.1 | edge |
| Gemma 4 E2B | Google | 4.6B | Q4_K_M | 4.4 GB | local (LM Studio) | 0.1 | edge |
| Claude Haiku 4.5 | Anthropic |  |  |  | API | 0.1 | frontier control |

The five edge models are the test subjects. Claude Haiku 4.5 is included as a frontier API reference for how good the cards can plausibly get on this prompt. Local models ran via LM Studio. Bonsai 8B is a natively 1-bit model and the other four edge models are Q4_K_M quantizations of conventionally-trained models.

### 2.2 Input Set

100 common German verbs were used as input, and the list includes many irregular verbs: the auxiliaries `sein` and `haben`, all six modal verbs (`können`, `müssen`, `sollen`, `wollen`, `dürfen`, `mögen`), strong verbs across multiple ablaut classes (`finden`, `bleiben`, `liegen`, `denken`), and a long tail of weak verbs and prefixed verbs (`bekommen`, `verstehen`, `entwickeln`). A key limitation is that 100 common verbs likely doesn't translate to the full language surface. It's possible that less common verbs will produce more hallucinations (they are less likely to be present in the model's training data). Conversely, it's also possible that less common verbs are less irregular and are easier for models to guess.

### 2.3 Card Schema and Prompt

Each generation produces a JSON object conforming to a five-field schema, provided two examples (`ankommen` for a separable verb, `machen` for a no-prefix verb) and explicit field rules.

```json
{
  "word_de":         "<infinitive>",
  "word_en":         "<English translation>",
  "separability":    "separable | not separable | no prefix",
  "past_participle": "<auxiliary + Partizip II, e.g. 'hat gemacht'>",
  "irregular_forms": "<irregular forms with subjects, or 'regular'>"
}
```

### 2.4 Evaluation

Each card was judged on two independent rubrics by Claude Sonnet 4.6 at 0.1 temperature. 

**Conjugations rubric** judges three booleans:
- `separability_correct`: pass if the value reflects whether the verb has a separable prefix in standard usage; verbs with no prefix at all should be tagged `"no prefix"`.
- `past_participle_correct`: pass if the value contains the correct Partizip II *and* the correct auxiliary (`hat` or `ist`).
- `irregular_forms_useful`: pass if the field contains at least one concrete irregular form, OR the tag `'regular'`/`'irregular'` consistent with the participle. Fail if the tag contradicts the participle (e.g. `"regular"` for a clearly strong participle like `gefunden`).

**Translation rubric** judges a single boolean:
- `acceptable`: the translation includes at least one correct, common English equivalent of the infinitive, does not list a meaning belonging to a different German verb, and does not duplicate the same meaning under different wording.

---

## 3. Results

### 3.1 Per-Field Pass Rates

| Model | separability | past_participle | irregular_forms | translation |
|---|---:|---:|---:|---:|
| Claude Haiku 4.5 | 91% | 100% | 97% | 100% |
| Qwen3.5 4B | 86% | 95% | 57% | 99% |
| Ministral 3 3B | 82% | 82% | 42% | 94% |
| Nemotron 3 Nano 4B | 81% | 70% | 42% | 95% |
| Gemma 4 E2B | 29% | 92% | 41% | 95% |
| Bonsai 8B | 70% | 16% | 39% | 96% |

Some notes by field:

- `translation` performance is high in all models (94–100% pass rate). The few translation failures per model are typically misleading secondary meanings (setzen → to sit, stellen → to stand).
- `past_participle` is the highest-variance field (16–100%). It also accounts for most of Bonsai's low all-pass score and Nemotron's lower-tier placement.
- `irregular_forms` is a uniformly weak field for edge models (39–57%), driven by challenging evaluation. See section 4.5.
- `separability` is strong for four of the five edge models (70–86%) but challenges Gemma 4 E2B (29%).

### 3.2 All-pass metric

The all-pass metric amplifies model-specific weaknesses. Bonsai's 3% reflects a participle field that fails on 84% of verbs. Qwen scores ≥57% on every individual grammar field but only 44% all-pass, because its strong-verb-tagged-as-regular pattern is uncorrelated with its other (good) fields.

| Model | All-pass metric |
|---|---:|
| Claude Haiku 4.5 | 89% |
| Qwen3.5 4B | 44% |
| Ministral 3 3B | 32% |
| Nemotron 3 Nano 4B | 25% |
| Gemma 4 E2B | 12% |
| Bonsai 8B | 3% |

---

## 4. Failure Modes

### 4.1 Bonsai 8B: past participle errors and cross-verb hallucination

Bonsai's 16% past-participle pass rate is the result of three distinct issues, often occurring for the same item.

**Auxiliary alone, participle dropped**. The model emits only the third-person singular present-tense form of the auxiliary and stops.

| Verb | Bonsai output | Correct |
|---|---|---|
| `sein` | `"past_participle": "ist"` | `ist gewesen` |
| `haben` | `"past_participle": "hat"` | `hat gehabt` |

**Wrong auxiliary `ist` for `hat`-verbs**. The participle stem is correct but the auxiliary is wrong. `ist` is being applied as a default.

| Verb | Bonsai output | Correct |
|---|---|---|
| `sagen` | `ist gesagt` | `hat gesagt` |
| `geben` | `ist gegeben` | `hat gegeben` |
| `wollen` | `ist gewollt` | `hat gewollt` |

**Cross-verb hallucination, where the participle belongs to an unrelated verb**. The worst examples are of drift in the infinitive field to words that don't exist in the input list (`bellen` and `wohlen`). The translation field stays at 96% because most translations come out more or less correct. Meaning can be consistently inferred through the model, but not always the exact words.

| Verb (`word_de`) | Bonsai `past_participle` | Notes |
|---|---|---|
| `sollen` | `ist gelungen` | Participle of `gelingen` |
| `kennen` | `ist bekannt` | Participle of `bekennen` (and wrong meaning) |
| `bellen` | `hat angerufen` | Participle of `anrufen` |

### 4.2 Gemma 4 E2B: separability defaults to `"separable"`

Gemma's 29% on separability is the result of a near-uniform mistake: it tags unprefixed verbs as `"separable"`. From the first 20 verbs in the input list, 12 were tagged separable when the correct value is `"no prefix"`. Gemma's `past_participle` for these cards is mostly correct (92% pass), which suggests the model is not confused about the verb itself but about the concept of separability. Gemma goes with `"separable"` as a default from the prompt's three permitted values (`separable | not separable | no prefix`). This could potentially be improved with a clarification in the prompt or different categories.

```
werden  → "separable" 
müssen  → "separable" 
sagen   → "separable"
geben   → "separable"
kommen  → "separable"
sollen  → "separable"
wollen  → "separable"
gehen   → "separable"
lassen  → "separable"
finden  → "separable"
bleiben → "separable"
heißen  → "separable"
```

### 4.3 Ministral 3 3B: `ist` as a default auxiliary

Ministral's 82% past-participle pass rate comes from a cluster of `hat`-verbs assigned `ist`. The participle stem is consistently correct. Several of these (`ist gestanden`, `ist gesessen`) are correct in Süddeutsch.

| Verb | Ministral output | Correct |
|---|---|---|
| `stehen` | `ist gestanden` | `hat gestanden` |
| `heißen` | `ist geheißen` | `hat geheißen` |
| `nennen` | `ist genannt` | `hat genannt` |
| `gelten` | `ist gegolten` | `hat gegolten` |
| `stellen` | `ist gestellt` | `hat gestellt` |
| `sitzen` | `ist gesessen` | `hat gesessen` |
| `scheinen` | `ist geschienen` | `hat geschienen` |
| `treffen` | `ist getroffen` | `hat getroffen` |

### 4.4 Nemotron 3 Nano 4B: Infinitiv confusion plus auxiliary errors

Nemotron's 70% past-participle pass rate has two distinct sources.

**Modal verbs given the infinitiv form** instead of the standalone Partizip II. `hat können` is grammatically correct in a modal-with-dependent-infinitive construction (`Ich habe das machen können`), but it is not the Partizip II that should appear on a flashcard.

| Verb | Nemotron output | Correct (standalone) |
|---|---|---|
| `können` | `hat können` | `hat gekonnt` |
| `müssen` | `hat müssen` | `hat gemusst` |
| `dürfen` | `hat dürfen` | `hat gedurft` |

**Wrong auxiliary** (similar to Ministral, but in both directions). Nemotron also produced `wohlen` for `wohnen` and translated `mögen` as `"to be able to"` (which is the meaning of `können`). This is minor evidence of the same verb-identity drift seen in Bonsai, but at much lower frequency.

| Verb | Nemotron output | Correct |
|---|---|---|
| `gehen` | `hat gegangen` | `ist gegangen` (motion) |
| `sehen` | `ist gesehen` | `hat gesehen` |
| `stehen` | `ist gestanden` | `hat gestanden` |

### 4.5 Qwen3.5 4B: `irregular_forms` defaults to `"regular"` on strong verbs

Qwen is the strongest edge model on every field except `irregular_forms`. On strong verbs, the model emits `"regular"` instead of the irregular forms (Präteritum stem and any vowel changes) that the field is meant to surface. From the first 20 verbs:

| Verb | Qwen's `irregular_forms` | Expected `irregular_forms` |
|---|---|---|
| `geben` | `"regular"` | `"gab, gegeben"` |
| `sehen` | `"regular"` | `"sah, gesehen"` |
| `lassen` | `"regular"` | `"ließ, gelassen"` |
| `finden` | `"regular"` | `"fand, gefunden"` |
| `bleiben` | `"regular"` | `"blieb, geblieben"` |
| `liegen` | `"regular"` | `"lag, gelegen"` |
| `denken` | `"regular"` | `"dachte, gedacht"` |

The rubric catches this via participle-consistency (`gefunden`/`gelegen`/etc.), but the true underlying issue is that `irregular_forms` is supposed to add information the participle alone doesn't carry (notably the Präteritum stem). Qwen defaults to the `"regular"` escape hatch rather than producing it. The card's other four fields, including the strong participle itself, are correct.

### 4.6 Claude Haiku 4.5: separability label format ambiguity

Haiku's only meaningful weakness is on separability (91%). Eight of its nine failures could be explained as rubric-format collisions. The prompt offers three values: `separable | not separable | no prefix`. The rubric prefers `"no prefix"` when a verb has no prefix at all and reserves `"not separable"` for verbs with an inseparable prefix (`be-`, `ent-`, `er-`, `ver-`, `zer-`, etc.). Haiku tends to use `"not separable"` for both cases. Only one Haiku separability miss is a genuine error: `bekommen → "no prefix"`, where `be-` is an inseparable prefix and the correct value is `"not separable"`.

| Verb | Haiku | Rubric expects |
|---|---|---|
| `nennen` | `not separable` | `no prefix` |
| `bringen` | `not separable` | `no prefix` |
| `gelten` | `not separable` | `no prefix` |
| `beginnen` | `not separable` | `not separable` |
| `entwickeln` | `not separable` | `not separable` |
| `schließen` | `not separable` | `no prefix` |
| `interessieren` | `not separable` | `no prefix` |
| `bekommen` | `no prefix` | `not separable` |

---

## 5. Discussion

**Translation is pretty good at the 3B scale.** Across 600 cards, every model scored ≥94% on the translation rubric. This is not surprising, since translation is a big part of any model's pretraining mix, but it shows these models can be accurate enough to be useful.

**Grammar field accuracy is dominated by model-specific errors.** The different error categories would respond to different interventions.

**The `irregular_forms` rubric and `separability` label don't map cleanly to German grammar.**  These are the largest improvements available to the experimental design: requiring principal parts (e.g. `liegen, lag, gelegen`) in the prompt for any non-weak verb would disambiguate the requirements. Making the expectation more clear for separability could also remove ambiguity from the model.

**These edge models are not viable for accurate flash cards on this prompt.** The best edge model (Qwen, 44%) has enough errors that an unattended pipeline would surface a very poor quality deck to learners. With prompt revisions targeting the two design issues above (plus maybe a self-eval?) Qwen3.5 4B could be viable.

---

## 6. Limitations

- **100 common verbs.** The data doesn't represent the full German language. We can't extrapolate the results to the entire German language.
- **Card format concept mismapping.** As mentioned in the discussion, the card format didn't map perfectly to German grammar and this potentially confused the small models.
- **Single sample per verb.** Each model generated one card per verb at 0.1 temperature. There is some amount of sampling uncertainty.
- **One judge.** All judgments came from Claude Sonnet 4.6 and it could bias towards answers of a model with similar training data.

---

## 7. Conclusion

On the task of generating five-field German verb flashcards for 100 common German verbs, translation is "solved" at this scale and edge-model quality is bound by content correctness on the grammar metadata fields. Qwen3.5 4B is the strongest edge model on this prompt at 44% all-pass. Two prompt revisions, requiring principal parts in `irregular_forms` and decomposing the separability label, would be the first follow-up experiment.

Note: I made the separability prompt change, did a re-run for Qwen3.5 4B and got identical results. It still stands that having a deterministic `irregular_forms` prompt could improve accuracy and future card-generation experiments will take it into account.

---

_Written by Claude Opus 4.7. Reviewed and heavily edited by Alexander Johnson. Generation models: Bonsai 8B, Qwen3.5 4B, Ministral 3 3B, Nemotron 3 Nano 4B, Gemma 4 E2B, Claude Haiku 4.5. LLM judge (translation and grammar evaluators): Claude Sonnet 4.6._
