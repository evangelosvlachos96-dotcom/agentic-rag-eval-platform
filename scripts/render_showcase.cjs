// Render local report HTML and screenshot it. Requires optional Node package playwright.
// Run from repository root: node scripts/render_showcase.cjs
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const evidence = JSON.parse(fs.readFileSync(path.join(root, 'docs/evidence/verification.json'), 'utf8'));
const candidates = fs.readFileSync(path.join(root, 'eval_sets/candidates/pilot_v2.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const esc = s => String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const css = `*{box-sizing:border-box}body{margin:0;background:#101b2b;color:#edf2f6;font:20px/1.5 Arial,sans-serif}.wrap{padding:52px 64px;width:1400px;min-height:900px}.eyebrow{color:#79dbc7;font-size:15px;font-weight:700;letter-spacing:3px;text-transform:uppercase}h1{font-size:49px;line-height:1.12;letter-spacing:-1.6px;margin:18px 0}h2{font-size:25px;margin:0 0 14px}p{color:#b6c3d1;margin:12px 0}.sub{max-width:1030px;font-size:22px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:32px 0}.card,.panel{background:#19283b;border:1px solid #304156;border-radius:16px;padding:25px}.number{font-size:49px;letter-spacing:-1px;font-weight:700}.label{color:#b6c3d1;font-size:17px}.split{display:grid;grid-template-columns:1.1fr 1fr;gap:24px}.line{padding:12px 0;border-bottom:1px solid #304156;display:flex;justify-content:space-between;font-size:18px}.ok{color:#79dbc7}.pending{color:#f8bf79}.note{border-left:4px solid #f8bf79;background:#26303c;padding:17px 22px;margin-top:26px;font-size:18px}.foot{display:flex;justify-content:space-between;color:#8da0b5;font-size:14px;margin-top:26px}code{color:#b9d9ec;font:16px Consolas,monospace}.question{font-size:25px;line-height:1.35;color:#fff}.tag{display:inline-block;border:1px solid #4a657b;border-radius:6px;padding:4px 10px;font-size:14px;margin-bottom:12px}.quote{font:17px/1.65 Consolas,monospace;white-space:pre-wrap;color:#c8d5e2}.step{margin:15px 0;font-size:18px}.small{font-size:16px}`;
function page(title, content){return `<!doctype html><html lang="en"><meta charset="utf-8"><title>${esc(title)}</title><style>${css}</style><main class="wrap">${content}</main></html>`;}
const checkpoint = page('Evaluation preparation checkpoint', `
<div class="eyebrow">Agentic RAG / Engineering checkpoint / ${evidence.date}</div>
<h1>A reproducible foundation.<br>A benchmark awaiting review.</h1>
<p class="sub">Offline evaluation tooling verified against a rebuilt PEP corpus. Real-world quality claims remain gated on human-reviewed questions.</p>
<div class="grid">
<div class="card"><div class="number">${evidence.tests.passed}</div><div class="label">offline tests passed</div></div>
<div class="card"><div class="number">${evidence.corpus.chunks.toLocaleString('en-US')}</div><div class="label">chunks / 56 PEP documents</div></div>
<div class="card"><div class="number">24</div><div class="label">unreviewed question drafts</div></div>
<div class="card"><div class="number ok">$0</div><div class="label">Anthropic API spend this phase</div></div></div>
<div class="split"><section class="panel"><h2>Verified engineering</h2>
<div class="line"><span>Lint + formatting + strict typing</span><b class="ok">PASS</b></div>
<div class="line"><span>Retrieval-only fixture smoke run</span><b class="ok">PASS</b></div>
<div class="line"><span>Dry-run / declined-spend provider checks</span><b class="ok">PASS</b></div>
<p class="small">2 model-download tests excluded. Fixture checks validate the workflow, not real retrieval quality.</p></section>
<section class="panel"><h2>A finding worth exposing</h2><p>Deduplication removed a passage referenced by one fixture label. The new audit reports that missing passage even when another valid source survives.</p><code>PEP dataset ${evidence.corpus.dataset_version}</code><p class="small">Full corpus: 53 exact duplicates + 1 near-duplicate removed.</p></section></div>
<div class="note"><b class="pending">Next gate: human review.</b> No real PEP scores, agent results or generation benchmarks are claimed.</div>
<div class="foot"><span>Local verification report · Python 3.12 / Windows</span><span>Evidence: docs/evidence/verification.json</span></div>`);
const sample = candidates[0];
const sourceText = [sample.source,...sample.additional_sources].map(s=>s.text).join('\n');
const excerptStart = sourceText.indexOf('While these annotations');
const excerpt = sourceText.slice(excerptStart,excerptStart+620).replace(/\s+/g,' ').trim();
const review = page('Candidate review preview', `
<div class="eyebrow">Agentic RAG / Evaluation set preparation</div><h1>Review the evidence.<br>Then establish the baseline.</h1>
<p class="sub">24 assistant-authored drafts · 6 question categories · 0 human decisions recorded</p>
<div class="split" style="margin-top:30px"><section class="panel"><span class="tag">${esc(sample.id)} / ${esc(sample.category)} / UNREVIEWED</span>
<div class="question">${esc(sample.question)}</div><p><b>Draft reference answer</b></p><p>${esc(sample.reference_answer)}</p>
<div class="note">Accept, edit or reject only after checking source support. Draft answers are not ground truth.</div></section>
<section class="panel"><h2>Attached source passage</h2><p class="small">PEP 484 · ${esc(sample.source.section_path)} · pinned corpus</p>
<div class="quote">${esc(excerpt)}…</div></section></div>
<div class="panel" style="margin-top:24px;padding:20px 25px"><h2>Workflow ready for review</h2><div class="step"><span class="ok">01</span> Source-backed drafts → <span class="pending">02 Human review</span> → 03 Label audit → 04 Retrieval baselines</div><p class="small">Pilot limitations: small sample, easy out-of-domain negatives, multi-hop difficulty needs review.</p></div>
<div class="foot"><span>Preview of the local review packet · not a deployed application</span><span>No Anthropic API calls</span></div>`);
(async()=>{
  const browser = await chromium.launch({headless:true,channel:process.env.SHOWCASE_BROWSER || 'msedge'});
  try {
    const tab = await browser.newPage({viewport:{width:1400,height:960},deviceScaleFactor:1});
    for(const [name,html] of [['evaluation-checkpoint',checkpoint],['evaluation-review',review]]){
      const filename=path.join(root,'docs/showcase',name+'.html');
      fs.writeFileSync(filename,html);
      await tab.goto(pathToFileURL(filename).href);
      await tab.screenshot({path:path.join(root,'docs/images',name+'.png'),fullPage:true});
      console.log('Saved docs/images/'+name+'.png');
    }
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
