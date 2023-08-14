import maya.api.OpenMaya as OpenMaya
from maya import cmds, mel
from importlib import reload
from MindBlast import app

reload(app)

mind_app = app.MindBlast()


def maya_useNewAPI():
    pass


class MindBlast(OpenMaya.MPxCommand):
    CommandName = "MindBlast"

    def __init__(self):
        super(MindBlast, self).__init__()

    @classmethod
    def creator(cls):
        pass


def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, 'Mindblownlab Studio', '1.0', 'MindBlast')
    try:
        plugin.registerCommand(MindBlast.CommandName, MindBlast.creator)
        mind_app.menu()
    except:
        pass


def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)
    try:
        __menu_name__ = "mind_menu"
        __menu_label__ = "MBLab"
        if cmds.menu(__menu_name__, exists=1):
            cmds.deleteUI(__menu_name__, menu=1)

        plugin.deregisterCommand(MindBlast.CommandName)
    except:
        pass
