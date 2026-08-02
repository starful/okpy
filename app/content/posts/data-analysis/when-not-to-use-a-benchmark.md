---
title: When not to use a benchmark
date: '2026-06-07'
category: data-analysis
slug: when-not-to-use-a-benchmark
summary: Five situations where copying a StatFacts number will mislead your team—and
  what to do instead.
lang: en
source: statfacts
---

Benchmarks save time because someone already measured a lever. They fail when **context diverges** or **causality is assumed without evidence**.

## 1. Different audience or platform

A mobile SaaS signup lift may not transfer to desktop enterprise software with SSO mandates. Check `sample_context` for platform, segment, and geography.

**Instead:** Use the benchmark as a prior; run a scoped test on your traffic.

## 2. Different baseline performance

Relative lifts compress when you are already optimized. A +20% checkout improvement from a bloated 23-field form is unlikely if you already run a 3-field flow.

**Instead:** Model from your baseline using [relative vs absolute effects](/blog/relative-vs-absolute-effects).

## 3. Mixed outcomes you do not want

Sports and product insights often trade one metric for another (e.g. contact rate up, power down). Copying only the favorable line is misleading.

**Instead:** Quote the full trade-off or link the whole insight.

## 4. Estimate labeled as certainty

An **estimate** is a compass, not GPS. Treating it like meta-analysis in a board slide is how teams pick wrong OKRs.

**Instead:** Pair estimates with your own experiment or a stronger source.

## 5. Legal, medical, or HR decisions without review

StatFacts summarizes published ranges for planning conversations—not professional advice. Health and HR insights especially need domain review.

**Instead:** Use insights to form questions for qualified advisors, not final policies.

## Red flags checklist

- [ ] You cannot explain the intervention in one sentence on your product
- [ ] Your baseline rate is unknown
- [ ] The confidence badge is estimate but the slide title says “proven”
- [ ] Sources are paywalled and unread
- [ ] The outcome metric is not what you actually measure

## What good usage looks like

> “Similar B2B mobile flows saw **+12–18%** relative signup lifts (meta-analysis). We run a two-week A/B on step removal; success = +5 points minimum.”

That sentence cites StatFacts **and** shows local validation—exactly the intent of this library.
