// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick
import QtQuick.Layouts

import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PlasmaComponents

ColumnLayout {
    id: control

    required property string title
    required property var limit
    property string resetText: ""

    readonly property real usedPercent: limit ? Math.max(0, Math.min(100, Number(limit.used_percent || 0))) : 0
    readonly property int remainingPercent: Math.round(100 - usedPercent)

    spacing: Kirigami.Units.smallSpacing

    RowLayout {
        Layout.fillWidth: true

        PlasmaComponents.Label {
            Layout.fillWidth: true
            text: control.title
            font.weight: Font.DemiBold
        }

        PlasmaComponents.Label {
            text: qsTr("%1% left").arg(control.remainingPercent)
            color: control.usedPercent >= 90 ? Kirigami.Theme.negativeTextColor
                : control.usedPercent >= 75 ? Kirigami.Theme.neutralTextColor
                : Kirigami.Theme.positiveTextColor
            font.weight: Font.Bold
        }
    }

    PlasmaComponents.ProgressBar {
        Layout.fillWidth: true
        from: 0
        to: 100
        value: control.remainingPercent
    }

    PlasmaComponents.Label {
        Layout.fillWidth: true
        text: control.resetText
        visible: text.length > 0
        color: Kirigami.Theme.disabledTextColor
        font: Kirigami.Theme.smallFont
        elide: Text.ElideRight
    }
}
