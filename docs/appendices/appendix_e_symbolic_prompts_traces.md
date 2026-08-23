# Appendix E — Symbolic rules, prompt contracts, and trace evidence

## E.1 Symbolic feature catalogue

The symbolic scorer is a standardized logistic-regression pipeline fitted on
82 development rows. Its weights are learned, not hand-set. The main scorer
contains 11 features; the IDF family is disabled under the main-pipeline rule
against TF-IDF-family evidence.

| Family | Exact features | Interpretation | Registered gameability | Main-pipeline standing |
|---|---|---|---|---|
| F1 IDF | `idf_min`, `idf_max`, `idf_mean` | Corpus-frequency summaries | Low | Disabled; pilot only |
| F2 length | `n_tokens`, `mean_word_chars` | Length and token shape | High | Enabled; removal improves CV F1 |
| F3 orthography | `punct_per_tok`, `digit_per_tok`, `latin_per_tok`, `ends_dandi` | Normalized script/form cues | Medium | Enabled |
| F4 connectives | `connective_frac` | Discourse-connective fraction | High | Enabled |
| F5 sentiment | `pos_frac`, `neg_frac`, `intensifier_frac` | Lexicon-presence fractions | High | Enabled |
| F6 richness | `guiraud` | Length-corrected lexical richness | Low–medium | Enabled |

The honest five-fold cross-validated macro-F1 is 0.5150 ± 0.0713; the 0.6570
resubstitution score is optimistic. Leave-one-family-out changes are +0.0647
for F3, +0.0386 for F6, −0.0188 for F5, −0.0189 for F4, and −0.1082 for F2,
where positive means performance falls when the family is removed. These
measurements do not support a claim that the symbolic scorer is a strong
standalone classifier. Its retained function is deterministic diagnosis.

Sources: `src/symbolic/features.py`, `configs/s35_symbolic.yaml`, and
`results/s35_symbolic.{md,json}`.

## E.2 Writer prompt contract

The following is the exact Bangla wrapper structure used by the renderer;
bracketed fields are runtime substitutions, not omitted instructions.

```text
তুমি একজন সাধারণ বাংলাদেশি দর্শক। নিচের ছবিটি দেখে ফেসবুক বা ইউটিউবে যেমন মন্তব্য করতে, ঠিক তেমন একটি মন্তব্য লেখো।

দুই ধরনের মন্তব্য হয়:
[VERBATIM TWO-LEVEL OPERATIONAL DEFINITION]

তোমাকে লিখতে হবে **স্তর [০/১]** ধরনের মন্তব্য।

[IF APPLICABLE]
আসল দর্শকেরা এভাবে লেখেন — উদাহরণ:
- [EXEMPLAR 1]
...
- [EXEMPLAR 10]

ছবির কাহিনি:
[PLOT SYNOPSIS]

[ON RETRY ONLY]
তোমার আগের মন্তব্য:
[PREVIOUS DRAFT]

যা ঠিক করতে হবে — ঠিক এই জিনিসগুলোই:
[REFLECTOR OR JUDGE FEEDBACK]

এক-দুই বাক্যে লেখো, ২০ শব্দের মধ্যে।

শুধু মন্তব্যটি লেখো, বাংলায়। আর কিছু লিখো না।
```

Zero-shot omits examples and retry material. Static few-shot supplies a frozen
instance-randomized R1 schedule; RAG conditions supply ten same-level R1
retrievals. Retry attempts append only the previous-draft and feedback block.
The length instruction is identical for both levels.

## E.3 Reflector template

```text
নিচের মন্তব্যটি একটি স্বয়ংক্রিয় যাচাইয়ে পাশ করেনি।

মন্তব্য:
[DRAFT]

যা চাওয়া হয়েছিল: স্তর [LEVEL] ধরনের মন্তব্য।
যাচাইয়ে যে দিকগুলো দুর্বল এসেছে: [HUMAN-READABLE FAILED FEATURES]
স্বয়ংক্রিয় স্কোর ঝুঁকেছে অন্য স্তরের দিকে।

এক বা দুই বাক্যে লেখো, ঠিক কী বদলালে মন্তব্যটি স্তর [LEVEL] হবে। নতুন মন্তব্য লিখো না — শুধু নির্দেশনা দাও, বাংলায়।
```

