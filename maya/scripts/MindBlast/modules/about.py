import os
from importlib import reload
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader

from ..utils import util

reload(util)


class About(QtWidgets.QDialog):

    def __init__(self):
        super(About, self).__init__(util.main_maya())
        self.setObjectName("AboutBlast")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/about.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setMinimumSize(QtCore.QSize(431, 299))
        self.setMaximumSize(QtCore.QSize(431, 299))
        self.manager_layout = QtWidgets.QVBoxLayout(self)
        self.manager_layout.setObjectName("manager_layout")
        self.setWindowTitle('About MindBlast')
        self.ui = self.load_ui()

        main = self.ui.findChild(QtWidgets.QWidget, "main_widget")
        footer = self.ui.findChild(QtWidgets.QWidget, "footer_widget")

        self.manager_layout.addWidget(main)
        self.manager_layout.addWidget(footer)

        self.show()

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(util.get_root_path(), "resources", "about.ui")
        return loader.load(path)


from ..resources import assets
