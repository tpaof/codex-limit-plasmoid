// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick

import org.kde.plasma.configuration

ConfigModel {
    ConfigCategory {
        name: qsTr("General")
        icon: "configure-symbolic"
        source: "ConfigGeneral.qml"
    }
}
