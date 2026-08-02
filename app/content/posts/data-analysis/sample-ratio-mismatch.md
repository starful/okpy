---
title: 'Detecting Sample Ratio Mismatch (SRM) in Experiments: A Methodological Guide'
date: '2026-06-28'
category: data-analysis
slug: sample-ratio-mismatch
summary: Sample Ratio Mismatch (SRM) can invalidate experiment results, leading to
  flawed decisions. This guide outlines practical steps for its detection and interpretation,
  ensuring the integrity of your A/B tests and observational studies.
lang: en
source: statfacts
---

Product Managers, growth hackers, and data analysts rely on experiments to make informed decisions. Yet, a silent killer can undermine even the most meticulously designed A/B tests: Sample Ratio Mismatch (SRM). Ignoring SRM is akin to building on a faulty foundation; it distorts your observed effect ranges, making accurate interpretation of experiment outcomes impossible and leading to wasted resources and incorrect strategic pivots.

## What is Sample Ratio Mismatch (SRM)?

Sample Ratio Mismatch (SRM) occurs when the observed distribution of users or units across experimental groups deviates statistically significantly from the expected distribution. For instance, in a standard A/B test designed to split traffic 50/50 between Control (A) and Treatment (B), an SRM would be detected if, after the experiment runs, you found 55% of users in Treatment and 45% in Control, and this deviation was unlikely to happen by chance.

The "sample ratio" refers to the proportion of units (e.g., users, sessions, devices) assigned to each variant. Most A/B tests aim for equal splits (e.g., 50/50, 33/33/33), but some designs might use unequal splits (e.g., 90/10 for rare feature rollouts). Regardless of the intended ratio, SRM implies that the actual assignment process did not adhere to the design, suggesting fundamental problems within the experimental system.

## Why SRM Is Critical for Experiment Validity

Detecting SRM is not merely a statistical formality; it is a fundamental sanity check that underpins the validity of all subsequent analysis. An unaddressed SRM can lead to:

*   **Invalidated Results:** If your groups are not truly randomized according to your design, then the core assumption of A/B testing—that any observed differences are due to the treatment, not pre-existing group differences—is violated. This means any calculated `effect ranges` for your metrics are unreliable.
*   **Biased Estimates:** An imbalance might indicate a systemic bias in how users are assigned or how data is logged. For example, if users with certain characteristics are disproportionately assigned to one group, any observed treatment effect will be confounded by these pre-existing differences.
*   **False Positives or Negatives:** SRM can mimic or mask true treatment effects. You might incorrectly conclude that a feature has a positive impact when it doesn't (false positive) or dismiss a genuinely impactful change (false negative), leading to suboptimal business decisions.
*   **Resource Waste:** Continuing an experiment with SRM consumes engineering, product, and data science resources without yielding trustworthy insights.

## Methodology for Detecting SRM

Detecting SRM is a straightforward statistical process that should be performed early and regularly during any experiment.

### Step 1: Define Expected Ratios

First, clearly articulate the expected split ratio for your experiment.
*   **Standard A/B Test:** Typically 50/50 (1:1 ratio).
*   **A/B/C Test:** Typically 33/33/33 (1:1:1 ratio).
*   **Staged Rollout:** Could be 90/10 (9:1 ratio) or other specific ratios.

Ensure you understand which units are being randomized. Is it users, devices, cookies, or something else? This `sample_context` is crucial for accurate counting.

### Step 2: Collect Observed Counts

Gather the total number of unique units assigned to each experimental variant. This count should ideally come from the very first interaction or assignment event, before any potential drop-off or conversion.

Let's assume an A/B test with two variants (Control, Treatment) aiming for a 50/50 split.

| Variant   | Observed Count (N) |
| :-------- | :----------------- |
| Control   | 49,000             |
| Treatment | 51,000             |
| **Total** | **100,000**        |

From this, calculate the observed ratios:
*   Control: 49,000 / 100,000 = 0.49 (49%)
*   Treatment: 51,000 / 100,000 = 0.51 (51%)

The expected ratios were 50% and 50%. There's a slight observed difference. Is it significant?

### Step 3: Perform a Statistical Test (Chi-Squared Goodness-of-Fit)

The most common and appropriate statistical test for detecting SRM is the Chi-squared (χ²) goodness-of-fit test. This test compares your observed counts against your expected counts to determine if the deviation is statistically significant.

**Hypotheses:**
*   **Null Hypothesis (H₀):** There is no significant difference between the observed and expected sample ratios. The observed distribution is consistent with the random assignment mechanism.
*   **Alternative Hypothesis (H₁):** There is a significant difference between the observed and expected sample ratios. The observed distribution is *not* consistent with the random assignment mechanism, indicating a potential problem.

