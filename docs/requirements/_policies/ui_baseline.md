---
id: gw_policy_00001
type: policy
title: UI baseline
lifecycle: active
summary: Cross-cutting UI standards every screen inherits.
created: '2026-05-07'
updated: '2026-05-07'
---
# UI baseline

Cross-cutting UI standards every screen inherits. Individual stories only restate these when they deviate.

## Accessibility

Meet WCAG 2.1 AA for color contrast, focus order, visible focus and keyboard operability. Every interactive element has an accessible name. Respect prefers-reduced-motion from the OS and from UserPrefs.reduced_motion.

## Loading State

Render a skeleton consistent with the final layout while data is loading.

## Empty State

Render a named empty state with a primary action when a list or dashboard has no data.

## Error State

Render a retry affordance and display the Request-Id for support when a screen errors.

## Localization

Use UserPrefs/user.language for locale, UserPrefs.compact_numbers for number formatting, and user.timezone for date/time rendering.
