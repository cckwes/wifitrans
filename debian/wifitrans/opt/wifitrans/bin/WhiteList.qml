import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    id: whiteListPage
    orientationLock: PageOrientation.LockPortrait

    tools: commonTools

    Component.onCompleted: {
        reloadModel();
    }

    function reloadModel() {
        whiteListModel.clear();
        var NOI = cControl.getWhiteLength();
        for (var i = 0; i < NOI; i++) {
            whiteListModel.append({"text": cControl.getWhiteItem(i)});
        }
    }

    Rectangle {
        id: headerRect
        anchors.top:whiteListPage.top; anchors.left: whiteListPage.left; anchors.right: whiteListPage.right
        width: whiteListPage.width ; height: whiteListPage.height/11
        color: "#1A7DD1"
        Text {
            id: titleText
            anchors.centerIn: headerRect
            color: "white"
            font.pixelSize: 35
            text: qsTr("Approved IP")
        }
    }

    ListModel {
        id: whiteListModel
    }

    ListView {
        id: whiteListView
        width: parent.width
        height: parent.height - headerRect.height - 20
        anchors.top: headerRect.bottom
        anchors.topMargin: 20
        clip: true

        model: whiteListModel

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
                    cControl.removeWhiteItem(model.text);
                    reloadModel();
                }
            }
        }
    }
}
