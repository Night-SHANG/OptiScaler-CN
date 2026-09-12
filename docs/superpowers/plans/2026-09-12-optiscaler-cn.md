# OptiScaler-CN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish a production-ready, automatically maintained Simplified Chinese OptiScaler localization repository with fail-safe upstream sync, clean Windows builds, and gated releases.

**Architecture:** Keep this repository as a low-coupling localization overlay. Materialize an exact official upstream ref for scan/build, maintain keyed language resources separately, instrument only recognized user-visible UI at build time, and stop publishing on unsafe integration changes.

**Tech Stack:** Python 3 standard library, C++20/header-only runtime localization, Dear ImGui, FreeType, PowerShell, GitHub Actions, Visual Studio 2022/MSBuild.

**Spec:** `docs/superpowers/specs/2026-09-12-optiscaler-cn-design.md`

## Global Constraints
- Official upstream is `https://github.com/optiscaler/OptiScaler` branch `master`.
- English is mandatory runtime fallback.
- Automatic translation must never overwrite reviewed Chinese.
- No API key may be committed.
- Source integration must fail closed on unsafe upstream changes.
- Windows Release x64 must build from a clean GitHub Actions runner before release.
- Community releases must clearly state they are unofficial and identify upstream ref/SHA.

---

### Task 1: Establish regression tests for localization core
**Files:**
- Create: `tests/test_loclib.py`
- Create: `tests/test_scan_ui.py`
- Create: `tests/test_generate_cpp.py`
- Modify only after RED: `tools/loclib.py`, `tools/scan_ui.py`, `tools/generate_cpp.py`

**Interfaces:**
- Consumes: JSON scanner rules and language resources.
- Produces: deterministic candidates, stable catalog entries, valid generated C++ table.

- [ ] Write tests for concatenated C++ strings, comments/escapes, UI API argument detection, exclusions, stable source keys, printf/std::format tokens, and UTF-8 byte-safe C++ generation.
- [ ] Run `python -m unittest discover -s tests -v` and confirm RED for missing/incorrect behavior.
- [ ] Implement minimal fixes in core tools.
- [ ] Re-run tests and confirm GREEN.

### Task 2: Test and harden source instrumentation
**Files:**
- Create: `tests/test_localize_source.py`
- Modify after RED: `tools/localize_source.py`
- Modify after RED if required: `overlay/OptiScaler/localization/Localization.h`

**Interfaces:**
- Consumes: catalog + upstream source tree.
- Produces: instrumented source tree with localization include, direct `T()` calls, dynamic `TL()` hooks, and Chinese font loading.

- [ ] Build a current-architecture fixture for `menu_common.cpp` covering include, `MenuCommon::Init`, HQ font gate, custom TTF block, dynamic menu options, tooltips, and splash text.
- [ ] Add idempotence and fail-closed tests.
- [ ] Run tests and confirm RED.
- [ ] Update patching logic to tolerate formatting changes but reject missing semantic anchors.
- [ ] Re-run all tests and confirm GREEN.

### Task 3: Populate maintained Chinese resources
**Files:**
- Update: `Localization/glossary.json`
- Update: `Localization/translation-memory.zh-CN.json`
- Update: `Localization/zh-CN.json`
- Update/generated from scan fixtures when possible: `Localization/master/{catalog,en-US,pending,meta}.json` and `Localization/stable/{catalog,en-US,pending,meta}.json`

**Interfaces:**
- Consumes: English UI inventory.
- Produces: reviewed Chinese entries and deterministic fallback status.

- [ ] Normalize glossary terminology for NVIDIA/AMD/Intel/common player usage.
- [ ] Seed reviewed translations from maintained translation memory without changing technical names/placeholders/ImGui IDs.
- [ ] Maintain one shared `zh-CN.json` across persisted master and stable inventories.
- [ ] Validate with `python tools/check_localization.py --channel all --strict`.

### Task 4: Complete upstream materialization and sync automation
**Files:**
- Create: `.github/workflows/upstream-sync.yml`
- Create: `tools/upstream_status.py`
- Create: `tests/test_upstream_status.py`
- Modify: `tools/prepare_tree.py`, `upstream.json`

**Interfaces:**
- Produces resolved upstream tag/SHA and release gating metadata.

- [ ] Write tests for stable tag selection, branch/SHA override, and no-new-release behavior.
- [ ] Confirm RED.
- [ ] Implement resolver using GitHub API only at workflow runtime; no secrets required for public upstream.
- [ ] Add daily + manual sync workflow that updates catalog/pending safely and opens/commits localization metadata only when changed.
- [ ] Ensure instrumentation conflict prevents downstream build/release.
- [ ] Confirm GREEN.

### Task 5: Harden build and release workflows
**Files:**
- Modify: `.github/workflows/build.yml`
- Modify: `.github/workflows/release.yml`
- Modify: `.github/workflows/localization-check.yml`
- Modify: `tools/package.ps1`, `tools/release_notes.py`
- Create: `tests/test_release_notes.py`

**Interfaces:**
- Consumes: exact upstream ref/SHA and validated localization tree.
- Produces: versioned ZIP, metadata JSON, Actions artifact, GitHub Release.

- [ ] Add tests for release-note translation statistics and tag-safe naming.
- [ ] Confirm RED then implement.
- [ ] Align build step with official MSBuild flow and official `x64/Release/a` package staging.
- [ ] Add workflow concurrency and least-required permissions.
- [ ] Gate release on build success and stable upstream release detection.

### Task 6: Documentation and repository integrity
**Files:**
- Modify: `README.md`, `README.zh-CN.md`, `UPSTREAM.md`, `TRANSLATION.md`, `CONTRIBUTING.md`, `LICENSE`, `.gitignore`
- Create: `SECURITY.md` only if needed for project-specific reporting guidance.

- [ ] Ensure unofficial/community relationship is explicit.
- [ ] Document install/language/font/update/fallback/contribution flow concisely.
- [ ] Document GPL-3.0 derivative obligations and upstream/FreeType attribution without changing upstream license text.
- [ ] Check all documented commands against actual scripts/workflows.

### Task 7: Full verification and handoff bundle
**Files:**
- Create: `reports/verification.md`
- Create: repository ZIP artifact outside working tree.

- [ ] Run Python compileall and full unit tests.
- [ ] Run localization validator and generated-header check.
- [ ] Run YAML parse/static workflow checks available in this environment.
- [ ] Run instrumentation against current-architecture fixtures.
- [ ] Attempt authoritative Windows build only where a VS2022/MSVC runner is available; otherwise record the environment limitation precisely and leave the GitHub Actions build as the reproducible build verifier.
- [ ] Verify no secrets, caches, `_upstream`, build output, or worktrees are included.
- [ ] Generate final ZIP and directory/coverage/build report.
