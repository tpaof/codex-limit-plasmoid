# Security policy

## Supported versions

Security fixes are provided for the latest published release.

## Reporting a vulnerability

Use GitHub private vulnerability reporting when it is enabled for the
repository. If it is unavailable, open an issue containing only a brief
description and a request for a private contact channel.

Do not post Codex session files, prompts, responses, account details, home
directory paths, API keys, or other credentials in a public issue.

## Security model

Codex Limit runs a bundled Python helper as the current desktop user. The
helper has the same access as that user. It launches the trusted local Codex
binary and requests account rate limits through `codex app-server`; Codex may
make an authenticated service request and update its own runtime state. The
widget does not read, store, or log Codex credentials.

If app-server data is unavailable, the helper searches only the configured
local Codex sessions directory. It never modifies session files, and all
helper output is restricted to an explicit rate-limit field allowlist.

Custom icon files are selected by the user and loaded by Plasma. Only select
files you trust and expect Plasma to decode.
