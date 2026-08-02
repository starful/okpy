---
title: 'Heterogeneous Treatment Effects: How to Read Subgroup Lift Without Fooling
  Yourself'
date: '2026-07-26'
category: data-analysis
slug: heterogeneous-treatment-effect-analysis
summary: Average treatment effects hide as much as they reveal — this guide covers
  how to analyze segment-level lift responsibly, from pre-registration to shrinkage
  to knowing when a subgroup difference is real. It's written for teams using effect-size
  benchmarks to decide whether a personalization strategy is worth building.
lang: en
source: statfacts
---

An experiment reports a 3% lift on the primary metric. Somewhere in that average, new users saw an 11% gain and returning users saw a 2% loss — but the topline number doesn't tell you that, and if you don't go looking, you'll ship a feature that helps a third of your users while quietly annoying the rest. Heterogeneous treatment effect (HTE) analysis is the practice of finding those splits deliberately, with enough statistical discipline that you're not just reading noise into a scatter plot.

This guide is about how to do subgroup analysis without the two failure modes that make it dangerous: p-hacking your way to a story you wanted to tell, and dismissing real segment-level effects because they didn't clear an average-effect bar that was never the right bar to begin with.

## Why the Average Effect Is the Wrong Unit of Decision

The average treatment effect (ATE) answers "did this work, on net, across everyone in the experiment." That's the right question for a go/no-go ship decision on a single, universally-applied change. It's the wrong question the moment you're deciding whether to personalize — because personalization only makes sense if the effect *varies* by segment. If it didn't vary, you'd just ship the winning variant to everyone and be done.

Practically, this means HTE analysis isn't a follow-up to your main readout — it's a separate analysis with its own hypotheses, its own multiple-comparisons budget, and its own confidence bar. When you're logging effect sizes on StatFacts, treat a segment-level lift as a distinct insight card with its own effect range and confidence tag, not a footnote on the ATE card.

## Pre-Specifying Segments Before You Look

The single biggest source of false HTE findings is post-hoc slicing: running the experiment, then cutting the data by device, plan tier, geography, tenure, and acquisition channel until one of them clears p < 0.05. With five uncorrelated cuts you already have a ~23% chance of a spurious "significant" segment; with twenty cuts, it's closer to certain.

The fix is boring but effective:

- Write down the segments you'll test *before* the experiment launches — typically 3-6, chosen because you have a mechanistic reason to expect a different response (e.g., new vs. returning users, because onboarding friction only exists for one group).
- Distinguish confirmatory segments (pre-registered, held to your normal significance threshold) from exploratory ones (reported with a label like "exploratory — not adjusted for multiplicity," and treated as hypothesis-generating only).
- If you must explore beyond the pre-specified list, apply a correction (Bonferroni or Benjamini-Hochberg are both fine starting points) and say so when you record the result.

## Shrinkage: Why the Naive Subgroup Estimate Is Almost Always Too Big

Even with a clean pre-specified segment, the naive difference-in-differences estimate for that subgroup is biased away from zero, because you're conditioning on a smaller sample and noise inflates the observed spread. A segment that shows a 22% lift on n=800 is genuinely more likely to regress toward something like 10-14% on replication than it is to hold at 22%.

Two practical responses:

- Apply partial pooling (a simple empirical Bayes or hierarchical shrinkage toward the grand mean) rather than reporting the raw per-segment estimate at face value, especially when a segment has under ~1,000 units.
- When you log a segment-level card on StatFacts, prefer the shrunk estimate and widen the confidence interval rather than reporting the flashiest raw number — the sample_context field should note the segment n, since a 15% lift on n=300 and a 15% lift on n=15,000 are not the same claim.

## Interaction Tests, Not Parallel Significance Tests

A common mistake: running the treatment-vs-control test separately inside each segment, finding it's significant in Segment A and not in Segment B, and concluding "the effect is different for A and B." That comparison is invalid — significance in one group and non-significance in another doesn't establish a statistically different effect between groups; the confidence intervals frequently still overlap.

What actually tests heterogeneity is an interaction term: treatment × segment, evaluated directly, or a formal test of whether the segment-specific effects differ from each other beyond what sampling variation would produce. If you don't have the bandwidth for a full interaction model, at minimum plot the two segment effect sizes with their confidence intervals side by side before claiming they differ — StatFacts insight cards that show overlapping ranges across segments are a useful gut check before you write the sentence "this works better for X than Y."

## Reading Segment-Level Cards on StatFacts

When you're pulling comparable numbers from StatFacts to sanity-check your own subgroup results, three fields matter more here than in a standard ATE lookup:

| Field | Why it matters for HTE |
|---|---|
| Effect range | A segment card's range should be read as *this segment's* plausible lift, not a universal constant — expect real variation across products even for structurally similar segments (e.g., "new user" cohorts differ by onboarding design) |
| Confidence | Segment-level confidence is typically lower than the parent ATE's, because n is smaller by construction — a "moderate" confidence subgroup card is not weaker evidence than a "high" confidence ATE card, it's answering a harder question with less data |
| Sample context | Tells you whether the benchmark segment resembles yours in size and composition — a lift measured on a segment of 50,000 doesn't transfer cleanly to a startup validating against a segment of 400 |

Use these fields to calibrate expectations before you run the experiment, not just to validate results after. If the benchmark range for a comparable segment is wide (say, a broad 4-18% band), that width is informative — it tells you the true effect is context-dependent, and your own point estimate should be trusted less on the strength of a single experiment.

## Deciding Whether to Personalize at All

Finding a statistically real HTE doesn't automatically justify building segment-specific treatments. The decision hinges on three things beyond significance:

- **Magnitude of the gap.** A confirmed but small gap (e.g., 3% vs. 5% lift across two segments) rarely justifies the engineering and maintenance cost of a branched experience. A large, confirmed gap (e.g., a segment showing a lift and another showing a null or negative effect) usually does.
- **Segment addressability.** Can you actually target this segment reliably in production (a stable attribute like tenure) or only in the analysis (a post-hoc behavioral cluster that's hard to identify before treatment)?
- **Stability over time.** Re-run the segment cut on a holdout period or a second experiment before committing engineering resources — a one-off interaction that doesn't replicate is the most common way personalization roadmaps waste a quarter.

If the gap clears all three bars, the segment-level effect size — shrunk, interval-bound, and replicated — is what should go into your rollout plan, not the original exploratory number that first caught your eye.

For the mechanics of reading effect ranges and confidence tags in general, see [How to Read Benchmarks](/blog/how-to-read-benchmarks). To sanity-check whether an observed segment gap is large enough to be worth acting on given your own sample size, use the [Benchmark Calculator](/tools/benchmark-calculator).
