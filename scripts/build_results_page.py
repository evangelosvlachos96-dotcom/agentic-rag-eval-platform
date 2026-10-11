"""Build the static GitHub Pages report exclusively from saved evidence."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/evangelosvlachos96-dotcom/agentic-rag-eval-platform"
NAMES = {
    "bm25_only": "BM25",
    "vector_only": "Vector",
    "hybrid": "Hybrid",
    "hybrid_rerank": "Hybrid + reranker",
}


def build() -> None:
    rows = []
    bars = []
    for name, label in NAMES.items():
        run = json.loads(
            (DOCS / f"evidence/pilot-baselines/{name}/summary.json").read_text(encoding="utf-8")
        )
        m = run["metrics"]
        hit = m["hit@8"]["mean"] * 100
        rows.append(
            f'<tr><th scope="row">{label}</th><td>{m["hit@1"]["mean"]:.0%}</td>'
            f"<td>{hit:.0f}%</td><td>{m['mrr']['mean']:.3f}</td>"
            f'<td><a href="evidence/pilot-baselines/{name}/report.md">Run report ↗</a></td></tr>'
        )
        bars.append(
            f'<div class="bar-row"><span>{label}</span><div class="track">'
            f'<div class="bar" style="width:{hit}%"></div></div><b>{hit:.0f}%</b></div>'
        )
    live = DOCS / "evidence/live-validation"
    live_rows = []
    for name, label in NAMES.items():
        path = live / name / "summary.json"
        if path.exists():
            run = json.loads(path.read_text(encoding="utf-8"))
            if run["retrieval_only"] or "fake" in (run["llm_provider"] or ""):
                raise ValueError("Live report refuses placeholder or retrieval-only evidence")
            correctness = run["metrics"].get("correctness")
            faithfulness = run["metrics"].get("faithfulness")
            abstention = run["metrics"].get("correct_abstention")
            score = (
                f"{correctness['mean']:.0%} (n={correctness['n']})"
                if correctness
                else "Not measured"
            )
            live_rows.append(
                f'<tr><th scope="row">{label}</th><td>{score}</td>'
                f"<td>{correctness['ci_lower']:.0%} to {correctness['ci_upper']:.0%}</td>"
                f"<td>{faithfulness['mean']:.1%} (n={faithfulness['n']})</td>"
                f"<td>{abstention['mean']:.0%} (n={abstention['n']})</td>"
                f'<td>{run["n_errors"]}</td><td><a href="evidence/live-validation/'
                f'{name}/report.md">Full evidence ↗</a></td></tr>'
            )
    completed = (live / "completion.json").exists()
    live_status = (
        "Live suite executed"
        if completed
        else ("Live validation in progress" if live_rows else "Live validation pending")
    )
    live_html = (
        '<div class="table-wrap"><table><thead><tr><th>Configuration</th>'
        "<th>Judged correctness</th><th>95% CI</th><th>Faithfulness</th>"
        "<th>Correct abstention</th><th>Errors</th><th>Source</th></tr></thead><tbody>"
        + "".join(live_rows)
        + "</tbody></table></div>"
        if live_rows
        else "<p>No completed full live evaluation is available yet. "
        "This section updates only from saved API-run evidence.</p>"
    )
    spend = "No live requests recorded."
    if (live / "budget.json").exists():
        ledger = json.loads((live / "budget.json").read_text(encoding="utf-8"))
        actual = sum(r["actual_usd"] or 0 for r in ledger["records"])
        unknown = sum(r["actual_usd"] is None for r in ledger["records"])
        reserved = sum(r["reserved_usd"] for r in ledger["records"] if r["actual_usd"] is None)
        spend = (
            f"{len(ledger['records'])} API completion attempts. Recorded usage estimate: "
            f"${actual:.4f}, plus ${reserved:.4f} reserved for {unknown} unmetered failures. "
            'See the <a href="evidence/live-validation/budget.json">usage ledger</a>.'
        )
        if unknown:
            spend += (
                " The interrupted run is preserved in the "
                f'<a href="{REPO}/tree/main/docs/evidence/live-validation/interrupted-attempts">'
                "failure archive</a>; its unknown cost was never reset to zero."
            )
    agents = []
    for path in sorted((live / "agents").glob("*.json")):
        trajectory = json.loads(path.read_text(encoding="utf-8"))
        if trajectory["placeholder"]:
            raise ValueError("Live agent evidence cannot be a placeholder")
        agents.append(
            f"<li><details><summary>{escape(trajectory['question'])}</summary>"
            f"<p>{escape(trajectory['answer']['text'])}</p>"
            f'<a href="evidence/live-validation/agents/{path.name}">'
            f"{escape(trajectory['stop_reason'])} · {len(trajectory['steps'])} steps ↗</a>"
            "</details></li>"
        )
    agent_html = (
        "<ul>" + "".join(agents) + "</ul>"
        if agents
        else (
            "<p>Offline agent checks cover search, citations, abstention and failure paths. "
            "Live trajectories are pending; no agent success rate is claimed.</p>"
        )
    )
    example_html = ""
    analysis_path = live / "analysis.json"
    if analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        cards = []
        for example in analysis["examples"]:
            result = example["result"]
            verdicts = ((result.get("judges") or {}).get("faithfulness") or {}).get("claims", [])
            concerns = [v for v in verdicts if not v["supported"]]
            concern_html = "".join(
                f'<p class="small">Judge grounding concern: {escape(v["claim"])} '
                f"— {escape(v['reasoning'])}</p>"
                for v in concerns[:2]
            )
            cards.append(
                f"<details><summary>{escape(example['selection'].title())}: "
                f"{escape(result['question'])}</summary><p>"
                f'{escape(result["answer"]["text"])}</p><p class="small">Reference: '
                f"{escape(result['reference_answer'])}</p>{concern_html}</details>"
            )
        example_html = (
            '<section><div class="eyebrow">Live answer notebook / Hybrid</div>'
            "<h2>Read the outputs behind the scores.</h2>"
            + "".join(cards)
            + f'<p><a href="{REPO}/blob/main/docs/live-results.md">'
            "Full analysis, paired comparisons &amp; limitations ↗</a></p></section>"
        )
    css = """
    :root{--ink:#202c2c;--muted:#526260;--paper:#f4f2e9;--line:#cdd3c8;--accent:#bd4c28}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);
    color:var(--ink);font:17px/1.65 system-ui,sans-serif}a{color:inherit;text-underline-offset:4px}
    a:hover{color:var(--accent)}a:focus-visible{outline:3px solid var(--accent);outline-offset:5px}
    .wrap{max-width:1160px;margin:auto;padding:0 32px}
    nav{display:flex;justify-content:space-between;
    align-items:center;border-bottom:1px solid var(--line);padding:24px 0;font-size:14px}
    nav div{display:flex;gap:24px}.brand{font-weight:750;letter-spacing:1px;text-decoration:none}
    header{padding:78px 0 44px}.eyebrow{font:700 12px/1.5 ui-monospace,monospace;letter-spacing:2px;
    text-transform:uppercase;color:var(--accent)}
    h1{font:500 clamp(42px,6vw,76px)/1.05 Georgia,serif;
    letter-spacing:-2px;max-width:900px;margin:20px 0 26px}h2{font:500 36px/1.2 Georgia,serif;
    letter-spacing:-.7px;margin:10px 0 22px}h3{font-size:20px;margin:0 0 12px}.lead{max-width:770px;
    font-size:20px;color:var(--muted)}.links{display:flex;gap:24px;margin-top:28px;font-size:15px}
    .facts{display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid var(--line);
    margin:20px 0 65px}.fact{padding:25px 18px;border-right:1px solid var(--line)}
    .fact:first-child{padding-left:0}.fact:last-child{border:0}.fact strong{display:block;
    font:500 36px/1.3 Georgia,serif}.fact span{font-size:13px;color:var(--muted)}
    section{margin:65px 0}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:55px}
    .small{font-size:14px;color:var(--muted)}
    .chart{padding-top:12px}.bar-row{display:grid;grid-template-columns:145px 1fr 42px;gap:14px;
    align-items:center;font-size:14px;margin-bottom:24px}.track{background:#dce2d9;height:18px}
    .bar{height:100%;background:#37615a}.bar-row:nth-child(3) .bar{background:var(--accent)}
    .table-wrap{overflow:auto;margin-top:30px}table{width:100%;border-collapse:collapse;font-size:15px}
    td,th{text-align:left;padding:17px 12px;border-bottom:1px solid var(--line)}
    thead th{font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)}
    .note{border-left:3px solid var(--accent);padding:12px 22px;background:#eae8dd;margin-top:28px}
    .status{display:inline-block;padding:5px 12px;border:1px solid #bda98c;font-size:13px;
    border-radius:30px;margin-bottom:18px}.panel{padding:35px;background:#e6ebe2}
    .gallery{display:grid;grid-template-columns:1fr 1fr;gap:22px}
    .gallery img{width:100%;height:auto;
    display:block;border:1px solid var(--line)}figure{margin:0}
    figcaption{font-size:13px;margin-top:10px}
    footer{border-top:1px solid var(--line);padding:30px 0 55px;font-size:13px;color:var(--muted)}
    details{padding:15px 0;border-bottom:1px solid var(--line)}summary{cursor:pointer}
    @media(max-width:720px){.wrap{padding:0 20px}header{padding-top:45px}nav div{gap:12px}
    .grid,.gallery{grid-template-columns:1fr;gap:25px}.facts{grid-template-columns:1fr 1fr}
    .fact:nth-child(3){padding-left:0}.fact:nth-child(2){border:0}.bar-row{grid-template-columns:
    130px 1fr 38px;gap:8px}
    h1{letter-spacing:-1px}.panel{padding:24px}
    section{margin:45px 0}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
    """
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Measured retrieval experiments and transparent validation
    for an agentic RAG evaluation platform by Evangelos Vlachos.">
    <title>Agentic RAG — Evidence & Results</title><style>{css}</style></head><body>
    <div class="wrap"><nav aria-label="Main"><a class="brand" href="#">EV / RAG LAB</a>
    <div><a href="#results">Results</a><a href="#validation">Validation</a>
    <a href="{REPO}">GitHub ↗</a></div></nav><header>
    <div class="eyebrow">Engineering study / Python enhancement proposals</div>
    <h1>Better answers begin<br>with measurable retrieval.</h1>
    <p class="lead">A reproducible agentic RAG platform: pinned source documents, reviewed
    questions, competing retrieval strategies, and evidence you can inspect.</p>
    <div class="links"><a href="#results">Explore the findings ↓</a>
    <a href="{REPO}/blob/main/docs/architecture.md">Read the architecture ↗</a></div></header>
    <div class="facts"><div class="fact"><strong>56</strong><span>Pinned PEP documents</span></div>
    <div class="fact"><strong>24</strong><span>Owner-approved pilot questions</span></div>
    <div class="fact"><strong>4</strong><span>Retrieval configurations</span></div>
    <div class="fact"><strong>7</strong><span>Verified retrieval experiments</span></div></div>
    <section id="results"><div class="grid"><div><div class="eyebrow">01 / Retrieval</div>
    <h2>Hybrid leads this pilot.<br>The uncertainty matters.</h2><p>Hybrid retrieved a labeled
    source in the top eight for 16 of 20 answerable questions. Its paired MRR improvement
    over BM25 remains inconclusive: the 95% interval includes zero.</p>
    <p class="small">Hit@8 measures source retrieval, not answer correctness.
    Four unanswerable questions are excluded from retrieval scoring.</p></div>
    <div class="chart" aria-label="Hit at eight by configuration">{"".join(bars)}</div></div>
    <div class="table-wrap"><table><thead><tr><th>Configuration</th><th>Hit@1</th>
    <th>Hit@8</th><th>MRR</th><th>Evidence</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
    <div class="note">Exploratory pilot, not a leaderboard. The questions are related and
    relevance labels are non-exhaustive. Intervals use 1,000 paired bootstrap resamples,
    seed 0; no multiple-comparison correction.</div></section>
    <section id="validation" class="panel"><div class="eyebrow">02 / Live validation</div>
    <h2>Real responses. Visible accounting.</h2><span class="status">{live_status}</span>
    <p class="small">Generator: Claude Sonnet 5. Judges: Claude Haiku 4.5.
    One generation per question/configuration; no tuning against these outcomes.</p>
    {live_html}<p class="small">{spend}</p><p class="small">A shared US$3 dispatch ceiling,
    buffered input counts, maximum output reservations, and zero automatic SDK retries
    protect the approved allowance. Billing adjustments are not an invoice guarantee.</p>
    <p class="small">Automated judges are not human ground truth. Correctness denominators
    are shown explicitly; errors and missing judgments must be read alongside the score.
    Answerable-question abstentions count as incorrect; faithfulness excludes abstentions.
    An all-success bootstrap interval does not prove perfect accuracy beyond this small sample.
    Human-judge calibration and a held-out benchmark remain outstanding.</p></section>
    {example_html}
    <section><div class="grid"><div><div class="eyebrow">03 / Controlled ablations</div>
    <h2>Smaller chunks trade<br>coverage for rank.</h2><p>250-token chunks raised BM25 Hit@1
    from 25% to 40%, while Hit@8 fell from 70% to 60%. All paired MRR intervals included
    zero. The experiment does not justify changing the default.</p>
    <a href="{REPO}/blob/main/docs/chunking-results.md">Inspect the ablation report ↗</a></div>
    <div><div class="eyebrow">04 / Tool-using agent</div><h2>Every action leaves a trace.</h2>
    {agent_html}<p class="small">A structurally valid cited answer is not proof of factual
    correctness. Single trajectories are demonstrations, not pass@k estimates.
    </p></div></div></section>
    <section><div class="eyebrow">05 / Research notebook</div><h2>Saved findings, not mockups.</h2>
    <div class="gallery"><figure><a href="images/chunking-results.png">
    <img loading="lazy" src="images/chunking-results.png" alt="Chunking ablation results"></a>
    <figcaption>Controlled BM25 chunking and header experiments.</figcaption></figure>
    <figure><a href="images/label-sensitivity.png"><img loading="lazy"
    src="images/label-sensitivity.png" alt="Label sensitivity findings and limitations"></a>
    <figcaption>One proposed missing source label; approved labels remain unchanged.</figcaption>
    </figure></div></section><section><div class="eyebrow">06 / Reproducibility</div>
    <h2>Follow the evidence back to the source.</h2><p>Dataset <code>27b46e65f45d</code> ·
    evaluation set <code>1f48f2e04ef7</code>. Each run records its configuration, prompts,
    code revision, item results and uncertainty. Full documents are fetched from the
    pinned Python PEP corpus; selected passages appear in evidence artifacts.</p>
    <div class="links"><a href="{REPO}/tree/main/docs/evidence">Evidence archive ↗</a>
    <a href="{REPO}/actions">Continuous integration ↗</a>
    <a href="{REPO}/blob/main/docs/readiness.md">Scope & limitations ↗</a></div></section>
    <footer>Built by Evangelos Vlachos · Agentic RAG Evaluation Platform<br>
    Static research showcase. No credentials, live API calls or visitor tracking in this page.
    </footer></div></body></html>"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    (DOCS / ".nojekyll").touch()
    print("Built docs/index.html from saved evidence")


if __name__ == "__main__":
    build()
