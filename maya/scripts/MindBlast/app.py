"""
MIND BLAST V1.0.0

Author: Thiago Silva
Vendor: Mindblownlab Studio
date: 2023-10-08

The MindBlast tool in Maya is essential for 3D animators. It provides a real-time preview of animations in development,
allowing quick assessments of movements and synchronization. Unlike time-consuming final renders, MindBlast is fast and efficient,
enabling swift iterations and corrections. With configuration options such as resolution and format, MindBlast is an indispensable tool
for effectively enhancing animations.
"""
import sys

from maya import cmds, mel
from utils import util
from importlib import reload

from modules import about
from modules import blast

reload(util)
reload(about)
reload(blast)

__menu_name__ = "mind_menu"
__menu_label__ = "MBLab"



class MindBlast:

    def __init__(self):
        pass

    def menu(self):

        if cmds.menu(__menu_name__, exists=1):
            cmds.deleteUI(__menu_name__, menu=1)

        gMainWindow = mel.eval("global string $gMainWindow;$temp = $gMainWindow")
        cmds.menu(__menu_name__, label=__menu_label__, parent=gMainWindow, tearOff=1, allowOptionBoxes=1)
        cmds.menuItem(label="About", parent=__menu_name__, image=util.load_icon(name='about'), command=lambda n=None: about.About())
        cmds.menuItem(divider=True, parent=__menu_name__)
        cmds.menuItem(label="Playblast", parent=__menu_name__, image=util.load_icon(name='shot'), command=lambda n=None: blast.Blast())

    def refresh(self, act=None):
        if cmds.menu(__menu_name__, exists=1):
            cmds.deleteUI(__menu_name__, menu=1)
        self.menu()
