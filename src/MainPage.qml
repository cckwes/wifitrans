import QtQuick 1.1
import com.nokia.meego 1.0

Page {
    id: appWindow
    objectName: "appWindow"
    orientationLock: PageOrientation.LockPortrait
    
    tools: commonTools

    property string ipAddr;
    property string clientIP;
    property bool custom;
    property string username;
    property string password;

    Component.onCompleted: {
        appWindow.custom = cControl.getCustomUP();
        //get the username and password
        appWindow.username = cControl.getUsername();
        appWindow.password = cControl.getPassword();

        //get ip address
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
        anchors.topMargin: 30
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
        text: appWindow.username
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
        text: appWindow.password
	anchors.top: passLabel.bottom
	anchors.topMargin: 20
	anchors.right: parent.right
	anchors.rightMargin: 20
	font.weight: Font.Bold
	font.pixelSize: 30
	color: "white"
    }

    Button {
        id: genEdBtn
        anchors.top: passwordLabel.bottom
        anchors.topMargin: 40
        anchors.horizontalCenter: parent.horizontalCenter
        text: (appWindow.custom) ? "Edit Username, Password" : "Generate new Password"

        onClicked: {
            if (appWindow.custom) {
                //edit username and password, bring up the sheet
                editUserPass.open();
            } else {
                cControl.generatePassword();
                appWindow.password = cControl.getPassword();
            }
        }
    }

    ButtonRow {
        id: customBtnRow
        anchors.top: genEdBtn.bottom
        anchors.topMargin: 40
        anchors.horizontalCenter: parent.horizontalCenter
        checkedButton: (appWindow.custom) ? customBtn : generateBtn
        Button {
            id: customBtn
            text: "Custom"
            onClicked: {
                appWindow.custom = true;
                cControl.loadCustom();
                cControl.storeCustom(true);
                appWindow.username = cControl.getUsername();
                appWindow.password = cControl.getPassword();
            }
        }
        Button {
            id: generateBtn
            text: "Generated"
            onClicked: {
                appWindow.custom = false;
                cControl.unloadCustom();
                cControl.storeCustom(false);
                appWindow.username = cControl.getUsername();
                appWindow.password = cControl.getPassword();
            }
        }
    }

    SipAttributes {
        id: nextAttrib
        actionKeyLabel: "Next"
        actionKeyEnabled: true
    }

    SipAttributes {
        id: saveAttrib
        actionKeyLabel: "Save"
        actionKeyEnabled: true
    }

    Sheet {
        id: editUserPass

        acceptButtonText: "Save"
        rejectButtonText: "Cancel"
        visualParent: appWindow

        content: Flickable {
            anchors.fill: parent
            anchors.margins: 40
            Column {
                spacing: 10
                width: parent.width

                Label {
                    text: "Username"
                }

                TextField {
                    id: usernameInput
                    maximumLength: 20
                    platformSipAttributes: nextAttrib
                    width: parent.width
                    text: appWindow.username

                    Keys.onReturnPressed: passwordInput.forceActiveFocus()
                }

                Label {
                    text: "Password"
                }

                TextField {
                    id: passwordInput
                    maximumLength: 12
                    //echoMode: TextInput.PasswordEchoOnEdit
                    platformSipAttributes: saveAttrib
                    width: parent.width
                    text: appWindow.password

                    Keys.onReturnPressed: {
                        passwordInput.platformCloseSoftwareInputPanel()
                        editUserPass.accept();
                    }
                }
            }
        }

        onAccepted: {
            cControl.storeUsernamePass(usernameInput.text, passwordInput.text);
            console.log("changed username to " + usernameInput.text + " and password to " + passwordInput.text);
            appWindow.username = cControl.getUsername();
            appWindow.password = cControl.getPassword();
            editUserPass.close();
        }

        onRejected: {
            editUserPass.close();
        }
    }

    QueryDialog {
        id: clientIPQuery
        icon: "image://theme/icon-l-installing"
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
