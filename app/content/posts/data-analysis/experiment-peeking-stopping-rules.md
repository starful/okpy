---
title: 'Stopping Rules for A/B Tests: How to Avoid the Peeking Problem'
date: '2026-07-26'
category: data-analysis
slug: experiment-peeking-stopping-rules
summary: Checking a test's p-value every day and stopping the moment it looks significant
  quietly inflates your false positive rate far past 5%. This guide walks through
  fixed-horizon, sequential, and alpha-spending stopping rules so you can call winners
  without fooling yourself.
lang: en
source: statfacts
---

If you've ever refreshed a dashboard three times a day during a launch test and stopped the moment the green checkmark appeared, you've run into the peeking problem — and you're not alone. Most experimentation programs inherit this habit from tooling that reports a live p-value, which invites exactly the wrong behavior: treating an in-progress test like a stock ticker instead of a pre-committed measurement. This guide is about the fix — setting a stopping rule before you launch, and picking one that matches how your team actually monitors tests.

## Why Checking Early Breaks the Math

A standard significance test assumes you look at the data once, at a sample size you decided on in advance. The 5% false positive rate you're used to trusting is a promise about that single look — not about a sequence of looks.

Every time you peek and could stop, you're effectively buying another lottery ticket. Random noise has another chance to cross your significance threshold, and eventually it will, even when the underlying effect is exactly zero. Run the same null test with daily peeking and an option to stop as soon as p < 0.05, and the effective false positive rate climbs well past 5% — commonly cited estimates in the sequential-testing literature put continuously-monitored tests at two to four times the nominal rate, depending on how many looks you take and how early you're willing to stop.

The insidious part: nothing about the peeked result looks wrong. The p-value is real, the lift is real in that sample, and the dashboard is not lying to you. What's broken is the correspondence between "p < 0.05" and "5% chance of a false positive" — a correspondence that only holds under the monitoring plan the test assumed.

## Three Stopping Rules, and When Each One Fits

You don't need to choose between "never look at the data" and "no statistical discipline at all." There are three well-established approaches, and the right one depends on how much your team wants to move fast versus stay flexible.

- **Fixed horizon.** Decide the sample size (or run duration) before launch, using a power calculation, and don't look at significance until you hit it. Simplest to reason about, cheapest to implement, and the best default when your traffic is predictable and stakeholders can tolerate waiting for the full window.
- **Sequential testing (e.g., group sequential or always-valid designs).** Built for monitoring. These methods pre-specify a schedule of interim looks and use adjusted significance boundaries at each one, so the cumulative false positive rate across all looks stays at your target — typically 5%. Good fit for teams that need the option to stop early on a strong win or a clear loser without inflating error rates.
- **Bayesian stopping with a fixed rule.** Stop when a posterior probability or credible interval crosses a pre-registered threshold. This sidesteps the peeking problem differently — the probability statement is about the parameter given the data so far, not about a fictional repeated-sampling process — but it only stays honest if the stopping threshold was fixed in advance, not adjusted after seeing how the test was trending.

The failure mode to avoid in all three: picking the rule *after* seeing preliminary results. A stopping rule chosen retroactively isn't a stopping rule, it's a rationalization.

## Alpha Spending, in Practice

Alpha spending is the mechanism most sequential methods use to make interim looks safe. Instead of spending your entire 5% error budget on one final test, you split it across a schedule of looks, spending a little at each one according to a spending function (Pocock and O'Brien-Fleming boundaries are the two most common shapes).

| Look | Fixed-horizon approach | Alpha-spending approach |
|---|---|---|
| Interim check at 25% of sample | Not statistically valid to stop | Requires p < ~0.001–0.005 (very strict early boundary) |
| Interim check at 50% of sample | Not statistically valid to stop | Requires p < ~0.01–0.02 |
| Final look at 100% of sample | Requires p < 0.05 | Requires p < ~0.04–0.045 |

The pattern to notice: early boundaries are deliberately conservative, so a false positive is unlikely to sneak through on a lucky early streak, and the boundary relaxes toward the nominal threshold as you approach the planned sample size. This is why sequential dashboards that show "stop now" recommendations are trustworthy only if they were built around a spending function — a live p-value with a flat 0.05 line at every look is not the same thing, no matter how similar it appears on screen.

## Reading Benchmarks Without Repeating the Same Mistake

The peeking problem doesn't only show up inside your own test — it shows up when you interpret someone else's. When you consult a StatFacts insight card for a comparable intervention, the effect range and confidence rating already reflect the discipline (or lack of it) in the underlying studies. A wide effect range with a lower confidence tag is often telling you that the underlying evidence base includes results measured at inconsistent stopping points, small samples, or non-preregistered endpoints — exactly the conditions that produce inflated, optimistic effects.

Two habits carry over directly from stopping-rule discipline to benchmark reading:

- Treat the **sample_context** on an insight card the way you'd treat your own test's planned sample size — it tells you what population and scale the effect range is actually valid for, not a number to extrapolate past.
- Use the **confidence** rating as a proxy for "was this measured with a pre-committed design," and weight point estimates from low-confidence cards accordingly instead of anchoring on the top of the range.

If your own test's result sits outside the benchmark's effect range, check your stopping discipline before you conclude you've found something unusual — an early, unadjusted peek is a more common explanation than a genuinely exceptional result.

## Making the Stopping Rule Stick Organizationally

The technical fix is well understood; the organizational one is harder. A stopping rule only protects you if it's written down before launch and if "the test looks done" isn't treated as sufficient reason to call it.

- Write the planned sample size or look schedule into the experiment brief, not just the analysis script — someone needs to be able to check compliance without re-deriving your math.
- If stakeholders need interim visibility for planning reasons, give them a sequential dashboard with real spending-function boundaries rather than asking them not to look.
- Log every early-stop decision and the boundary it satisfied. Over a quarter, this creates an audit trail that catches drift toward "we stopped because it looked good" long before it becomes a pattern.
- When a test is inconclusive at the planned horizon, resist the urge to extend it opportunistically. Extending is a legitimate move only if it was itself part of the pre-registered plan (e.g., a group sequential design with a maximum sample size).

None of this requires exotic tooling — most experimentation platforms now support at least one sequential method natively. The discipline is choosing the rule before the data can influence the choice.

Related reading: see [how to read benchmark confidence and effect ranges](/blog/how-to-read-benchmarks) for more on interpreting insight cards, and use the [benchmark calculator](/tools/benchmark-calculator) to sanity-check a planned sample size against comparable effect ranges before you lock in your stopping rule.
