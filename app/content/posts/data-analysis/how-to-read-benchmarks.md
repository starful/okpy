---
title: How to Read and Interpret Benchmarks Correctly
date: '2026-06-10'
category: data-analysis
slug: how-to-read-benchmarks
summary: A short guide to effect labels, confidence tags, and sample context—before
  you paste a number into Slack.
lang: en
source: statfacts
---

StatFacts insights follow one pattern: **if you change X, Y moves by about Z**—with a range, a confidence label, and linked sources. This guide explains the fields you see on every card.

## The core fields

| Field | What it tells you |
|-------|-------------------|
| `intervention` | What changed (e.g. remove one signup step) |
| `outcome` | What was measured (e.g. signup completion) |
| `effect_label` | The headline range (e.g. +12–18%) |
| `sample_context` | Who, where, and when the number applied |
| `confidence` | How strong the evidence is |
| `sources` | Primary references to verify |

## Effect labels

- **+12–18%** usually means a *relative* percent change (e.g. 20% → 23%).
- **+8%** with unit `percent_point` means *percentage points* (e.g. 30% → 38%).

Always check the insight detail page for `effect_unit`—mixing these up is the most common citation mistake.

## Confidence at a glance

| Label | Meaning |
|-------|---------|
| Meta-analysis | Multiple studies aggregated |
| A/B test | Controlled experiment on real traffic |
| Study | Published research; causality not guaranteed |
| Estimate | Directional industry rule-of-thumb |

## Sample context

`sample_context` is the guardrail. A benchmark from mobile B2B SaaS may not apply to your desktop marketplace. When context differs, treat the insight as a **hypothesis**, not a forecast.

## Sources

We link primary references where possible. Open them before citing in investor decks, client proposals, or published content.

## Next guides

- [Relative vs absolute effects](/blog/relative-vs-absolute-effects)
- [Confidence levels explained](/blog/confidence-levels-explained)
- [When not to use a benchmark](/blog/when-not-to-use-a-benchmark)
