import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
    id: mainWindow
    
    //showToolBar: false
    showStatusBar: false      
    
    Component.onCompleted: {
        theme.inverted = true
    }

    property bool thumb: false;

    function openFile(file) {
        var component = Qt.createComponent(file)
        if (component.status === Component.Ready)
            pageStack.push(component);
        else
            console.log("Error loading component:", component.errorString());
    }

    initialPage: MainPage {}
    
    ToolBarLayout {
        id: commonTools
        visible: false
        ToolIcon { iconId: "toolbar-back"; onClicked: pageStack.pop(); }
        ToolIcon { iconId: "toolbar-view-menu"; onClicked: commonMenu.open(); }
    }

    Menu {
        id: commonMenu
        visualParent: pageStack

        MenuLayout {
            MenuItem {
                text: "Approved IP"
                onClicked: openFile("WhiteList.qml");
            }
            MenuItem {
                text: "Blocked IP"
                onClicked: openFile("BlackList.qml");
            }
            MenuItem {
                text: (mainWindow.thumb) ? "Photo Thumbnail Enabled" : "Photo Thumbnail Disabled"
                onClicked: {
                    mainWindow.thumb = !mainWindow.thumb;
                    cControl.setPhotoThumb(mainWindow.thumb);
                }
            }

            MenuItem {
                text: "About"
                onClicked: openFile("AboutPage.qml");
            }
        }
    }
}
