# pylint: disable-all

from __future__ import annotations


# Python [Tool Script] for MotionBuilder.
# This script is used for improved take management with extra customization options.


from pyfbsdk import *
from pyfbsdk_additions import *

import types
import shiboken2 as shiboken
import sys
import os
import uuid
import re

from importlib import reload

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QShortcut
from PySide2.QtGui import QKeySequence

# Find folder path to this file. This will enable all other files to be accessed within the same folder.
CurrentDirectory = os.path.dirname(__file__)
if "builtin" in __name__:
    if CurrentDirectory not in sys.path:
        sys.path.append(CurrentDirectory)
    import Utils.WindowCreator as WindowCreator
else:
    from .Utils import WindowCreator

# Reload this script if the imported script has been edited.
reload(WindowCreator)

# Define application if it has not already been defined.
if not globals().get("Application"):
    Application = FBApplication()
System = FBSystem()
QApp = QtWidgets.QApplication

# Define tool name.
TOOL_NAME = "[JC] Take Manager"

# Define custom property name of parent.
PROPERTY_NAME_TAKE_UUID = "Take UUID"

# Set max allowed length of characters in text.
MAX_PACKAGE_LENGTH = 160



# ----------------- CLOSE EVENT ----------------- #



def ConnectToCloseEvent(Widget, Callback):
    """
    Alternative to closeEvent(), which doesn't fire for FBTools
    Args:
        Widget - Current widget
        Callback - Function to be called
    """
    DockWidget = FindParentWidgetByType(Widget, QtWidgets.QDockWidget) 
    if DockWidget:
        DockWidget.destroyed.connect(lambda: Callback(Widget, None))


def FindParentWidgetByType(Widget, Type):
    """ Iterate through the parents until a widget by the given type is found. """
    ParentWidget = Widget.parent()
    while True:
        if not ParentWidget:
            break
        if isinstance(ParentWidget, Type):
            return ParentWidget
        ParentWidget = ParentWidget.parent()



# ----------------- TAKES CUSTOM PROPERTIES ----------------- #



def GetUniqueIdByTake(Take: FBTake) -> str:
    """ Get the unique ID that the take owns. """
    UUIDProperty = Take.PropertyList.Find(PROPERTY_NAME_TAKE_UUID, False)
    # If no ID is found, create a new one.
    if UUIDProperty is None:
        UUIDProperty: FBPropertyListObject = Take.PropertyCreate(PROPERTY_NAME_TAKE_UUID, FBPropertyType.kFBPT_charptr, "", False, True, None)
        UUIDProperty.Data = str(uuid.uuid4())
    return UUIDProperty.Data


def GetTakeByUniqueID(UUID: str) -> FBTake:
    """ Get take by their unique ID. """
    # Go through every takes in scene and check if they own an ID.
    for Take in System.Scene.Takes:
        UUIDProperty = Take.PropertyList.Find(PROPERTY_NAME_TAKE_UUID, False)
        # return takes that have matching data with UUID.
        if UUIDProperty:
            if UUIDProperty.Data == UUID:
                return Take



# ----------------- IS BOUND ----------------- #



def IsBound(Object: FBComponent):
    """ Check if an object exists. """
    return "Unbound" not in str(Object.__class__)



# ----------------- TAKE SORTING ----------------- #



def ApplyTakeOrder(TakeList: list[FBTake], bKeepCurrentTake = True):
    """ Sort take order by piping in a new list with the expected order. """
    if len(TakeList) != len(System.Scene.Takes):
        raise ValueError("Length of the given sorted takes list does not match the scene takes!")
    
    CurrentTake = System.CurrentTake

    # Disconnect all of the takes from the scene.
    for Take in TakeList[1:]:
        Take.DisconnectDst(System.Scene)
    # Populate the take list with the takes in the specified order.
    for Take in TakeList[1:]:
        System.Scene.ConnectSrc(Take, FBConnectionType.kFBConnectionTypeSystem)

    # Set current active take again once reordering has finished.
    if bKeepCurrentTake:
        System.CurrentTake = CurrentTake


def GetMoBuSelection() -> list[FBComponent]:
    """ Get selected objects in MotionBuilder. """
    return [x for x in System.Scene.Components if x.Selected == True]


def DeselectAllModels():
    """ Deselect everything in scene. """
    FBBeginChangeAllModels()
    # Get selected models in scene.
    SelectedModels = FBModelList()
    FBGetSelectedModels (SelectedModels, None, True)
    for Model in SelectedModels:
        Model.Selected = False
    FBEndChangeAllModels()



# ---------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------- TREE WIDGET ITEM CLASS -------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------- #



class TakeTreeItem(QtWidgets.QTreeWidgetItem):


    # Set name of custom property that the takes will get.
    PROPERTY_NAME_GROUP = "Parent UUID"
    PROPERTY_NAME_EXPANDED = "Expanded"
    PROPERTY_NAME_COLOR = "Color"


    def __init__(self, Take: FBTake):
        super().__init__()

        # Define take.
        self.Take = Take
        # Match item name with take name.
        self.setText(0, self.Take.Name)
        # Make item editable.
        self.setFlags(self.flags() |QtCore.Qt.ItemIsEditable)
        # Check if a take has color property on initialize. If it does then set correct color on the item in list.
        Color = self.GetColor()
        if Color:
            self.SetColor(Color)


    def SelectActiveTake(self, bUpdateGuiOnly = False):
        """ Customize the active take in list. Set current take in MoBu. """
        FontStyle = QtGui.QFont()
        FontStyle.setBold(True)
        FontStyle.setWeight(100)
        self.setFont(0, FontStyle)
        self.setBackgroundColor(0, QtGui.QColor(60,60,65))
        if not bUpdateGuiOnly:
            System.CurrentTake = self.Take


    def DeselectActiveTake(self):
        """ Reset bold and background color on previous active item in list. """
        self.setData(0, QtCore.Qt.BackgroundRole, None)
        self.setData(0, QtCore.Qt.FontRole, None)


    def DeleteTake(self):
        """ Delete take. """
        # Only delete if the item exists.
        if IsBound(self.Take):
            self.Take.FBDelete() 


    def GetParentTake(self) -> FBTake:
        """ Get parent of selected item. """
        GroupProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_GROUP, False)
        if not GroupProperty:
            return None
        return GetTakeByUniqueID(GroupProperty.Data)


    def SetParentProperty(self, Parent: TakeTreeItem):
        """ Set parent property of selected item. """
        GroupProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_GROUP, False)
        if GroupProperty is None:
            GroupProperty: FBPropertyListObject = self.Take.PropertyCreate(self.PROPERTY_NAME_GROUP, FBPropertyType.kFBPT_charptr, "", False, True, None)
        GroupProperty.Data = GetUniqueIdByTake(Parent.Take)


    def RemoveParentProperty(self):
        """ Remove parent property of selected item. """
        GroupProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_GROUP, False)
        if GroupProperty:
            self.Take.PropertyRemove(GroupProperty)


    def SetItemExpanded(self, bIsExpanded):
        """ Set expanded property on item. """
        ExpandedProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_EXPANDED, False)
        if not ExpandedProperty:
            ExpandedProperty = self.Take.PropertyCreate(self.PROPERTY_NAME_EXPANDED, FBPropertyType.kFBPT_bool, "", False, True, None)
        ExpandedProperty.Data = bIsExpanded


    def GetItemExpanded(self):
        """ Get if item is expanded or not. """
        ExpandedProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_EXPANDED, False)
        if not ExpandedProperty:
            return False
        return ExpandedProperty.Data
        

    def SetColor(self, Color):
        """ Set color of item. """
        # Colors.
        ColorVariable = QtGui.QColor(*Color)
        self.setForeground(0, ColorVariable)
        # Custom property.
        ColorProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_COLOR, False)
        if not ColorProperty:
            ColorProperty = self.Take.PropertyCreate(self.PROPERTY_NAME_COLOR, FBPropertyType.kFBPT_ColorRGB, "", False, True, None)
        ColorProperty.Data = FBColor(Color[0] / 255, Color[1] / 255, Color[2] / 255)


    def GetColor(self):
        """ Get color of item. """
        ColorProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_COLOR, False)
        if not ColorProperty:
            return None
        return ColorProperty.Data[0] * 255, ColorProperty.Data[1] * 255, ColorProperty.Data[2] * 255


    def ResetColor(self):
        """ Reset color of item. """
        # Colors.
        self.setData(0, QtCore.Qt.ForegroundRole, None)
        # Custom property.
        ColorProperty = self.Take.PropertyList.Find(self.PROPERTY_NAME_COLOR, False)
        if ColorProperty:
            self.Take.PropertyRemove(ColorProperty)



