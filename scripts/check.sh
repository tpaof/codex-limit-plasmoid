#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Codex Limit contributors
# SPDX-License-Identifier: MIT

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/.." && pwd)"
temporary_dir="$(mktemp -d)"
trap 'rm -rf -- "$temporary_dir"' EXIT

cd -- "$project_root"

python3 -B -m unittest discover -s tests -v
python3 -m json.tool metadata.json >/dev/null
python3 - <<'PY'
import xml.etree.ElementTree as ET

ET.parse("contents/config/main.xml")
PY

if command -v qmllint >/dev/null 2>&1; then
    qml_import_path=""
    for candidate in /usr/lib/qt6/qml /usr/lib64/qt6/qml; do
        if [[ -d "$candidate" ]]; then
            qml_import_path="$candidate"
            break
        fi
    done

    if [[ -n "$qml_import_path" ]]; then
        qmllint -I "$qml_import_path" contents/ui/*.qml contents/config/*.qml
    else
        printf 'Skipping qmllint: Qt 6 QML import path was not found.\n'
    fi
else
    printf 'Skipping qmllint: command is not installed.\n'
fi

"$script_dir/package.sh" "$temporary_dir/codex-limit.plasmoid"
unzip -tq "$temporary_dir/codex-limit.plasmoid"

if unzip -Z1 "$temporary_dir/codex-limit.plasmoid" \
    | grep -Eq '(^|/)(\.|__pycache__)|\.pyc$|\.kate-swp$|codex\.png$'; then
    printf 'Package contains a private, generated, or legacy file.\n' >&2
    exit 1
fi

printf 'All checks passed.\n'
