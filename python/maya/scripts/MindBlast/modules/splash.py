import os
import sys
from utils import util
from importlib import reload
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader

reload(util)



class Splash(QtWidgets.QDialog):

    def __init__(self):
        super(Splash, self).__init__(util.main_maya())
        self.setObjectName("Splash")
        self.setStyleSheet("background:transparent")

        self.setMinimumSize(QtCore.QSize(640, 360))
        self.setMaximumSize(QtCore.QSize(640, 360))
        self.manager_layout = QtWidgets.QVBoxLayout(self)
        self.manager_layout.setObjectName("manager_layout")
        self.manager_layout.setContentsMargins(0, 0, 0, 0)
        self.manager_layout.setSpacing(0)
        self.setWindowTitle('Create MindSplash')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui = self.load_ui()

        splash_widget = self.ui.findChild(QtWidgets.QWidget, "splash_widget")
        self.manager_layout.addWidget(splash_widget)

        self.show()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(util.get_root_path(), "resources", "Splash.ui")
        return loader.load(path)


from resources import assets
