---
title: 'How Much Does Chunk Size Actually Move the Needle? Effect Sizes for Retrieval A/B Tests in Agentic RAG'
date: 2026-11-17
category: data-analysis
slug: a-b-testing-retrieval-strategies-in-agentic-rag-systems-effect-size-analysis-for
summary: 'Agentic RAG systems — pipelines where an LLM-based agent plans retrieval steps, calls tools, and iterates on queries before producing an answer — have made "…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261117110424.jpg'
lang: en
ja_pending: true
source: hq-draft
---

# How Much Does Chunk Size Actually Move the Needle? Effect Sizes for Retrieval A/B Tests in Agentic RAG

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261117110424.jpg)


Agentic RAG systems — pipelines where an LLM-based agent plans retrieval steps, calls tools, and iterates on queries before producing an answer — have made "just A/B test it" harder than it sounds. In a classic web A/B test, you change a button color and measure a conversion rate. In an agentic retrieval system, you change a chunk size or add a reranker, and that single change cascades through query reformulation, tool-call counts, context window usage, and final answer grounding. The metric you actually care about — "did the agent answer correctly, with the right citations, without hallucinating" — sits three or four steps downstream of the lever you pulled.

This piece is about closing that gap: how to design A/B (or multi-armed) tests for retrieval strategy changes in agentic RAG, how to think about effect sizes rather than point estimates, and what a defensible "effect snapshot" looks like for the two levers that dominate real-world tuning conversations — **chunk size** and **reranking**. It is written for PMs and analysts who need to decide whether a retrieval change is worth shipping, not for researchers optimizing benchmark leaderboards.

## Why retrieval A/B tests in agentic systems are different

Three structural issues make this harder than typical product experimentation:

**1. The unit of analysis is ambiguous.** Is your experimental unit a single query, a full agent session (which may issue 3–8 retrieval calls before answering), or a user? Agentic loops mean one "trial" can touch your retrieval system multiple times with different reformulated queries. If you measure at the query level you get more statistical power but risk pseudo-replication — the queries within one session are correlated, so your variance estimates will be too optimistic unless you cluster standard errors by session.

**2. The outcome metric is multi-dimensional and partly latent.** Retrieval quality (recall@k, NDCG) is a proxy; what you actually want is downstream answer correctness and groundedness, which usually requires either human labeling or an LLM-as-judge step, each with its own noise and bias. A chunk size change can improve recall@10 while making the final answer worse because the agent now has to reason over more fragmented, redundant context — the proxy and the target metric can move in opposite directions.

**3. Confounding between retrieval and the agent's control flow.** In a static RAG pipeline, retrieval and generation are separable. In an agentic pipeline, the agent decides whether to retrieve again, rephrase, or stop — so a retrieval change that returns worse results in isolation might trigger more re-querying, which changes latency and cost even if final accuracy is unaffected. You need to log and report on latency/cost deltas alongside accuracy, because a "statistically significant improvement" that doubles the number of tool calls is not free.

Given this, effect size — not just p-values — is the right lens: you want a magnitude estimate with a confidence interval that a PM can weigh against latency and infrastructure cost, not a binary "significant/not significant" verdict in isolation. Standardized effect sizes (Cohen's h for proportions, Cohen's d for continuous metrics like NDCG, odds ratios for binary correctness judgments) let you compare a chunk-size change against a reranking change on the same scale, even though the underlying metrics differ.

## Designing the experiment: what to hold fixed, what to vary

Before touching chunk size or reranking, fix the rest of the pipeline as an experimental control surface:

- **Fixed embedding model** across arms, unless the embedding model itself is the variable under test. Changing chunk size and embedding model simultaneously confounds the result.
- **Fixed query set, ideally a held-out stratified sample** across intent types (factual lookup, multi-hop reasoning, comparison, summarization) — agentic RAG systems tend to show divergent effects across these buckets, and averaging across them can wash out or invert an effect that's real on multi-hop queries specifically.
- **Fixed agent policy / tool-use budget**, or explicitly measure it as a secondary outcome. If the agent is allowed unlimited retries, a worse retrieval arm may compensate via more loop iterations, masking the effect on accuracy while inflating cost — report both.
- **A stable judge.** If you're using an LLM-as-judge for answer correctness, use the same judge model and rubric across both arms, run it at temperature 0 or with majority-vote-of-3 sampling, and periodically audit judge agreement against a small human-labeled gold set (even 50–100 examples) so you know the judge's own error rate before trusting its verdict on your effect size.

