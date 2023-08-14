import os

__version__ = "1.0.0"

try:
    import maya.OpenMayaUI as omui
    from maya import cmds, mel
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except:
    pass


def load_icon(name="settings"):
    return os.path.join(get_root_path(), "resources", "{}.ico".format(name))


def get_root_path():
    return os.path.normpath(os.path.dirname(os.path.dirname(__file__)))


def get_root_project():
    return cmds.workspace(q=True, act=True)


def main_maya():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def get_ffmpeg():
    try:
        return os.path.normpath(os.path.join(get_root_path(), "libs", "ffmpeg", "bin", "ffmpeg.exe"))
    except:
        return "ffmpeg path error"
