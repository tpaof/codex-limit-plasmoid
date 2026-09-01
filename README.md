# Codex Limit for KDE Plasma

An unofficial KDE Plasma 6 widget that shows the latest 5-hour and weekly
Codex usage limits found in local Codex session logs.

Codex Limit is an independent community project. It is not affiliated with,
endorsed by, or sponsored by OpenAI.

## Features

- Shows the remaining percentage and reset time for short- and long-term
  limits.
- Supports percentage and progress-bar modes on the panel.
- Lets you change the panel icon, icon size, label visibility, and refresh
  interval.
- Works locally without an API key or network requests.

## Compatibility

Codex Limit requires:

- Linux with KDE Plasma 6;
- Python 3 available as `python3`;
- the Plasma 5 Support module used by Plasma's executable data engine; and
- local Codex session logs under `$CODEX_HOME/sessions` or
  `~/.codex/sessions`.

It does not support Plasma 5, Windows, macOS, browser-only Codex usage, or
machines where Codex has not written a local rate-limit event.

The local Codex JSONL event format is not a documented public API. A future
Codex update may require a corresponding update to this widget.

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

The helper scans local Codex JSONL session logs to identify rate-limit events.
This means it opens and decodes candidate log lines in memory, which can also
contain conversation data. It emits only the small allowlist of rate-limit
fields used by the UI and does not display, store, or transmit conversation
content.

The widget contains no network client and requires no OpenAI API key. See
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
