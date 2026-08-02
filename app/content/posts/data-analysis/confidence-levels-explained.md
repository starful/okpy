---
title: 'Confidence Levels Explained: Understanding Statistical Evidence'
date: '2026-06-08'
category: data-analysis
slug: confidence-levels-explained
summary: What meta-analysis, A/B test, study, and estimate mean on StatFacts—and how
  much weight to give each.
lang: en
source: statfacts
---

Every StatFacts card carries a confidence badge. It is not a quality score for the writing—it describes **how the number was produced**.

## Meta-analysis

**What it means:** Multiple studies or datasets were aggregated; the range reflects pooled evidence.

**Strengths:** Broader than a single experiment; useful for planning bands.

**Limits:** Publication bias, different populations mixed together, still may not match your product.

**Use for:** Roadmap prioritization, rough sizing, stakeholder education.

## A/B test

**What it means:** A controlled experiment—usually on live traffic—with a measured lift.

**Strengths:** Closest to how product teams actually learn; often includes real UX context.

**Limits:** One company, one season, one segment; may not replicate for you.

**Use for:** Justifying a test you are about to run, comparing magnitude across tactics.

## Study

**What it means:** Published research (observational or experimental) that supports a directional effect.

**Strengths:** Peer-reviewed or primary data sources; good for non-product domains (sports, health).

**Limits:** Causality is not guaranteed; lab conditions differ from your environment.

**Use for:** Hypothesis generation, category pages, science-backed hooks.

## Estimate

**What it means:** A directional industry rule-of-thumb—useful, but not tied to one cited experiment on the card.

**Strengths:** Fast orientation when no clean study exists; honest about uncertainty.

**Limits:** Wide variance in the wild; easiest label to over-trust.

**Use for:** Icebreakers in workshops, backlog grooming—not board-level forecasts without backup.

## How we apply labels

Editors pick the **best available evidence** linked on the insight. When evidence is thin, we label it estimate rather than inflate confidence.

## Practical weighting

| Your decision | Lean on |
|---------------|---------|
| Ship a test this sprint | A/B test, then study |
| Annual revenue model | Meta-analysis + your own baseline |
| Twitter / newsletter hook | Any—cite the label honestly |
| Investor memo | Meta-analysis or study + primary source PDF |

When in doubt, open the sources and upgrade or downgrade the label yourself.
