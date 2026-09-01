// SPDX-FileCopyrightText: 2026 Codex Limit contributors
// SPDX-License-Identifier: MIT

import QtQuick

import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5Support
import org.kde.plasma.plasmoid

PlasmoidItem {
    id: root

    property var primary: null
    property var secondary: null
    property var credits: null
    property string planType: ""
    property string errorMessage: ""
    property double updatedAt: 0
    property bool loading: true

    readonly property int primaryRemaining: primary ? Math.max(0, Math.round(100 - Number(primary.used_percent || 0))) : 0
    readonly property int secondaryRemaining: secondary ? Math.max(0, Math.round(100 - Number(secondary.used_percent || 0))) : 0
    readonly property url codexIcon: Qt.resolvedUrl("../images/codex-limit.svg")
    readonly property string customIcon: String(Plasmoid.configuration.customIcon || "")
    readonly property var displayIcon: customIcon.length > 0 ? customIcon : codexIcon
    readonly property bool usingDefaultIcon: customIcon.length === 0
    readonly property int panelIconSize: Math.max(12, Math.min(64, Number(Plasmoid.configuration.panelIconSize || 22)))
    readonly property bool showPanelIcon: Plasmoid.configuration.showPanelIcon !== false
    readonly property bool showCodexLabel: Plasmoid.configuration.showCodexLabel !== false
    readonly property int panelDisplayMode: Math.max(0, Math.min(1,
        Number(Plasmoid.configuration.panelDisplayMode || 0)))
    readonly property string helperPath: decodeURIComponent(String(Qt.resolvedUrl("../code/read_limits.py")).replace(/^file:\/\//, ""))
    readonly property string helperCommand: "python3 " + JSON.stringify(helperPath)
    readonly property int refreshMilliseconds: Math.max(15, Number(Plasmoid.configuration.refreshInterval || 60)) * 1000

    switchWidth: Kirigami.Units.gridUnit * 11
    switchHeight: Kirigami.Units.gridUnit * 4
    Plasmoid.icon: displayIcon
    Plasmoid.status: errorMessage ? PlasmaCore.Types.NeedsAttentionStatus : PlasmaCore.Types.ActiveStatus
    toolTipMainText: "Codex Limit"
    toolTipSubText: errorMessage ? errorMessage : qsTr("5-hour: %1% left · Weekly: %2% left").arg(primaryRemaining).arg(secondaryRemaining)

    compactRepresentation: CompactRepresentation {
        widget: root
    }

    fullRepresentation: FullRepresentation {
        widget: root
    }

    function refresh() {
        loading = true
        limitSource.disconnectSource(helperCommand)
        limitSource.connectSource(helperCommand)
    }

    function consumeOutput(data) {
        let output = data.stdout || ""
        try {
            const result = JSON.parse(output.trim())
            if (!result.ok) {
                errorMessage = result.error || qsTr("Unable to read Codex limits")
                return
            }

            primary = result.primary || null
            secondary = result.secondary || null
            credits = result.credits || null
            planType = result.plan_type || ""
            updatedAt = Number(result.updated_at || 0)
            errorMessage = ""
        } catch (error) {
            errorMessage = data.stderr || qsTr("Invalid response from the limit reader")
        } finally {
            loading = false
        }
    }

    P5Support.DataSource {
        id: limitSource
        engine: "executable"
        connectedSources: [root.helperCommand]
        interval: root.refreshMilliseconds

        onNewData: function(sourceName, data) {
            root.consumeOutput(data)
        }
    }
}
