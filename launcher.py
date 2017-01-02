#!/usr/bin/env python

import launcherui
import sys
import os
from subprocess import Popen
from ResourceHelpers import SettingsHelper
from PyQt5 import QtWidgets, QtGui


class MainWindow(QtWidgets.QWidget, launcherui.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_save.clicked.connect(self.write_settings)
        self.btn_launch.clicked.connect(self.launch)
        self.load_settings()

    def load_settings(self):
        settings = SettingsHelper()
        detailed_water = settings.get('world_water_tiled', False)
        resolution = (settings.get('screen_width', 800), settings.get('screen_height', 600))
        if resolution == (1366, 768):
            self.fs_cb.setChecked(True)
        if detailed_water is True:
            self.wat_cb.setChecked(True)

    def write_settings(self):
        settings = SettingsHelper()
        settings.set('world_water_tiled', self.wat_cb.isChecked())
        if self.fs_cb.isChecked():
            settings.set('screen_width', 1366)
            settings.set('screen_height', 768)
        else:
            settings.set('screen_width', 800)
            settings.set('screen_height', 600)

    def launch(self):
        self.write_settings()
        # os.system("python main.py")
        proc = Popen(['python main.py'], shell=True,
             stdin=None, stdout=None, stderr=None, close_fds=True)
        self.close()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()