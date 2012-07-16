import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
    id: mainWindow
    
    //showToolBar: false
    showStatusBar: false      
    
    Component.onCompleted: {
        theme.inverted = true
    }
    
    initialPage: MainPage {}
    
    ToolBarLayout {
        id: commonTools
        visible: false
        ToolIcon { iconId: "toolbar-back" }
    }
}
