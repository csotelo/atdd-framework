# ATF — Scope

## What ATF Does

- Executes Gherkin feature files (`acceptance.feature`) inside a Playwright Docker container
- Reports pass/fail per scenario with JSON and HTML output
- Writes structured `feedback.md` on failure for AI code-generation tools to consume
- Updates `atf-state.json` and `STATE.md` after every run
- Pulls the Docker image automatically when not present on the host
- Runs host-side fixture setup (`setup.sh`) before Docker starts
- Passes fixture data (`seed.json`, `seed.sql` path) into Docker via environment variables
- Provides a `behave`-compatible step library for browser UI and HTTP API testing
- Wires Screenplay actors (`WebUser`, `ApiClient`) in `environment.py`

## What ATF Does NOT Do

- **Generate feature files** — Claude (or another LLM) writes `acceptance.feature` files
- **Execute implementation prompts** — OpenCode (or another coding agent) reads `prompt.md`
  and modifies project source files
- **Manage source code** — ATF never edits the project under test
- **Install browsers on the host** — all browser execution happens inside Docker
- **Manage Docker Compose or app startup** — the app under test must already be running;
  use `setup.sh` fixtures for pre-test setup if needed
- **Generate reports with Allure** — ATF uses `behave-html-formatter` for zero-dependency HTML

## What ATF Supports

- Any web UI accessible in a Chromium browser (React, Vue, Angular, Django, Rails, etc.)
- Any REST API reachable over HTTP/HTTPS
- Stack-agnostic: the project under test can be written in any language or framework
- Any host OS that can run Docker (Linux, macOS, Windows with WSL2)

## Out of Scope

- Mobile native apps (iOS, Android)
- Desktop (Electron, Qt, native GUI)
- Non-HTTP protocols (WebSockets at the protocol level, gRPC, MQTT)
- Visual regression / pixel-diff testing
- Performance / load testing
- Security scanning

## Integration Contract

| Input | Path | Produced by |
|-------|------|-------------|
| Feature file | `prompts/sprint_NN/acceptance.feature` | Claude / LLM |
| Implementation prompt | `prompts/sprint_NN/prompt.md` | Claude / LLM |
| Host fixture setup | `prompts/sprint_NN/fixtures/setup.sh` | Claude / LLM |
| Seed data (JSON) | `prompts/sprint_NN/fixtures/seed.json` | Claude / LLM |
| Seed SQL | `prompts/sprint_NN/fixtures/seed.sql` | Claude / LLM |

| Output | Path | Produced by |
|--------|------|-------------|
| JSON results | `reports/sprint_NN/results.json` | ATF (inside Docker) |
| HTML report | `reports/sprint_NN/index.html` | ATF (inside Docker) |
| Failure screenshot | `reports/sprint_NN/failed_<name>.png` | ATF (inside Docker) |
| Feedback | `prompts/sprint_NN/feedback.md` | ATF (host-side, `feedback.py`) |
| State | `atf-state.json` | ATF (host-side, `state.py`) |
| State summary | `STATE.md` | ATF (host-side, `state.py`) |
