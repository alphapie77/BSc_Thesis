# `src/agents/` — Phase 4, the compound AI system

**The identity sentence, verbatim from pipeline §4.0, and it is not optional:**

> a compound AI system (Zaharia et al., BAIR 2024) implementing the
> evaluator-optimizer workflow (Anthropic, *Building Effective Agents*, 2024) —
> generator + external trained verifier + reflection loop, with role-separated
> deterministic and generative components.

⛔ **Never call this an autonomous multi-agent system.** Control flow is
predefined and **two of the four components make no LLM call at all**. The title
keeps "Multi-Agent Framework"; the first Methods paragraph carries the honest
definition. With no autonomy claim there is nothing to attack.

---

## The four components

| | File | LLM? | Contract |
|---|---|---|---|
| 1 | `researcher.py` | **no** | ChromaDB, top-10, **R1 index only**, filtered to the target level. On retry the original query stays **anchored**; feedback keywords only augment |
| 2 | `writer.py` | **yes** | temp 0.8 / top_p 0.9 / seed logged. Appends every generation to JSONL **as it completes** |
| 3 | `critic.py` | **no, deliberately** | `w·VerifierA + (1−w)·symbolic` vs τ. §4.2 calls this separation "the architecture's soul" |
| 4 | `reflector.py` | yes, small | Names **which symbolic rules failed**. FAIL only |

`graph.py` wires them. `state.py` holds the state and guarantees `trace`.

## Supporting files

| File | What it is |
|---|---|
| `build_index.py` | Builds the R1-only retrieval index. Run once |
| `prompts.py` | **The one** prompt renderer. §5.1 row 1 is `render(exemplars=(), feedback=None)` |
| `preflight.py` | Does the committed Verifier-A reproduce itself on this host? Read-only |
| `groq_preflight.py` | Does the key work, and are the registered models served here? |

---

## The five rules this package cannot break

1. **RAG index = R1 only** (rule 5) and **Gold-300 never enters it** (rule 4) —
   enforced as *refusals* in `build_index.py`, checked twice by two different
   mechanisms, pinned by `tests/test_s4_index.py`.
2. **Verifier-B is unreachable from here** (rule 6). An AST scan walks every
   import in this package, including inside function bodies. **That wall *is*
   the Goodhart test**; a companion test proves the scanner can actually fail.
3. **`w` and τ have no values.** Both are required arguments with no defaults.
   A default becomes a value by use — which is how `0.6/0.4` survived in the
   spec for months with no derivation anywhere.
4. **`enable_f1` stays false.** The Critic refuses a symbolic artifact carrying
   `enable_f1=True`: that is a rule-7 pilot object and the amendment is
   unsigned. Artifacts load *silently*, which is why the guard is in code.
5. **The retired vocabulary never reaches a prompt** — *persona*, *cluster*,
   *audience type*. Permitted: **axis, gradient, the cut, level**.

---

## Two things that are true and easy to forget

**Phase 4 generations are not reproducible by re-running.** `2601.17768` traces
the non-determinism to floating-point non-associativity plus **dynamic
batching** — batch composition depends on other tenants' traffic on Groq's
servers. `2604.22411` shows even T=0 diverges. So the seed is logged and is
**not** the guarantee: **the archived JSONL is**. A trace that cannot be
regenerated must never be deleted. Results are *replicable in distribution, not
reproducible bit-for-bit*, and Ch.5 says so.

**Both halves of the Critic were fitted on human reviews and are applied to
generated text.** `kapur2026length` shows the length/specificity relation is
flat or reversed in machine text — which is why `w` is fitted on dev-plot
*generations*, not on dev-82. The shift is stated wherever the scores appear.

---

## Order of operations

```
python src/agents/build_index.py --config configs/s4_index.yaml   # once
python src/agents/groq_preflight.py                                # key + models
python src/agents/preflight.py --config configs/s3c_verifier_a.yaml  # host parity
# then the pilot (configs/s4_pilot.yaml) -- NOT A RESULT, it selects a generator
```

## Where the reasoning lives

- `docs/protocol.md` §"S4 pre-commitment" — every registered decision
- `docs/axis_definition.md` — the level definitions, and the prompt text itself
- `docs/research_pipeline_en.md` §4 — the normative spec
- `docs/lab_notebook.md` — what each step found, dated
