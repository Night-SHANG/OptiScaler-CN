# OptiScaler-CN Long-Term Localization Design

## Goal
Build a community Simplified Chinese derivative of OptiScaler that follows official upstream automatically, localizes user-visible UI through a separate localization layer, fails back to official English, builds from a clean GitHub Actions Windows runner, and only publishes when integration and build checks are safe.

## Upstream baseline
- Official repository: `https://github.com/optiscaler/OptiScaler`
- Default branch: `master`
- Build: Visual Studio 2022 / MSBuild, solution `OptiScaler.sln`, Release package staging directory `x64/Release/a`.
- UI: Dear ImGui overlay centered primarily in `OptiScaler/menu/`, with user-visible strings also possible elsewhere in `OptiScaler/**/*.cpp|h`.
- Font: official overlay supports an HQ bundled Hack font and an external `TTFFontPath`; Chinese mode must use a font verified to cover the active Chinese catalog.
- License: GPL-3.0; upstream also credits FreeType under FTL.

## Repository model
This repository is a low-coupling localization overlay rather than a vendored fork snapshot. The maintained repository stores localization resources, deterministic source instrumentation, tests, documentation, and CI. A build materializes an exact upstream ref into `_upstream`, scans it, applies the localization layer, builds it, and packages the official staging output.

This model is intentionally fail-closed. If upstream changes an integration anchor in a way the patcher cannot prove safe, instrumentation exits non-zero and release stops. The last stable release remains untouched.

## Localization model
- `Localization/en-US.json`: generated source-of-truth English catalog mirroring current upstream UI text.
- `Localization/zh-CN.json`: keyed Simplified Chinese translations with `source_hash` and state (`reviewed` or `machine_translated`).
- `Localization/translation-memory.zh-CN.json`: maintained exact-source translation memory used only to seed new keys.
- `Localization/glossary.json`: terminology guidance.
- `Localization/pending.json`: generated missing/changed work queue.
- `Localization/catalog.json`: generated inventory of active/obsolete strings and occurrences.

Runtime calls use a small header-only layer copied into the materialized upstream tree. Direct literal UI arguments become `OptiScalerCN::Loc::T(key, englishFallback)`. Dynamic labels/tooltips stored in known menu containers pass through `TL(englishSource)`. English is always the runtime fallback.

## UI discovery
The scanner walks configured `OptiScaler/**/*.cpp|h` scopes and only inspects known UI APIs plus explicitly configured UI containers. It deliberately ignores arbitrary string literals, logs, file paths, shader text, DLL names, technical-only identifiers, and comments. Each hit records file, line, callee, and argument index.

Keys are stable across ordinary source movement because exact source text is matched first. Changed text in the same file/callee scope can retain a key via conservative fuzzy matching; its translation becomes stale until reviewed or machine-translated for the new `source_hash`.

## Translation safety
- Existing `reviewed` translations are never overwritten by automatic translation.
- Missing strings may be machine-translated only when API secrets are configured.
- Changed reviewed strings receive a machine candidate instead of replacing the reviewed translation.
- Stale/missing translations render official English.
- Validation preserves printf/std::format placeholders and ImGui `##` IDs.

## Chinese font handling
Chinese mode requests HQ font creation even if official `UseHQFont` is false. Font selection order:
1. `OptiScalerCN.ini` explicit `FontPath`.
2. Official OptiScaler `TTFFontPath` if configured.
3. Known Windows CJK fonts.

A candidate is accepted only if FreeType confirms glyph coverage for every non-ASCII code point in the effective Chinese catalog. ImGui glyph ranges are built from the default Latin range plus the exact Chinese translation text. If no valid font exists, Chinese is disabled in-memory and UI falls back to English instead of showing tofu/missing glyphs.

## Upstream synchronization
`upstream-sync.yml` runs daily and manually. It resolves the latest upstream stable release and/or branch head, materializes the exact source, scans UI, optionally translates only pending strings, validates resources, performs instrumentation smoke checks, and commits generated localization metadata when it changed. It then dispatches/starts a Windows build. Integration conflicts stop the workflow and prevent release.

Stable automatic release is gated by a new upstream stable tag. Manual builds may target a tag/branch/SHA without publishing.

## Build and release
Windows Actions use official-compatible VS2022/MSBuild flow:
1. Checkout this repository.
2. Clone exact upstream ref with recursive submodules.
3. Scan/update localization catalog.
4. Validate localization.
5. Generate and inject localization code.
6. Build `OptiScaler.sln` Release x64.
7. Package `x64/Release/a` plus community config/docs.
8. Upload artifact.
9. For release workflow, create a clearly named community release with upstream ref/SHA, translation stats, build date, known limitations, metadata, and SHA256.

## Failure policy
No workflow may force-merge or publish after source instrumentation conflicts, localization validation failure, missing output package, or MSBuild failure. Automatic synchronization never overwrites reviewed translations. Previous releases are never mutated by a failed sync.

## Testing
Local Python unit tests cover scanner parsing, exclusion rules, stable keys, translation-state preservation, placeholder checks, generated C++ UTF-8 escaping, instrumentation idempotence/fail-closed anchors, and release metadata generation. GitHub Actions provide the authoritative Windows compile verification because the project requires MSVC/VS2022.

## Known non-automatable cases
A major upstream UI architecture refactor can require updating scanner call rules or source-instrumentation anchors. New custom UI widgets whose strings do not flow through known ImGui/menu APIs require adding a scanner/container rule. Semantically poor machine translation still requires human review. A user on a stripped/custom Windows installation may need to configure a CJK font explicitly.
