# Privacy

Codex Limit is a local-only KDE Plasma widget. It has no networking code and
does not require an OpenAI API key.

## Data it accesses

The helper searches up to 40 recently modified `*.jsonl` files below:

- `$CODEX_HOME/sessions`, when `CODEX_HOME` is visible to Plasma; or
- `~/.codex/sessions` otherwise.

It reads candidate files from newest to oldest and decodes JSON lines until it
finds the latest supported `token_count` rate-limit event. Session lines can
contain prompts, responses, paths, or other private information, so the
process may temporarily hold such a decoded line in memory while determining
its event type.

## Data it exposes to the widget

The helper uses an allowlist and emits only:

- update timestamp and plan type;
- `used_percent`, `window_minutes`, and `resets_at` for each limit; and
- `has_credits`, `unlimited`, and `balance` when credit information exists.

Unknown fields are discarded. Conversation content is not displayed, saved,
logged, or included in helper output.

## Network and storage

- The widget makes no network requests.
- It does not write to Codex session files.
- It does not create its own analytics or telemetry.
- Plasma stores widget preferences such as refresh interval, display mode,
  and a user-selected custom-icon path in the normal Plasma configuration.

## Recommendations

Treat Codex session files as sensitive. Do not attach session JSONL files to
public bug reports. Reproduce parser issues with a minimal synthetic event or
use GitHub private vulnerability reporting for security-sensitive reports.
