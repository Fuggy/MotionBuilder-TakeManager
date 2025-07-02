# pylint: disable-all


# Python [Utils Script] for MotionBuilder.
# This script is used to fix frozen viewport on MotionBuilder when executing various scripts.


from pyfbsdk import *
from pyfbsdk_additions import *

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance, getCppPointer



# ----------------- WINDOW CREATION ----------------- #


# Spawn window and close it immediately.
class ViewportPatchWindow(QtWidgets.QWidget):
    def __init__(self, Parent = None):
        super().__init__(Parent)

        # Using foreign window to make sure the popup is never visible.
        self.setWindowFlags(QtCore.Qt.ForeignWindow)

        self.show()
        self.close()



# ----------------- WINDOW DOCKING ----------------- #


class ViewportPatchWindowHolder(FBWidgetHolder):
    def WidgetCreate(self, WidgetParentPtr):
        WidgetParent = wrapInstance(WidgetParentPtr, QtWidgets.QWidget).parentWidget()
        self.ExecuteScriptWidget = ViewportPatchWindow(WidgetParent)
        return getCppPointer(self.ExecuteScriptWidget)[0]

class ViewportPatchWindowTool(FBTool):            
    def __init__(self, Name):
        FBDestroyToolByName(Name)
        super().__init__(Name)
        self.WidgetHolder = ViewportPatchWindowHolder()
        FBAddTool(self)
        ShowTool(self)



# ----------------- EXECUTION FUNCTION CALL ----------------- #

# Call this function after executing in your own script.
def UnFreezeViewport():
    ToolName = "viewportpatch"
    Tool = ViewportPatchWindowTool(ToolName)

    # Destroy all tools including the "viewportpatch", doing this incase e.g. "viewportpatch 1" would've been created.
    for x in list(FBToolList):
        if ToolName in x:
            FBDestroyToolByName(x)
