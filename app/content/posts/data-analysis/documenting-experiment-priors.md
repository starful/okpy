---
title: Documenting external priors in experiment briefs
date: '2026-06-28'
category: data-analysis
slug: documenting-experiment-priors
summary: Use industry benchmarks and past tests to set realistic effect-size expectations
  before you launch an A/B test.
lang: en
source: statfacts
---

Setting clear expectations before an experiment begins is fundamental for any Product Manager, Growth Lead, or Analyst. Without robust pre-experiment context, interpreting results can devolve into subjective narratives, leading to misinformed decisions and wasted resources. This guide outlines a structured methodology for documenting external priors within your experiment briefs, ensuring a precise, benchmark-driven approach to A/B testing and feature evaluation.

## Why External Priors Are Non-Negotiable

An external prior is an established baseline expectation of an effect size, derived from data sources *outside* your immediate experimental setup. This could be industry benchmarks, competitive intelligence, academic research, or analogous past experiments. Incorporating these priors into your experiment briefs offers several critical advantages:

*   **Contextualizes Expected Effect Sizes:** It helps define a realistic range for the change you anticipate, preventing teams from either chasing impossibly large gains or dismissing genuinely significant, albeit modest, improvements.
*   **Informs Hypothesis Formulation:** Priors guide the precision of your hypotheses, moving beyond vague "we expect X to increase" to "we expect X to increase Y by Z% (based on prior P)."
*   **Optimizes Experiment Design:** Crucially, well-defined priors are essential for accurate power analysis, ensuring you collect sufficient data to detect meaningful effects without overspending on unnecessary sample sizes.
*   **Fosters Objective Interpretation:** By setting expectations upfront, you create a neutral framework for evaluating results, minimizing the risk of confirmation bias or post-hoc rationalization.
*   **Builds Institutional Knowledge:** Documented priors serve as a valuable knowledge base, refining future estimates and improving the accuracy of subsequent experiments.

## Sources for Constructing External Priors

Developing robust external priors requires diligent research across various data streams. Consider the following common sources:

*   **Industry Benchmarks:** Reports, case studies, or aggregated data from similar products, services, or user behaviors within your industry. StatFacts, for instance, provides anonymized effect ranges across different sectors and metrics.
*   **Internal Historical Data:** Past experiments, feature launches, or product updates on similar aspects of your product. Even if not directly comparable, these can offer directional insights into typical effect magnitudes.
*   **Academic Research & Public Studies:** Peer-reviewed papers or public datasets can provide generalized effect sizes for behavioral changes, user interactions, or market responses relevant to your experiment.
*   **Competitive Analysis:** Observing competitor feature rollouts or stated impact can sometimes hint at expected effect sizes, though direct comparison is often challenging due to differing contexts.
*   **Market Research & User Surveys:** While not direct effect sizes, these can inform the *potential magnitude* of user pain points or desires, indirectly suggesting the likely impact of solutions.

## Integrating Priors into Your Experiment Brief

The experiment brief is the central document that guides your team through the entire experimentation lifecycle. Integrate external priors explicitly within key sections:

### 1. Hypothesis Statement Refinement

Transform generic hypotheses into precise, quantitatively informed statements.

**Before:** "We hypothesize that changing the button color will increase conversions."
**After:** "We hypothesize that changing the button color to blue will increase conversion rate by 1-3%, based on observed industry benchmarks for UI element changes impacting low-friction actions (e.g., newsletter sign-ups)."

### 2. Expected Effect Size & Range

This section is paramount. Explicitly state the anticipated effect size, not as a single point estimate, but as a plausible *range* informed by your external priors.

