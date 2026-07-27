# Legacy assets — context, NOT ground truth

These predate pipeline v7. Where they disagree with `docs/research_pipeline_en.md`
or with the verified S0 numbers, **they are wrong**.

Known corrections required (pipeline "LEGACY ASSETS" section):
- The "9,998 -> 6,114" story vs "5,000 raw": S0 is the truth.
- Emoji preprocessing tables: this data file has zero emoji.
- 97.5% (LaBSE+LogReg CV) and 87.49% (BanglaBERT) are different experiments —
  do not conflate them.
- "100% accuracy, 1.0 attempts" is evidence of a dead loop, not success.
- v1 HF model was trained on a leaked split — the new verifier is retrained.
