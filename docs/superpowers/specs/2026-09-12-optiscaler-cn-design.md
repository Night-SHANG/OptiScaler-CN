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
- `Localization/master/{catalog,en-US,pending,meta}.json`: persisted inventory for the current upstream development branch.
- `Localization/stable/{catalog,en-US,pending,meta}.json`: persisted inventory for the current upstream stable release.
- `Localization/zh-CN.json`: one shared keyed Simplified Chinese translation store used by both channels, with `source_hash` and state (`reviewed` or `machine_translated`).
- `Localization/translation-memory.zh-CN.json`: maintained exact-source translation memory used only to seed new keys.
- `Localization/glossary.json`: terminology guidance.
- Root `catalog.json`, `en-US.json`, and `pending.json` are compatibility mirrors of `master/`; channel directories are authoritative.

Runtime calls use a small header-only layer copied into the materialized upstream tree. Direct literal UI arguments become `OptiScalerCN::Loc::T(key, englishFallback)`. Dynamic labels/tooltips stored in known menu containers pass through `TL(englishSource)`. English is always the runtime fallback.

## UI discovery
The scanner walks configured `OptiScaler/**/*.cpp|h` scopes and only inspects known UI APIs plus explicitly configured UI containers. It deliberately ignores arbitrary string literals, logs, file paths, shader text, DLL names, technical-only identifiers, and comments. Each hit records file, line, callee, and argument index.

Keys are derived from exact English source text and remain stable across ordinary source movement. If upstream changes the English wording, the new wording receives a new immutable key while the old key remains available for the other channel or historical translation memory. This prevents `master` and `stable` from ever sharing one key with different English meanings.

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
`upstream-sync.yml` runs daily and manually. It resolves both the latest upstream `master` head and latest stable release, materializes and scans both exact sources, optionally translates only pending strings, validates the shared language store against both catalogs, performs instrumentation smoke checks, and commits generated localization metadata when it changed. Empty channel catalogs are treated as a bootstrap condition even when upstream itself has not changed.

A master change dispatches the Windows development build. A new stable tag dispatches a stable release, and an automated change to shared Chinese translations refreshes the current stable release as well. Integration conflicts stop the workflow and prevent publication.

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