# ---------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- CUSTOM TREE WIDGET CLASS ------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------- #



class CustomTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args):
        super().__init__(*args)

        # Define MouseHoverEvent.
        self.MouseHoverEvent: types.FunctionType = None


    def enterEvent(self, EnterEvent: QtCore.QEvent): # pylint: disable=invalid-name
        """ Calls when mouse is hovering over widget. """
        if callable(self.MouseHoverEvent):
            self.MouseHoverEvent(True, EnterEvent) # pylint: disable=not-callable
        return False


    def leaveEvent(self, Event: QtCore.QEvent): # pylint: disable=invalid-name
        """ Calls when mouse is NOT hovering over widget. """
        if callable(self.MouseHoverEvent):
            self.MouseHoverEvent(False, Event) # pylint: disable=not-callable
        return False


    def startDrag(self, SupportedActions: QtCore.Qt.DropActions): # pylint: disable=invalid-name
        """ Calls when starting to drag items. """
        # Hide that annoying pixmap when dragging items in list.
        Drag = QtGui.QDrag(self) 
        Drag.setMimeData(self.mimeData(self.selectedItems()))
        Drag.exec_(SupportedActions)


    def mousePressEvent(self, event):
        """ Calls when mouse is clicked. """
        # Prevent horizontal scrollbar view from resetting when an item is clicked.
        self.setAutoScroll(False)
        super().mousePressEvent(event)
        self.setAutoScroll(True)



# --------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------- WINDOW CREATION ----------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------- #



