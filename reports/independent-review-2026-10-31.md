# Independent review: OptiScaler-CN

Baseline worker snapshot preserved as local commit `44e7c34`.

## Confirmed P2 and repair

New global FPS `overlayRowNames` and `overlayRowTips` initialized `Loc::T` before menu font validation. Font-load failure later switches `activeLanguage` to English but cannot change cached pointers. Their direct Checkbox/ShowTooltip consumers therefore retained Chinese under the English font. The previous report treated this as a general risk; the two current call sites are concrete.

Repair: keep these two arrays raw and catalogued; translate only at their draw uses. Keep persistence `overlayRowKeys` excluded. Fail closed if either array remains present without its corresponding draw adapter. Other currently scanned menu C-string arrays are automatic render-function locals, not these global static caches.

Regression: actual scanner/injector output compiled as portable C++17, initialized Chinese, then simulated font failure and redrew. Before repair assertion `label=="Frame Time"` aborted (exit -6); after repair Chinese and English label/tooltip assertions pass. Changed-anchor failure test also passes.

## Source audit

- Structured MenuBox/Tab/OverlayPreset data preserved raw; display-only TL temporary lifetime extends through consuming ImGui calls.
- Requested tab strcmp, scoped row ID, settings codes and box IDs remain raw.
- Dynamic opt/flag tooltip consumption is translated after format-literal injection.
- Audited display-return anchors remain display helpers; formatFg uses runtime F instead of invalid compile-time std::format(T(...)).
- FPS adapter resolves a catalog-glyph-validated CJK font; English branch preserved; missing separate font returns to validated menu font. Static-cache repair avoids the identified early-initialization violation.
- Tests and probes are not a complete UI/runtime claim. Windows/MSVC build, real GPU/game, font fallback/layout still require external validation; arbitrary runtime external strings are not certified by catalog coverage.

## Fresh validation

79 Python tests passed (includes generated C++ compile/run); strict master1113/stable744 with zero missing/stale; reviewed translation memory274 unchanged; diff whitespace check passed. Fresh local upstream clones at pinned SHAs were separately materialized; results recorded after completion below.

Fresh master/stable injection: 1029/679 literal rewrites; both fixed UI probes passed, including raw global FPS arrays and translated draw uses. Final fail-closed helper reapplied idempotently on both generated trees.
