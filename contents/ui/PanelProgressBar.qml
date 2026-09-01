// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick
import QtQuick.Layouts

import org.kde.kirigami as Kirigami

Item {
    id: control

    property real value: 0

    readonly property real fraction: Math.max(0, Math.min(1, value / 100))

    implicitWidth: Kirigami.Units.gridUnit * 5
    implicitHeight: Kirigami.Units.iconSizes.small
    Layout.minimumWidth: implicitWidth
    Layout.preferredWidth: implicitWidth
    Layout.maximumWidth: implicitWidth
    Layout.preferredHeight: implicitHeight

    Rectangle {
        id: track

        x: 0
        y: 2
        width: control.width
        height: control.height - 4
        color: Kirigami.Theme.textColor
        opacity: 0.28
    }

    Rectangle {
        x: track.x
        y: track.y
        width: track.width * control.fraction
        height: track.height
        color: Kirigami.Theme.textColor

        Behavior on width {
            NumberAnimation {
                duration: Kirigami.Units.shortDuration
                easing.type: Easing.OutCubic
            }
        }
    }
}
