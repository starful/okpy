---
title: Planning an A/B test from a benchmark
date: '2026-06-05'
category: data-analysis
slug: planning-ab-test-from-benchmark
summary: Turn a StatFacts range into a test hypothesis, success metric, and realistic
  minimum detectable effect.
lang: en
source: statfacts
---

A benchmark answers: *“What have others seen?”* An A/B test answers: *“What happens here?”* This guide connects the two.

## Step 1 — Translate the insight

From the StatFacts card, write:

- **Hypothesis:** “If we [intervention], [outcome] will improve.”
- **Prior range:** copy `effect_min` / `effect_max` and note `effect_unit`.
- **Context fit:** highlight mismatches in `sample_context` (platform, segment, season).

If context mismatch is large, widen your expected range or run a discovery test first.

## Step 2 — Pick one primary metric

Match the insight’s `outcome` field when possible. Secondary metrics can guard against mixed effects (e.g. signup up, activation down).

## Step 3 — Estimate baseline

You need your current rate to interpret relative lifts. Example:

- Baseline signup completion: **22%**
- Benchmark: **+12–18% relative**
- Implied band: **24.6% – 26.0%** (not 34–40%)

See [Relative vs absolute effects](/blog/relative-vs-absolute-effects) if this math is unfamiliar.

## Step 4 — Set success and guardrails

| Element | Example |
|---------|---------|
| Success | +5 relative points vs control (conservative vs benchmark mid) |
| Guardrail | No increase in support tickets; activation ≥ control |
| Runtime | 2 weeks or until significance + minimum sample |

Benchmarks set **ambition**; your power calculation sets **feasibility**.

## Step 5 — Size the sample (simplified)

Use a standard power calculator with:

- Baseline conversion = your measured rate
- MDE = minimum lift you care about (often below the benchmark max)
- Significance 95%, power 80%

If required traffic exceeds two weeks of volume, shrink scope or accept a higher MDE.

## Step 6 — Document sources in the test brief

```
Prior: +12–18% relative signup completion (StatFacts, meta-analysis, mobile B2B SaaS)
Link: /insight/signup-one-fewer-step_en
Our success criterion: +5 relative points in 14 days
```

Future you (and leadership) will trust results more when the prior is explicit.

## After the test

- **Beat benchmark?** Great—document context wins (segment, season).
- **Miss benchmark?** Also valuable—your product may differ; update internal priors.
- **Publish externally?** Cite your experiment; StatFacts was the planning input, not the result.

## Related guides

- [How to read StatFacts benchmarks](/blog/how-to-read-benchmarks)
- [When not to use a benchmark](/blog/when-not-to-use-a-benchmark)
- [How to cite StatFacts in a deck](/blog/how-to-cite-in-a-deck)
