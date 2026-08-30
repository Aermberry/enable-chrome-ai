# Enable Chrome AI ✨

由 [lcandy2](https://twitter.com/vanillaCitron) 研究并制作脚本。

[![Twitter](https://img.shields.io/twitter/follow/vanillaCitron)](https://twitter.com/vanillaCitron)

[English](README.md) | 中文

在 Google Chrome 中启用 Gemini、AI 历史搜索、DevTools AI 等创新功能——无需清除数据或重新安装。

<img width="512" alt="Google Chrome Gemini in Chrome" src="https://github.com/user-attachments/assets/a88c56a7-f20b-432a-926c-0184194225b4" />

轻量 Python 脚本，通过修改本地 Chrome 的 GLIC/Gemini 资格缓存（`profile.info_cache.*.is_glic_eligible`）、地区变体配置与启动器配置来启用浏览器内置 AI 功能，无需额外开关。

## ✅ 环境要求
- Python `3.13+`（见 `.python-version` / `pyproject.toml`）
- 已安装 Google Chrome（Stable/Canary/Dev/Beta）

## ⚡️ 快速开始（uv）
1. 安装 uv（一次性）：
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - macOS & Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - 更多安装方式请参考 [uv 安装文档](https://docs.astral.sh/uv/getting-started/installation/)。
2. 安装依赖（自动创建虚拟环境）：`uv sync`。
3. 运行脚本：`uv run main.py`。
4. 补丁过程中 Chrome 会被关闭；重启后根据提示按 Enter 结束。

## ⚡️ 快速开始（pip）
1. 创建并激活虚拟环境。
2. 安装依赖：`python -m pip install psutil`。
3. 运行：`python main.py`。

## 🔧 做了什么
- 自动定位 Windows / macOS / Linux 上的 Chrome Stable / Canary / Dev / Beta 用户数据目录。
- 关闭所有 Chrome 进程并等待其完全退出以避免文件锁，再在补丁后恢复此前运行的 Chrome 可执行文件。
- 在 `Local State` 中递归查找并将所有 `is_glic_eligible` 设为 `true`。
- 为每个本地配置文件将 `profile.info_cache.<profile>.is_glic_eligible` 设为 `true`。Chrome 152 将资格值存放在这里，并非顶层 `glic` 属性。
- 在 `Local State` 中将 `variations_country` 设为 `"us"`，并将 `variations_permanent_consistency_country` 设为 `["<版本号>", "us"]`。
- 等待所有 Chrome 进程完全退出后再替换 `Local State`，避免 Chrome 在关闭过程中覆盖补丁。
- 重启补丁前已运行的 Chrome 版本。

## ⚠️ 已知限制 / 注意事项
- 脚本假设 `User Data/Local State` 已存在；若缺失可能直接失败（可先启动一次 Chrome 生成配置）。
- 只有在能从进程信息中取到可执行文件路径时，脚本才会自动重启 Chrome。
- macOS 上按进程名（`Google Chrome*`）识别，可能会终止不止"顶层"应用进程。
- Linux 上按可执行文件名 `chrome` 识别；若你的发行版/安装方式使用其他名字，可能不会关闭 Chrome（从而仍可能有文件锁）。

## 🛟 注意
- 脚本会修改现有 Chrome 配置，如需保险请先备份 `User Data`。
- 使用拥有该 Chrome 配置的同一系统用户运行，确保有写入权限。
- 本工具只能修改本地 Chrome 配置。Gemini in Chrome 还会由 Google 根据登录账号、年龄/家长监管或组织策略、设备语言及网络地区进行服务端校验；脚本无法绕过服务端拒绝。
- 与 Google 无关，风险自担。

## 📜 许可
转载或基于本研究二次创作需要注明来源。

## 🙏 致谢
- [show-copilot](https://github.com/hzkaai/show-copilot)
