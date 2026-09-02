# Contributing

Bug reports and pull requests are welcome. Never include real Codex session
logs or other private user data in an issue, fixture, screenshot, or commit.

## Local checks

Run all portable checks:

```bash
./scripts/check.sh
```

On a Plasma 6 development machine, also validate QML imports:

```bash
qmllint -I /usr/lib/qt6/qml contents/ui/*.qml contents/config/*.qml
```

Then test the widget interactively:

```bash
plasmawindowed dev.codex.limitwatch
```

## Pull requests

- Keep changes focused and explain user-visible behavior.
- Add or update parser tests for data-reader changes.
- Use synthetic fixtures only.
- Update `CHANGELOG.md` for user-visible changes.
- Preserve the no-widget-telemetry design and document any data-flow changes
  before release.

All contributions are accepted under the repository's MIT License.
