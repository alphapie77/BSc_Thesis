# S5 archive manifest

Verified 2026-08-22. The ZIP files are retained outside Git because the active
generation archive contains raw prompts, responses and provider payloads. This
manifest is the portable integrity record; a copied archive is accepted only
if its SHA-256 matches.

## Final generation archive

| Field | Value |
|---|---|
| File | `s5_checkpoint.zip` |
| SHA-256 | `bd29b7a387df8c09f36d2c5be93f661c41d80ed66245027af3996f86e45a0ed2` |
| Runner commit | `22124a816e5ecc9d6fa59c957bd939cfd311a28a` |
| Cases | 5,400 |
| Local Writer/Reflector calls | 7,068 |
| Hosted Gemma-4 judge calls | 654 |
| Active hosted transport failures | 0 |
| Non-null Verifier-B scores during generation | 0 |
| Runtime | Python 3.12.13; transformers 5.15.0; scikit-learn 1.9.0; Tesla T4 (`device_count=2`, Writer fixed to `cuda:0`) |

The exact environment snapshot extracted from this archive is committed as
`results/env_snapshot_s5_bn_kaggle.json`.

## Final post-run archive

| Field | Value |
|---|---|
| File | `s5_bn_postrun_results_complete.zip` |
| SHA-256 | `2270bdd0b3a4bbc88258c991648d463eb215b23cd17e3cdd298372eb1bbc499f` |
| Cases / Verifier-B scores | 5,400 / 5,400 |
| Source-cases SHA-256 | `816a631be36f7e0a5918eb0298f7dce0c62b195ec80f43c8873ed923f94b3fd3` |
| Contents | 16 committed `results/s5_main_bn_*` files |

## Superseded diagnostic archive

These files came from the 10-case diagnostic run at commit `510a95c`. They are
not S5 result inputs and must never be restored into the live paths in
`configs/s5_main_bn.yaml`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `env_snapshot_s5_bn_kaggle.json` | 26,151 | `1eb335e9179290562ff0806b8573d7f5d1516d391d2784366d1dc30321617be1` |
| `s5_main_bn_calls.jsonl` | 89,328 | `a2405cb2141a9bb4e5ee7ef15de917b060db7a73aedab9444087f072064a1007` |
| `s5_main_bn_cases_pre_final_partial.jsonl` | 25,911 | `dc0acc9c976ee66bddfd687c3b4ec8982a75b2f374e5bc079bd487c501dc9192` |
| `s5_main_bn_gemini_calls.jsonl` | 9,493 | `901d4b7aa1e685ee179562643191a2518f05afafa5e5d77e1da8460ea3402bfd` |

On Sabbir's workstation the archives are organized below
`E:\Research\Thesis\S5_archives\` as `final_22124a8`, `postrun_366df8c`, and
`diagnostic_510a95c`. That path is convenience only; the hashes above are the
identity contract.