For traffic allocation, standard considerations from online experimentation apply (see the [Evan Miller sample size calculator](https://www.evanmiller.org/ab-testing/sample-size.html) and general treatments like [Kohavi, Tang & Xu's "Trustworthy Online Controlled Experiments"](https://experimentguide.com/)) — but because agentic RAG eval is often expensive (human labels, LLM-judge calls, or both), most teams run these as **offline A/B evaluations on a frozen query set** with bootstrap resampling for confidence intervals, rather than live traffic splits. That's a reasonable and common compromise; just be explicit that your confidence intervals reflect sampling variance over the query set, not live-traffic variance, and that doesn't capture distribution shift if your production query mix changes.

## Lever 1: Chunk size

Chunk size is usually the first knob anyone turns, because it's cheap to change and has an intuitive story: smaller chunks → higher precision, more fragmented context; larger chunks → higher recall of surrounding context, more noise per retrieved unit, and fewer chunks fit in the context window.

### What the public evidence actually supports

There is no single canonical number, and you should be suspicious of any blog post that states one. What's consistently reported across vendor benchmarks and practitioner write-ups:

- **There is a real, often non-monotonic effect of chunk size on retrieval and downstream QA quality**, and it interacts heavily with document structure and query type. Pinecone's and LlamaIndex's chunking guides both report that retrieval/QA metrics move meaningfully across chunk sizes in the few-hundred-to-low-thousand-token range, with the optimum depending on corpus and task — see [Pinecone's chunking strategies guide](https://www.pinecone.io/learn/chunking-strategies/) and [LlamaIndex's evaluation of chunk sizes](https://docs.llamaindex.ai/en/stable/examples/evaluation/) work, where response quality and retrieval metrics were shown to vary non-trivially across chunk sizes in their test corpora.
- **Smaller chunks tend to raise precision/recall@k on narrowly factual queries but can hurt multi-hop or synthesis queries** because the answer-supporting evidence gets split across chunks that may not all be retrieved together. This is a recurring theme in RAG chunking literature and is one of the core motivations behind "parent-child" or hierarchical chunking strategies (retrieve small, pass up the parent context) — see [LangChain's documentation on parent document retrievers](https://python.langchain.com/docs/how_to/parent_document_retriever/).
- **Semantic/structure-aware chunking (splitting on section or sentence-group boundaries rather than fixed token windows) reported improvements over naive fixed-size chunking** in several vendor and open benchmark write-ups, though the reported magnitude varies widely by corpus — treat any single "+X% improvement" headline figure as corpus-specific rather than a general constant. [Chroma's "Evaluating Chunking Strategies for Retrieval"](https://research.trychroma.com/evaluating-chunking) technical report is one of the more rigorous public attempts to quantify this across multiple chunking strategies and is a good reference for method, even if you shouldn't port their exact numbers to your own corpus.
- **In agentic pipelines specifically**, chunk size also interacts with the agent's re-querying behavior: smaller chunks with low per-chunk recall can trigger more agent retrieval loops (the agent "notices" the answer is incomplete and issues follow-up queries), which can partially self-correct accuracy at the cost of latency and token spend. This is an under-measured effect in public benchmarks — most chunking studies are done on static, single-shot RAG, not agentic multi-step retrieval — so treat any chunk-size number lifted from a non-agentic benchmark as a prior, not a prediction, for your agentic system.

### Practical test design for chunk size

Treat chunk size as an ordinal variable with at least 4–5 levels (e.g., ~128, 256, 512, 1024, 2048 tokens) rather than a two-arm A/B, because the relationship is frequently non-monotonic — both too-small and too-large chunks underperform a middle range, and a two-arm test can easily miss the inflection point or misattribute direction. Use overlap (10–20% is a common default) as a separate, explicitly logged parameter rather than letting it vary incidentally between arms.

Report, per chunk-size level, both:
- a **retrieval-layer metric** (Recall@k, NDCG@k, MRR) against a labeled relevance set, and
- a **downstream metric** (answer correctness via judge or human label, citation precision/recall if you track grounding)

and flag any case where these two move in different directions — that divergence is itself the most actionable finding, because it tells you the retrieval metric you've been optimizing is not a faithful proxy for the thing you actually want.

## Lever 2: Reranking

Reranking — running a secondary, typically cross-encoder or LLM-based scorer over the top-N candidates from first-stage retrieval to reorder them before passing the top-k to the generator — is the other high-leverage, well-studied lever.

### What the public evidence actually supports

- **Cross-encoder rerankers (e.g., Cohere Rerank, BGE-reranker, ColBERT-style late-interaction models) reliably and substantially improve ranking-quality metrics (NDCG@k, MRR) over first-stage dense or hybrid retrieval alone**, in both academic IR benchmarks (BEIR) and vendor evaluations. This is one of the more robust and reproducible findings in applied IR — see [Cohere's Rerank documentation and benchmark write-ups](https://docs.cohere.com/docs/reranking) and the [BEIR benchmark paper and leaderboard](https://github.com/beir-cellar/beir), which consistently show reranking stages lifting ranking metrics over bi-encoder-only retrieval across most of its heterogeneous task suite. The reported range of improvement varies a great deal by domain and first-stage retriever quality — treat any single aggregate "+N points NDCG" figure as an average across a very heterogeneous benchmark, not a per-domain guarantee.
- **The marginal value of reranking shrinks as first-stage retrieval quality improves and as k (the number of candidates passed to the generator) shrinks** — reranking has the most room to help when first-stage recall@50-or-so is decent but precision@top-5 is weak, which is the common case for hybrid BM25+dense retrieval over heterogeneous enterprise corpora. If your first-stage retriever already has strong precision@5, expect reranking's incremental lift to be modest.
- **For agentic RAG specifically, reranking's effect on final answer quality is generally reported as positive but smaller in relative terms than its effect on ranking metrics**, because the agent's downstream reasoning can partially compensate for ordering problems (e.g., by reading more of the context window, or issuing a follow-up query) — so a large NDCG lift does not translate one-for-one into a large answer-accuracy lift. This is consistent with the general RAG literature's caution that retrieval-metric gains and end-task-metric gains decouple increasingly as the generator gets more capable at handling noisy or imperfectly-ordered context — see discussion in [Anthropic's contextual retrieval write-up](https://www.anthropic.com/news/contextual-retrieval), which reports retrieval-and-rerank combinations substantially reducing failed-retrieval rates relative to embeddings-only retrieval in their internal evaluation, while being explicit that results are corpus- and task-dependent.
- **Reranking adds latency and cost** (an extra model call, typically over 20–100 candidates) that must be weighed against the accuracy gain — in agentic pipelines where the agent may call the retriever multiple times per session, this latency multiplies, and several practitioner write-ups note that reranking cost/latency becomes the binding constraint before accuracy gains plateau, especially for real-time user-facing agents versus batch/offline agentic workflows.

### Practical test design for reranking

The cleanest reranking A/B design is a 2×1 comparison holding first-stage retrieval fixed: **(first-stage top-k passed directly to generator) vs (first-stage top-N → rerank → top-k passed to generator)**, with N typically 3–10× larger than k. Key design points:

- Vary N (the reranker's candidate pool size) as a secondary factor — too small an N and the reranker can't find candidates the first stage missed in its precision ordering; too large and you pay latency for little gain, since most reranking lift comes from reordering within a first-stage recall@50-ish pool.
- Measure **latency and cost per query/session explicitly as a co-primary metric**, not an afterthought — report it in the same effect-snapshot table as accuracy, because the PM decision is almost always a joint one ("is +X points of accuracy worth +Y ms and +Z cents per query").
- In agentic settings, also track **re-query rate** (how often the agent issues a follow-up retrieval call) as a secondary outcome — a good reranker should reduce re-query rate (the agent finds what it needs faster) alongside improving accuracy, and if it doesn't, that's worth flagging as a signal the reranker isn't actually fixing the thing the agent was compensating for.

## The effect snapshot

The table below is a template for how to report findings — not a claim about universal numbers. **Treat every effect size and CI here as a plausible reported range synthesized from the public literature and vendor benchmarks cited above, not as a number you should port directly into your own system.** Your corpus, embedding model, query mix, and agent policy will shift these, often substantially. The point of this table is the *shape* of reporting — intervention, metric, effect size with a confidence interval, a confidence/evidence-quality rating, and the context that bounds its applicability — which you should reproduce with your own measured numbers before making a ship decision.

| Intervention | Metric | Effect size (reported range) | Evidence confidence | Context / caveats |
|---|---|---|---|---|
| Chunk size: 256 → 512 tokens (fixed-size chunking, dense retrieval) | Recall@10 | Small-to-moderate lift, often reported in the range of a few percentage points to ~0.05–0.15 in absolute recall, direction corpus-dependent | Moderate — consistent direction across vendor write-ups, but magnitude highly corpus-specific | Gains concentrated on queries where answer spans a few sentences; can reverse on highly fragmented source docs |
| Chunk size: naive fixed-size → semantic/structure-aware chunking | Downstream answer correctness (judge-rated) | Reported improvements vary widely; several public write-ups report moderate relative gains, but near-zero gains are also reported on well-structured corpora | Low-to-moderate — fewer rigorous head-to-head studies; most evidence is single-vendor or single-corpus | Benefit shrinks when source documents are already short/well-segmented (e.g., FAQ-style content) |
| Chunk size: very small (<128 tok) vs mid-range (512 tok) | Multi-hop QA accuracy | Often reported as a *negative* effect for very small chunks — accuracy drop plausible in the range of several percentage points | Moderate — the fragmentation problem for multi-hop queries is a widely repeated qualitative finding, less often rigorously quantified | Strongest effect on comparison/synthesis queries requiring evidence from multiple source locations |
| Adding cross-encoder reranking (top-50 → rerank → top-5) over first-stage dense/hybrid retrieval | NDCG@5 or MRR | Consistently positive; BEIR-style benchmarks and vendor reports often show double-digit relative improvement, with absolute NDCG lift commonly reported in the range of ~0.05–0.20 depending on first-stage baseline strength | High for the ranking-metric effect direction; moderate for exact magnitude (highly dependent on first-stage retriever quality) | Marginal lift shrinks substantially if first-stage precision@5 is already strong |
| Adding reranking | Downstream agentic answer accuracy / groundedness | Positive but smaller in relative terms than the NDCG effect; reported reductions in failed-retrieval or hallucination-adjacent error rates, magnitude very setup-dependent | Moderate — directionally consistent, magnitude not well standardized across public sources | Effect partially absorbed by capable agents that can compensate for suboptimal ordering via re-querying or wider context reads |
| Adding reranking | Per-query latency | Consistently negative (added latency), typically an incremental model call over the candidate pool; magnitude depends on reranker model size and N | High — this is a near-mechanical cost, well understood | Multiplies across agentic re-query loops; batch/offline agents tolerate this better than real-time user-facing agents |
| Chunk size increase + reranking combined | Context window utilization / token cost per query | Chunk-size increase raises token cost roughly linearly with chunk size at fixed k; reranking adds a comparatively small token cost (scoring only, not generation) but a real latency cost | High for the mechanical token-cost relationship; moderate for how this nets out against accuracy gains | PM tradeoff is rarely "accuracy vs nothing" — it's "accuracy vs latency+cost," and that ratio is the actual decision variable |

A few things to notice about how this table is built, because the construction matters as much as the content:

- Every row distinguishes a **ranking-layer metric** from a **downstream task metric**, because conflating them is the single most common mistake in retrieval A/B reporting. A reranker can look transformative on NDCG and only modestly move answer accuracy — reporting only the NDCG number overstates the business impact.
- Confidence ratings are *not* p-values. "High" confidence on the reranking-latency row reflects that it's a near-mechanical, almost definitional relationship; "low-to-moderate" confidence on semantic chunking reflects genuinely thin and inconsistent public evidence, not a weak effect per se.
- Cost/latency rows are included as co-equal citizens with accuracy rows, because a retrieval change that's "significant" on accuracy but silent on cost is an incomplete analysis for a PM decision.

## Statistical mechanics: what "effect size" should mean here

For binary/proportion-style metrics (e.g., answer-correct vs. not, judged pass/fail), use **Cohen's h** or simply report the risk difference with a **Wilson or bootstrap confidence interval** — don't rely on a normal-approximation CI with small sample sizes, which is common in offline eval sets of a few hundred queries and can produce misleadingly tight intervals. For continuous ranking metrics (NDCG, MRR), use **Cohen's d** computed on bootstrap-resampled query-level scores, resampling at the session level if your queries are clustered within agent sessions, to avoid the pseudo-replication problem flagged earlier. A practical default: bootstrap with 1,000–2,000 resamples, cluster-resample by session, and report the 95% percentile interval alongside the point estimate — this is cheap to compute and considerably more honest than a t-test p-value when your query set is a few hundred items and not a true random sample of production traffic.

Two reporting habits are worth adopting as defaults:

1. **Always report the effect size with its interval, never a bare point estimate**, even in an internal Slack update — "reranking improved NDCG@5 by 0.08 (95% CI: 0.03–0.13) on 400 held-out queries, clustered by session" is a materially more decision-useful sentence than "reranking improved NDCG by 8%."
2. **Report the null or negative findings with the same rigor as the positive ones.** Chunk-size and reranking experiments frequently produce flat or mixed results on certain query segments (e.g., reranking helps factual lookup but is flat on summarization-style queries) — that segment-level null result is often the most actionable part of the analysis, because it tells you where to *not* spend further tuning effort.

## Segment your results — the average effect is frequently misleading

The single biggest practical failure mode in retrieval A/B testing is reporting one pooled effect size across a heterogeneous query mix. Chunk size and reranking effects documented across public benchmarks are consistently reported as **varying by query type** — factual lookup, multi-hop reasoning, summarization/synthesis, and comparison queries each respond differently, sometimes in opposite directions, to the same retrieval change. Before running your test, stratify your held-out query set into at least these buckets (even a rough heuristic classifier or manual tagging of 200–300 queries is enough), and report the effect size per segment, not just pooled. A chunk-size increase that's flat on average can be a clear win on multi-hop queries and a clear loss on short factual lookups — a decision-maker needs that breakdown to decide whether to ship a uniform chunk size or a query-type-conditional retrieval strategy (which agentic systems, unlike static RAG, can actually implement, since the agent's planning step can route to different retrieval configurations based on query classification).

## Practical takeaway for PMs and analysts

1. **Don't ship on a single pooled metric.** Require, at minimum: a ranking-layer metric (recall/NDCG), a downstream accuracy metric (judge- or human-rated), a latency/cost delta, and a re-query-rate delta, segmented by at least 3–4 query-intent buckets. A chunk-size or reranking change that looks good on one of these and silent or bad on the others is not a clean win — it's a tradeoff that needs an explicit decision, not an automatic ship.

2. **Treat chunk size as a swept ordinal variable, not a binary choice**, because the relationship with accuracy is frequently non-monotonic. Running only a 512-vs-1024 test risks missing that 256 or 2048 is actually better, or that the optimum differs by content type in your corpus.

3. **Reranking is the more reliably positive of the two levers on ranking metrics**, and is the better first bet if you need a change with higher confidence of a real effect — but size its latency/cost impact explicitly before committing, especially for real-time or multi-step agentic workflows where the cost multiplies across retrieval calls per session.

4. **Treat every number in a vendor blog post, including the ones in this article, as a prior from a different corpus, not a forecast for yours.** The direction of these effects (reranking helps ranking quality; mid-range chunk sizes tend to beat extremes; semantic chunking tends to help more on poorly-structured source docs) is reasonably well supported across independent sources. The magnitude is not portable. Budget for running your own offline evaluation — even a few hundred labeled or judge-scored queries, properly stratified and bootstrapped — before making a chunk-size or reranking decision that affects production cost or latency.

5. **Report confidence intervals and segment breakdowns as a default habit, not a special request.** The cost of computing a bootstrap CI and a 4-way segment breakdown is low relative to the cost of shipping a retrieval change on a misleadingly clean pooled average that reverses on your most important query segment in production.

6. **When the ranking metric and the downstream task metric disagree, trust the downstream metric for the ship decision, but investigate the disagreement before discarding the ranking metric** — a persistent gap between the two usually means either your judge/labeling process has a blind spot, or the agent's control flow is compensating for (or being defeated by) a retrieval problem in a way that a one-shot ranking metric can't see. That investigation is often where the next real improvement — in agent policy, not retrieval configuration — gets found.
