# HEDS 3.0 preregistration snapshot — S5 Bangla human evaluation

**Status:** design frozen and annotation in progress; response-dependent fields
are marked `PENDING`. This repository-native snapshot follows the five HEDS 3.0
sections (`belz2025heds3`). The official digital HEDS form remains the export
target for supplementary material.

## 1. Main reference and supplementary resources

- **1.1.1 Main reference:** unpublished BSc thesis; repository protocol is the
  preregistration record (`docs/protocol.md`, “S5 Bangla human evaluation”).
- **1.1.2 Experiment:** human target-level match evaluation of 100 frozen Bangla
  (Bengali), Bangladeshi-variety, Bengali-script generated film comments from
  ten Phase-5 conditions and two engagement-specificity axis levels.
- **1.2 Resources:** config, builder, scorer, frozen interfaces and anonymized
  response/result artifacts are repository resources. The researcher key is
  tracked for reproducibility but is never shown to evaluators.
- **1.3 Contact details:** `PENDING` thesis-author affiliation/contact fields for
  the final public HEDS export. Participant identities are not contact fields
  and are never included.

## 2. Evaluated systems

- **2.1 Input:** Bangla film-plot synopsis plus a shared axis-level instruction;
  some conditions additionally receive frozen R1-only examples, verifier
  diagnostics, self-critique, or judge feedback as registered in §5.1.
- **2.2 Output:** one short Bangla audience-style film comment per case.
- **2.3 Task:** controlled/end-to-end text generation; some conditions include
  post-editing/correction stages.
- **2.4 Input language:** Bangla (Bengali), Bangladeshi variety, Bengali script.
- **2.5 Output language:** Bangla (Bengali), Bangladeshi variety, Bengali script.
- **Systems compared:** ten frozen Phase-5 conditions. Human evaluators are
  blinded to condition, model, target, replicate and automatic scores.

## 3. Sample, evaluators and experimental design

### 3.1 Sample

- **3.1.1 Outputs per system:** 10 per condition: five requested level 0 and
  five requested level 1; 100 unique case keys total. Every item is rated by
  all three evaluators, yielding 300 planned judgments.
- **3.1.2 Selection:** deterministic automatic stratified selection from the
  frozen 5,400-case surface. It enforces five cases per condition × level,
  replicate allocation 2/2/1 per cell, 90 distinct plots and zero exact repeated
  emitted texts. It is blind to Verifier-A/B, success, attempts, cost and
  gave-up state. Global seed is 42.
- **3.1.3 Power:** N/A. The pipeline fixed 100 human-evaluated outputs before
  this instrument was built; no prospective power calculation established that
  n=5 per condition × level can rank systems. Cell results are therefore
  descriptive. Primary uncertainty is a case-level bootstrap CI over the
  balanced 100-item surface.

### 3.2 Evaluators

- **3.2.1 Number:** three.
- **3.2.2.1 Domain experts:** no domain expertise is required or claimed; the
  task relies on native-language judgment of the previously human-validated
  engagement-specificity construct.
- **3.2.2.2 Compensation:** no monetary honorarium; refreshments are provided.
  In the official HEDS form this is disclosed under non-monetary compensation,
  not silently labelled unpaid.
- **3.2.2.3 Previously known:** yes. All are the researcher's university
  batchmates/friends.
- **3.2.2.4 Researchers as evaluators:** no.
- **3.2.3 Recruitment:** direct invitation from the researcher's university
  batchmate/friend network. Consent text states that participation is voluntary
  and non-participation/withdrawal has no academic or personal consequence.
- **3.2.4 Training/practice:** the interface provides the full task instruction,
  definitions of both levels, and explicit warnings that length, sentiment and
  emotional intensity do not determine the level. No scored calibration items
  or feedback are supplied, preventing training on hidden answers.
- **3.2.5 Characteristics:** all three are adults (18+) and self-identified
  native Bangla speakers. No additional demographic attributes are collected.

### 3.3 Experimental design

- **3.3.1 Preregistered:** yes, in `docs/protocol.md`, committed before interface
  instantiation and before any response was collected.
- **3.3.2 Medium:** three self-contained local HTML files; responses download as
  text CSV and are returned to the researcher.
- **3.3.3 Quality assurance:** native-speaker eligibility; SHA-256 binding to the
  sealed 5,400-case archive; exact 3 × 100 response-surface validation; rejection
  of missing, extra, duplicate or non-binary responses. No evaluator or item is
  excluded post hoc and no hidden gold attention check is used.
