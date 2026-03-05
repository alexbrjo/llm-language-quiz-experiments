# LLM Language quiz experiments

**TL;DR: I deployed an LLM-powered vocabulary acquisition tool and learned some lessons about LLM content generation. To better understand how to get the most out of LLMs, I'm taking a more structured/data-driven approach with experiments.**

To better enjoy content (books and TV shows) in Spanish, I regularly invested time in studying vocabulary. My process was: when I found a word I didn't know I would add it to a spaced repetition flashcard deck and review them on a daily basis (well.. not 100% daily). Spaced repetition flashcards work great and their effectiveness is backed by research, but I have found some pain points in long-term use:

1. **Studying flashcards connects the front of a card to the back**. Memorizing the definition or translation of a word is not acquiring it. The learner must read or hear the word several times in context to understand when and how it is used.
1. **Memorizing the wrong thing**. Some words have multiple unrelated definitions and it's not feasible to cover each one in a single review.
1. **Not fully acquiring all facets of a word**. Words can have contextual meanings, irregular forms when conjugated, pronunciation and associated attributes (like noun-class or gender). It's challenging to capture all of these facets on a single flashcard.
1. **User-provided ease ratings are subjective**. Spaced repetition systems require user input to determine how to schedule a review. This user input is subjective and it's difficult to be consistent and accurate.
1. **Missing out on grammar/usage practice**. Time spent memorizing vocabulary is time not spent practicing how to use that vocabulary.

Fueled by the new vibe-coding paradigm, I built an LLM-powered vocabulary acquisition app to address these problems. Below are some screenshots as it evolved.

![Language learning apps](images/vocabulary_apps.png)

After iterating on question generation and evaluation techniques, I became familiar with a new set of problems:

1. **Correctness**. Hallucinations, prompt issues, and poorly designed questions can result in incorrect content being displayed to the user. Inaccurate or incorrect content breaks user trust and is an extremely bad user experience.
1. **Response time**. The big frontier models can take 5-30 seconds to generate content. This is too much time to be waiting for a new question or feedback on an answered question. This problem can be avoided by asynchronously generating questions that don't require a second LLM call for grading (ex: multiple choice questions).
1. **Cost**. Generating content costs energy, time, and money.

Correctness is a make or break issue for using LLMs for learning material. If the system can generate diverse learning content with high correctness, response time and cost are factors that can be addressed later. Instead of iterating within the vocabulary acquisition app, I created a new tool to experiment with prompting, evaluation techniques and models.

## Experiment 1: Evaluation of GPT-4o, GPT-4o-mini, and GPT-4-Turbo generating Basic German Grammar quiz questions ([full report](reports/e01_gpt4o_comparison.md))

This was a small experiment (n=270) that I would consider more of a trial or test-experiment. Before the experiment, I tested some of the prompts, but the experiment also included untested prompts and some had contradictory input. Regardless, there were some take-aways:

- GPT-4o-mini has trouble with generating 4 unique options for multiple choice questions; it often generates 2 identical distractors.
- GPT-4-Turbo takes roughly x2 longer than GPT-4o and GPT-4o-mini to generate a response but it does perform better on the evaluations.
- The editor evaluator (receives the question content with the blank filled in) is both time and cost efficient for finding inaccurate questions.
- 2 prompts provided an incorrect example for the requested grammatical concept (ex: the prompt topic is the dative case and the one-shot example is for accusative). This confused the model during question generation and evaluation. The model does not have the opportunity to push back against the contradictory input because the output is constrained to a specific JSON schema.
