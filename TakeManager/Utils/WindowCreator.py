# pylint: disable-all


# Python [Utils Script] for MotionBuilder.
# This script is used to help create various window popups.


from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QShortcut
from PySide2.QtGui import QKeySequence


if "builtin" in __name__:
    import FixFrozenViewport as UnFreeze
else:
    from . import FixFrozenViewport as UnFreeze
# Reload this script if the imported script has been edited.
from importlib import reload
reload(UnFreeze)






# CONTENT:
# BasicOneButtonPopup
# BasicTwoButtonPopup
# BasicThreeButtonPopup






# -------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- BASIC ONE BUTTON POPUP ------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------- #






# ----------------- WINDOW CREATION ----------------- #



class BasicOneButtonPopup(QtWidgets.QDialog): 
    def __init__(self, Parent = None, 
                                    Title = "[JC] Insert Title", 
                                    WindowWidth = 250,
                                    WindowHeight = 100,
                                    Label = "Insert Text.",
                                    LabelAlignment = QtCore.Qt.AlignCenter,
                                    ButtonName = "Close", 
                                    ButtonExtraShortcuts = "",
                                    ButtonToolTip = "Shortcut: Enter",
                                    ButtonStyle = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",                                   
                                    ): 
        super().__init__(Parent)


        # Default value on startup.
        self.ButtonClickedValue = None



        # ----------------- MAIN WINDOW SETTINGS ----------------- #



        # Main window.
        self.setWindowTitle(Title)
        self.setFixedWidth(WindowWidth)
        self.setFixedHeight(WindowHeight)
        # Remove maximize, minimize and help buttons.
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Set if user can click outside the window.
        self.setModal(True)
        # Restore default arrow cursor on initialize to prevent loading cursor bug.
        QtWidgets.QApplication.restoreOverrideCursor()



        # ----------------- TEXT LABEL SETTINGS ----------------- #



        # Text label.
        self.Label = QtWidgets.QLabel(self)
        self.Label.setText(Label)
        self.Label.setAlignment(LabelAlignment)
        


        # ----------------- BUTTON SETTINGS ----------------- #



        # Button.
        self.Button = QtWidgets.QPushButton(ButtonName, self)
        self.Button.setFixedWidth(230)
        self.Button.setFixedHeight(30)
        self.Button.setDefault(True)
        self.ButtonShortcut = QShortcut(QKeySequence(ButtonExtraShortcuts), self)
        self.Button.setToolTip(ButtonToolTip)
        self.Button.setStyleSheet(ButtonStyle)
        self.Button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 1 in your own script.
        self.ButtonShortcut.activated.connect(self.OnClickButton)
        self.Button.clicked.connect(self.OnClickButton)

        

        # ----------------- LAYOUT CUSTOMIZATION ----------------- #



        # Create layout.
        self.LayoutMainWindow = QtWidgets.QVBoxLayout(self)
        # Create sub layouts.
        self.LayoutLabel = QtWidgets.QHBoxLayout(self)
        self.LayoutButton = QtWidgets.QHBoxLayout(self)

        # Add widgets (buttons, labels, etc.) to sub layouts.
        self.LayoutLabel.addWidget(self.Label)
        self.LayoutButton.addWidget(self.Button)

        # Set main layout.
        self.setLayout(self.LayoutMainWindow)
        # Set sub layouts to main layout.
        self.LayoutMainWindow.addLayout(self.LayoutLabel)
        self.LayoutMainWindow.addLayout(self.LayoutButton)



        # ----------------- STARTUP CALL EVENTS ----------------- #



        # (Call function) Fix issues with center window to desktop screen.
        #self.CenterWindowToScreenFix()
        # (Call function) Center window to desktop screen.
        #self.CenterWindowToScreen()

        # (Call function) Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. 
        self.CustomLayoutSetup()
        # (Call function) Execute script.
        self.ExecuteScript()
       


    # ----------------- BUTTON EVENTS ----------------- #



    # (Function) Execute button in your own script.
    def OnClickButton(self):
        """ Execute button in your own script. """
        self.ButtonClickedValue = 1
        self.close()



    # ----------------- CENTER WINDOW EVENTS ----------------- #



    def CenterWindowToScreenFix(self):
        """ Executing this before [CenterWindowToScreen] will fix center issues. Execute this only on initialize. """
        self.hide()
        self.show()
        

    def CenterWindowToScreen(self):
        """ Center window position to screen. """
        FrameGeo = self.frameGeometry()
        CenterPosition = QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen()).center()
        FrameGeo.moveCenter(CenterPosition)
        self.move(FrameGeo.topLeft())



    # ----------------- EXECUTE SCRIPT ----------------- #



    def CustomLayoutSetup(self):
        """ Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. """
        pass


    def ExecuteScript(self):
        """ Execute and create window popup. Then unfreeze viewport. """
        self.exec_()
        UnFreeze.UnFreezeViewport()
        self.destroy(True)






