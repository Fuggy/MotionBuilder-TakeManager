# pylint: disable-all


# Python [Utils Script] for MotionBuilder.
# This script is used to fix frozen viewport on MotionBuilder when executing various scripts.


from pyfbsdk import *
from pyfbsdk_additions import *
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance, getCppPointer



# ----------------- DESTROY WINDOW ----------------- #



# (Function) Destroy tool window.
def DestroyToolInstancesByName(Name):
    [FBDestroyToolByName(x) for x in [y for y in FBToolList if Name in y]]



# ----------------- WINDOW CREATION ----------------- #



# Spawn window and close it immediately.
class ViewportPatchWindow(QtWidgets.QWidget):
    def __init__(self, Parent = None):
        super(ViewportPatchWindow, self).__init__(Parent)

        # Using foreign window to make sure the popup is never visible.
        self.setWindowFlags(QtCore.Qt.ForeignWindow)

        self.show()
        self.close()



# ----------------- WINDOW DOCKING ----------------- #



class ViewportPatchWindowHolder(FBWidgetHolder):
    def WidgetCreate(self, WidgetParentPtr):
        WidgetParent = wrapInstance(WidgetParentPtr, QtWidgets.QWidget).parentWidget()  # type: ignore
        self.ExecuteScriptWidget = ViewportPatchWindow(WidgetParent)
        return getCppPointer(self.ExecuteScriptWidget)[0]  # type: ignore

class ViewportPatchWindowTool(FBTool):            
    def __init__(self, Name):
        DestroyToolInstancesByName(Name)
        FBTool.__init__(self, Name)
        self.WidgetHolder = ViewportPatchWindowHolder()
        X = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        Y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
        W = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
        H = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
        self.AddRegion("main","main", X, Y, W, H)
        self.SetControl("main", self.WidgetHolder)  
        self.StartSizeX = 0
        self.StartSizeY = 0
        FBAddTool(self)
        ShowTool(self)



# ----------------- EXECUTION FUNCTION CALL ----------------- #



# Call this function after executing in your own script.
def UnFreezeViewport():
    ToolName = "viewportpatch"
    Tool = ViewportPatchWindowTool(ToolName)
    DestroyToolInstancesByName(ToolName)