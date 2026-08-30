# Enable Chrome AI ✨

Researched and scripted by [lcandy2](https://twitter.com/vanillaCitron).

[![Twitter](https://img.shields.io/twitter/follow/vanillaCitron)](https://twitter.com/vanillaCitron)


English | [中文](README.zh.md)

Enable Gemini in Chrome, AI Powered History search, and DevTools AI Innovations in Google Chrome—without cleaning data or reinstalling.

<img width="512" alt="Google Chrome Gemini in Chrome" src="https://github.com/user-attachments/assets/a88c56a7-f20b-432a-926c-0184194225b4" />

Tiny Python helper that updates Chrome's local GLIC/Gemini eligibility cache (`profile.info_cache.*.is_glic_eligible`), region variation preferences, and launcher preference—no browser flags required.

## ✅ Requirements
- Python `3.13+` (see `.python-version` / `pyproject.toml`)
- Google Chrome installed (Stable/Canary/Dev/Beta)

## ⚡️ Quick Start (uv)
1. Install uv (once):
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - macOS & Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - See [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for more options.
2. Install deps (creates venv automatically): `uv sync`.
3. Run the script: `uv run main.py`.
4. Chrome will close while patching; after it restarts, press Enter to finish.

## ⚡️ Quick Start (pip)
1. Create and activate a venv.
2. Install deps: `python -m pip install psutil`.
3. Run: `python main.py`.

## 🔧 What Happens
- Finds Chrome user data for Stable/Canary/Dev/Beta on Windows, macOS, and Linux.
- Stops all Chrome processes, waits for them to exit, then brings the previously running Chrome executable back.
- Sets all `is_glic_eligible` to `true` in `Local State` (recursive search).
- Sets `profile.info_cache.<profile>.is_glic_eligible` to `true` for every local profile. Chrome 152 stores the eligibility value here; it is not a top-level `glic` property.
- Sets `variations_country` to `"us"` and `variations_permanent_consistency_country` to `["<version>", "us"]` in `Local State`.
- Waits for all Chrome processes to exit before replacing `Local State`, preventing Chrome from overwriting the patch during shutdown.
- Restarts any Chrome builds that were running before the patch.

## ⚠️ Caveats / Known Limitations
- The script expects `User Data/Local State` to exist; if it's missing, the run can fail (launch Chrome once to generate it).
- Chrome restart only happens if the executable path can be detected from running processes.
- On macOS, process detection is name-based (`Google Chrome*`) and may terminate more than just the "top-level" app process.
- On Linux, process detection expects an executable name of `chrome`; if your build uses a different name, Chrome may not be closed (and files may remain locked).

## 🛟 Notes
- The script writes to your existing Chrome profile; back up `User Data` if you want a safety net.
- Run as the same OS user who owns the Chrome profile to ensure write access.
- This only changes local Chrome preferences. Gemini in Chrome is also gated by Google using the signed-in account, age/supervision or organization policy, device language, and network region; the script cannot override a server-side denial.
- Not affiliated with Google—use at your own risk.

## 📜 License
Please credit this project when reposting or creating derivative works.

## 🙏 Acknowledgments
- [show-copilot](https://github.com/hzkaai/show-copilot)
