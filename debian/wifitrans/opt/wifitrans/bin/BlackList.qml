import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    id: blackListPage
    orientationLock: PageOrientation.LockPortrait

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-back"
            onClicked: pageStack.pop()
        }
    }

    Component.onCompleted: {
        reloadModel();
    }

    function reloadModel() {
        blackListModel.clear();
        var NOI = cControl.getBlackLength();
        for (var i = 0; i < NOI; i++) {
            blackListModel.append({"text": cControl.getBlackItem(i)});
        }
    }

    Rectangle {
        id: headerRect
        anchors.top:blackListPage.top; anchors.left: blackListPage.left; anchors.right: blackListPage.right
        width: blackListPage.width ; height: blackListPage.height/11
        color: "#1A7DD1"
        Text {
            id: titleText
            anchors.centerIn: headerRect
            color: "white"
            font.pixelSize: 35
            text: qsTr("Blocked IP")
        }
    }

    ListModel {
        id: blackListModel
    }

    ListView {
        id: blackListView
        width: parent.width
        height: parent.height - headerRect.height - 20
        anchors.top: headerRect.bottom
        anchors.topMargin: 20
        clip: true

        model: blackListModel

        delegate: Item {
            id: containingRect
            width: parent.width
            height: 88

            Rectangle {
                anchors.fill: parent
                color: "#DFE1E2"
                visible: mouseArea.pressed
            }

            Label {
                text: model.text
                anchors.left: parent.left
                anchors.centerIn: parent
                font.pixelSize: 35
            }

            MouseArea {
                id: mouseArea
                anchors.fill: parent
                onClicked: {
                    cControl.removeBlackItem(model.text);
                    reloadModel();
                }
            }
        }
    }
}
