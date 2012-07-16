import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    id: appWindow
    objectName: "appWindow"
    orientationLock: PageOrientation.LockPortrait
    
    tools: commonTools

    property string ipAddr;
    property string clientIP;

    Component.onCompleted: {
        if (sControl.retrieveIP() != "") {
            appWindow.ipAddr = "http://" + sControl.retrieveIP() + ":8080";
        } else {
            appWindow.ipAddr = 0;
        }
    }

    function showThing(msg) {
        appWindow.clientIP = msg;
        clientIPQuery.message = "Approve IP Address " + msg + "?";
        clientIPQuery.open();
        console.log("request: " + msg);
    }


    Rectangle {
        id: headerRect
        anchors.top:appWindow.top; anchors.left: appWindow.left; anchors.right: appWindow.right
        width: appWindow.width ; height: appWindow.height/11
        color: "#1A7DD1"
        Text {
            id: titleText
            anchors.centerIn: headerRect
            color: "white"
            font.pixelSize: 35
            text: qsTr("Wifi Transfer")
        }
    }

    Label {
        id: wifiLabel
        text: "Wifi Server"
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: headerRect.bottom
        anchors.topMargin: 50
    }

    Switch {
        id: wifiSwitch
        checked: false
        anchors.top: headerRect.bottom
        anchors.topMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20
        visible: (appWindow.ipAddr == 0) ? false : true

        onCheckedChanged: {
            if (wifiSwitch.checked) {
                sControl.startServer();
            } else {
                sControl.stopServer();
            }
        }
    }

    Label {
        id: ipLabel
        text: "Point your browser to this address for accessing the files"
	width: parent.width - 40
        anchors.top: wifiSwitch.bottom
        anchors.topMargin: 50
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        anchors.right: parent.right
    }

    Text {
        id: ipAddrLabel
        text: (appWindow.ipAddr == 0) ? "None" : appWindow.ipAddr
        anchors.top: ipLabel.bottom
        anchors.topMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20
        font.italic: true
        font.pixelSize: 30
        color: "white"
    }
    
    Label {
        id: userLabel
        text: "Username:"
	anchors.top: ipAddrLabel.bottom
	anchors.topMargin: 20
	anchors.left: parent.left
	anchors.leftMargin: 20
    }
    
    Text {
        id: usernameLabel
        text: "n9user"
	anchors.top: userLabel.bottom
	anchors.topMargin: 20
	anchors.right: parent.right
	anchors.rightMargin: 20
	font.weight: Font.Bold
	font.pixelSize: 30
	color: "white"
    }
    
    Label {
        id: passLabel
        text: "Password:"
	anchors.top: usernameLabel.bottom
	anchors.topMargin: 20
	anchors.left: parent.left
	anchors.leftMargin: 20
    }
    
    Text {
        id: passwordLabel
        text: cControl.getPassword()
	anchors.top: passLabel.bottom
	anchors.topMargin: 20
	anchors.right: parent.right
	anchors.rightMargin: 20
	font.weight: Font.Bold
	font.pixelSize: 30
	color: "white"
    }

    QueryDialog {
        id: clientIPQuery
        titleText: "Client IP Approval"
        acceptButtonText: "Approve"
        rejectButtonText: "Reject"

        onAccepted: {
            clientIPQuery.close();
            cControl.addIP(appWindow.clientIP);
        }

        onRejected: {
            clientIPQuery.close();
            cControl.addBlackList(appWindow.clientIP);
        }
    }
}