# -------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- BASIC TWO BUTTON POPUP ------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------------- #






# ----------------- WINDOW CREATION ----------------- #



class BasicTwoButtonPopup(QtWidgets.QDialog): 
    def __init__(self, Parent = None, 
                                    Title = "[JC] Insert Title", 
                                    WindowWidth = 250,
                                    WindowHeight = 100,
                                    Label = "Insert Text.",
                                    Button1Name = "Yes", 
                                    Button1ExtraShortcuts = "",
                                    Button1ToolTip = "Shortcut: Enter",
                                    Button1Style = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",
                                    Button2Name = "Cancel",
                                    Button2ExtraShortcuts = "",
                                    Button2ToolTip = "Shortcut: Esc",
                                    Button2Style = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",
                                    ): 
        super().__init__(Parent)


        # Default value on startup.
        self.ButtonClickedValue = None



        # ----------------- MAIN WINDOW SETTINGS ----------------- #



        # Main window.
        self.setWindowTitle(Title)
        self.setFixedWidth(WindowWidth)
        self.setFixedHeight(WindowHeight)
        # Remove maximize, minimize and help buttons.
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Set if user can click outside the window.
        self.setModal(True)
        # Restore default arrow cursor on initialize to prevent loading cursor bug.
        QtWidgets.QApplication.restoreOverrideCursor()



        # ----------------- TEXT LABEL SETTINGS ----------------- #



        # Text label.
        self.Label = QtWidgets.QLabel(self)
        self.Label.setText(Label)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        


        # ----------------- BUTTON SETTINGS ----------------- #



        # Button 1.
        self.Button1 = QtWidgets.QPushButton(Button1Name, self)
        self.Button1.setFixedWidth(90)
        self.Button1.setFixedHeight(30)
        self.Button1.setDefault(True)
        self.Button1Shortcut = QShortcut(QKeySequence(Button1ExtraShortcuts), self)
        self.Button1.setToolTip(Button1ToolTip)
        self.Button1.setStyleSheet(Button1Style)
        self.Button1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 1 in your own script.
        self.Button1Shortcut.activated.connect(self.OnClickButton1)
        self.Button1.clicked.connect(self.OnClickButton1)

        # Button 2.
        self.Button2 = QtWidgets.QPushButton(Button2Name, self)
        self.Button2.setFixedWidth(90)
        self.Button2.setFixedHeight(30)
        self.Button2.setDefault(False)
        self.Button2Shortcut = QShortcut(QKeySequence(Button2ExtraShortcuts), self)
        self.Button2.setToolTip(Button2ToolTip)
        self.Button2.setStyleSheet(Button2Style)
        self.Button2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 2 in your own script.
        self.Button2Shortcut.activated.connect(self.OnClickButton2)
        self.Button2.clicked.connect(self.OnClickButton2)



        # ----------------- LAYOUT CUSTOMIZATION ----------------- #



        # Create layout.
        self.LayoutMainWindow = QtWidgets.QVBoxLayout(self)
        # Create sub layouts.
        self.CustomLayout = QtWidgets.QVBoxLayout(self)
        self.LayoutLabel = QtWidgets.QHBoxLayout(self)
        self.LayoutButtons = QtWidgets.QHBoxLayout(self)

        # Add widgets (buttons, labels, etc.) to sub layouts.
        self.LayoutLabel.addWidget(self.Label)
        self.LayoutButtons.addWidget(self.Button1)
        self.LayoutButtons.addWidget(self.Button2)

        # Set main layout.
        self.setLayout(self.LayoutMainWindow)
        # Set sub layouts to main layout.
        self.LayoutMainWindow.addLayout(self.CustomLayout)
        self.LayoutMainWindow.addLayout(self.LayoutLabel)
        self.LayoutMainWindow.addLayout(self.LayoutButtons)



        # ----------------- STARTUP CALL EVENTS ----------------- #



        # # (Call function) Fix issues with center window to desktop screen.
        # self.CenterWindowToScreenFix()
        # # (Call function) Center window to desktop screen.
        # self.CenterWindowToScreen()

        # (Call function) Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. 
        self.CustomLayoutSetup()
        # (Call function) Execute script.
        self.ExecuteScript()

       

    # ----------------- BUTTON EVENTS ----------------- #



    def OnClickButton1(self):
        """ Execute button 1 in your own script. """
        self.ButtonClickedValue = 1
        self.close()


    def OnClickButton2(self):
        """ Execute button 2 in your own script. """
        self.ButtonClickedValue = 2
        self.close()



    # ----------------- CENTER WINDOW EVENTS ----------------- #



    def CenterWindowToScreenFix(self):
        """ Executing this before [CenterWindowToScreen] will fix center issues. Execute this only on initialize. """
        self.hide()
        self.show()
        

    def CenterWindowToScreen(self):
        """ Center window position to screen. """
        FrameGeo = self.frameGeometry()
        CenterPosition = QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen()).center()
        FrameGeo.moveCenter(CenterPosition)
        self.move(FrameGeo.topLeft())



    # ----------------- EXECUTE SCRIPT ----------------- #



    def CustomLayoutSetup(self):
        """ Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. """
        pass


    def ExecuteScript(self):
        """ Execute and create window popup. Then unfreeze viewport. """
        self.exec_()
        UnFreeze.UnFreezeViewport()
        self.destroy(True)






