# OptiScaler-CN maintenance — 2026-10-31 UTC

## Scope and provenance

- CN baseline: `4b34ac192a4e80d1ae2fad13eb69a43763f1003d` (`main`).
- Local branch: `maintenance/upstream-zh-20261031`; no remote writes performed.
- Prior scanned master: `e7e3872d410f704479d94d318d68d163b6b58947`.
- Current official master: `97e7e7933d1ee93d4953136658767281af3a4ba0`.
- Two upstream changes: `6a7b0336` treats DXGI success statuses as success; `97e7e793` allows Pascal to run FSR4. They introduce no new catalog UI strings. Official business logic remains materialized verbatim, never copied into this maintenance repository.
- Latest official stable release checked through GitHub API: `v0.9.4`; resolved tag commit `7534ad00bf9e590eedb99e8dd9fd8c89dae3654f`.
- No open CN pull requests when work began. No repository AGENTS.md found.

## Changes

- Add 428 source-bound entries across master/stable (Chinese text plus explicitly retained technical/format templates), all `machine_translated`, not falsely human-reviewed. All 909 pre-existing entries are byte-for-byte structurally unchanged; reviewed translation memory remains 274 sources.
- Exclude only the `overlayRowKeys` array from C-string array localization. These seven values are used to parse/serialize FpsOverlayRows and as ScopedID, not display labels. The separate `overlayRowNames` and tips remain translated.
- Extend narrowly scoped scanning to FPS display helpers, ConfigCheckbox/SectionTitle, status helpers, display-only returns, Keybind names, reassigned FG option containers, structured MenuBox/Tab/OverlayPreset display fields, user notifications and audited dynamic status assignments. Do not translate `.Value` IDs, table keys, DLL names, settings code or tab-routing comparisons.
- Keep structured table data raw; translate at actual display uses, preserving original widget IDs with `###`. Preserve adjacent C++ literal expressions and runtime-format wrapping.
- Repair dynamic tooltip integration after the literal pass wraps the `%s` argument.
- Adapt the new independent FPS font through the existing validated CJK-font resolver and glyph builder; preserve English font paths and menu-font fallback.
- Follow the existing dual-channel catalog, exact source hash, English fallback and CJK integration model.

## Validation boundaries

The catalog count is a scanner inventory, **not proof of full runtime coverage**. Existing scope excludes logs, third-party code and installation scripts. Windows MSVC build, real game/GPU behavior, font fallback and layout remain separate checks. No Windows build, release or Actions dispatch has been performed in this local preparation.

The existing static C-string-array injection can cache translated pointers before font validation. No runtime redesign is included here; font-unavailable behavior for these existing paths needs specific runtime review. New display helper wrappers are evaluated at render time.

## Publication warning

`release.yml` automatically publishes/refreshes stable releases on `main` pushes touching `Localization/zh-CN.json`. Review through a non-main branch/PR rather than assuming a push is build-only. Remote writes and publication are reserved for the parent maintainer's authorization workflow.

## Final local evidence (2026-10-31 16:24 UTC)

- `python -m compileall -q tools tests`: passed.
- `python -m unittest discover -s tests -q`: **77 tests passed** (baseline 60). Includes actual portable C++ compilation/execution of injected adjacent-literal and brace-title snippets.
- `python tools/check_localization.py --channel all --strict`: master **1113 active / 0 missing / 0 stale**, stable **744 active / 0 missing / 0 stale**. Compared with baseline 878/708, these are expanded scanner inventories, not a whole-runtime coverage percentage.
- `python tools/update_translation_memory.py --check`: 274 reviewed sources synchronized, unchanged.
- Actual master/stable injection succeeded (1043 / 679 literal call-site rewrites). The final dynamic-tooltip and FPS-font adapter passes were also applied and checked in both materialized trees.
- `python tools/verify_materialized_ui.py --source _upstream_master --channel master` and equivalent stable command: passed. Fixed probes check newly found display paths, actual translated uses, raw table/ID preservation and generated dictionary completeness.
- Both generated dictionaries compiled/executed with GCC C++17 and C++20 (`-Wall -Wextra -Werror`). This is not the Windows DLL build.
- `git diff --check`: passed.
- Read-only lexical audit across first-party `OptiScaler/**/*.cpp,h` found no additional direct literal-bearing ImGui APIs beyond scanned calls and explicitly classified ID/layout calls. Third-party `imgui`/external trees are excluded. Dynamic arbitrary runtime data cannot be certified from this lexical audit.

No remote commit, Actions dispatch or release has been made. Windows MSVC + real GPU/game/CJK font/layout checks remain required before publication. Existing static C-string arrays cache translated pointers: font-missing fallback on those old injection paths remains an explicitly reported runtime risk, not proven fixed by these checks.
