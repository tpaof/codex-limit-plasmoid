// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick
import QtQuick.Layouts

import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.core as PlasmaCore

MouseArea {
    id: compact

    required property var widget
    property bool wasExpanded: false

    readonly property real horizontalPadding: Kirigami.Units.largeSpacing * 2

    implicitWidth: row.implicitWidth + horizontalPadding * 2
    implicitHeight: Math.max(Kirigami.Units.gridUnit * 2,
        widget.panelIconSize + Kirigami.Units.smallSpacing * 2)
    Layout.minimumWidth: implicitWidth
    Layout.preferredWidth: implicitWidth
    Layout.maximumWidth: implicitWidth
    Layout.fillHeight: true
    hoverEnabled: true
    onPressed: wasExpanded = widget.expanded
    onClicked: widget.expanded = !wasExpanded

    RowLayout {
        id: row
        anchors.centerIn: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Icon {
            visible: widget.showPanelIcon
            Layout.preferredWidth: widget.panelIconSize
            Layout.preferredHeight: width
            source: widget.displayIcon
            fallback: widget.codexIcon
            isMask: widget.usingDefaultIcon
            color: "white"
        }

        PlasmaComponents.Label {
            visible: widget.panelDisplayMode === 0 || widget.showCodexLabel || widget.errorMessage
            text: {
                const value = widget.errorMessage ? "!" : qsTr("%1%").arg(widget.primaryRemaining)
                if (widget.panelDisplayMode === 1 && !widget.errorMessage) {
                    return qsTr("Codex")
                }
                return widget.showCodexLabel ? qsTr("Codex %1").arg(value) : value
            }
            font.weight: Font.DemiBold
            textFormat: Text.PlainText
        }

        PanelProgressBar {
            visible: widget.panelDisplayMode === 1 && !widget.errorMessage
            value: widget.primaryRemaining
        }

        PlasmaComponents.BusyIndicator {
            visible: widget.loading
            running: visible
            Layout.preferredWidth: Kirigami.Units.iconSizes.small
            Layout.preferredHeight: width
        }
    }
}
