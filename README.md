# OptiScaler-CN

Community-maintained Simplified Chinese localization and automated build layer for [OptiScaler](https://github.com/optiscaler/OptiScaler). This project is not affiliated with or endorsed by the official OptiScaler project.

The repository intentionally uses a low-coupling overlay model: CI materializes an exact official upstream ref, scans user-visible UI, applies a deterministic localization layer, builds with the official Visual Studio/MSBuild project, and packages the result. It does not keep a permanently modified copy of all upstream business source files.

Key properties:

- English is always the runtime fallback.
- Translation resources are separate from upstream UI code.
- Reviewed translations are never overwritten by automated translation.
- Master and current stable keep separate persisted UI inventories while sharing one zh-CN translation store.
- New/changed/deleted UI strings are reported automatically for both channels.
- UTF-8 Chinese is emitted as byte-escaped generated C++ and loaded with validated CJK fonts/glyph ranges.
- Unsafe integration changes fail closed and block publication.
- Daily/manual upstream sync and clean Windows build workflows are included.
- Stable upstream releases can produce community CN GitHub Releases automatically.

For installation, language switching, fonts and maintenance instructions, see [README.zh-CN.md](README.zh-CN.md). Translation rules are in [TRANSLATION.md](TRANSLATION.md), and the researched upstream integration contract is in [UPSTREAM.md](UPSTREAM.md).

## Quick validation

```bash
python -m unittest discover -s tests -v
python tools/check_localization.py
```

## License

GPL-3.0. See [LICENSE](LICENSE). OptiScaler remains the work of its upstream authors; this repository only maintains the community localization/integration layer and generated derivative builds.
