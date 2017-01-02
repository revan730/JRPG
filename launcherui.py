# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'launcher.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(237, 115)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.fs_cb = QtWidgets.QCheckBox(Form)
        self.fs_cb.setObjectName("fs_cb")
        self.gridLayout.addWidget(self.fs_cb, 0, 0, 1, 1)
        self.wat_cb = QtWidgets.QCheckBox(Form)
        self.wat_cb.setObjectName("wat_cb")
        self.gridLayout.addWidget(self.wat_cb, 1, 0, 1, 1)
        self.btn_save = QtWidgets.QPushButton(Form)
        self.btn_save.setObjectName("btn_save")
        self.gridLayout.addWidget(self.btn_save, 2, 0, 1, 1)
        self.btn_launch = QtWidgets.QPushButton(Form)
        self.btn_launch.setObjectName("btn_launch")
        self.gridLayout.addWidget(self.btn_launch, 2, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "JRPG Launcher"))
        self.fs_cb.setText(_translate("Form", "Fullscreen"))
        self.wat_cb.setText(_translate("Form", "Draw Water"))
        self.btn_save.setText(_translate("Form", "Save"))
        self.btn_launch.setText(_translate("Form", "Play!"))

