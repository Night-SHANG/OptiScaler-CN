# Verification Report — 2026-09-12

This package implements the dual-channel localization model (current upstream `master` + current stable release) with one shared `zh-CN.json` translation store.

## Local verification

- Python syntax: PASS (`python -m compileall -q tools tests`)
- Unit tests: PASS — 60/60
- Workflow YAML parse: PASS — 4/4
- Translation-memory consistency: PASS — 274 reviewed sources
- Hard-coded translation API secret scan: PASS
- Master compatibility mirrors: PASS
- Generated master C++ localization header: PASS — 807 entries

## Current master localization

- Active UI strings: 807
- Reviewed Chinese: 232
- Machine-translated/assistant-curated Chinese: 575
- Missing: 0
- Stale: 0
- Effective coverage: 100.00%

The shared language store contains 849 entries total: 274 reviewed and 575 machine-translated. The extra entries are retained translation history/older-source strings and can be reused by the stable channel when exact English sources match.

## Stable channel bootstrap

`Localization/stable/` is intentionally an empty bootstrap catalog in this local handoff because the current execution environment could not materialize the complete official v0.9.4 source tree. This is not treated as a real 0/0 coverage measurement.

After the package is pushed, `Upstream Sync` detects the empty stable catalog as `bootstrap_needed=true`, fetches the exact current stable tag on GitHub Actions, scans it, and persists the real stable catalog. `Release CN` also independently scans the exact stable source before every stable build, so an empty bootstrap catalog is never used as the authoritative release scan.

If the first persisted stable scan discovers stable-only text that is absent from the shared Chinese store, those entries remain safely in English and are written to `Localization/stable/pending.json` for the next translation pass.

## Windows build

The C++/MSVC build is authoritative on GitHub Actions (`windows-2022`). The repository's existing Build CN path has already reached successful Windows compilation in the user's GitHub repository after the encoding and PCH integration fixes; this local Linux environment does not claim a new Windows build for this translation-only handoff.