# ---------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------- BASIC THREE BUTTON POPUP ------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------- #






# ----------------- WINDOW CREATION ----------------- #



class BasicThreeButtonPopup(QtWidgets.QDialog): 
    def __init__(self, Parent = None, 
                                    Title = "[JC] Insert Title", 
                                    WindowWidth = 350,
                                    WindowHeight = 100,
                                    Label = "Insert Text.",
                                    AllButtonWidth = 90,
                                    AllButtonHeight = 30,
                                    Button1Name = "Yes", 
                                    Button1ExtraShortcuts = "",
                                    Button1ToolTip = "Shortcut: Enter",
                                    Button1Style = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",
                                    Button2Name = "No",
                                    Button2ExtraShortcuts = "",
                                    Button2ToolTip = "Shortcut: None",
                                    Button2Style = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",
                                    Button3Name = "Cancel",
                                    Button3ExtraShortcuts = "",
                                    Button3ToolTip = "Shortcut: Esc",
                                    Button3Style = """QPushButton { 
                                                                    background-color : rgb(100,100,100);
                                                                    font-weight: Normal;
                                                                    font-size: 8pt;
                                                                    }""",
                                    ): 
        super().__init__(Parent)


        # Default value on startup.
        self.ButtonClickedValue = None



        # ----------------- MAIN WINDOW SETTINGS ----------------- #



        # Main window.
        self.setWindowTitle(Title)
        self.setFixedWidth(WindowWidth)
        self.setFixedHeight(WindowHeight)
        # Remove maximize, minimize and help buttons.
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Set if user can click outside the window.
        self.setModal(True)
        # Restore default arrow cursor on initialize to prevent loading cursor bug.
        QtWidgets.QApplication.restoreOverrideCursor()



        # ----------------- TEXT LABEL SETTINGS ----------------- #



        # Text label.
        self.Label = QtWidgets.QLabel(self)
        self.Label.setText(Label)
        self.Label.setAlignment(QtCore.Qt.AlignCenter)
        


        # ----------------- BUTTON SETTINGS ----------------- #



        # Button 1.
        self.Button1 = QtWidgets.QPushButton(Button1Name, self)
        self.Button1.setFixedWidth(AllButtonWidth)
        self.Button1.setFixedHeight(AllButtonHeight)
        self.Button1.setDefault(True)
        self.Button1Shortcut = QShortcut(QKeySequence(Button1ExtraShortcuts), self)
        self.Button1.setToolTip(Button1ToolTip)
        self.Button1.setStyleSheet(Button1Style)
        self.Button1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 1 in your own script.
        self.Button1Shortcut.activated.connect(self.OnClickButton1)
        self.Button1.clicked.connect(self.OnClickButton1)

        # Button 2.
        self.Button2 = QtWidgets.QPushButton(Button2Name, self)
        self.Button2.setFixedWidth(AllButtonWidth)
        self.Button2.setFixedHeight(AllButtonHeight)
        self.Button2.setDefault(False)
        self.Button2Shortcut = QShortcut(QKeySequence(Button2ExtraShortcuts), self)
        self.Button2.setToolTip(Button2ToolTip)
        self.Button2.setStyleSheet(Button2Style)
        self.Button2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 2 in your own script.
        self.Button2Shortcut.activated.connect(self.OnClickButton2)
        self.Button2.clicked.connect(self.OnClickButton2)

        # Button 3.
        self.Button3 = QtWidgets.QPushButton(Button3Name, self)
        self.Button3.setFixedWidth(AllButtonWidth)
        self.Button3.setFixedHeight(AllButtonHeight)
        self.Button3.setDefault(False)
        self.Button3Shortcut = QShortcut(QKeySequence(Button3ExtraShortcuts), self)
        self.Button3.setToolTip(Button3ToolTip)
        self.Button3.setStyleSheet(Button3Style)
        self.Button3.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # (Call function) Execute button 3 in your own script.
        self.Button3Shortcut.activated.connect(self.OnClickButton3)
        self.Button3.clicked.connect(self.OnClickButton3)



        # ----------------- LAYOUT CUSTOMIZATION ----------------- #



        # Create layout.
        self.LayoutMainWindow = QtWidgets.QVBoxLayout(self)
        # Create sub layouts.
        self.CustomLayout = QtWidgets.QVBoxLayout(self)
        self.LayoutLabel = QtWidgets.QHBoxLayout(self)
        self.LayoutButtons = QtWidgets.QHBoxLayout(self)

        # Add widgets (buttons, labels, etc.) to sub layouts.
        self.LayoutLabel.addWidget(self.Label)
        self.LayoutButtons.addWidget(self.Button1)
        self.LayoutButtons.addWidget(self.Button2)
        self.LayoutButtons.addWidget(self.Button3)

        # Set main layout.
        self.setLayout(self.LayoutMainWindow)
        # Set sub layouts to main layout.
        self.LayoutMainWindow.addLayout(self.CustomLayout)
        self.LayoutMainWindow.addLayout(self.LayoutLabel)
        self.LayoutMainWindow.addLayout(self.LayoutButtons)



        # ----------------- STARTUP CALL EVENTS ----------------- #



        # # (Call function) Fix issues with center window to desktop screen.
        # self.CenterWindowToScreenFix()
        # # (Call function) Center window to desktop screen.
        # self.CenterWindowToScreen()

        # (Call function) Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. 
        self.CustomLayoutSetup()
        # (Call function) Execute script.
        self.ExecuteScript()

       

    # ----------------- BUTTON EVENTS ----------------- #



    def OnClickButton1(self):
        """ Execute button 1 in your own script. """
        self.ButtonClickedValue = 1
        self.close()


    def OnClickButton2(self):
        """ Execute button 2 in your own script. """
        self.ButtonClickedValue = 2
        self.close()


    def OnClickButton3(self):
        """ Execute button 3 in your own script. """
        self.ButtonClickedValue = 3
        self.close()



    # ----------------- CENTER WINDOW EVENTS ----------------- #



    def CenterWindowToScreenFix(self):
        """ Executing this before [CenterWindowToScreen] will fix center issues. Execute this only on initialize. """
        self.hide()
        self.show()
        

    def CenterWindowToScreen(self):
        """ Center window position to screen. """
        FrameGeo = self.frameGeometry()
        CenterPosition = QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen()).center()
        FrameGeo.moveCenter(CenterPosition)
        self.move(FrameGeo.topLeft())



    # ----------------- EXECUTE SCRIPT ----------------- #



    def CustomLayoutSetup(self):
        """ Overwrite custom layout setup function in your own script. If nothing is overwritten then the function will pass. """
        pass


    def ExecuteScript(self):
        """ Execute and create window popup. Then unfreeze viewport. """
        self.exec_()
        UnFreeze.UnFreezeViewport()
        self.destroy(True)