# Upstream and Chinese inventory maintenance plan

> **For agentic workers:** Use executing-plans for this bounded maintenance change.

**Goal:** Follow official master and complete its existing untranslated UI inventory without replacing reviewed translations.
**Architecture:** Retain the upstream-materialization overlay. Scan exact master and stable refs, add missing source-bound translations, and validate the same injection and fallback contracts used in CI.
**Tech Stack:** Python unittest, JSON catalogs, generated C++/ImGui, Windows MSBuild.
**Spec:** User request: follow upstream and complete Chinese localization for OptiScaler-CN.

## Global Constraints
- Cloud workspace only; no remote writes or build dispatch during local preparation.
- Preserve reviewed translations, source hashes, printf placeholders, ImGui suffixes, fonts and English fallback.
- Technical names and persisted configuration keys stay unchanged.

## Review Focus
- Newly introduced upstream text and obsolete source entries.
- UI container scans mistakenly treating persistence keys as display labels.
- Format-only and product-name strings must not acquire misleading Chinese.
- Exact master/stable injection anchors, including existing Chinese font fallback.
- Windows build and actual GPU/UI behavior require separate verification, not inferred from Python tests.

## Tasks
- [x] Inspect repository docs, workflows, upstream identity, open PRs and clean baseline (60 tests).
- [x] Scan current master and stable independently and inspect added/removed sources.
- [x] Add missing Chinese translations; preserve technical-only strings with explicit reasons.
- [x] Regenerate pending inventories and validate placeholder/hash/memory contracts.
- [x] Run unit tests, syntax checks, both generated headers and actual source integration.
- [x] Record exact refs and verification gaps; hand off local diff for independent review.

Expanded execution: upstream UI refactoring required scoped helper/table/notification/return scanners, actual display adapters and FPS font handling; see maintenance report. Independent review and Windows validation are parent handoff gates, not claimed complete here.
