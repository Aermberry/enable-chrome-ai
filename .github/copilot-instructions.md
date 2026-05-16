# Copilot Instructions for Enable Chrome AI

## Quick Start

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run the script
uv run main.py
```

**Requirements:** Python 3.13+, `psutil` (auto-installed). No test suite, linter, or CI configured.

## Project Purpose

A single-file Python script (~200 lines) that activates Chrome's built-in AI features (Gemini, AI History search, DevTools AI) by patching Chrome's `Local State` JSON configuration. Supports Windows, macOS, and Linux across Chrome Stable, Canary, Dev, and Beta channels.

## High-Level Architecture

The script performs a 3-step workflow:

1. **Discovery Phase** → `get_version_and_user_data_path()`
   - Detects the current OS (Windows, macOS, Linux) and maps each Chrome channel to its user data directory
   - Returns only paths that exist on disk (channels user has installed)
   - Raises an exception if no Chrome installations are found

2. **Shutdown Phase** → `shutdown_chrome()`
   - Uses `psutil` to find and kill top-level Chrome processes (avoids file locks during patching)
   - On macOS: matches by process name prefix (`Google Chrome*`)
   - On Windows/Linux: matches by executable name (`chrome`)
   - Returns a set of executable paths so Chrome can be restarted later

3. **Patching Phase** → `patch_local_state(user_data_path, last_version)`
   - Reads Chrome's `Local State` JSON file
   - **Recursively** sets all `is_glic_eligible` keys to `true`
   - Sets `variations_country` to `"us"`
   - Sets `variations_permanent_consistency_country` to `[<last_version>, "us"]`
   - Only writes back to disk if modifications were made
   - `get_last_version()` reads the `Last Version` file (version string from Chrome profile)

The `main()` function orchestrates all three phases and optionally waits for user input.

## Key Implementation Details

- **Platform Paths**: Hardcoded paths per OS/channel in `get_version_and_user_data_path()`. Update these if Chrome changes directory locations.
- **Recursive Patching**: `set_all_is_glic_eligible()` recursively traverses dicts and lists; returns `bool` to indicate whether the object was modified.
- **Process Matching**: `shutdown_chrome()` filters out child processes (e.g., helper processes) by comparing parent process name; only top-level Chrome processes are killed.
- **Error Handling**: Script uses try-except blocks to gracefully skip processes/paths that fail (permission denied, process terminated, etc.).

## Code Organization

- `main.py`: Single file containing all functions
  - Imports: `os`, `sys`, `json`, `subprocess`, `psutil`
  - No internal modules or packages; flat structure by design

## Known Issues

- **Dead Code**: Lines 98-101 in `get_last_version()` are unreachable (duplicate code after an early `return` on line 96). This does not affect functionality but could be cleaned up.
- **User Data Requirement**: Script expects `Local State` file to exist. If missing, the run may fail. Chrome creates this file on first launch.
- **macOS Process Matching**: Based on process name prefix only; may terminate more processes than intended if multiple Chrome variants are running.
- **Linux Executable Name**: Expects executable to be named `chrome`. Custom builds with different names may not be auto-restarted.

## Common Modifications

- **Adding a New Chrome Channel**: Add the channel name and path in the `os_and_user_data_paths` dict in `get_version_and_user_data_path()`.
- **Changing Patch Values**: Modify the hardcoded strings in `patch_local_state()` or pass them as parameters if making the script more flexible.
- **Adjusting Platform Detection**: Modify `sys.platform` checks in `shutdown_chrome()` or platform path logic in `get_version_and_user_data_path()`.
