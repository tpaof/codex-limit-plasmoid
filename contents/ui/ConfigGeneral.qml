// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Dialogs as QtDialogs
import QtQuick.Layouts

import org.kde.iconthemes as KIconThemes
import org.kde.kcmutils as KCM
import org.kde.kirigami as Kirigami

KCM.SimpleKCM {
    id: root

    property string cfg_customIcon: ""
    property alias cfg_panelIconSize: panelIconSize.value
    property alias cfg_showPanelIcon: showPanelIcon.checked
    property alias cfg_showCodexLabel: showCodexLabel.checked
    property alias cfg_panelDisplayMode: panelDisplayMode.currentIndex
    property alias cfg_refreshInterval: refreshInterval.value
    readonly property url defaultIcon: Qt.resolvedUrl("../images/codex-limit.svg")

    KIconThemes.IconDialog {
        id: iconDialog
        title: qsTr("Choose an icon")
        onIconNameChanged: function(iconName) {
            if (iconName) {
                root.cfg_customIcon = iconName
            }
        }
    }

    QtDialogs.FileDialog {
        id: imageDialog
        title: qsTr("Choose an icon image")
        nameFilters: [
            qsTr("Icon images (*.svg *.svgz *.png *.webp *.jpg *.jpeg)"),
            qsTr("All files (*)")
        ]
        onAccepted: root.cfg_customIcon = String(selectedFile)
    }

    Kirigami.FormLayout {
        RowLayout {
            Kirigami.FormData.label: qsTr("Icon:")
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Icon {
                Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                Layout.preferredHeight: width
                source: root.cfg_customIcon || root.defaultIcon
                fallback: root.defaultIcon
                isMask: !root.cfg_customIcon
                color: "white"
            }

            QQC2.Button {
                text: qsTr("System icon…")
                onClicked: iconDialog.open()
            }

            QQC2.Button {
                text: qsTr("Image file…")
                onClicked: imageDialog.open()
            }

            QQC2.ToolButton {
                icon.name: "edit-clear-symbolic"
                enabled: root.cfg_customIcon.length > 0
                onClicked: root.cfg_customIcon = ""
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.text: qsTr("Use the default Codex icon")
            }
        }

        QQC2.SpinBox {
            id: panelIconSize
            Kirigami.FormData.label: qsTr("Panel icon size:")
            from: 12
            to: 64
            stepSize: 1
            editable: true
            textFromValue: function(value) {
                return qsTr("%1 px").arg(value)
            }
            valueFromText: function(text) {
                const match = text.match(/\d+/)
                return match ? Number(match[0]) : 22
            }
        }

        RowLayout {
            Kirigami.FormData.label: qsTr("Show on panel:")
            spacing: Kirigami.Units.largeSpacing

            QQC2.CheckBox {
                id: showPanelIcon
                text: qsTr("Icon")
            }

            QQC2.CheckBox {
                id: showCodexLabel
                text: qsTr("“Codex” label")
            }
        }

        QQC2.ComboBox {
            id: panelDisplayMode
            Kirigami.FormData.label: qsTr("Panel display:")
            model: [
                qsTr("Percentage"),
                qsTr("Progress bar")
            ]
        }

        QQC2.SpinBox {
            id: refreshInterval
            Kirigami.FormData.label: qsTr("Refresh every:")
            from: 15
            to: 3600
            stepSize: 15
            editable: true
            textFromValue: function(value) {
                return qsTr("%1 seconds").arg(value)
            }
            valueFromText: function(text) {
                const match = text.match(/\d+/)
                return match ? Number(match[0]) : 60
            }
        }
    }
}
