import os
import sys
from glob import glob
import datetime
from utils import util
from importlib import reload
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader
from maya import cmds, mel
from modules import splash

reload(util)
reload(splash)

local_path = os.path.join(util.get_root_path(), "libs")
local_path = os.path.normpath(local_path)

if local_path not in sys.path:
    sys.path.append(local_path)

import ffmpeg


class Blast(QtWidgets.QDialog):
    spl = None
    resolutions = {
        "HD 1080": {
            "width": 1920,
            "height": 1080
        },
        "HD 720": {
            "width": 1280,
            "height": 720
        },
        "HD 540": {
            "width": 960,
            "height": 540
        },
    }
    viewport = None

    def __init__(self):
        super(Blast, self).__init__(util.main_maya())
        self.setObjectName("Blast")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/shot.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setMinimumSize(QtCore.QSize(512, 200))
        self.setMaximumSize(QtCore.QSize(512, 200))
        self.manager_layout = QtWidgets.QVBoxLayout(self)
        self.manager_layout.setObjectName("manager_layout")
        self.setWindowTitle('Create MindBlast')
        self.ui = self.load_ui()

        main = self.ui.findChild(QtWidgets.QWidget, "main_widget")
        footer = self.ui.findChild(QtWidgets.QWidget, "footer_widget")

        self.manager_layout.addWidget(main)
        self.manager_layout.addWidget(footer)

        self.spl = splash.Splash()
        QtCore.QTimer.singleShot(1000, self.bootstrap)

    # close window
    def closeEvent(self, event):
        self.prepare_viewport(active=False)

    def populate_selects(self):
        self.ui.shot.clear()
        self.ui.sequence.clear()
        self.ui.step.clear()

        for seq in range(1, 5):
            self.ui.sequence.addItem("SC{:02d}".format(seq))

        for shot in range(10, 1000, 10):
            self.ui.shot.addItem("SHOT_{:03d}".format(shot))

        for step in ["Story Poses", "Blocking", "Blocking Plus", "Spline/Polish", "Final"]:
            self.ui.step.addItem(step.upper())

    # get all cameras
    def get_all_cameras(self):
        try:
            self.ui.cameras.clear()
            self.all_cameras = cmds.listCameras(p=True)
            self.all_cameras.sort()
            self.all_cameras = list(map(lambda cam: {"name": cam.upper(), "cam": cam}, self.all_cameras))
            for cam in self.all_cameras:
                self.ui.cameras.addItem(cam.get("name"))
        except:
            pass

    # set camera select
    def set_camera(self):
        try:
            current_camera_index = self.ui.cameras.currentIndex()
            current_camera = self.all_cameras[current_camera_index].get("cam")
            self.viewport = cmds.getPanel(withFocus=True)
            if self.viewport != "modelPanel4":
                self.viewport = "modelPanel4"
            cmds.modelEditor(self.viewport, e=True, camera=current_camera)
            self.prepare_viewport()
            cmds.modelEditor(self.viewport, edit=True,
                             displayAppearance='smoothShaded',
                             grid=False,
                             activeView=True,
                             displayLights='default',
                             cameras=False,
                             nurbsCurves=False,
                             headsUpDisplay=False,
                             displayTextures=True,
                             lights=False,
                             shadows=True)

            cmds.select(clear=True)
        except:
            pass

    # prepare viewport for playblast
    def prepare_viewport(self, active=True):
        if active:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(self.viewport, e=True,
                             allObjects=False,
                             polymeshes=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            mel.eval('generateAllUvTilePreviews;')
        else:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(self.viewport, e=True,
                             allObjects=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )

    # get sound timeline
    def get_sound(self):
        audio = cmds.ls(type='audio')
        if not audio:
            cmds.warning('No sound node.')
            return ""
        else:
            return audio[0]

    def create_blast(self):
        try:
            if self.ui.animator.text() == "":
                cmds.confirmDialog(title="Animator", message="Enter the name of the animator!", button=['Ok'], defaultButton="Ok")
                return

            QtCore.QCoreApplication.processEvents()
            self.ui.progress_bar.setVisible(True)
            self.setDisabled(True)
            cmds.optionVar(stringValue=())

            self.data = {
                "animator": self.ui.animator.text(),
                "format": self.ui.format.currentText(),
                "step": self.ui.step.currentText(),
                "sequence": self.ui.sequence.currentText(),
                "shot": self.ui.shot.currentText(),
                "date": datetime.date.today().strftime("%d/%m/%Y")
            }

            # Get the file path from Maya
            file_path = cmds.file(q=True, sn=True)

            if file_path is None:
                cmds.confirmDialog(title="Scene", message="I do not save", button=['Ok'], defaultButton="Ok")
                return

            # Get the file name
            path = os.path.join(util.get_root_project(), "movies", "playblast", "Review", self.ui.sequence.currentText(), self.ui.shot.currentText())

            if not os.path.exists(path):
                os.makedirs(path)

            if not os.path.exists(path.replace("Review", "Final")):
                os.makedirs(path.replace("Review", "Final"))

            path_version = os.path.join(path, "{}_Anim.*".format(self.ui.shot.currentText()))
            list_version = glob(path_version)
            version = len(list_version)
            if version <= 0:
                version = 1
            else:
                version += 1
            filename = os.path.join(path, "{}_Anim.v{:03d}.avi".format(self.ui.shot.currentText(), version))
            filename = os.path.normpath(filename)
            frame_start, frame_end = (cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True))
            QtCore.QCoreApplication.processEvents()

            resolution = self.ui.resolution.currentText()
            width, height = list(self.resolutions[resolution].values())
            self.filename = filename.replace("\\", "/")
            QtCore.QCoreApplication.processEvents()
            self.ui.progress_bar.setFormat("Create playblast")
            self.ui.progress_bar.setProperty("value", 33)
            cmds.select(clear=True)
            cmds.playblast(
                format='avi',
                percent=100,
                quality=100,
                viewer=False,
                sequenceTime=False,
                combineSound=True,
                sound=self.get_sound(),
                clearCache=True,
                startTime=int(frame_start),
                endTime=int(frame_end),
                offScreen=True,
                showOrnaments=True,
                forceOverwrite=True,
                filename=self.filename,
                widthHeight=[width, height],
                rawFrameNumbers=False,
                framePadding=4)

            cmds.optionVar(stringValue=("animator", self.ui.animator.text()))
            QtCore.QTimer.singleShot(300, self.create_layout)

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def create_layout(self):

        logo_path = os.path.join(util.get_root_path(), "resources", "logo.png")
        font_path = os.path.join(util.get_root_path(), "resources", "font.ttf")
        QtCore.QCoreApplication.processEvents()

        height_bar = 120
        space = (height_bar / 2)
        font_size = 18
        font_color = '#FFFFFF'
        bar_color = '#00000080'
        border_color = '#3c3c3c00'
        border_width = 1
        line_spacing = -2

        base = ffmpeg.input(self.filename)
        audio = base.audio
        base = ffmpeg.drawbox(base, 0, t='fill', width='iw', height=height_bar, y=0, color=bar_color)

        base = ffmpeg.filter([base, ffmpeg.input(logo_path)], 'overlay', 'W-overlay_w-{}'.format(space), (space / 2))

        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text=self.data.get("date"), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='ANIMATOR: {}'.format(self.data.get('animator')), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text="{}".format(self.data.get('step')), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='COUNT\: %{n}', start_number=1, fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='FRAMES\: %{n}', start_number=int(cmds.playbackOptions(q=True, max=True)), fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
        base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='{} {}'.format(self.data.get('sequence'), self.data.get('shot')), fontcolor=font_color, escape_text=True, x='{} * 5 + 100'.format(space), y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

        try:
            self.ui.progress_bar.setFormat("Convert and create layout")
            self.ui.progress_bar.setProperty("value", 66)
            joined = ffmpeg.concat(base, audio, v=1, a=1).node
            cmd_blast = ffmpeg.output(joined[0], joined[1], self.filename.replace(".avi", ".{}".format(self.data.get("format").lower())), loglevel="quiet")
            cmd_blast.global_args('-y').run(cmd=util.get_ffmpeg())
            cmds.launch(mov=self.filename.replace(".avi", ".{}".format(self.data.get("format").lower())))
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

        QtCore.QCoreApplication.processEvents()
        self.ui.progress_bar.setVisible(False)
        self.setDisabled(False)
        self.ui.progress_bar.setFormat("Playnlast complete create")
        self.ui.progress_bar.setProperty("value", 99)
        os.unlink(self.filename)
        self.prepare_viewport(active=False)
        self.close()

    # playpause timeslider
    def play_pause(self):
        if self.ui.play_pause.isChecked():
            cmds.play(state=True)
            name = "pause"
        else:
            name = "play"
            cmds.play(state=False)

        QtCore.QCoreApplication.processEvents()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/{}".format(name)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.play_pause.setIcon(icon)

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(util.get_root_path(), "resources", "blast.ui")
        return loader.load(path)

    def bootstrap(self):
        self.spl.close()
        self.show()
        self.populate_selects()
        QtCore.QCoreApplication.processEvents()
        self.ui.cameras.currentIndexChanged.connect(self.set_camera)
        self.ui.play_pause.clicked.connect(self.play_pause)
        self.ui.export_blast.clicked.connect(self.create_blast)
        resolutions = self.resolutions.keys()
        self.ui.resolution.clear()
        self.ui.resolution.addItems(resolutions)
        QtCore.QTimer.singleShot(250, self.get_all_cameras)


from resources import assets