The Critic chooses failed features deterministically. The Reflector turns those
features into short instructions; it does not decide PASS/FAIL.

## E.4 Self-critique and external-role control

Both controls share one generated critique:

```text
[BASE RAG PROMPT]

তোমার লেখা মন্তব্য:
[DRAFT]

মন্তব্যটি চাওয়া স্তর [LEVEL]-এর সঙ্গে কতটা মেলে তা সমালোচনা করো। এক বা দুইটি বাংলা বাক্যে শুধু কী বদলানো দরকার বলো; নতুন মন্তব্য লিখো না।
```

Both revision conditions use the same `user → assistant → user` topology. In
the intrinsic condition the critique is appended to the assistant draft; in
the external-role condition it is placed in the final user revision request.
This isolates role placement without changing the critique text.

## E.5 Hosted-judge contract

The hosted Gemma-4 judge receives the operational definition, requested level,
plot and draft, and must return structured JSON only. A PASS carries empty
feedback. A FAIL carries one frozen target-specific Bangla correction string
and an integer target-fit score from 0 to 100. The judge may request up to two
Writer retries but never supplies the final thesis outcome score; Verifier-B
remains the only final scorer.

## E.6 Failure-taxonomy census

The development failure taxonomy covers the complete eight-case census of
three-attempt neural-gate failures, not the 50 cases anticipated by the earlier
specification. It was coded once by Codex under researcher authorization and
reviewed by the researcher; there is no independent coder or agreement score.

| Category | Count |
|---|---:|
| No observable registered emitted-text error | 5 |
| Off-topic or unsupported factual claim | 1 |
| Medium misidentification | 1 |
| Specificity-level mismatch | 1 |
| Wrong sentiment, too short, template repetition, or register/honorific error | 0 |

This small single-coder census is descriptive. Exact case IDs and notes remain
in `results/s4_failure_taxonomy.json`.

## E.7 Rule-selected representative correction trace

To prevent outcome-based selection, the displayed case is the lexicographically
first key among seed-42 `rag_neural_symbolic_feedback` cases requiring more than
one attempt. The rule selects `S5BN|s42|BN006|L0|rag_neural_symbolic_feedback`
without using Verifier-B or reading response quality.

| Field | Attempt 1 | Attempt 2 |
|---|---|---|
| Draft | ব্যাপারটা কেমন যেন, বুঝলাম না ভালো লাগছেও না, খারাপও লাগছে না! | মোটামুটি লাগছে। এমন অনেক মুভি দেখতেছি, ভালো লাগাটা আর আগের মতো নেই। |
| Verifier-A target score | 0.00000054 | 1.00000000 |
| Symbolic diagnostic score | 0.602156 | 0.886522 |
| Gate verdict | FAIL | PASS |
| Retrieved IDs | bn_1766, bn_1111, bn_1779, bn_1505, bn_0711, bn_1219, bn_1936, bn_0518, bn_0929, bn_0106 | bn_1111, bn_1766, bn_1505, bn_1779, bn_0711, bn_1219, bn_0518, bn_1936, bn_0106, bn_0929 |

Feedback used for the retry:

> মন্তব্যটিকে স্তর ০-তে নিয়ে আসার জন্য, প্রথমে “ব্যাপারটা কেমন যেন” এর মতো
> অস্পষ্ট শব্দ বাদ দিন। এরপর “ভালো লাগছেও না, খারাপও লাগছে না!”-এর বদলে আরও
> সাধারণ প্রতিক্রিয়া যেমন “ঠিক আছে” অথবা “মোটামুটি” লিখলে এটি স্তর ০-এর
> কাছাকাছি চলে আসবে।

The case used three logical model calls: initial Writer, Reflector, and retry
Writer. Verifier-B was applied only after the archive was sealed and assigns
the emitted Level-0 response target probability 0.986332. This trace illustrates
the mechanism; it is not an estimate of typical improvement. Complete traces
remain authoritative in `results/s5_main_bn_cases.jsonl`, with final outcome
scores in `results/s5_main_bn_scored_cases.csv`.
