---
title: 'Relative vs Absolute: Understanding Difference, Change & Risk'
date: '2026-06-09'
category: data-analysis
slug: relative-vs-absolute-effects
summary: Why +10% and +10 points are not the same—and how to avoid embarrassing math
  in your next deck.
lang: en
source: statfacts
---

The same headline number can mean very different things. Before you cite a StatFacts insight, know which unit you are looking at.

## Relative percent change

**Example:** +12–18% signup completion

This is a *relative* lift on the baseline rate.

- Baseline 20% → upper bound ≈ 23.6% (20 × 1.18)
- Baseline 5% → upper bound ≈ 5.9%

The absolute gain in points shrinks when your baseline is low. A “+15%” story can be a fraction of a point in practice.

**When to use:** Comparing proportional improvement across teams, prioritizing levers when baselines are similar.

## Percentage points

**Example:** +8% signup conversion (percent_point)

This is an *absolute* shift on the rate itself.

- 30% → 38% conversion (+8 points)
- Not the same as “+8% relative” (30% → 32.4%)

**When to use:** Finance models, funnel math, forecasting revenue from conversion changes.

## Mixed or directional labels

Some insights (especially sports or health) report **mixed** effects—one metric up, another down. Read the outcome field and body text together; do not cherry-pick the favorable line.

## Quick checklist

1. Find `effect_unit` on the insight page.
2. Write down your **current baseline** before applying the range.
3. State both relative and absolute impact if your audience includes finance and product.

## Rule of thumb

If someone says “conversion went up 10%,” ask: **10% of what, or 10 points?** StatFacts tries to label this explicitly—your job is to carry that precision forward.