**Steps for Calculation (or using a tool):**
1.  **Calculate Expected Counts:** For each variant, multiply the total number of units by its expected ratio.
    *   Expected Control: 100,000 * 0.50 = 50,000
    *   Expected Treatment: 100,000 * 0.50 = 50,000
2.  **Calculate the Chi-Squared Statistic:**
    χ² = Σ [ (Observed - Expected)² / Expected ]
    For our example:
    χ² = [ (49,000 - 50,000)² / 50,000 ] + [ (51,000 - 50,000)² / 50,000 ]
    χ² = [ (-1,000)² / 50,000 ] + [ (1,000)² / 50,000 ]
    χ² = [ 1,000,000 / 50,000 ] + [ 1,000,000 / 50,000 ]
    χ² = 20 + 20 = 40
3.  **Determine Degrees of Freedom (df):** `df = number of variants - 1`. For an A/B test, df = 2 - 1 = 1.
4.  **Find the p-value:** Using the calculated χ² statistic and degrees of freedom, find the corresponding p-value. Many online calculators or statistical software (like Python's `scipy.stats.chisquare` or R's `chisq.test`) can do this.

In our example, a χ² of 40 with 1 degree of freedom yields a p-value extremely close to 0 (e.g., < 0.00001).

### Step 4: Interpret the p-value

Compare the p-value to your pre-defined significance level (alpha, α), typically 0.05.

*   **If p < α:** Reject the null hypothesis. There is statistically significant evidence of SRM. This means the observed deviation is unlikely to be due to chance, and you likely have a problem in your experiment setup.
*   **If p ≥ α:** Fail to reject the null hypothesis. There is not enough statistically significant evidence of SRM. The observed deviations are within the realm of what could occur by random chance.

In our example, with p < 0.00001 and α = 0.05, we would strongly reject the null hypothesis. An SRM is detected. This calls for immediate investigation. For more on interpreting p-values and `confidence` levels, consult StatFacts insight cards.

## What to Do When SRM Is Detected

An SRM detection means **do not proceed with analyzing your core experiment metrics** until the root cause is understood and addressed. Analyzing outcomes under SRM will likely lead to misleading conclusions about your `effect ranges`.

1.  **Stop the Experiment (or pause analysis):** The integrity of your results is compromised.
2.  **Investigate Root Causes:** SRM points to issues in your experimental platform or data logging. Common causes include:
    *   **Randomization Bugs:** Flaws in the code that assigns users to groups.
    *   **Exclusion Logic Issues:** Users being unintentionally excluded or double-counted in one group more than another.
    *   **Client-Side vs. Server-Side Assignment Mismatches:** Discrepancies between where a user is assigned and where their data is logged.
    *   **Data Pipeline Issues:** Data from one group failing to log correctly or completely.
    *   **User Logout/Login/Device Changes:** How your system handles returning users, especially if assignment is cookie-based.
    *   **Bots/Spiders:** Automated traffic that might not be randomized correctly or logged consistently.
    *   **Late Assignment:** Users entering the experiment at different points in their journey, causing selection bias.
3.  **Focus on the Assignment Unit:** Ensure the SRM check is performed on the primary randomization unit (e.g., unique user ID, not page views). If you randomize by user, but check on sessions, a legitimate SRM could be masked or falsely flagged due to behavioral differences. Understanding the `sample_context` is key here.
4.  **Consider Magnitude and Direction:** While the p-value tells you if a deviation is statistically significant, also look at the practical magnitude of the imbalance. A very small percentage deviation (e.g., 0.1%) might be statistically significant with millions of users but could be deemed practically negligible if the cause is benign and unfixable in the short term, though this is rare and risky. However, larger deviations demand immediate attention.
5.  **Fix and Re-run:** Once the root cause is identified and fixed, the experiment should ideally be re-run from scratch to ensure clean, unbiased data. Do not attempt to "correct" for SRM in post-hoc analysis by weighting groups; this is a poor substitute for true randomization.
6.  **A/A Tests:** Running A/A tests (splitting traffic between two identical experiences) is an excellent way to proactively detect SRM and validate your experimental platform's integrity *before* running A/B tests with real changes. If an A/A test shows SRM, your system is broken.

## Continuous Monitoring and Proactive Measures

SRM detection should not be a one-time check. Integrate it into your experiment reporting dashboards and monitor it daily or weekly, especially for long-running experiments or those with high traffic. Automated alerts can flag SRM early, minimizing wasted time and resources.

Moreover, clearly define your `confidence` thresholds for SRM detection. While 0.05 is standard, some teams might opt for a stricter 0.01 for critical experiments, ensuring higher certainty before dismissing the null hypothesis.

By rigorously applying this methodology, product, business, and health teams can significantly enhance the reliability of their experimental findings, ensuring that insights derived from data truly reflect the impact of their interventions.

## Related guides
*   [How to read benchmarks](/blog/how-to-read-benchmarks)
*   [Benchmark calculator](/tools/benchmark-calculator)
