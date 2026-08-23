'use client';

import { useMemo, useState } from 'react';
import { EXPERIMENT_ROWS } from './experiment-data';

const LEVELS = [
  { id: 0, label: 'Level 0', note: 'সংক্ষিপ্ত, তুলনামূলক সাধারণ প্রতিক্রিয়া' },
  { id: 1, label: 'Level 1', note: 'plot-এর নির্দিষ্ট দিক উল্লেখ করা প্রতিক্রিয়া' },
];

type Attempt = { attempt:number; retrieved:string[]; draft:string; neural_score:number; symbolic_score:number; gate_score:number; verdict:'PASS'|'FAIL'; feedback:string|null; failed_rules:string[] };
type LevelOutput = { target_level:number; final:Attempt; attempts:Attempt[]; gave_up:boolean; writer_calls:number; reflector_calls:number; llm_calls:number; faithfulness:{status:string; automated_claim:false} };
type DemoResult = { request_id:string; plot_id:string; outputs:LevelOutput[]; backend:{live_writer:string; reported_s5_writer:string; rag:string; gate:string; tau:number; verifier_b_loaded:false; standing:string} };

export default function Home() {
  const [plot, setPlot] = useState('');
  const [target, setTarget] = useState<'both' | '0' | '1'>('both');
  const [notice, setNotice] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<DemoResult | null>(null);
  const chars = useMemo(() => plot.trim().length, [plot]);

  async function generate() {
    if (!plot.trim() || loading) return;
    setLoading(true); setError(''); setNotice(false); setResult(null);
    const requestId = crypto.randomUUID().replaceAll('-', '');
    const levels = target === 'both' ? [0,1] : [Number(target)];
    const base = process.env.NEXT_PUBLIC_DEMO_API_URL || 'http://localhost:8000';
    try {
      const response = await fetch(`${base}/api/generate`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({plot:plot.trim(), target_levels:levels, request_id:requestId})});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Backend HTTP ${response.status}`);
      setResult(payload as DemoResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Live backend request failed');
      setNotice(true);
    } finally { setLoading(false); }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Audience Response Lab home">
          <span className="brandMark">অ</span>
          <span><b>Audience Response Lab</b><small>Bangla cinema · research demonstration</small></span>
        </a>
        <nav aria-label="Primary navigation"><a className="active" href="#simulator">Simulator</a><a href="#experiment">Experiment</a><a href="#method">Method</a></nav>
        <span className="status"><i /> Interface preview</span>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow">Verifier-in-the-loop · R1-grounded</div>
        <h1>একটি plot, দুই ধরনের<br /><em>audience-style response</em></h1>
        <p>Bangla movie synopsis থেকে engagement-specificity axis-এর দুই level-এ মন্তব্য তৈরি করুন—আর প্রতিটি correction ধাপ দেখুন।</p>
        <div className="boundary"><b>গবেষণার সীমা</b><span>এটি বাস্তব audience বা box-office prediction নয়।</span></div>
      </section>

      <section className="workspace" id="simulator">
        <div className="inputPanel">
          <div className="sectionHead"><span className="step">01</span><div><h2>Movie plot দিন</h2><p>Bangla/Bengali, Bangladeshi variety</p></div></div>
          <label htmlFor="plot">Plot বা synopsis</label>
          <textarea id="plot" value={plot} onChange={(e) => setPlot(e.target.value)} placeholder="উদাহরণ: এক তরুণ সাংবাদিক একটি নিখোঁজ মেয়ের সন্ধান করতে গিয়ে..." />
          <div className="fieldMeta"><span>{chars} characters</span><button type="button" onClick={() => setPlot('এক তরুণ সাংবাদিক একটি নিখোঁজ মেয়ের সন্ধান করতে গিয়ে শহরের প্রভাবশালী ব্যক্তিদের গোপন অপরাধ আবিষ্কার করে।')}>উদাহরণ বসান</button></div>
          <fieldset><legend>কোন output চান?</legend><div className="segmented">
            {([['both','দুই level'],['0','Level 0'],['1','Level 1']] as const).map(([value,label]) => <button key={value} type="button" className={target === value ? 'selected' : ''} onClick={() => setTarget(value)}>{label}</button>)}
          </div></fieldset>
          <button className="generate" type="button" disabled={!plot.trim() || loading} onClick={generate}><span>{loading ? 'Pipeline চলছে…' : 'Response তৈরি করুন'}</span><b>{loading ? '···' : '→'}</b></button>
          <p className="backendNote">Live backend: Gemma-4 via Gemini API · reported S5 Writer: local Gemma-3-12B। Output thesis result নয়।</p>
          {notice && <p role="status" className="connectionNotice">{error || 'Backend সংযোগ সম্পূর্ণ হয়নি—কোনো fabricated output দেখানো হয়নি।'}</p>}
        </div>

        <aside className="pipelineCard" aria-label="Fixed research pipeline">
          <div className="sectionHead"><span className="step">02</span><div><h2>Fixed pipeline</h2><p>User-adjustable নয়</p></div></div>
          <ol className="flow">
            <li><span>R</span><div><b>R1 retrieval</b><small>886 reviews · same level · top 10</small></div><i>fixed</i></li>
            <li><span>W</span><div><b>Gemma Writer</b><small>plot-conditioned Bangla draft</small></div></li>
            <li><span>V</span><div><b>Verifier-A</b><small>neural gate · τ 0.4384071</small></div></li>
            <li><span>F</span><div><b>Symbolic feedback</b><small>failed-rule diagnostics</small></div></li>
            <li><span>↻</span><div><b>Revision loop</b><small>maximum 3 attempts</small></div></li>
          </ol>
          <div className="isolation"><span>✓ Gold-300 excluded</span><span>✓ R2 excluded</span><span>✓ Verifier-B outside loop</span></div>
        </aside>
      </section>

      <section className="outcomePreview">
        <div className="sectionHead"><span className="step">03</span><div><h2>Output contract</h2><p>Live result এভাবেই দেখা যাবে</p></div></div>
        <div className="levelGrid">
          {LEVELS.filter((x) => target === 'both' || String(x.id) === target).map((level) => {
            const output = result?.outputs.find((x) => x.target_level === level.id);
            return <article key={level.id} className="levelCard">
              <header><div><b>{level.label}</b><small>{level.note}</small></div><span className={output ? (output.gave_up ? 'gaveUp' : 'passed') : ''}>{output ? (output.gave_up ? 'GAVE_UP' : 'PASS') : loading ? 'Generating' : 'Waiting for input'}</span></header>
              <div className={output ? 'finalComment' : 'emptyComment'}>{output?.final.draft || 'Generated Bangla comment এখানে আসবে'}</div>
              <footer><span>Verifier-A {output ? output.final.neural_score.toFixed(3) : '—'}</span><span>Attempts {output ? output.attempts.length : '—'}</span><span>Faithfulness {output ? 'unvalidated' : '—'}</span></footer>
              {output && <details className="trace"><summary>Correction trace দেখুন <b>{output.llm_calls} LLM calls</b></summary>{output.attempts.map((attempt) => <div className="attempt" key={attempt.attempt}><div className="attemptHead"><b>Attempt {attempt.attempt}</b><span className={attempt.verdict === 'PASS' ? 'passText' : 'failText'}>{attempt.verdict}</span></div><p>{attempt.draft}</p><div className="scoreRow"><span>Verifier-A {attempt.neural_score.toFixed(3)}</span><span>Symbolic {attempt.symbolic_score.toFixed(3)}</span><span>τ 0.438</span></div><small>R1 exemplars: {attempt.retrieved.join(', ')}</small>{attempt.feedback && <blockquote><b>Reflector feedback</b>{attempt.feedback}<em>Failed rules: {attempt.failed_rules.join(', ') || '—'}</em></blockquote>}</div>)}</details>}
            </article>;
          })}
        </div>
        <div className="traceHint"><span>Trace</span> প্রতিটি attempt-এ retrieved exemplar IDs, draft, Verifier-A score, failed rules এবং Reflector feedback দেখা যাবে। Chain-of-thought দেখানো হবে না।</div>
      </section>

      <section className="lowerGrid" id="experiment">
        <article><span className="kicker">Frozen evidence</span><h2>5,400 outputs—read only</h2><p>দশটি experimental condition, দুই level এবং তিন replicate seed আলাদা explorer-এ দেখা যাবে। এখানে কোনো regeneration হবে না।</p><a href="#method">Experiment explorer তৈরি হচ্ছে →</a></article>
        <article className="warning"><span className="kicker">Open validation</span><h2>Plot-faithfulness audit</h2><p>Unsupported character, event, actor বা scene শনাক্ত করার audit pre-register না হওয়া পর্যন্ত interface hallucination-free দাবি করবে না।</p><b>Not independently validated</b></article>
      </section>

      <section className="experimentTable" aria-labelledby="experiment-title">
        <div className="tableIntro"><div><span className="kicker">Audited S5 snapshot</span><h2 id="experiment-title">দশটি condition, একই frozen surface</h2></div><p>প্রতি cell n=270 · Verifier-B outcome scoring · 5,400/5,400 rows</p></div>
        <div className="tableScroll"><table><thead><tr><th rowSpan={2}>Condition</th><th colSpan={2}>Verifier-B accuracy</th><th colSpan={2}>Mean generator calls</th></tr><tr><th>L0</th><th>L1</th><th>L0</th><th>L1</th></tr></thead><tbody>
          {EXPERIMENT_ROWS.map(([id,label,a0,a1,c0,c1]) => <tr key={id} className={id === 'rag_neural_symbolic_feedback' ? 'proposed' : ''}><td><b>{label}</b><small>{id}</small></td><td>{(a0*100).toFixed(1)}%</td><td>{(a1*100).toFixed(1)}%</td><td>{c0.toFixed(2)}</td><td>{c1.toFixed(2)}</td></tr>)}
        </tbody></table></div>
        <p className="tableCaveat">Descriptive table only. Registered inference is in the thesis reporting artifact; rows should not be ranked from this display alone. Verifier-B calibration improvement was not established.</p>
      </section>

      <footer id="method"><p>Compound AI system · predefined evaluator–optimizer workflow</p><p>Reported S5 Writer: Gemma-3-12B · Live Writer: Gemma-4 via Gemini API</p></footer>
    </main>
  );
}
