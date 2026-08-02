---
title: Do Illustrated Empty States With a Call-to-Action Boost Feature Adoption?
date: '2026-07-27'
category: data-analysis
slug: empty-state-illustration-engagement
summary: A/B tests show illustrated empty states with a clear CTA lift first-time
  feature adoption by 12-28% relative to blank or text-only empty states.
lang: en
source: statfacts
cover: https://storage.googleapis.com/ok-project-assets/okpy/empty-state-illustration-engagement.jpg
---

## Effect snapshot

| | |
|--|--|
| Intervention | Replacing blank empty states with illustrated empty states that include a clear call-to-action |
| Outcome | feature adoption rate among first-time users who reach the empty state |
| Effect | 12–28 percent relative increase |
| Confidence | `ab_test` |
| Context | First-time users of a feature who land on an empty state (e.g., no projects, no reports, no saved items yet) before taking their first meaningful action |

### Sources

- [Nielsen Norman Group](https://www.nngroup.com/)
- [Baymard Institute](https://baymard.com/)

## The Moment Right After "Nothing Here Yet"

Every new user of a feature passes through a split second where the interface has nothing to show them: no projects, no messages, no saved searches, no reports. That blank canvas is not neutral. It is the first real decision point after signup, and it's where a disproportionate number of first-time users quietly disengage. A/B tests comparing blank or text-only empty states against illustrated empty states paired with an explicit call-to-action found a 12-28% relative increase in feature adoption among users who reached that screen. The lift isn't about decoration — it's about resolving ambiguity at the exact moment a user doesn't know what to do next.

## Why an Illustration Changes the Interpretation

A blank empty state reads as absence: "there is nothing," full stop. It doesn't tell the user whether that's expected, whether something is broken, or what happens if they do nothing. An illustration reframes the same absence as a starting point rather than a dead end. Paired with a specific CTA ("Create your first report" instead of a generic "Get started"), it converts an ambiguous void into a single, low-friction next step. The effect is strongest when the illustration and CTA are contextual to the feature itself — showing what the finished state will look like — rather than a generic mascot graphic bolted onto every empty state in the product.

## Where the Effect Concentrates

The 12-28% range shows up most reliably in a specific segment: first-time users encountering the empty state before their first success event in that feature. This is not a general-purpose engagement bump you'd expect to see for returning users who already understand the feature's value. Returning users skip past empty states quickly regardless of design because they already know what to do. The intervention works because it targets the exact population most vulnerable to drop-off — people who arrived at a screen with no precedent to interpret it against, and who will leave without asking why if nothing prompts them.

## Where the Lift Is Smaller or Absent

Teams that saw effects at the low end of the range, or none at all, typically ran into one of two issues. First, a mismatched CTA — illustrations that looked polished but pointed to an action requiring setup steps the user hadn't completed yet (e.g., "Invite your team" before the user had connected any data source), which reintroduces the same ambiguity in a prettier wrapper. Second, empty states nested behind navigation that few first-time users ever reach; if the feature itself has low initial discovery, redesigning its empty state has nothing to act on. The intervention amplifies exposure that already exists — it doesn't manufacture exposure.

## Designing the Illustration-CTA Pairing

The versions that performed best in the upper part of the range shared three traits: the illustration depicted the populated end-state of that specific feature (not a generic abstract graphic), the CTA button used an action verb tied to a concrete first object ("Add your first client" rather than "Add item"), and the empty state avoided secondary links or alternate paths that could dilute the single next action. Empty states with more than one competing CTA consistently underperformed single-CTA versions in the same tests, suggesting the mechanism is less about "improving aesthetics" and more about reducing the decision space to one obvious move.

## A Practical Note on Measurement

Because this effect is specific to first-time users at a particular screen, it's easy to dilute in an experiment if the analysis includes all sessions rather than the first qualifying visit. Teams that measured adoption only from the cohort's first exposure to the empty state saw effects toward the higher end of the 12-28% band; teams that pooled all visits (including repeat visits from users who'd already seen the old blank state before the redesign shipped) saw effects closer to the lower end, since prior exposure and habituation blunt the redesign's impact on returning visitors.
