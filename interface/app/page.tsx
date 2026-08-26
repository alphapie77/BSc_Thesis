'use client';
/* eslint-disable @next/next/no-html-link-for-pages -- Vinext's Link shim fails during local HMR. */

import { useEffect, useMemo, useState } from 'react';

const LEVELS = [
  { id: 0, short: 'Level 0', label: 'সাধারণ প্রতিক্রিয়া', note: 'কোনো বিষয় উল্লেখ করতে পারে, কিন্তু বিস্তারিত ব্যাখ্যা করে না' },
  { id: 1, short: 'Level 1', label: 'নির্দিষ্ট প্রতিক্রিয়া', note: 'নির্দিষ্ট বিষয় ধরে ঘটনা, কারণ বা ব্যক্তিগত প্রতিক্রিয়া ব্যাখ্যা করে' },
];
type Attempt = { attempt:number; retrieved:string[]; draft:string; neural_score:number; symbolic_score:number; verdict:'PASS'|'FAIL'; feedback:string|null; failed_rules:string[] };
type Faithfulness = { status:'supported'|'review'|'unsupported'|'check_failed'; support_score:number|null; explanation:string; unsupported_claims:string[]; model:string; standing:string };
type LevelOutput = { target_level:number; final:Attempt; attempts:Attempt[]; gave_up:boolean; writer_calls:number; reflector_calls:number; llm_calls:number; faithfulness:Faithfulness };
type DemoResult = { outputs:LevelOutput[] };
const FAITH_LABEL = { supported:'প্লটের সঙ্গে সামঞ্জস্যপূর্ণ', review:'মানুষের পর্যালোচনা প্রয়োজন', unsupported:'অসমর্থিত তথ্য শনাক্ত হয়েছে', check_failed:'প্লট যাচাই সম্পন্ন হয়নি' };
const EXAMPLE_PLOT = 'রাশেদ তার নিখোঁজ ভাইকে খুঁজতে গিয়ে শহরের ক্ষমতাবান এক পরিবারের গোপন অপরাধ আবিষ্কার করে। শেষ দৃশ্যে সে সত্য প্রকাশ করবে নাকি পরিবারকে রক্ষা করবে—এই সিদ্ধান্তের মুখোমুখি হয়।';

