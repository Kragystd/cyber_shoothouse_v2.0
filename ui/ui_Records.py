# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Records.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Records(object):
    def setupUi(self, Records):
        Records.setObjectName("Records")
        Records.resize(1920, 1080)
        Records.setStyleSheet("background:black")
        self.bt_back = QtWidgets.QPushButton(Records)
        self.bt_back.setGeometry(QtCore.QRect(40, 1020, 75, 23))
        self.bt_back.setStyleSheet("color:white")
        self.bt_back.setObjectName("bt_back")

        self.retranslateUi(Records)
        QtCore.QMetaObject.connectSlotsByName(Records)

    def retranslateUi(self, Records):
        _translate = QtCore.QCoreApplication.translate
        Records.setWindowTitle(_translate("Records", "Form"))
        self.bt_back.setText(_translate("Records", "返回"))