*   **Define the Range:** Based on your research, articulate the minimum detectable effect (MDE) that would be considered practically significant, and the maximum effect you reasonably expect.
*   **Justify the Range:** Explain *why* this range was chosen, citing specific sources or analogous situations.
*   **Link to StatFacts:** For a deeper understanding of how to interpret these effect ranges and contextualize them against broader industry data, consult StatFacts insight cards on [effect ranges](/guide/how-to-read-benchmarks#effect-ranges-explained).

### 3. Sample Size and Power Calculation Context

External priors are indispensable for accurate sample size calculations.

*   **Inform MDE:** Your chosen expected effect range (particularly the lower bound of practical significance) directly feeds into calculating the necessary sample size to achieve sufficient statistical power.
*   **Avoid Over/Under-Powering:** Without a prior-informed MDE, you risk running experiments that are either too small to detect real effects (underpowered) or unnecessarily large (overpowered), wasting time and resources.
*   **StatFacts Context:** Understanding the interplay between MDE, sample size, and the reliability of your findings is critical. Explore StatFacts cards on [confidence](/guide/how-to-read-benchmarks#understanding-confidence) for more context on interpreting statistical reliability.

### 4. Success Criteria and Decision Making

Priors help establish objective thresholds for success and guide post-experiment decision-making.

*   **Thresholds:** What effect size, within your prior-informed range, will signify a 'win' worth pursuing further investment?
*   **Learning:** Even if the experiment doesn't meet the optimistic end of your prior range, did it fall within the acceptable learning range? This helps classify outcomes beyond simple "pass/fail."

## Practical Documentation Steps

Follow these steps to systematically document external priors in your experiment briefs:

1.  **Identify Key Metrics:** For each primary metric targeted by your experiment, determine what external priors are relevant.
2.  **Gather Data:** Collect specific data points, reports, or studies that provide benchmark effect sizes for similar actions or user behaviors.
3.  **Define a Plausible Range:** Based on the gathered data, establish a realistic lower and upper bound for the expected effect size. This range should account for potential variability and contextual differences.
4.  **Articulate Source and Sample Context:** Crucially, document where the prior comes from and, importantly, the *sample context* of that source data. For example, "Industry benchmark for e-commerce conversion lift on product page UI changes (source: XYZ Report, Q4 2023, data from B2C retail sites with >1M monthly users)."
5.  **Justify Applicability:** Briefly explain *why* you believe this external prior is relevant to your specific experiment, acknowledging any potential differences or limitations.
6.  **Include Caveats:** No external prior is a perfect fit. Note any significant differences between the source context and your experiment's context that might influence the actual outcome.

Here's a simple example of how this could be structured in an experiment brief:

| Metric               | External Prior Range | Source / Context                                                               | Rationale / Caveats                                                                                                                                                                                                                                                            |
| :------------------- | :------------------- | :----------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Conversion Rate      | +1.0% to +3.0%       | StatFacts UI Optimization Benchmarks (Q2 2024, B2C SaaS trial sign-ups)        | Benchmarks show typical lifts for CTA placement/color changes. Our product is B2B, which may result in slightly lower elasticities. Range reflects potential B2B dampening compared to B2C.                                                                                     |
| Engagement (Avg. Time on Page) | +5% to +10%          | Internal A/B test (Feature X, similar content type, Q1 2023)                   | Prior experiment on an adjacent feature showed similar engagement lifts for content enrichment. Assumes similar user response to content improvements.                                                                                                                           |
| Retention (Day 7)    | No direct prior      | Qualitative user feedback suggests high pain point (prior indicates potential) | While no direct benchmark for this specific intervention exists, qualitative data strongly points to a significant pain point. We expect *any* positive movement, even modest, to be meaningful. Will use a lower MDE to detect small but positive signals.                             |

### Understanding Sample Context

The "Source / Context" column in the table above is critical. When leveraging external benchmarks, the `sample_context` is paramount to judging its applicability. A benchmark for a large e-commerce site might not translate directly to a niche B2B SaaS platform. Factors like user base size, industry, product maturity, and specific user behavior can significantly alter effect magnitudes. Always delve into the `sample_context` behind any benchmark you consult; StatFacts insight cards specifically address the importance of understanding `sample_context` when interpreting and applying benchmarks.

## Conclusion

Documenting external priors in your experiment briefs transforms experiment design from an intuitive guess to a data-informed process. It provides a robust framework for setting expectations, optimizing resource allocation, and ensuring objective interpretation of results. By consistently integrating benchmarks and contextual information, teams can make more confident, data-driven decisions that propel product and business growth.

---
Related guides:
*   [How to Read Benchmarks](/blog/how-to-read-benchmarks)
*   [Benchmark Calculator](/tools/benchmark-calculator)