export default function Home() {
  const [plot,setPlot]=useState('');
  const [target,setTarget]=useState<'both'|'0'|'1'>('both');
  const [loading,setLoading]=useState(false);
  const [online,setOnline]=useState<boolean|null>(null);
  const [error,setError]=useState('');
  const [result,setResult]=useState<DemoResult|null>(null);
  const chars=useMemo(()=>plot.trim().length,[plot]);
  const base=process.env.NEXT_PUBLIC_DEMO_API_URL||'http://localhost:8000';
  useEffect(()=>{fetch(`${base}/api/health`).then(r=>setOnline(r.ok)).catch(()=>setOnline(false))},[base]);

  async function generate(){
    if(!plot.trim()||loading)return;
    setLoading(true);setError('');setResult(null);
    const levels=target==='both'?[0,1]:[Number(target)];
    const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),600000);
    try{
      const response=await fetch(`${base}/api/generate`,{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({plot:plot.trim(),target_levels:levels,request_id:crypto.randomUUID().replaceAll('-','')})});
      const payload=await response.json().catch(()=>({detail:`Backend HTTP ${response.status}`}));
      if(!response.ok)throw new Error(payload.detail||`Backend HTTP ${response.status}`);
      setOnline(true);setResult(payload as DemoResult);
    }catch(caught){
      setOnline(false);setError(caught instanceof DOMException&&caught.name==='AbortError'?'১০ মিনিটেও অনুরোধটি শেষ হয়নি। Backend log দেখে আবার চেষ্টা করুন।':caught instanceof Error?caught.message:'অনুরোধটি সম্পন্ন হয়নি।');
    }finally{clearTimeout(timer);setLoading(false)}
  }
  const visibleLevels=LEVELS.filter(level=>target==='both'||String(level.id)===target);

  return <main className="productShell">
    <header className="productNav">
      <a href="/" className="productBrand" aria-label="Audience Response Lab home"><span aria-hidden="true">অ</span><span className="brandCopy"><b>Audience Response Lab</b><small>Bangla cinema research demo</small></span></a>
      <a href="/research" className="researchLink">পদ্ধতি ও ফলাফল <span aria-hidden="true">↗</span></a>
    </header>

    <section className="productIntro">
      <div className="introCopy">
        <p className="overline">Verifier-in-the-loop · Bangla generation</p>
        <h1>একটি প্লট, দুই স্তরের নিয়ন্ত্রিত মন্তব্য</h1>
        <span>একই চলচ্চিত্রের plot থেকে সাধারণ ও নির্দিষ্ট—দুই ধরনের সংক্ষিপ্ত বাংলা মন্তব্য তৈরি ও যাচাই করুন।</span>
        <div className="scopeNotice"><b>গবেষণার সীমা</b><span>এটি বাস্তব দর্শকের মতামত, audience prediction বা box-office forecast নয়।</span></div>
      </div>
      <ol className="methodStrip" aria-label="Bounded generation workflow">
        <li><span>01</span><b>R1 retrieval</b><small>প্রাসঙ্গিক corpus উদাহরণ</small></li>
        <li><span>02</span><b>Writer</b><small>বাংলা draft generation</small></li>
        <li><span>03</span><b>Verifier-A</b><small>target-level acceptance gate</small></li>
        <li><span>04</span><b>Reflector</b><small>প্রয়োজনে সর্বোচ্চ ২ revision</small></li>
      </ol>
    </section>

    <section className="composer" aria-labelledby="composer-title">
      <div className="composerHead">
        <div><span className="sectionNumber">01</span><div><h2 id="composer-title">প্লট ও লক্ষ্য নির্বাচন</h2><p>বাংলা plot বা synopsis দিন; নাম, ব্যক্তিগত তথ্য বা গোপন লেখা দেবেন না।</p></div></div>
        <div className={`connectionState ${online===true?'online':online===false?'offline':''}`} role="status">{online===true?'সিস্টেম প্রস্তুত':online===false?'Local API চালু নেই':'সিস্টেম যাচাই হচ্ছে'}</div>
      </div>
      <label htmlFor="plot">সিনেমার plot বা synopsis</label>
      <textarea id="plot" value={plot} maxLength={6000} onChange={e=>setPlot(e.target.value)} placeholder="এখানে বাংলা plot লিখুন…" aria-describedby="plot-guidance"/>
      <div className="composerMeta" id="plot-guidance"><span>{chars.toLocaleString('bn-BD')} / ৬,০০০ অক্ষর</span><button type="button" onClick={()=>setPlot(EXAMPLE_PLOT)}>উদাহরণ plot ব্যবহার করুন</button></div>
      <fieldset><legend>কোন স্তরের মন্তব্য তৈরি হবে?</legend><div className="levelChoices">
        <button type="button" aria-pressed={target==='both'} className={target==='both'?'chosen':''} onClick={()=>setTarget('both')}><span className="choiceIcon" aria-hidden="true">01+02</span><span><b>দুই স্তরই</b><small>পাশাপাশি তুলনা করুন</small></span></button>
        {LEVELS.map(level=><button type="button" key={level.id} aria-pressed={target===String(level.id)} className={target===String(level.id)?'chosen':''} onClick={()=>setTarget(String(level.id) as '0'|'1')}><span className="choiceIcon" aria-hidden="true">0{level.id+1}</span><span><b>{level.label}</b><small>{level.note}</small></span></button>)}
      </div></fieldset>
      <div className="actionRow"><button type="button" className="primaryAction" disabled={!plot.trim()||loading||online===false} onClick={generate}><span>{loading?'তৈরি ও যাচাই হচ্ছে…':'মন্তব্য তৈরি করুন'}</span><span aria-hidden="true">{loading?'•••':'→'}</span></button><p className="modeNote"><b>Live · Seed 42</b><span>Hosted model-এর output পুনরায় চালালে সামান্য বদলাতে পারে</span></p></div>
      {online===false&&<p className="connectionHelp">Demo চালাতে repository root থেকে <code>start_demo.cmd</code> খুলুন। Interface দেখা যাবে, কিন্তু API প্রস্তুত না হওয়া পর্যন্ত generation বন্ধ থাকবে।</p>}
      {error&&<p className="productError" role="alert">{error} <button type="button" onClick={generate}>আবার চেষ্টা করুন</button></p>}
    </section>

    {(loading||result)&&<section className="resultsArea" aria-live="polite" aria-busy={loading}>
      <div className="resultsTitle"><div><span className="sectionNumber">02</span><div><h2>তৈরি করা মন্তব্য</h2><p>Final draft আগে; audit evidence নিচে on-demand</p></div></div>{loading&&<span className="loadingNote">Hosted model-এর response পেতে কিছু সময় লাগতে পারে</span>}</div>
      <div className="resultGrid">{visibleLevels.map(level=>{const output=result?.outputs.find(item=>item.target_level===level.id);const faith=output?.faithfulness;return <article className="responseCard" key={level.id}>
        <header><div className="resultLabel"><span>{level.short}</span><div><b>{level.label}</b><small>{level.note}</small></div></div>{output&&<span className={output.gave_up?'axisFail':'axisPass'} title="Requested-level proxy assessment; not a human-confirmed judgment">{output.gave_up?'Verifier-A: unresolved':'Verifier-A: accepted'}</span>}</header>
        <div className={`responseText ${loading&&!output?'skeleton':''}`}>{output?.final.draft||'মন্তব্য প্রস্তুত হচ্ছে…'}</div>
        {faith&&<div className={`faithBox ${faith.status}`}><div><b>Plot grounding — {FAITH_LABEL[faith.status]}</b></div><p>{faith.explanation}</p>{faith.unsupported_claims.length>0&&<ul>{faith.unsupported_claims.map((claim,i)=><li key={i}>{claim}</li>)}</ul>}<small>এটি generation-এর পরের আলাদা automated check; Verifier-A acceptance বদলায় না, correction loop-এর অংশ নয় এবং human-validated thesis metric নয়।</small></div>}
        {output&&<details className="runEvidence"><summary><span><b>এই run কীভাবে তৈরি হয়েছে</b><small>Component activity ও correction trace</small></span><span>{output.attempts.length} attempt</span></summary>
          <div className="agentActivity"><div className="activityHead"><b>Bounded component activity</b><span>{output.llm_calls} generation-loop LLM call</span></div><ul><li><i>✓</i><span><b>Researcher</b><small>R1-only retrieval</small></span></li><li><i>✓</i><span><b>Writer</b><small>{output.writer_calls} draft call</small></span></li><li><i>✓</i><span><b>Critic</b><small>Verifier-A requested-level gate</small></span></li><li className={output.reflector_calls?'':'skipped'}><i>{output.reflector_calls?'✓':'—'}</i><span><b>Reflector</b><small>{output.reflector_calls?`${output.reflector_calls} correction call`:'চালানো হয়নি—Verifier-A প্রথম attempt গ্রহণ করেছে'}</small></span></li></ul></div>
          <div className="expertTrace">{output.attempts.map(a=><article className="traceItem" key={a.attempt}><div><b>Attempt {a.attempt}</b><span className={a.verdict==='PASS'?'passText':'failText'}>{a.verdict==='PASS'?'ACCEPTED':'REVISE'}</span></div><p>{a.draft}</p><div className="traceMetrics"><span>Target-level proxy score (Verifier-A) {a.neural_score.toFixed(3)}</span><span>Symbolic diagnostic score {a.symbolic_score.toFixed(3)}</span></div><small className="metricCaveat">Verifier-A requested level-এর proxy assessment দেয়; এটি human-confirmed judgment, overall quality, factual accuracy বা real audience response নয়। Symbolic score diagnostic মাত্র; acceptance নির্ধারণ করে না। Verifier-B live interface-এ load হয় না।</small><small className="retrievedIds">R1 evidence IDs: {a.retrieved.join(', ')}</small>{a.feedback&&<blockquote>{a.feedback}</blockquote>}</article>)}</div>
        </details>}
      </article>})}</div>
    </section>}

    <section className="trustBand" aria-label="Scientific safeguards"><div><span>01</span><p><b>R1-only retrieval</b><small>Gold-300 বা R2 prompt-এ যায় না</small></p></div><div><span>02</span><p><b>Verifier-B sealed</b><small>Outcome scorer live loop-এর বাইরে</small></p></div><div><span>03</span><p><b>Hosted processing disclosed</b><small>Plot Google-hosted model-এ যায়; app repository-তে সংরক্ষণ করে না</small></p></div></section>
    <footer className="productFooter"><span>Research demonstration · Thesis Phase 8</span><a href="/research">পদ্ধতি, safeguards ও frozen experiment দেখুন →</a></footer>
  </main>;
}
