# Upstream integration contract

Last full source review for this localization layer: **2026-09-12**.

## Official project

- Repository: https://github.com/optiscaler/OptiScaler
- Tracked development branch: `master`
- Latest stable release observed during this review: `v0.9.4` (2026-07-18)
- License: GPL-3.0
- Solution: `OptiScaler.sln`, Visual Studio 17 / VS2022 generation
- Main C++ project: `OptiScaler/OptiScaler.vcxproj`

The current `master` is already the v10 development line. Its release notes describe a major package-layout change in which bundled files move under an `OptiScaler` subfolder. This is why this project never assumes the older v0.9.4 package layout when scanning source; packaging starts from the directory produced by the checked-out upstream project's own Release PostBuild step.

## Current UI implementation

The primary overlay/menu implementation is `OptiScaler/menu/menu_common.cpp`, with DX11/DX12/Vulkan overlay backends and additional menu helpers under `OptiScaler/menu/`.

Current user-visible strings are mostly direct ImGui calls (`Text`, `Checkbox`, `Button`, `BeginCombo`, `SeparatorText`, tooltips, etc.) plus a smaller number of `MenuOption`/container strings. `Localization/scanner-rules.json` therefore uses API-aware scanning instead of a global string-literal replacement.

The scanner intentionally covers `OptiScaler/**/*.cpp` and `OptiScaler/**/*.h` so future UI file splits remain discoverable, but only whitelisted UI APIs/known containers are catalogued. `external/`, generated localization code, logs, shaders and ordinary internal strings are not blindly translated.

## Current font integration point

On the reviewed `master`, `MenuCommon::Init` loads the custom `[Menu] TTFFontPath` with ImGui's `GetGlyphRangesDefault()`. That range is insufficient for Simplified Chinese even if a Chinese TTF/TTC is supplied.

The CN integration replaces only this font-loading decision in the materialized build tree. It builds glyph ranges from the actual translated UTF-8 strings and validates candidate fonts with the FreeType dependency already linked by upstream. If validation fails, localization is disabled for the session and English remains visible.

## Official build model reused here

The upstream GitHub Actions build uses MSBuild with a Release configuration. The current project PostBuild assembles end-user files under `x64/Release/a`. This repository preserves that model:

```text
checkout/materialize upstream + submodules
→ microsoft/setup-msbuild
→ msbuild OptiScaler.sln /m /p:Configuration=Release /p:Platform=x64
→ package x64/Release/a
```

No local developer-only dependency is assumed by the CN workflow. Upstream Git submodules are initialized recursively. Current `.gitmodules` includes SimpleIni, unordered_dense, XeSS, Vulkan-Headers, spdlog, FidelityFX SDK variants, magic_enum and NVAPI, among upstream-managed dependencies.

## Fail-closed integration anchors

`tools/localize_source.py` verifies these current structural contracts before modifying the temporary upstream tree:

1. `OptiScaler/menu/menu_common.cpp` exists.
2. `MenuCommon::Init(HWND, bool)` still exists.
3. the HQ-font initialization gate is recognizable.
4. the `TTFFontPath` / bundled Hack-font branch is recognizable and still contains `AddFontFromFileTTF`, `GetGlyphRangesDefault` and the bundled fallback.

If any required anchor no longer matches, the tool exits non-zero. Upstream Sync does not commit its new tracking state, and Release does not publish anything. The maintainer then reviews the official change and updates only the integration adapter.

## Why an overlay repository instead of a permanent source fork

Keeping thousands of upstream source files in the CN branch would turn ordinary upstream edits into Git merge conflicts around translated UI lines. Here the official source is always reconstructed from an exact upstream ref, while the maintained delta is limited to localization resources, scanner/injector code and a small header-only runtime. This is the main mechanism that keeps future maintenance automatic.

## Automation state semantics

`last_scanned_commit` means the development-branch UI scan and localization injection contract were accepted and persisted. The subsequent Windows `Build CN` is a separate workflow; a transient master build failure therefore requires a manual rerun or a later upstream change.

`last_released_upstream_tag` has stronger semantics: it is written only after the exact stable tag has scanned, localized, compiled, packaged and successfully published as a GitHub Release. A failed stable build/publish remains eligible for the next scheduled retry.
