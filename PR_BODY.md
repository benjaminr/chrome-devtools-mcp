feat: CLI binary + auto-start Chrome on connect + packaging fixes

Summary
- Adds a global CLI entrypoint `chrome-devtools-mcp` so the MCP server can be installed and run via `uv tool install .` or `pipx install .` and referenced by Codex CLI (or other MCP clients) as a single command.
- Improves UX by auto-starting Chrome (with `--remote-debugging-port`) when `connect_to_browser()` is called and Chrome isn’t already running.
- Fixes packaging so all subpackages (e.g., `src.tools`) are included when installed as a tool.

Changes
- build(pyproject): add `[project.scripts]` entry `chrome-devtools-mcp = "src.main:main"`.
- deps: add `mcp[cli]` to ensure Typer-based CLI is available for the MCP tooling.
- build(setuptools): enable package discovery with `[tool.setuptools.packages.find] include = ["src*"]`.
- feat(chrome_management): `connect_to_browser(port=..., auto_start=True, headless=False, chrome_path=None, url=None)`; auto-starts Chrome if missing; ensures CDP client uses the requested port before connecting.
- feat(start_chrome): set client port before auto-connecting for consistency.
- docs(README): document auto-start usage and Codex config snippet.

Behavior notes
- Default `connect_to_browser()` now attempts to start Chrome if it isn’t already running on the requested port. To retain prior behavior, call `connect_to_browser(auto_start=False)`.
- You can pass `headless=True`, `chrome_path=...`, and `url=...` to control auto-start behavior.

Install and test
- uv: `uv tool install --force .` (or bump version and use `uv tool install .`)
- pipx: `pipx install .`
- Verify:
  - `which chrome-devtools-mcp`
  - `chrome-devtools-mcp` logs “Registering MCP tools…” and waits for client.

Codex CLI config example (TOML)
```toml
[mcp_servers.chrome-devtools]
command = "chrome-devtools-mcp"
args = []

[mcp_servers.chrome-devtools.env]
CHROME_DEBUG_PORT = "9222"
```

Checklist
- [x] CLI works when installed as a uv/pipx tool
- [x] Packaging includes subpackages (`src.tools`, etc.)
- [x] README updated
- [ ] Validate on Windows/Linux (tested on macOS)
- [ ] Consider adding a `--version/--help` fast-path for smoke tests

