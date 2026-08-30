# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enable Chrome AI — a single-file Python script that activates Chrome's built-in AI features (Gemini, AI History search, DevTools AI) by patching the `Local State` JSON in Chrome's user data directory. Supports Windows, macOS, and Linux across Chrome Stable, Canary, Dev, and Beta channels.

## Commands

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run the script
uv run main.py
```

No test suite, linter, or CI is configured. Python 3.13+ required; sole dependency is `psutil`.

## Architecture

Everything lives in `main.py` (~200 lines). The flow is:

1. **`get_version_and_user_data_path()`** — detects OS and returns a dict of Chrome channel → user-data path (only paths that exist on disk).
2. **`shutdown_chrome()`** — uses `psutil` to find and kill top-level Chrome processes, returns a set of executable paths for restart.
3. **`get_last_version(user_data_path)`** — reads the `Last Version` file from a Chrome profile.
4. **`set_all_is_glic_eligible(obj)`** — recursive helper that sets every `is_glic_eligible` key to `True` in a JSON object.
5. **`patch_local_state(user_data_path, last_version)`** — loads `Local State` JSON, patches `is_glic_eligible` → `true`, `variations_country` → `"us"`, `variations_permanent_consistency_country` → `["<version>", "us"]`, writes it back.
6. **`main()`** — orchestrates discovery → shutdown → patch → restart.

## Known Issues

- `get_last_version()` has dead code after a premature `return` (unreachable lines ~98-101).
