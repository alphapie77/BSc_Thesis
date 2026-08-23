# Thesis front matter

## Title

*A Neuro-Symbolic Multi-Agent Framework for Pre-Release Audience Response
Generation in Bangla Cinema: A Verifier-in-the-Loop Approach*

## Abstract

Pre-release film analysis has limited access to authentic audience commentary,
while unconstrained language-model generation provides no guarantee that a
requested response style is meaningful or consistently realized. This thesis
develops and evaluates a neuro-symbolic multi-agent framework for controlled
Bangla cinema-response generation. A 5,000-row Bangla review corpus is audited,
cleaned and separated under frozen data-isolation rules. Initial clustering is
shown to recover corpus source more strongly than sentiment and does not support
discrete audience personas. Analysis therefore proceeds with a reproducible
two-level cut through an engagement-specificity continuum. Length-matched
comparative judgments establish that native-Bangla annotators can recognize the
distinction, while the negative clusterability evidence is retained.

The framework coordinates a Researcher, Writer, Critic and Reflector. Retrieval
uses only the R1 partition; a frozen LaBSE logistic probe serves as the in-loop
Verifier-A; symbolic rules provide diagnostic feedback; and a fine-tuned
BanglaBERT trained on disjoint R2 data serves only as outcome Verifier-B. The
completed experiment contains 5,400 outputs across 90 held-out plots, two
requested levels, ten conditions and three paired generation seeds. All nine
registered alternatives improve Verifier-B target probability over zero-shot.
Neural gating with symbolic feedback produces the largest registered
zero-shot effect, +0.2570 with 95% paired-bootstrap interval [0.2151, 0.2987],
although its incremental advantage over neural-only gating was not a registered
contrast. On a frozen balanced 100-item subset, three adult native-Bangla
annotators achieve 0.9133 pooled target-level match and nominal Krippendorff
alpha 0.8405. Same-case revisions also widen the Verifier-A–Verifier-B gap in
the neural loops, revealing proxy divergence that a single evaluator would
hide. The results support controllable Bangla response generation under an
auditable verifier loop, not audience prediction, discrete personas or
film-level realism.

## Keywords

Bangla natural language processing; controllable text generation;
neuro-symbolic AI; multi-agent systems; retrieval-augmented generation;
verifier-in-the-loop; human evaluation; Goodhart effect.

## Author and institutional fields

The following must be supplied from the university record when the final
template is available:

- Researcher full legal name and student ID
- Department, faculty and university
- Degree title and submission date
- Supervisor name, title and affiliation
- Required declaration/signature wording

These fields are intentionally not guessed in the repository.
