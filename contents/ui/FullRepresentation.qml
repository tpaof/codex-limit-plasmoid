// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick
import QtQuick.Layouts

import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PlasmaComponents

Item {
    id: full

    required property var widget

    implicitWidth: Kirigami.Units.gridUnit * 20
    implicitHeight: content.implicitHeight + Kirigami.Units.largeSpacing * 2
    Layout.minimumWidth: implicitWidth
    Layout.minimumHeight: implicitHeight
    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight

    function resetLabel(limit) {
        if (!limit || !limit.resets_at) {
            return ""
        }
        const resetDate = new Date(Number(limit.resets_at) * 1000)
        return qsTr("Resets %1").arg(Qt.formatDateTime(resetDate, Qt.DefaultLocaleShortDate))
    }

    ColumnLayout {
        id: content
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing

        RowLayout {
            Layout.fillWidth: true

            Kirigami.Icon {
                Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                Layout.preferredHeight: width
                source: widget.displayIcon
                fallback: widget.codexIcon
                isMask: widget.usingDefaultIcon
                color: "white"
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0

                PlasmaComponents.Label {
                    text: qsTr("Codex usage")
                    font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.2
                    font.weight: Font.Bold
                }

                PlasmaComponents.Label {
                    text: widget.planType ? widget.planType.charAt(0).toUpperCase() + widget.planType.slice(1) + qsTr(" plan") : qsTr("Local account")
                    color: Kirigami.Theme.disabledTextColor
                }
            }

            PlasmaComponents.ToolButton {
                icon.name: "view-refresh-symbolic"
                enabled: !widget.loading
                onClicked: widget.refresh()
                PlasmaComponents.ToolTip.text: qsTr("Refresh")
                PlasmaComponents.ToolTip.visible: hovered
            }
        }

        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: widget.errorMessage.length > 0
            type: Kirigami.MessageType.Error
            text: widget.errorMessage
        }

        ColumnLayout {
            Layout.fillWidth: true
            visible: !widget.errorMessage
            spacing: Kirigami.Units.largeSpacing

            LimitBar {
                Layout.fillWidth: true
                title: widget.primary && widget.primary.window_minutes
                    ? qsTr("%1-hour limit").arg(Number(widget.primary.window_minutes) / 60)
                    : qsTr("Short-term limit")
                limit: widget.primary
                resetText: full.resetLabel(widget.primary)
            }

            LimitBar {
                Layout.fillWidth: true
                title: widget.secondary && Number(widget.secondary.window_minutes) === 10080
                    ? qsTr("Weekly limit")
                    : qsTr("Long-term limit")
                limit: widget.secondary
                resetText: full.resetLabel(widget.secondary)
            }

            LimitBar {
                Layout.fillWidth: true
                visible: widget.reserve !== null
                title: qsTr("gpt-reserve Weekly limit")
                limit: widget.reserve
                resetText: full.resetLabel(widget.reserve)
            }

            RowLayout {
                Layout.fillWidth: true
                visible: widget.credits && (widget.credits.has_credits || widget.credits.unlimited)

                PlasmaComponents.Label {
                    Layout.fillWidth: true
                    text: qsTr("Credits")
                    color: Kirigami.Theme.disabledTextColor
                }

                PlasmaComponents.Label {
                    text: !widget.credits ? "0"
                        : widget.credits.unlimited ? qsTr("Unlimited")
                        : String(widget.credits.balance || "0")
                    font.weight: Font.DemiBold
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: Kirigami.Theme.textColor
            opacity: 0.12
        }

        PlasmaComponents.Label {
            Layout.fillWidth: true
            text: widget.updatedAt
                ? qsTr("Codex snapshot · updated %1").arg(Qt.formatDateTime(new Date(widget.updatedAt * 1000), Qt.DefaultLocaleShortDate))
                : qsTr("Waiting for Codex data…")
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
            elide: Text.ElideRight
        }
    }
}
