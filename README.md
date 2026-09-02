# Codex Limit for KDE Plasma

An unofficial KDE Plasma 6 widget that shows Codex 5-hour, weekly, and
gpt-reserve weekly usage limits.

Codex Limit is an independent community project. It is not affiliated with,
endorsed by, or sponsored by OpenAI.

## Features

- Shows the remaining percentage and reset time for 5-hour, weekly, and
  gpt-reserve weekly limits when available.
- Supports percentage and progress-bar modes on the panel.
- Lets you change the panel icon, icon size, label visibility, and refresh
  interval.
- Uses the authentication already managed by the local Codex installation;
  no separate API key is required.

## Compatibility

Codex Limit requires:

- Linux with KDE Plasma 6;
- Python 3 available as `python3`;
- a local Codex CLI with `codex app-server` support for multi-bucket limits;
- the Plasma 5 Support module used by Plasma's executable data engine; and
- an authenticated local Codex installation.

It does not support Plasma 5, Windows, macOS, browser-only Codex usage, or
machines without a local Codex installation. If the installed Codex version
does not provide the app-server rate-limit method, the widget falls back to
local session logs and shows only the standard 5-hour and weekly limits.

The fallback Codex JSONL event format is not a documented public API. A future
Codex update may require a corresponding widget update.

## Install a release

Download `codex-limit.plasmoid` from the GitHub release and run:

```bash
kpackagetool6 --type Plasma/Applet --install ./codex-limit.plasmoid
```

To replace an existing installation:

```bash
kpackagetool6 --type Plasma/Applet --upgrade ./codex-limit.plasmoid
kquitapp6 plasmashell && kstart plasmashell
```

Open Plasma's **Add Widgets…** panel and add **Codex Limit**. Run at least one
local Codex task first so that a recent rate-limit snapshot exists.

## Build from source

Building requires Bash, `zip`, and `unzip`. The portable checks use Python 3;
`qmllint` is also used automatically when it is installed with Qt 6 and the
KDE Plasma QML modules.

```bash
./scripts/check.sh
./scripts/package.sh
kpackagetool6 --type Plasma/Applet --install ./codex-limit.plasmoid
```

The package script uses an explicit file set and excludes editor state,
Python caches, tests, and locally retained artwork.

## Privacy

The helper normally asks the local Codex app-server for account rate limits.
Codex may make an authenticated service request using its existing login and
may update its own runtime state. The widget never reads or stores Codex
credentials and emits only the small allowlist of fields used by the UI.

When app-server data is unavailable, the helper scans local Codex JSONL
session logs. Those files can contain conversation data, but conversation
content is not displayed, stored, or included in helper output. See
[PRIVACY.md](PRIVACY.md) for the complete data-flow description.

## Development

Test the reader directly:

```bash
python3 contents/code/read_limits.py
```

Run the widget in a standalone Plasma window:

```bash
plasmawindowed dev.codex.limitwatch
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and contribution guidance.

## License and trademarks

The source code and original `codex-limit.svg` artwork are licensed under the
[MIT License](LICENSE). See [NOTICE](NOTICE) for trademark and project-status
notices.

OpenAI and Codex are trademarks of their respective owner. Their names are
used only to identify compatibility; no ownership or endorsement is claimed.