class MainWidget(QtWidgets.QWidget): 

    # Set RGB color values for when creating color buttons. 
    COLOR_NONE = (200,200,200)
    COLOR_PURPLE = (180,170,235)
    COLOR_BLUE = (160,215,235)
    COLOR_GREEN = (170,225,180)
    COLOR_YELLOW = (220,220,160)
    COLOR_ORANGE = (230,175,140)
    COLOR_RED = (230,130,130)
    COLOR_PINK = (250,195,220)

    def __init__(self, Parent = None): 
        super().__init__(Parent)



        # ----------------- ICONS DIRECTORY ----------------- #



        # Find Icons folder path.
        QtCore.QDir.addSearchPath('icons', os.path.join(CurrentDirectory, 'Resources/Icons'))



        # ----------------- MAIN WINDOW SETTINGS ----------------- #



        # Restore default arrow cursor on initialize to prevent loading cursor bug.
        QApp.restoreOverrideCursor()



        # ----------------- TAKE LIST SETTINGS ----------------- #



        # Create tree list that will contain all takes in scene.
        self.TakeList = CustomTreeWidget()
        self.TakeList.setHeaderHidden(True)
        self.TakeList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.TakeList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.TakeList.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.TakeList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.TakeList.header().setStretchLastSection(False)
        self.TakeList.resizeEvent = self.OnResize

        TakeListStyle = """

        QTreeWidget::item {     
        padding: 2px 0;
        }

        QTreeView::branch:has-siblings:adjoins-item {
        border-image: url(icons:TreeWidget_Branch_More.png) 0;
        }

        QTreeView::branch:!has-children:!has-siblings:adjoins-item {
        border-image: url(icons:TreeWidget_Branch_End.png) 0;
        }

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {
        border-image: none;
        image: url(icons:TreeWidget_Branch_Closed.png);
        }

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings  {
        border-image: none;
        image: url(icons:TreeWidget_Branch_Opened.png);
        }

        """
        self.TakeList.setStyleSheet(TakeListStyle)
        self.TakeList.setExpandsOnDoubleClick(False)
        self.TakeList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # (Call function) Show context menu on right click.
        self.TakeList.customContextMenuRequested.connect(self.HandleRightClicked)
        # (Call function) Select current take when double clicking on an item.
        self.TakeList.itemDoubleClicked.connect(self.SetCurrentTake)
        # (Call function) Rename takes when an item's name has been changed.
        self.TakeList.model().dataChanged.connect(self.OnItemDataChanged)
        # (Call function) Expand / Collapse all selected items if shift key + left click are pressed on group icon.
        self.TakeList.itemExpanded.connect(self.OnExpand)
        self.TakeList.itemCollapsed.connect(self.OnCollapse)
        # (Call function) Move and group items in list.
        self.TakeList.model().rowsInserted.connect(self.MoveTakeItems)
        # (Call function) Selecting items in list also selects takes in MotionBuilder navigator.
        self.TakeList.itemSelectionChanged.connect(self.MakeMoBuSelection)

        # Define MouseHoverEvent.
        self.TakeList.MouseHoverEvent = self.HoveringTakeList



        # ----------------- SHORTCUT SETTINGS ----------------- #



        # Set no focus policy which disables all default shortcuts, but fixes dot-rectangle background on selected item.
        self.TakeList.setFocusPolicy(QtCore.Qt.NoFocus)

        self.ShortcutRefresh =   QShortcut(QKeySequence("F5"),     self.TakeList, self.RefreshTakeList)
        self.ShortcutNew =       QShortcut(QKeySequence("Ctrl+N"), self.TakeList, self.OnClickActionNew)
        self.ShortcutDuplicate = QShortcut(QKeySequence("Ctrl+D"), self.TakeList, self.OnClickActionDuplicate)
        self.ShortcutRename =    QShortcut(QKeySequence("F2"),     self.TakeList, self.OnClickActionRename)
        self.ShortcutDelete =    QShortcut(QKeySequence("Del"),    self.TakeList, self.OnClickActionDelete)
        self.ShortcutGroup =     QShortcut(QKeySequence("Ctrl+G"), self.TakeList, self.CreateNewGroup)
        self.ShortcutSelectAll = QShortcut(QKeySequence("Ctrl+A"), self.TakeList, self.ToggleSelectOrDeselectAll)
        self.ShortcutDeselect = QShortcut(QKeySequence("D"),       self.TakeList, self.Deselect)


        
        # ----------------- TEXT LABEL SETTINGS ----------------- #



        # Warning label.
        self.LabelWarnings = QtWidgets.QLabel(self)
        self.LabelWarnings.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        


        # ----------------- HELP BUTTON SETTINGS ----------------- #



        # Help button.
        self.ButtonHelp = QtWidgets.QPushButton(self)
        self.ButtonHelp.setFixedWidth(25)
        self.ButtonHelp.setFixedHeight(25)
        self.ButtonHelp.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_TitleBarContextHelpButton)) 
        self.ButtonHelp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))        
        self.ButtonHelp.setToolTip("Help")
        # (Call function) Show help window popup.
        self.ButtonHelp.clicked.connect(self.HelpPopup)



        # ----------------- LAYOUT CUSTOMIZATION ----------------- #



        # Create main layout.
        self.LayoutMainWindow = QtWidgets.QVBoxLayout(self)
        # Create sub layouts.
        self.LayoutSubWindowTop = QtWidgets.QVBoxLayout(self)
        self.LayoutSubWindowBottom = QtWidgets.QHBoxLayout(self)
        self.LayoutSubWindowBottomLeft = QtWidgets.QHBoxLayout(self)
        self.LayoutSubWindowBottomRight = QtWidgets.QHBoxLayout(self)
        
        # Set main layout.
        self.setLayout(self.LayoutMainWindow)
        # Set sub layouts to main layout.
        self.LayoutMainWindow.addLayout(self.LayoutSubWindowTop)
        self.LayoutMainWindow.addLayout(self.LayoutSubWindowBottom)
        self.LayoutSubWindowBottom.addLayout(self.LayoutSubWindowBottomLeft)
        self.LayoutSubWindowBottom.addLayout(self.LayoutSubWindowBottomRight)

        # Align sub layouts.
        self.LayoutSubWindowBottomRight.setAlignment(QtCore.Qt.AlignRight)

        # Add widgets (buttons, labels, etc.) to sub layouts.
        self.LayoutSubWindowTop.addWidget(self.TakeList)
        self.LayoutSubWindowBottomLeft.addWidget(self.LabelWarnings)
        self.LayoutSubWindowBottomRight.addWidget(self.ButtonHelp)
        
        
        
        # ----------------- STARTUP CALL EVENTS ----------------- #



        self.bIsUpdatingNatively = True
        self.bIsMovingTakesFromTool = False
        self.bPreventSelectionUpdate = False
        self.bIsDuplicatingItems = False
        self.bIsSettingActiveTakeFromTool = False
        self.bIsSelectingTakesFromTool = False
        self.bIsRenamingTakes = False

        self.RefreshTakeList()
        self.RegisterNativeMoBuEvents()
        ConnectToCloseEvent(self, self.onClose)
        self.bIsUpdatingNatively = False



    # ----------------- REFRESH LIST ----------------- #



    def RefreshTakeList(self):
        """ Refresh items in list. """
        self.bIsUpdatingNatively = True
        TopLevelItems = self.GetAllListTopLevelItems()
        for Item in TopLevelItems:
            self.GetParent(Item).removeChild(Item)

        for Take in System.Scene.Takes:
            item = TakeTreeItem(Take)
            self.TakeList.addTopLevelItem(item)
            if Take == System.CurrentTake:
                item.SelectActiveTake(bUpdateGuiOnly = True)

        Root = self.TakeList.invisibleRootItem()
        for Item in self.GetAllListItems():
            ParentTake = Item.GetParentTake()
            if ParentTake:
                ParentItem = self.GetItemByTake(ParentTake)
                if ParentItem:
                    # Take away children from old parent. 
                    Root.takeChild(Root.indexOfChild(Item))
                    # Add children to new parent.
                    ParentItem.addChild(Item)
            Item.setExpanded(Item.GetItemExpanded())
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bIsUpdatingNatively = False
        


    # ----------------- NATIVE MOBU EVENTS ----------------- #



    def RegisterNativeMoBuEvents(self):
        """ Tool will register native MotionBuilder events. """
        System.Scene.OnTakeChange.Add(self.OnTakeChanged)
        System.Scene.OnChange.Add(self.OnSceneChanged)
        Application.OnFileOpenCompleted.Add(self.OnFileOpenCompleted)
        Application.OnFileNewCompleted.Add(self.OnFileOpenCompleted)
        Application.OnFileOpen.Add(self.OnFileOpen)
        Application.OnFileNew.Add(self.OnFileOpen)
        Application.OnFileMerge.Add(self.OnFileOpen)


    def onClose(self, *args):
        """ Stop register when closing the tool. """
        self.UnRegisterNativeMoBuEvents()


    def UnRegisterNativeMoBuEvents(self):
        """ Stop register when closing the tool. """
        System.Scene.OnTakeChange.Remove(self.OnTakeChanged)
        System.Scene.OnChange.Remove(self.OnSceneChanged)
        Application.OnFileOpenCompleted.Remove(self.OnFileOpenCompleted)
        Application.OnFileNewCompleted.Remove(self.OnFileOpenCompleted)
        Application.OnFileOpen.Remove(self.OnFileOpen)
        Application.OnFileNew.Remove(self.OnFileOpen)
        Application.OnFileMerge.Remove(self.OnFileOpen)



    def OnTakeChanged(self, Scene: FBScene, Event: FBEventTakeChange):
        """ Signal if any takes are changed natively. """
        self.bIsUpdatingNatively = True
        # New / Duplicate / Group.
        if Event.Type == FBTakeChangeType.kFBTakeChangeAdded:    
            Item = TakeTreeItem(Event.Take)
            self.AddNewItemsToList(Item)
            if len(System.Scene.Takes) == 1:
                self.RefreshTakeList()
        # Rename.
        elif Event.Type == FBTakeChangeType.kFBTakeChangeRenamed:
            Item = self.GetItemByTake(Event.Take)
            self.RenameTakeOnListOnly(Item)
        # Delete.
        elif Event.Type == FBTakeChangeType.kFBTakeChangeRemoved:
            Item = self.GetItemByTake(Event.Take)
            self.DeleteTakeItems(Item, bDeleteChildren = False, bUpdateGuiOnly = True)
        # Move.
        elif Event.Type == FBTakeChangeType.kFBTakeChangeMoved:
            if not self.bIsMovingTakesFromTool:
                self.RefreshTakeList()
        # Current Active Take.
        elif Event.Type == FBTakeChangeType.kFBTakeChangeOpened:
            if not self.bIsSettingActiveTakeFromTool:
                self.SetCurrentTakeListOnly()
        self.bIsUpdatingNatively = False


    def OnSceneChanged(self, Scene: FBScene, Event: FBEventSceneChange):
        " Signal if anything in scene is changed natively. "
        # Filter to takes only.
        if isinstance(Event.Component, FBTake):
            self.bIsUpdatingNatively = True
            # Take selected.
            if Event.Type == FBSceneChangeType.kFBSceneChangeSelect:
                if not self.bIsSelectingTakesFromTool:
                    Item = self.GetItemByTake(Event.Component)
                    Item.setSelected(True)
            # Take deselected.
            elif Event.Type == FBSceneChangeType.kFBSceneChangeUnselect:
                if not self.bIsSelectingTakesFromTool:
                    Item = self.GetItemByTake(Event.Component)
                    Item.setSelected(False)
            self.bIsUpdatingNatively = False


    def OnFileOpen(self, InApplication: FBApplication, Event: FBEvent):
        """ Remove when file is opened. """
        System.Scene.OnTakeChange.Remove(self.OnTakeChanged)


    def OnFileOpenCompleted(self, InApplication: FBApplication, Event: FBEvent):
        """ Refresh list when opening a scene is completed. """
        self.RefreshTakeList()
        System.Scene.OnTakeChange.Add(self.OnTakeChanged)
        
    

    # ----------------- CONTEXT MENU SETTINGS ----------------- #



    def HandleRightClicked(self, Pos):
        """ Show context menu on right click. """
        # Create menu.
        Menu = QtWidgets.QMenu(self)
        SubMenuColor = QtWidgets.QMenu("Colors", self)
        # Define take item position.
        Item = self.TakeList.itemAt(Pos)

        def CreateAction(Name, Icon, Connection):
            """ Create actions. """
            Action = QtWidgets.QAction(Name, self)
            Action.setIcon(QtGui.QIcon(Icon))
            Action.triggered.connect(Connection)
            return Action
        # Create actions using previous function.
        ActionNew =       CreateAction("New",       "icons:New.png",       self.OnClickActionNew)
        ActionDuplicate = CreateAction("Duplicate", "icons:Duplicate.png", self.OnClickActionDuplicate)
        ActionRename =    CreateAction("Rename",    "icons:Rename.png",    self.OnClickActionRename)
        ActionDelete =    CreateAction("Delete",    "icons:Delete.png",    self.OnClickActionDelete)

        def CreateColorPickerAction(Name, Icon, Color, bIsNone = False):
            """ Create color picker actions. """
            NewColorPickerAction = QtWidgets.QAction(Name, self)
            NewColorPickerAction.setIcon(QtGui.QIcon(Icon))
            NewColorPickerAction.triggered.connect(lambda: self.AssignColor(Color, bIsNone))
            return NewColorPickerAction
        # Create color picker actions using previous function.
        ActionColorNone =   CreateColorPickerAction("None",    "icons:Color_None.png",    self.COLOR_NONE,      bIsNone = True)
        ActionColorPurple = CreateColorPickerAction("Purple",  "icons:Color_Purple.png",  self.COLOR_PURPLE                   )
        ActionColorBlue =   CreateColorPickerAction("Blue",    "icons:Color_Blue.png",    self.COLOR_BLUE                     )
        ActionColorGreen =  CreateColorPickerAction("Green",   "icons:Color_Green.png",   self.COLOR_GREEN                    )
        ActionColorYellow = CreateColorPickerAction("Yellow",  "icons:Color_Yellow.png",  self.COLOR_YELLOW                   )
        ActionColorOrange = CreateColorPickerAction("Orange",  "icons:Color_Orange.png",  self.COLOR_ORANGE                   )
        ActionColorRed =    CreateColorPickerAction("Red",     "icons:Color_Red.png",     self.COLOR_RED                      )
        ActionColorPink =   CreateColorPickerAction("Pink",    "icons:Color_Pink.png",    self.COLOR_PINK                     )

        # Create color reset action.
        ActionColorResetAll = QtWidgets.QAction("Reset All", self)
        ActionColorResetAll.triggered.connect(self.ResetAllColors)

        # Create group actions.
        ActionGroupCreate = QtWidgets.QAction("Create Group",self)
        ActionGroupCreate.triggered.connect(self.CreateNewGroup)
        ActionGroupCreate.setIcon((QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder)))
        ActionGroupSelected = QtWidgets.QAction("Group Selected",self)
        ActionGroupSelected.triggered.connect(self.CreateNewGroup)
        ActionGroupSelected.setIcon((QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder)))
        ActionGroupExpandAll = QtWidgets.QAction("Expand All",self)
        ActionGroupExpandAll.triggered.connect(self.ExpandAllItems)
        ActionGroupCollapseAll = QtWidgets.QAction("Collapse All",self)
        ActionGroupCollapseAll.triggered.connect(self.CollapseAllItems)

        # Show different context menu depending on if an item was selected or not.
        if not Item:
            Menu.addAction(ActionNew)
            Menu.addSeparator()
            Menu.addMenu(SubMenuColor)
            SubMenuColor.addAction(ActionColorResetAll)
            Menu.addSeparator()
            Menu.addAction(ActionGroupCreate)
            Menu.addAction(ActionGroupExpandAll)
            Menu.addAction(ActionGroupCollapseAll)
            # Execute.
            Menu.exec_(self.TakeList.viewport().mapToGlobal(Pos))
        else:
            Menu.addAction(ActionNew)
            Menu.addAction(ActionDuplicate)
            Menu.addAction(ActionRename)
            Menu.addAction(ActionDelete)
            Menu.addSeparator()
            Menu.addMenu(SubMenuColor)
            SubMenuColor.addAction(ActionColorNone)
            SubMenuColor.addAction(ActionColorPurple)
            SubMenuColor.addAction(ActionColorBlue)
            SubMenuColor.addAction(ActionColorGreen)
            SubMenuColor.addAction(ActionColorYellow)
            SubMenuColor.addAction(ActionColorOrange)
            SubMenuColor.addAction(ActionColorRed)
            SubMenuColor.addAction(ActionColorPink)
            SubMenuColor.addSeparator()
            SubMenuColor.addAction(ActionColorResetAll)
            Menu.addSeparator()
            Menu.addAction(ActionGroupSelected)
            Menu.addAction(ActionGroupExpandAll)
            Menu.addAction(ActionGroupCollapseAll)
            # Execute.
            Menu.exec_(self.TakeList.viewport().mapToGlobal(Pos))



    # ----------------- GET LIST ITEMS ----------------- #



    def GetAllListItems(self) -> list[TakeTreeItem]:
        """ Get all items in take list. """
        ListOfAllItems = []
        for TopLevelItem in self.GetAllListTopLevelItems():
            ListOfAllItems.append(TopLevelItem) 
            ListOfAllItems.extend(self.GetChildItems(TopLevelItem, bRecursively = True))
        return ListOfAllItems


    def GetAllListTopLevelItems(self):
        """ Get all top level items in take list. """
        NumberOfItems = self.TakeList.topLevelItemCount()
        ListOfTopLevelItems = []
        for Index in range(NumberOfItems):
            Item = self.TakeList.topLevelItem(Index)
            ListOfTopLevelItems.append(Item)
        return ListOfTopLevelItems


    def GetParent(self, Item: TakeTreeItem):
        """ Get parent of item. If item has no parent, return root of the list. """
        if Item.parent():
            return Item.parent()     
        else:
            return self.TakeList.invisibleRootItem()


    def GetChildItems(self, ParentItem: TakeTreeItem, bRecursively = False) -> list[TakeTreeItem]:
        """ Find all children in an item. """
        ListOfChildItems = []
        for ChildIndex in range(ParentItem.childCount()):
            ChildItem = ParentItem.child(ChildIndex)
            ListOfChildItems.append(ChildItem)
            if bRecursively:
                ListOfChildItems.extend(self.GetChildItems(ChildItem, bRecursively = True))
        return ListOfChildItems


    def GetSelectedItems(self) -> list[TakeTreeItem]:
        """ Get selected items in list. """
        return self.TakeList.selectedItems()


    def GetItemByTake(self, Take: FBTake):
        """ Find item that matches take. """
        for Item in self.GetAllListItems():
            if Item.Take == Take:
                return Item
        return None



    # ----------------- NAME VALIDATION ----------------- #



    def CancelRenameEditMode(self):
        """ Cancel any items that are currently in rename edit mode. """
        self.TakeList.setDisabled(True)
        self.TakeList.setDisabled(False)


    def ValidateTakeNames(self):
        """ Check if name of existing takes don't have too long name. """
        # Define all list items.
        AllListItems = self.GetAllListItems()
        # Create a list that will contain warnings.
        Warnings = []
        # Go through all items and check if their names are valid.
        for Item in AllListItems:
            TakeName: str = Item.text(0)
            # Take names that starts with these characters will always be valid.
            if TakeName.startswith(("=", "-")):
                continue     
            # Report warning if full name is longer than max limit.
            bIsLengthValid = len(TakeName) <= MAX_PACKAGE_LENGTH
            if not bIsLengthValid:
                Warnings.append(f"{TakeName} - Name is too long!")
            # Report warning if take name contains any invalid characters.
            if not re.match(r"^[A-Za-z0-9_#=\s]*$", TakeName):
                Warnings.append(f"{TakeName} - Contains invalid characters!")
        # Customize warning label depending on if there are any warnings or not.
        if not Warnings:
            self.LabelWarnings.setText("No warnings detected.")
            self.LabelWarnings.setStyleSheet("QLabel { color : rgb(125,125,125) }")
            self.LabelWarnings.setToolTip("Warnings regarding takes will be shown here")
        else:
            SingularOrPluralWarning = "warning"
            if len(Warnings) > 1:
                SingularOrPluralWarning = "warnings"            
            self.LabelWarnings.setText(f"{len(Warnings)} {SingularOrPluralWarning} detected. Hover for more info.")
            self.LabelWarnings.setStyleSheet("QLabel { color : rgb(255,0,0) }")
            WarningTooltip = "\n".join(Warnings)
            self.LabelWarnings.setToolTip(WarningTooltip)    



    # ----------------- SYNC TAKE ORDER NATIVELY ----------------- #



    def SyncTakeOrderNatively(self):
        """ Sync take order natively to match our own list. """
        AllListItems = self.GetAllListItems()
        if len(AllListItems) != len(System.Scene.Takes):
            return
        SortedTakeList: list[FBTake] = []
        for Item in AllListItems:
            SortedTakeList.append(Item.Take)
            Item.setExpanded(Item.GetItemExpanded())
        self.bIsMovingTakesFromTool = True
        ApplyTakeOrder(SortedTakeList)



    # ----------------- NEW / DUPLICATE TAKE EVENTS ----------------- #



    def AddNewItemsToList(self, Item: TakeTreeItem):
        """ Add new items to list not caring about if it's new, duplicate or group. """
        if self.bIsMovingTakesFromTool:
            self.TakeList.addTopLevelItem(Item)


    def OnClickActionNew(self):
        """ Create new empty take from current active take. """
        self.bIsMovingTakesFromTool = True
        self.bPreventSelectionUpdate = True
        # Stops an item from still being in edit rename mode if a new take is created.
        self.CancelRenameEditMode()
        # Create new take.
        NewTake = FBTake(None)
        System.Scene.Takes.append(NewTake)
        # Set current active take.
        System.CurrentTake = NewTake
        # Deselect all items.
        self.TakeList.selectionModel().clearSelection()
        # Find matching item of take.
        Item: TakeTreeItem = self.GetItemByTake(NewTake)
        # Check if item exists.
        if Item is not None:
            # Deselect all models in scene as some native shortcuts may interfere when there is a selection, such as S or Shift+S keys.
            DeselectAllModels()
            # Select newly created item and start renaming it.
            Item.setSelected(True)
            self.TakeList.editItem(Item)
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bIsMovingTakesFromTool = False
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()


    def OnClickActionDuplicate(self):
        """ Duplicate takes from selection. """
        self.bIsMovingTakesFromTool = True
        self.bPreventSelectionUpdate = True
        self.bIsDuplicatingItems = True
        # Define selected items.
        SelectedItems = self.GetSelectedItems()
        # Do nothing if no items are selected.
        if not SelectedItems:
            return
        # Stops an item from still being in edit rename mode if a new take is created.
        self.CancelRenameEditMode()
        # Duplicate selected items.
        for Item in SelectedItems:
            DuplicatedTake = Item.Take.CopyTake(Item.Take.Name)
            # Deselect item once it has duplicated.
            Item.setSelected(False)
            # Find duplicated item and select it.
            DuplicatedItem = self.GetItemByTake(DuplicatedTake)
            # Check if duplicated item exists.
            if DuplicatedItem is not None:
                # Move duplicated item to the same parent as the original item.
                ParentTake = Item.GetParentTake()
                if ParentTake:
                    ParentItem = self.GetItemByTake(ParentTake)
                    if ParentItem:
                        self.SetItemRelationship(ParentItem, DuplicatedItem)
                # Select duplicated item.
                DuplicatedItem.setSelected(True)
        self.bIsDuplicatingItems = False
        # Sync take order natively to match our own list.
        self.SyncTakeOrderNatively()
        # Start renaming if only 1 item was duplicated.
        if len(SelectedItems) == 1:
            # Deselect all models in scene as some native shortcuts may interfere when there is a selection, such as S or Shift+S keys.
            DeselectAllModels()
            # Start renaming duplicated item.
            self.TakeList.editItem(DuplicatedItem)
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bIsMovingTakesFromTool = False
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()



    # ----------------- RENAME TAKE EVENTS ----------------- #



    def OnClickActionRename(self):
        """ Start rename edit mode from shortcut. """
        # Define selected items.
        SelectedItems = self.GetSelectedItems()
        # Do nothing of no items are selected.
        if not SelectedItems:
            return
        # Deselect all models in scene as some native shortcuts may interfere when there is a selection, such as S or Shift+S keys.
        DeselectAllModels()
        # Start renaming on last selected item.
        Item = SelectedItems[-1]
        self.TakeList.editItem(Item)
            

    def OnItemDataChanged(self, ModelIndex1: QtCore.QModelIndex, ModelIndex2: QtCore.QModelIndex, Roles: list[int]):
        """ Confirm rename takes from selection. """
        # Prevent dataChanged from activating this function if the item was renamed from MotionBuilder natively.
        if self.bIsUpdatingNatively:
            return
        # Only continue if item was renamed.
        if QtCore.Qt.DisplayRole not in Roles:
            return
        self.bIsRenamingTakes = True
        # Define selected items.
        SelectedItems = self.GetSelectedItems()
        # Rename all selected items to newly inputed name.
        RenamedItem: TakeTreeItem = self.TakeList.itemFromIndex(ModelIndex1)
        for Item in SelectedItems:
            Item.Take.Name = RenamedItem.text(0)
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bIsRenamingTakes = False

    
    def RenameTakeOnListOnly(self, Item: TakeTreeItem):
        """ Confirm rename take on list only if rename was executed natively. """
        Item.setText(0, Item.Take.Name)
        if not self.bIsRenamingTakes:
            # Check if take name is valid.
            self.ValidateTakeNames()



    # ----------------- DELETE TAKE EVENTS ----------------- #



    def OnClickActionDelete(self):
        """ Show delete takes popup. """
        self.bIsMovingTakesFromTool = True
        # Define selected items.
        SelectedItems = self.GetSelectedItems()
        # Do nothing if no items are selected.
        if not SelectedItems:
            return
        # Go through every selected takes and check if they have children.
        bHasChildren = False
        for Item in SelectedItems:
            NumberOfChildren = Item.childCount()
            if NumberOfChildren > 0:
                bHasChildren = True
                break
        # Show different popup depending on if selected takes have children or not.
        if bHasChildren:
            # (Call class) Create delete window popup and customize it.
            NewWindow = WindowCreator.BasicThreeButtonPopup(self,
                Title = "Delete Selected Takes",
                WindowWidth = 550,
                WindowHeight = 120,
                Label = """WARNING: You cannot undo this operation!""",
                AllButtonWidth = 170,
                AllButtonHeight = 30,
                Button1Name = "Delete selected",
                Button1Style = """QPushButton { 
                                                background-color : rgb(140,50,50);
                                                font-weight: bold;
                                                }""",
                Button2Name = "Delete selected + children",
                Button2Style = """QPushButton { 
                                                background-color : rgb(110,30,30);
                                                font-weight: bold;
                                                }""",
                Button3Name = "Cancel",                              
            )
            # Confirm deletion of parent + child.
            if NewWindow.ButtonClickedValue == 1:
                for Item in SelectedItems:
                    self.DeleteTakeItems(Item, bDeleteChildren = False)
            # Confirm deletion of only parent.
            if NewWindow.ButtonClickedValue == 2:
                for Item in SelectedItems:
                    self.DeleteTakeItems(Item, bDeleteChildren = True)
        else:
            # (Call class) Create delete window popup and customize it.
            NewWindow = WindowCreator.BasicTwoButtonPopup(self,
                Title = "Delete Selected Takes",
                WindowWidth = 240,
                WindowHeight = 90,
                Label = "WARNING: You cannot undo this operation!",
                Button1Name = "Delete",
                Button1Style = """QPushButton { 
                                                background-color : rgb(140,50,50);
                                                font-weight: bold;
                                                }""",
            )
            # Confirm deletion.
            if NewWindow.ButtonClickedValue == 1:
                for Item in SelectedItems:
                    self.DeleteTakeItems(Item, bDeleteChildren = False)
        self.bIsMovingTakesFromTool = False


    def DeleteTakeItems(self, Item: TakeTreeItem, bDeleteChildren, bUpdateGuiOnly = False):
        """ Confirm delete takes from selection. """
        self.bPreventSelectionUpdate = True
        # Delete children or reparent them to their parent's parent.
        for Child in self.GetChildItems(Item):
            if bDeleteChildren:
                # Delete children.
                self.DeleteTakeItems(Child, bDeleteChildren = True)
            else:
                # Take away children from old parent. 
                Item.takeChild(Item.indexOfChild(Child))
                # Add children to new parent.
                self.GetParent(Item).addChild(Child)
        # Check if deletion was executed from this tool or natively.
        if not bUpdateGuiOnly:
            Item.DeleteTake()
        else:
            # Delete new parent's child which is old parent.
            self.GetParent(Item).removeChild(Item)
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bPreventSelectionUpdate = False



    # ----------------- MOVE TAKE EVENTS ----------------- #



    def MoveTakeItems(self, ParentModelIndex: QtCore.QModelIndex, FirstIndex: int, LastIndex: int):
        """ Move and group items in list. """
        if self.bIsUpdatingNatively or self.bIsDuplicatingItems:
            return
        self.bPreventSelectionUpdate = True
        # Grouping.
        Parent: TakeTreeItem = self.TakeList.itemFromIndex(ParentModelIndex)
        for Index in range(FirstIndex, LastIndex + 1):
            if Parent is None:
                Item: TakeTreeItem = self.TakeList.invisibleRootItem().child(Index)
                Item.RemoveParentProperty()
            else:
                Item: TakeTreeItem = Parent.child(Index)
                Item.SetParentProperty(Parent)
                Parent.setExpanded(True)
            Item.setSelected(True)
        # Sync take order natively to match our own list.
        self.SyncTakeOrderNatively()
        self.bIsMovingTakesFromTool = False
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()

        

    # ----------------- GROUP MANAGEMENT ----------------- #
          


    def CreateNewGroup(self):
        """ Create new empty take group with predefined settings. """
        self.bIsMovingTakesFromTool = True
        self.bPreventSelectionUpdate = True
        # Stops an item from still being in edit rename mode if a new take is created.
        self.CancelRenameEditMode()
        # Create new empty take.
        DefaultGroupName = "===== " + "GROUP" + " ====="
        NewTakeGroup = FBTake(DefaultGroupName)
        # Set newly created take to be 1 frame long.
        NewTakeGroup.LocalTimeSpan = FBTimeSpan(FBTime.Zero, FBTime(0, 0, 0, 1, 0))
        # Append take to scene.
        System.Scene.Takes.append(NewTakeGroup)
        # Set current active take to be the new group.
        System.CurrentTake = NewTakeGroup
        # Define item group.
        NewItemGroup: TakeTreeItem = self.GetItemByTake(NewTakeGroup)
        # If any items were selected when creating the group, parent them inside the group.
        SelectedItems = self.GetSelectedItems()
        if SelectedItems:
            # Check if selected items have same parent.
            CommonParent = None
            for Item in SelectedItems:
                NewParent = self.GetParent(Item)
                if CommonParent and NewParent != CommonParent:
                    CommonParent = None
                    break
                CommonParent = NewParent
            # Place selected items inside newly created group.
            for Item in SelectedItems:
                self.SetItemRelationship(NewItemGroup, Item)
            # If selected items had same parent before, then the new group should be placed under said parent. If not, then the group should be placed under root.
            if CommonParent:
                self.SetItemRelationship(CommonParent, NewItemGroup)
            # Set group to be expanded on creation. 
            NewItemGroup.setExpanded(True)
        # Deselect all items.
        self.TakeList.selectionModel().clearSelection()
        # Deselect all models in scene as some native shortcuts may interfere when there is a selection, such as S or Shift+S keys.
        DeselectAllModels()
        # Select newly created group and start renaming it.
        NewItemGroup.setSelected(True)
        self.TakeList.editItem(NewItemGroup)
        # Check if take name is valid.
        self.ValidateTakeNames()
        self.bIsMovingTakesFromTool = False
        self.bPreventSelectionUpdate = False


    def SetItemRelationship(self, Parent: TakeTreeItem, Child: TakeTreeItem):
        """ Remove child from current parent and give it to a new parent of choice. """
        if Parent == Child:
            raise RuntimeError("Parent and Child are the same!")
        CurrentParent = self.GetParent(Child)
        CurrentParent.takeChild(CurrentParent.indexOfChild(Child))
        Parent.addChild(Child)

        if Parent == self.TakeList.invisibleRootItem():
            Child.RemoveParentProperty()      
        else:
            Child.SetParentProperty(Parent)



    # ----------------- EXPAND AND COLLAPSE ----------------- #



    def ExpandAllItems(self):
        """ Expand all groups / parents. """
        AllItems = self.GetAllListItems()
        for Item in AllItems:
            NumberOfChildren = Item.childCount()
            if NumberOfChildren > 0:
                self.TakeList.expandItem(Item)


    def ExpandAllChildrenOfSelectedItem(self, Item: TakeTreeItem):
        """ Expand all selected items if shift key + left click are pressed on group icon. """
        # Find and expand all children recursively of selected item.
        for Child in self.GetChildItems(Item, bRecursively = True):
            NumberOfChildren = Child.childCount()
            if NumberOfChildren > 0:
                self.TakeList.expandItem(Child)


    def OnExpand(self, Item: TakeTreeItem):
        """ Expand selected items. """
        # Expand all children if shift is pressed when left clicking.
        Modifiers = QtWidgets.QApplication.keyboardModifiers()
        if Modifiers == QtCore.Qt.ShiftModifier:
            # Find item that the cursor is at.
            self.ExpandAllChildrenOfSelectedItem(Item)
        Item.SetItemExpanded(bIsExpanded = True)


    def CollapseAllItems(self):
        """ Collapse all groups / parents. """
        AllItems = self.GetAllListItems()
        for Item in AllItems:
            NumberOfChildren = Item.childCount()
            if NumberOfChildren > 0:
                self.TakeList.collapseItem(Item)


    def CollapseAllChildrenOfSelectedItem(self, Item: TakeTreeItem):
        """ Collapse all selected items if shift key + left click are pressed on group icon. """
        # Find and expand all children recursively of selected item.
        for Child in self.GetChildItems(Item, bRecursively = True):
            NumberOfChildren = Child.childCount()
            if NumberOfChildren > 0:
                self.TakeList.collapseItem(Child)


    def OnCollapse(self, Item: TakeTreeItem):
        """ Collapse selected items. """
        self.bPreventSelectionUpdate = True
        # Deselect all children of selected item when collapsing.
        for Child in self.GetChildItems(Item, bRecursively = True):
            if Child.isSelected():
                Child.setSelected(False)
        # Collapse all children if shift is pressed when left clicking.
        Modifiers = QtWidgets.QApplication.keyboardModifiers()
        if Modifiers == QtCore.Qt.ShiftModifier:
            # Find item that the cursor is at.
            self.CollapseAllChildrenOfSelectedItem(Item)
        Item.SetItemExpanded(bIsExpanded = False)
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()



    # ----------------- SELECT AND DESELECT ----------------- #



    def ToggleSelectOrDeselectAll(self):
        """ Toggle select / deselect all items in list. """
        AllItems = self.GetAllListItems()
        bItemIsSelected = True
        self.bPreventSelectionUpdate = True
        # Check if any items are not selected in list.
        for Item in AllItems:
            if not Item.isSelected():
                bItemIsSelected = False
                break
        # Toggle all items selected / deselected
        for Item in AllItems:
            if bItemIsSelected:
                Item.setSelected(False)
            else:
                Item.setSelected(True)
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()


    def Deselect(self):
        """ Deselect all selected items. """
        SelectedItems = self.GetSelectedItems()
        self.bPreventSelectionUpdate = True
        for Item in SelectedItems:
            Item.setSelected(False)
        self.bPreventSelectionUpdate = False
        self.MakeMoBuSelection()



    # ----------------- SET CURRENT TAKE ----------------- #



    def DeselectAllTakes(self):
        """ Deselect all items in the list. """
        AllItems = self.GetAllListItems()
        for Item in AllItems:
            Item.DeselectActiveTake()


    def SetCurrentTake(self, DoubleClickedItem: TakeTreeItem, ColumnIndex: int):
        """ Set current active take. """
        self.bIsSettingActiveTakeFromTool = True
        # Clear background color and font on current active item.
        CurrentActiveItem: TakeTreeItem = self.GetItemByTake(System.CurrentTake)
        CurrentActiveItem.DeselectActiveTake()
        # (Call function) Set background color and font on current take.
        DoubleClickedItem.SelectActiveTake(bUpdateGuiOnly = False)
        self.bIsSettingActiveTakeFromTool = False


    def SetCurrentTakeListOnly(self):
        """ Set current active take list only. """
        # Clear background color and font on all items.
        self.DeselectAllTakes()
        # (Call function) Set background color and font on current take.
        ActiveItem = self.GetItemByTake(System.CurrentTake)
        ActiveItem.SelectActiveTake(bUpdateGuiOnly = True)   



    # ----------------- SELECTING ----------------- #



    def MakeMoBuSelection(self):
        """ Select takes natively also when selecting takes in tool. """
        if self.bIsUpdatingNatively or self.bPreventSelectionUpdate:
            return
        self.bIsSelectingTakesFromTool = True
        # Deselect everything except models in scene.
        for Object in GetMoBuSelection():
            if not isinstance(Object, FBModel):
                Object.Selected = False

        SelectedItems = self.GetSelectedItems()
        # Select takes natively.
        for Item in SelectedItems:
            if IsBound(Item.Take):
                Item.Take.Selected = True 
        self.bIsSelectingTakesFromTool = False



    # ----------------- COLOR PICKER EVENTS ----------------- #



    def AssignColor(self, Color, bAssignedNone = False):
        """ Assign selected takes with a color. """
        # Define selected items.
        SelectedItems = self.GetSelectedItems()
        # Do nothing if no items are selected.
        if not SelectedItems:
            return
        # (Call function) Set color on selected items. If color [none] is selected, reset color instead.
        if not bAssignedNone:
            for Item in SelectedItems:
                Item.SetColor(Color)
        else:
            for Item in SelectedItems:
                Item.ResetColor()
        # Deselect all items.
        self.TakeList.selectionModel().clearSelection()


    def ResetAllColors(self):
        """ Resets all takes to default color. """
        # (Call class) Create reset color window popup and customize it.
        NewWindow = WindowCreator.BasicTwoButtonPopup(self,
            Title = "Reset All",
            WindowWidth = 240,
            WindowHeight = 90,
            Label = "Reset all takes to default color?",
            Button1Name = "Reset",
            Button1ToolTip = "Shortcut: Enter",
            Button1Style = """QPushButton { 
                                            background-color : rgb(60,70,80);
                                            font-weight: bold;
                                            }""",
        )
        # Confirm reset.
        if NewWindow.ButtonClickedValue == 1:
            ListOfItems = self.GetAllListItems()
            for Item in ListOfItems:
                Item.ResetColor()
            # Deselect all items.
            self.TakeList.selectionModel().clearSelection()



    # ----------------- HOVERING & RESIZE ----------------- #



    def HoveringTakeList(self, bHovering: bool, Event: QtCore.QEvent):
        """ Enable shortcuts when mouse is hovering over tool. Disable when not hovering. """
        self.ShortcutRefresh.setEnabled(bHovering)
        self.ShortcutNew.setEnabled(bHovering)
        self.ShortcutDuplicate.setEnabled(bHovering)
        self.ShortcutRename.setEnabled(bHovering)
        self.ShortcutDelete.setEnabled(bHovering)
        self.ShortcutGroup.setEnabled(bHovering)
        self.ShortcutSelectAll.setEnabled(bHovering)
        self.ShortcutDeselect.setEnabled(bHovering)


    def OnResize(self, Event):
        """ Fix horizontal scroll bar when resizing the window. """
        # Get width of tree widget, specifically the viewport as it takes into account of the vertical scrollbar visibility. 
        Width = self.TakeList.viewport().width()
        # Because the horizontal scroll bar checks the header width, the header width has to match the window width.
        self.TakeList.header().setMinimumSectionSize(Width)
        self.TakeList.header().setDefaultSectionSize(Width * 2)
   


    # ----------------- HELP POPUP ----------------- #



    def HelpPopup(self):
        """ Show help window popup. """
        # (Call class) Create help window popup and customize it.
        NewWindow = WindowCreator.BasicOneButtonPopup(self,
            Title = "Help",
            WindowWidth = 430,
            WindowHeight = 430,
            Label = """
                    <html><head/><body>
                    <p style="line-height:1.3"><span>

                    <font color=\"Orange\"><b>General Controls:</b></font><br>
                    * (Left-Click) Make selection (shift / ctrl for multiple selection)<br>
                    * (Double Left-Click) Set active take<br>
                    * (Right-Click) Show context menu<br>
                    <br>
                    <font color=\"Orange\"><b>Organizing Takes:</b></font><br>
                    * Drag-and-drop selected takes in between takes to move them<br>
                    * Drag-and-drop selected takes inside another take to make parent<br>
                    * Drag-and-drop selected takes outside to remove from parent<br>
                    * Customize selected takes with a color which can be found in context menu<br>
                    <br>
                    <font color=\"Orange\"><b>Shortcuts:</b></font> <i>(Tool has to be in focus!)</i><br>
                    * (Ctrl + N) Create <b>new</b> empty take from current active take<br>
                    * (Ctrl + D) <b>Duplicate</b> takes from selection<br>
                    * (F2) <b>Rename</b> takes from selection<br>
                    * (Del) <b>Delete</b> takes from selection<br>
                    * (Ctrl + G) Create <b>group</b><br>
                    * (Shift + Left-Click on group icon) Expand / Collapse all children in selected parent<br>
                    * (Ctrl + A) Select / Deselect all<br>
                    * (D) Deselect
                    
                    </span></p>
                    </body></html>""",
            LabelAlignment = QtCore.Qt.AlignLeft,
            ButtonName = "Close",
            ButtonExtraShortcuts = "",
            ButtonToolTip = "",
            ButtonStyle = """QPushButton { background-color : rgb(100,100,100); }""",
        )



