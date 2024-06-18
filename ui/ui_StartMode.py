# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StartMode.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_StartMode(object):
    def setupUi(self, StartMode):
        StartMode.setObjectName("StartMode")
        StartMode.resize(1920, 1080)
        StartMode.setStyleSheet("backGround:black")
        self.bt_back = QtWidgets.QPushButton(StartMode)
        self.bt_back.setGeometry(QtCore.QRect(30, 1000, 239, 68))
        self.bt_back.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/HomePageBtnBg.png);\n"
"font-family:微软雅黑;\n"
"font-size:16px}\n"
".QPushButton:hover{color:#79d9ff;\n"
"border-image:url(./ui/resources/HomePageBtnBg_hover.png);\n"
"font-size:16px}")
        self.bt_back.setObjectName("bt_back")
        self.layoutWidget = QtWidgets.QWidget(StartMode)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 1921, 981))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.bt_Mode1 = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_Mode1.sizePolicy().hasHeightForWidth())
        self.bt_Mode1.setSizePolicy(sizePolicy)
        self.bt_Mode1.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/mode1_gray.png);\n"
"font-family:微软雅黑;\n"
"font-size:30px}\n"
".QPushButton:hover{\n"
"border-image:url(./ui/resources/mode1.png);\n"
"font-size:35px}")
        self.bt_Mode1.setObjectName("bt_Mode1")
        self.horizontalLayout.addWidget(self.bt_Mode1)
        self.bt_Mode2 = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_Mode2.sizePolicy().hasHeightForWidth())
        self.bt_Mode2.setSizePolicy(sizePolicy)
        self.bt_Mode2.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/mode2_gray.png);\n"
"font-family:微软雅黑;\n"
"font-size:30px}\n"
".QPushButton:hover{\n"
"border-image:url(./ui/resources/mode2.png);\n"
"font-size:35px}")
        self.bt_Mode2.setObjectName("bt_Mode2")
        self.horizontalLayout.addWidget(self.bt_Mode2)
        self.bt_Mode3 = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_Mode3.sizePolicy().hasHeightForWidth())
        self.bt_Mode3.setSizePolicy(sizePolicy)
        self.bt_Mode3.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/mode3_gray.png);\n"
"font-family:微软雅黑;\n"
"font-size:30px}\n"
".QPushButton:hover{\n"
"border-image:url(./ui/resources/mode3.png);\n"
"font-size:35px}")
        self.bt_Mode3.setObjectName("bt_Mode3")
        self.horizontalLayout.addWidget(self.bt_Mode3)
        self.layoutWidget.raise_()
        self.bt_back.raise_()

        self.retranslateUi(StartMode)
        QtCore.QMetaObject.connectSlotsByName(StartMode)

    def retranslateUi(self, StartMode):
        _translate = QtCore.QCoreApplication.translate
        StartMode.setWindowTitle(_translate("StartMode", "Form"))
        self.bt_back.setText(_translate("StartMode", "返回"))
        self.bt_Mode1.setText(_translate("StartMode", "自由射击练习"))
        self.bt_Mode2.setWhatsThis(_translate("StartMode", "<html><head/><body><p>敬请期待</p></body></html>"))
        self.bt_Mode2.setText(_translate("StartMode", "常规射击训练（敬请期待）"))
        self.bt_Mode3.setWhatsThis(_translate("StartMode", "<html><head/><body><p>敬请期待</p></body></html>"))
        self.bt_Mode3.setText(_translate("StartMode", "莫桑比克训练（敬请期待）"))