- **3.3.4 Interface/information:** plot synopsis, generated comment, verbatim
  definitions of level 0 and level 1, and two radio-button responses. Hidden:
  condition, target, replicate, case key, Writer identity, Verifier-A/B scores,
  attempts, cost and success. Each evaluator receives an independently shuffled
  order over the identical 100 cases.
- **3.3.5 Timing freedom:** no researcher-imposed item or total time limit;
  evaluators choose place and time. The static page does not persist selections
  after a reload, so it should remain open until CSV download; this technical
  constraint is disclosed rather than described as a scientific time limit.
- **3.3.6 Questions/feedback:** evaluators may ask procedural questions but may
  not discuss item answers with each other. `PENDING`: record any substantive
  question or post-task feedback without revealing identities.
- **3.3.7 Conditions:** place of each evaluator's choosing, outside a controlled
  lab.
- **3.3.8 Variation:** device, browser, location, session timing and interruptions
  are not controlled. `PENDING`: actual completion time if voluntarily reported.

## 4. Quality criterion and response elicitation

- **4.1 Criterion type:** correctness with respect to the requested external
  engagement-specificity axis level; the whole generated comment is assessed
  against the plot and the shared level definition.
- **4.2 Assessment:** absolute/pointwise and intrinsic. One output is shown per
  assessment; no pairwise system preference or general-quality rating is asked.
- **4.3.1 Interface name:** “engagement-specificity level” / “Level 0” / “Level
  1”.
- **4.3.2 Verbatim operational definition:** Level 0 is a general/formulaic
  reaction with little engagement with a specific film aspect. Level 1 clearly
  engages with a specific film aspect, event or construction element. Length,
  praise/criticism and emotion alone do not determine the level.
- **4.3.3–4 Instrument:** forced binary choice with two possible values, 0 or 1;
  no ordinal rating and no abstention.
- **Aggregation/analysis:** per-evaluator and pooled target-match accuracy;
  case-level 10,000-resample bootstrap CI; descriptive condition × level cells;
  raw three-way agreement; nominal Krippendorff alpha with item-bootstrap CI;
  disagreement/confusion by target level. No best-annotator selection.
- **Observed responses/results (2026-08-23):** all three exact CSVs passed the
  registered ingestion gate: 100 items and 300 judgments, with no missing,
  extra, duplicate or non-binary responses. Pooled target-match accuracy is
  **0.9133** (case-bootstrap 95% CI **0.8667--0.9567**). Per-evaluator accuracy
  is A **0.91** (0.85--0.96), B **0.93** (0.88--0.98), and C **0.90**
  (0.84--0.95). Raw three-way agreement is **0.88**; nominal Krippendorff alpha
  is **0.8405** (item-bootstrap 95% CI **0.7473--0.9200**). Both target levels
  have 137/150 correct judgments (0.9133). Five of 50 level-0 items and seven of
  50 level-1 items split 2-to-1. Condition × level cells remain descriptive
  (`n=15` judgments each), not a system-ranking analysis.

## 5. Ethics

- **5.1 Research ethics committee:** `PENDING` institutional determination. The
  repository does not claim approval or exemption that has not been obtained.
- **Consent:** written informed consent obtained from all three adults before
  annotation. The tracked template is `docs/s5_human_eval_consent_bn.md`;
  identity-bearing replies/logs remain private and outside Git.
- **5.2 Personal data:** no participant names or direct identifiers occur in
  evaluation items or committed responses. Persistent public codes are A/B/C.
  The private identity-to-code mapping and consent evidence are not committed.
- **5.3 Special-category data:** none intentionally collected from evaluators.
  Film plots/comments are not used to solicit participant personal information.
- **5.4 Impact assessment:** no formal impact assessment carried out; minimal
  screen-reading burden, voluntary withdrawal before anonymized aggregation,
  data minimization and blinding are documented safeguards.

## Post-collection completion checklist

- [x] Record received judgments and exact completeness gate.
- [ ] Record voluntarily reported completion times and procedural feedback, if any.
- [x] Insert per-evaluator/pooled accuracy and confidence intervals.
- [x] Insert raw agreement, nominal Krippendorff alpha/CI and disagreement pattern.
- [ ] Record institutional ethics determination accurately.
- [ ] Export the final answers through the official HEDS 3.0 form for the thesis
      supplementary package.
