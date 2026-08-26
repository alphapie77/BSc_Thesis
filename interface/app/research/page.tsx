/* eslint-disable @next/next/no-html-link-for-pages -- Vinext's Link shim fails during local HMR. */
import { EXPERIMENT_ROWS } from '../experiment-data';

const SUMMARY = [
  ['5,400', 'frozen Bangla outputs', '৯০ plot × ২ level × ১০ condition × ৩ seed'],
  ['+0.2570', 'largest registered Δ vs zero-shot', '95% paired-bootstrap CI [+0.2151, +0.2987]'],
  ['0.9133', 'human target-level recovery', 'Frozen balanced 100-item subset; 95% CI [0.8667, 0.9567]'],
];

export default function ResearchPage(){return <main className="researchShell">
  <header className="productNav"><a href="/" className="productBrand"><span aria-hidden="true">অ</span><span className="brandCopy"><b>Audience Response Lab</b><small>Research record</small></span></a><a href="/">← Simulator-এ ফিরুন</a></header>
  <section className="researchHero"><span>Method · safeguards · frozen evidence</span><h1>Demo-র পেছনের গবেষণা</h1><p>এই page live output-এর প্রচারণা নয়; কোন component কী করে, কোন data ব্যবহার করতে পারে এবং completed experiment কী দেখিয়েছে—তার সংক্ষিপ্ত audit view।</p></section>
  <section className="evidenceSummary" aria-label="Key frozen evidence">{SUMMARY.map(([value,label,note])=><article key={value}><strong>{value}</strong><b>{label}</b><small>{note}</small></article>)}</section>
  <section className="researchSection"><div className="researchSectionHead"><span>01</span><div><h2>Live workflow ও isolation wall</h2><p>Demo result নয়; implemented system contract</p></div></div><div className="researchCards">
    <article><span className="cardTag">Live path</span><h3>Bounded generation</h3><p>R1-only top-10 retrieval → Gemma Writer → Verifier-A gate → symbolic diagnostic feedback → সর্বোচ্চ ৩ attempt। এটি predefined workflow, open-ended autonomous system নয়।</p></article>
    <article><span className="cardTag">Post-check</span><h3>Plot support triage</h3><p>আলাদা Gemma-4-31B judge generation শেষে source plot-এর বিপরীতে claims পরীক্ষা করে। এটি correction loop-এর অংশ বা human-validated thesis metric নয়।</p></article>
    <article><span className="cardTag">Isolation</span><h3>Evaluation wall</h3><p>Gold-300, R2 এবং Verifier-B live loop-এ প্রবেশ করে না। Verifier-B কেবল frozen experiment-এর outcome scorer।</p></article>
    <article><span className="cardTag">Disclosure</span><h3>Demo ≠ experiment</h3><p>Frozen S5 Writer ছিল local Gemma-3-12B; live Writer hosted Gemma-4-26B। Live output thesis result নয় এবং repeated call বদলাতে পারে।</p></article>
  </div></section>
  <section className="experimentTable"><div className="tableIntro"><div><span className="kicker">02 · Audited S5 snapshot</span><h2>Frozen 5,400-output experiment</h2></div><p>প্রতি cell n=270 · display only · কোনো rerun নয়</p></div><div className="tableScroll"><table><caption className="srOnly">Verifier-B accuracy and mean generator calls for ten frozen experimental conditions</caption><thead><tr><th rowSpan={2}>Condition</th><th colSpan={2}>Verifier-B accuracy</th><th colSpan={2}>Mean generator calls</th></tr><tr><th>L0</th><th>L1</th><th>L0</th><th>L1</th></tr></thead><tbody>{EXPERIMENT_ROWS.map(([id,label,a0,a1,c0,c1])=><tr key={id} className={id==='rag_neural_symbolic_feedback'?'reportedFocus':''}><td><b>{label}</b><small>{id}</small></td><td>{(a0*100).toFixed(1)}%</td><td>{(a1*100).toFixed(1)}%</td><td>{c0.toFixed(2)}</td><td>{c1.toFixed(2)}</td></tr>)}</tbody></table></div><div className="tableCaveat"><b>কীভাবে পড়বেন</b><p>Highlighted row thesis framework-এর implemented condition; highlight superiority দাবি করে না। Registered inference হলো প্রতিটি active condition বনাম zero-shot। Active-condition comparison exploratory।</p></div></section>
  <section className="claimBoundary"><div><span>সমর্থিত</span><p>Bangla short-response surface-এ requested engagement-specificity level-এর auditable, human-recognizable control।</p></div><div><span>সমর্থিত নয়</span><p>বাস্তব audience reception prediction, discrete audience segment, film-level realism বা box-office forecasting।</p></div></section>
  <footer className="productFooter"><span>Numbers copied from the audited S5 result artifact</span><a href="/">Live simulator খুলুন →</a></footer>
 </main>}
