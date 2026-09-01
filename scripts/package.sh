#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Codex Limit contributors
# SPDX-License-Identifier: MIT

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
requested_output="${1:-$project_root/codex-limit.plasmoid}"

if [[ "$requested_output" = /* ]]; then
    output_path="$requested_output"
else
    output_path="$(pwd)/$requested_output"
fi

temporary_dir="$(mktemp -d)"
trap 'rm -rf -- "$temporary_dir"' EXIT
temporary_archive="$temporary_dir/codex-limit.plasmoid"

cd -- "$project_root"
{
    printf '%s\n' metadata.json LICENSE NOTICE README.md PRIVACY.md
    find contents -type f \
        ! -name '*.kate-swp' \
        ! -name '*.pyc' \
        ! -path '*/__pycache__/*' \
        ! -path 'contents/images/codex.png' \
        -print
} | LC_ALL=C sort | zip -X -q "$temporary_archive" -@

mkdir -p -- "$(dirname -- "$output_path")"
mv -f -- "$temporary_archive" "$output_path"
unzip -tq "$output_path"
printf 'Created %s\n' "$output_path"
