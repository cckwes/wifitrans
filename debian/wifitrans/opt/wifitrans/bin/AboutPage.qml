import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    id: aboutPage
    orientationLock: PageOrientation.LockPortrait

    tools: ToolBarLayout {
        ToolIcon {
            iconId: "toolbar-back"
            onClicked: pageStack.pop()
        }
    }

    Image {
        id: logo
        source: "/opt/wifitrans/file/wifitrans.png"
        height: 300
        width: 300
        fillMode: Image.PreserveAspectFit
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 80
    }

    Label {
        id: appName
        text: "WifiTrans"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: logo.bottom
        anchors.topMargin: 60

        platformStyle: LabelStyle {
            fontPixelSize: 30
        }
    }

    Label {
        id: version
        text: "v0.2.1"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: appName.bottom
        anchors.topMargin: 20

        platformStyle: LabelStyle {
            fontPixelSize: 30
        }
    }

    Label {
        id: author
        text: "Wesley Chong 2012"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: version.bottom
        anchors.topMargin: 20

        platformStyle: LabelStyle {
            fontPixelSize: 30
        }
    }
}
