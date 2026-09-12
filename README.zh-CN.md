# OptiScaler-CN

OptiScaler-CN 是 [OptiScaler](https://github.com/optiscaler/OptiScaler) 的社区简体中文本地化与自动构建层。它不是 OptiScaler 官方项目，也不冒充官方版本。

本仓库不长期复制一份上游业务源码，而是在构建时拉取指定的官方 OptiScaler commit/tag，对可见 UI 做确定性的低侵入本地化注入，然后使用官方的 Visual Studio/MSBuild 构建方式生成中文版。这样普通上游更新不会反复产生大面积 fork 合并冲突。

## 下载与安装

从本仓库 GitHub Releases 下载 `OptiScaler-CN-*.zip`，按对应 OptiScaler 官方版本的安装方式解压到游戏目录。压缩包中额外包含 `OptiScalerCN.ini`。

```ini
[Localization]
Language=zh-CN
FontPath=
```

- `Language=zh-CN`：简体中文。
- `Language=en-US`：强制英文。
- 修改语言后重新启动游戏。

如果某一条中文不存在、已因上游英文变化而失效，程序只对该条自动显示官方英文，不会出现空白菜单。

## 中文字体

OptiScaler 当前支持 `[Menu] TTFFontPath`，但上游默认字体加载只使用默认拉丁字形范围。OptiScaler-CN 在中文模式下会：

1. 优先读取 `OptiScalerCN.ini` 的 `FontPath`；
2. 其次复用官方 `OptiScaler.ini` 的 `TTFFontPath`；
3. 再尝试 Windows 常见 CJK 字体；
4. 用 FreeType 检查该字体是否真的覆盖当前中文语言包所需字符；
5. 动态构建只包含默认字形和当前中文字符的 ImGui glyph ranges。

如果找不到能完整覆盖当前语言包的字体，中文会整体验证失败并自动退回英文，避免方框/缺字。仓库不捆绑大型中文字体。

如需手动指定字体，可填写绝对路径或相对 OptiScaler DLL 所在目录的路径，例如：

```ini
FontPath=C:\Windows\Fonts\msyh.ttc
```

## 自动更新机制

`Upstream Sync` 每天执行一次，也可手动运行。它会同时维护两套长期 UI 清单：`Localization/master/` 对应最新开发分支，`Localization/stable/` 对应当前最新稳定版；两者共用一份 `Localization/zh-CN.json`。

同步流程：

`检查官方 master/稳定 Release → 分别拉取两套精确源码 → 分别扫描 UI → 合并复用已有中文 → 生成各自待翻译项 → 可选增量机器翻译 → 双通道结构检查 → 验证两套源码注入锚点 → 安全提交语言资源与跟踪状态`

同步成功后，master 有变化时会触发独立的 `Build CN` Windows 干净构建；发现新的官方稳定 Release 时会触发 `Release CN`。如果自动同步过程中共享中文翻译发生变化，也会刷新当前稳定版 Release。人工 `git push` 修改 `Localization/zh-CN.json` 时同样会自动刷新稳定版 Release。只有新的稳定 tag 真正发布成功后，才会记录 `last_released_upstream_tag`。

扫描/翻译结构错误、源码注入锚点变化、Git push 冲突/分支保护、MSBuild 失败或打包失败都不会生成损坏的 Release。普通 master 构建失败时保留诊断日志，可手动重新运行；稳定 Release 构建失败不会写入已发布标记，因此下一次同步仍会继续尝试。

## 上传到 GitHub 后

把本仓库全部文件上传到你自己的 GitHub 仓库，建议默认分支使用 `main`。随后：

1. 打开 `Settings → Actions → General`，确认允许 GitHub Actions 运行；仓库/组织策略不能禁止工作流所需的 `contents: write` 与 `actions: write` 权限。
2. 在 `Actions` 页面先手动运行一次 `Localization Check`，再运行一次 `Build CN`。
3. 确认两者正常后，手动运行一次 `Upstream Sync`。以后它会按计划每天检查上游。
4. 如果希望自动翻译新增文字，在 `Settings → Secrets and variables → Actions` 增加 `TRANSLATION_API_URL`、`TRANSLATION_API_KEY`、`TRANSLATION_MODEL`。不配置也可以正常同步和构建，缺失中文会显示英文；API 临时失败时也会保留待翻译项并继续使用英文 fallback。

首次启用或升级到双通道结构时，如果 `master/` 或 `stable/` 清单为空，`Upstream Sync` 会自动执行一次 bootstrap，即使官方当天没有新提交也会补齐两套 UI 清单。之后只处理新的上游变化。

仓库中不需要保存任何 API Key。

## 为什么偶尔会看到英文

这通常表示官方刚新增或修改了 UI，而对应中文仍处于待翻译/待审核状态。英文是设计好的安全 fallback，不代表菜单损坏。

无翻译 API 时，新文本会进入 `Localization/master/pending.json` 或 `Localization/stable/pending.json`，构建仍可继续；配置翻译 API 后，只会处理两套清单中的新增、变化或缺失文本，不会覆盖 `reviewed` 人工翻译。

## 手动同步/构建

需要 Python 3.11+、Git、Visual Studio 2022 C++ 工具链和 MSBuild。Windows 下：

```powershell
python tools/prepare_tree.py --worktree _upstream --ref master
python tools/scan_ui.py --source _upstream --channel master --update
python tools/check_localization.py --channel master
python tools/localize_source.py --source _upstream --channel master
msbuild _upstream\OptiScaler.sln /m /p:Configuration=Release /p:Platform=x64 /verbosity:minimal
```

最终官方式打包目录由 OptiScaler 工程的 PostBuild 生成在 `_upstream\x64\Release\a`；本仓库的 `tools/package.ps1` 会在此基础上加入 `OptiScalerCN.ini` 与社区说明后压缩。

## 翻译修正

术语表位于 `Localization/glossary.json`。稳定人工翻译通过 `reviewed` 状态保护。具体资源格式、候选翻译审核方法、占位符和 ImGui `##` ID 规则见 [TRANSLATION.md](TRANSLATION.md)。

提交翻译修正时不要修改英文 source，也不要改动 `%s`、`%.2f`、`{0}` 等格式占位符和 `##xxx` 隐藏 ID。

## 与官方项目的关系

- 官方仓库：https://github.com/optiscaler/OptiScaler
- 本项目：非官方社区派生/本地化构建系统。
- OptiScaler 与本仓库衍生代码按 GPL-3.0 分发；详见 `LICENSE`。
- 上游版本、目录、构建与本地化集成点记录在 [UPSTREAM.md](UPSTREAM.md)。

## 维护文件

- `Localization/master/`：最新开发版的英文目录、UI 索引与待翻译列表。
- `Localization/stable/`：当前最新稳定版的英文目录、UI 索引与待翻译列表。
- `Localization/zh-CN.json`：两套版本共用的简中翻译库；同一英文源文只维护一次。
- 根目录旧的 `catalog.json / en-US.json / pending.json` 仅作为 master 的兼容镜像保留，正式维护以 `master/` 与 `stable/` 为准。
- `Localization/` 其余文件：翻译记忆、术语表、扫描规则和中文配置。
- `overlay/`：低侵入 C++ 本地化运行时。
- `tools/`：扫描、增量更新、校验、翻译、注入、打包与 Release Notes 工具。
- `.github/workflows/`：本地化检查、构建、上游同步、Release。