# ----------------- FBTOOL WIDGET ----------------- #



class NativeToolContainer(FBTool):
    def __init__(self, UIClass, WindowName, Data = None, StartSize = None):
        super(NativeToolContainer, self).__init__(WindowName)
        self.UIClass = UIClass
        self.QtToolWidget = None

        ToolWidgetHolder = NativeWidgetHolder(self, Data)
        PositionX = FBAddRegionParam(0, FBAttachType.kFBAttachLeft,   "")
        PositionY = FBAddRegionParam(0, FBAttachType.kFBAttachTop,    "")
        Width =     FBAddRegionParam(0, FBAttachType.kFBAttachRight,  "")
        Height =    FBAddRegionParam(0, FBAttachType.kFBAttachBottom, "")
        self.AddRegion("main", "main", PositionX, PositionY, Width, Height)
        self.SetControl("main", ToolWidgetHolder)
        
        if StartSize:
            self.StartSizeX = int(StartSize[0])
            self.StartSizeY = int(StartSize[1])
        
        FBAddTool(self)
        ShowTool(self)
        
    def GetPtrs(self):
        return self, self.QtToolWidget

    def SetSize(self, Size, bFixedWidth = False, bFixedHeight = False):
        self.MinSizeX = int(Size[0])
        self.MinSizeY = int(Size[1])

        if bFixedWidth:
            self.MaxSizeX = self.MinSizeX
        if bFixedHeight:
            self.MaxSizeY = self.MinSizeY


class NativeWidgetHolder(FBWidgetHolder):
    def __init__(self, Instigator, Data = None):
        super(NativeWidgetHolder, self).__init__()
        self.Instigator = Instigator
        self.Data = Data
            
    def WidgetCreate(self, WidgetParentPtr):
        WidgetParent = shiboken.wrapInstance(WidgetParentPtr, QtWidgets.QWidget).parentWidget()  # type: ignore
        self.Instigator.QtToolWidget = self.Instigator.UIClass(WidgetParent)
        return shiboken.getCppPointer(self.Instigator.QtToolWidget)[0]  # type: ignore



# ----------------- EXECUTE SCRIPT ----------------- #



def main():
    """ Create Take Manager tool. """
    # Check if tool already exists. Remove it from toollist to prevent duplicate windows.
    if TOOL_NAME in FBToolList:
        FBDestroyToolByName(TOOL_NAME)
    # Create FBTool widget.
    Window = NativeToolContainer(MainWidget, TOOL_NAME, StartSize = (400,500))
    Window.MinSizeX = 100
    Window.MinSizeY = 100

# Execute script.
if __name__ == '__builtin__' or __name__ == 'builtins':
    main()