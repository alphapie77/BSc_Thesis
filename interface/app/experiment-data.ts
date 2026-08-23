// Read-only display copy of results/s5_main_bn_master_table.csv.
// The audited CSV remains the canonical scientific source.
export const EXPERIMENT_ROWS = [
  ['zero_shot','Zero-shot',.329630,.807407,1.000,1.000],
  ['static_few_shot','Static few-shot',.603704,.840741,1.000,1.000],
  ['rag_only','RAG-only',.518519,.870370,1.000,1.000],
  ['rag_neural_loop','RAG + neural gate',.688889,.962963,1.904,1.681],
  ['rag_symbolic_loop','RAG + symbolic gate',.518519,.851852,1.022,3.630],
  ['rag_neural_symbolic_feedback','RAG + neural gate + symbolic feedback',.733333,.959259,1.889,1.630],
  ['intrinsic_self_critique','Intrinsic self-critique',.681481,.922222,3.000,3.000],
  ['external_role_self_critique','External-role self-critique',.611111,.922222,3.000,3.000],
  ['gemma4_26b_a4b_judge_loop','Gemma-4 judge loop',.629630,.881481,1.389,1.033],
  ['blind_resampling','Blind resampling',.644444,.940741,1.456,1.326],
] as const;
