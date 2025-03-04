# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Setting(object):
    def setupUi(self, Setting):
        Setting.setObjectName("Setting")
        Setting.resize(1920, 1080)
        Setting.setStyleSheet("backGround:black")
        self.bt_back = QtWidgets.QPushButton(Setting)
        self.bt_back.setGeometry(QtCore.QRect(30, 1000, 239, 68))
        self.bt_back.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/HomePageBtnBg.png);\n"
"font-family:微软雅黑;\n"
"font-size:16px}\n"
".QPushButton:hover{color:#79d9ff;\n"
"border-image:url(./ui/resources/HomePageBtnBg_hover.png);\n"
"font-size:16px}")
        self.bt_back.setObjectName("bt_back")
        self.bg_label = QtWidgets.QLabel(Setting)
        self.bg_label.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.bg_label.setStyleSheet("background:url(./ui/resources/SettingBg.png)\n"
"")
        self.bg_label.setText("")
        self.bg_label.setObjectName("bg_label")
        self.cam_input = QtWidgets.QLineEdit(Setting)
        self.cam_input.setGeometry(QtCore.QRect(560, 330, 336, 42))
        self.cam_input.setStyleSheet("QLineEdit {\n"
"    border: 0px solid #A0A0A0;\n"
"    background: url(./ui/resources/lineEdit.png),transparent;\n"
"    color: #5e7884; \n"
"    selection-background-color: #5e7884; \n"
"    selection-color: white; /* 选中文本的颜色 */\n"
"    font-family: 微软雅黑;\n"
"    font-size: 14pt; /* 文本字体大小 */\n"
"    text-align:center\n"
"}\n"
"\n"
"QLineEdit:hover { /* 鼠标悬浮在QLineEdit时的状态 */\n"
"    border: 0px solid #298DFF;\n"
"    background: url(./ui/resources/lineEdit_hover.png),transparent;\n"
"    color: #87d8ff;\n"
"    selection-background-color: black;\n"
"    selection-color: white;\n"
"}")
        self.cam_input.setText("")
        self.cam_input.setObjectName("cam_input")
        self.fire_sound = QtWidgets.QCheckBox(Setting)
        self.fire_sound.setGeometry(QtCore.QRect(1600, 330, 30, 30))
        self.fire_sound.setAcceptDrops(False)
        self.fire_sound.setAutoFillBackground(False)
        self.fire_sound.setStyleSheet("\n"
"QCheckBox{\n"
"    border: none;/*最外层边框*/\n"
"    background:transparent\n"
"}\n"
"QCheckBox::indicator{/*选择框尺寸*/\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: 0px solid #b1b1b1;\n"
"    width: 30px;\n"
"    height: 30px;\n"
"}\n"
" \n"
"QCheckBox::indicator:unchecked {\n"
"        image: url(./ui/resources/unchecked.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:hover {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:pressed {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"        image: url(./ui/resources/checked.png);\n"
"}\n"
"QCheckBox::indicator:checked:hover {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked:pressed {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}")
        self.fire_sound.setText("")
        self.fire_sound.setIconSize(QtCore.QSize(30, 30))
        self.fire_sound.setChecked(False)
        self.fire_sound.setObjectName("fire_sound")
        self.shell_sound = QtWidgets.QCheckBox(Setting)
        self.shell_sound.setGeometry(QtCore.QRect(1600, 380, 30, 30))
        self.shell_sound.setAcceptDrops(False)
        self.shell_sound.setAutoFillBackground(False)
        self.shell_sound.setStyleSheet("\n"
"QCheckBox{\n"
"    border: none;/*最外层边框*/\n"
"    background:transparent\n"
"}\n"
"QCheckBox::indicator{/*选择框尺寸*/\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: 0px solid #b1b1b1;\n"
"    width: 30px;\n"
"    height: 30px;\n"
"}\n"
" \n"
"QCheckBox::indicator:unchecked {\n"
"        image: url(./ui/resources/unchecked.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:hover {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:pressed {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"        image: url(./ui/resources/checked.png);\n"
"}\n"
"QCheckBox::indicator:checked:hover {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked:pressed {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}")
        self.shell_sound.setText("")
        self.shell_sound.setIconSize(QtCore.QSize(30, 30))
        self.shell_sound.setChecked(False)
        self.shell_sound.setObjectName("shell_sound")
        self.hit_sound = QtWidgets.QCheckBox(Setting)
        self.hit_sound.setGeometry(QtCore.QRect(1600, 430, 30, 30))
        self.hit_sound.setAcceptDrops(False)
        self.hit_sound.setAutoFillBackground(False)
        self.hit_sound.setStyleSheet("\n"
"QCheckBox{\n"
"    border: none;/*最外层边框*/\n"
"    background:transparent\n"
"}\n"
"QCheckBox::indicator{/*选择框尺寸*/\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: 0px solid #b1b1b1;\n"
"    width: 30px;\n"
"    height: 30px;\n"
"}\n"
" \n"
"QCheckBox::indicator:unchecked {\n"
"        image: url(./ui/resources/unchecked.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:hover {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:pressed {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"        image: url(./ui/resources/checked.png);\n"
"}\n"
"QCheckBox::indicator:checked:hover {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked:pressed {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}")
        self.hit_sound.setText("")
        self.hit_sound.setIconSize(QtCore.QSize(30, 30))
        self.hit_sound.setChecked(False)
        self.hit_sound.setObjectName("hit_sound")
        self.kill_sound = QtWidgets.QCheckBox(Setting)
        self.kill_sound.setGeometry(QtCore.QRect(1600, 480, 30, 30))
        self.kill_sound.setAcceptDrops(False)
        self.kill_sound.setAutoFillBackground(False)
        self.kill_sound.setStyleSheet("\n"
"QCheckBox{\n"
"    border: none;/*最外层边框*/\n"
"    background:transparent\n"
"}\n"
"QCheckBox::indicator{/*选择框尺寸*/\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: 0px solid #b1b1b1;\n"
"    width: 30px;\n"
"    height: 30px;\n"
"}\n"
" \n"
"QCheckBox::indicator:unchecked {\n"
"        image: url(./ui/resources/unchecked.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:hover {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:unchecked:pressed {\n"
"        image: url(./ui/resources/unchecked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"        image: url(./ui/resources/checked.png);\n"
"}\n"
"QCheckBox::indicator:checked:hover {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}\n"
"QCheckBox::indicator:checked:pressed {\n"
"        image: url(./ui/resources/checked_hover.png);\n"
"}")
        self.kill_sound.setText("")
        self.kill_sound.setIconSize(QtCore.QSize(30, 30))
        self.kill_sound.setChecked(False)
        self.kill_sound.setObjectName("kill_sound")
        self.bt_apply = QtWidgets.QPushButton(Setting)
        self.bt_apply.setGeometry(QtCore.QRect(310, 1000, 239, 68))
        self.bt_apply.setStyleSheet(".QPushButton{color:white;\n"
"border-image:url(./ui/resources/HomePageBtnBg.png);\n"
"font-family:微软雅黑;\n"
"font-size:16px}\n"
".QPushButton:hover{color:#79d9ff;\n"
"border-image:url(./ui/resources/HomePageBtnBg_hover.png);\n"
"font-size:16px}")
        self.bt_apply.setObjectName("bt_apply")
        self.tick_input = QtWidgets.QLineEdit(Setting)
        self.tick_input.setGeometry(QtCore.QRect(560, 380, 336, 42))
        self.tick_input.setStyleSheet("QLineEdit {\n"
"    border: 0px solid #A0A0A0;\n"
"    background: url(./ui/resources/lineEdit.png),transparent;\n"
"    color: #5e7884; \n"
"    selection-background-color: #5e7884; \n"
"    selection-color: white; /* 选中文本的颜色 */\n"
"    font-family: 微软雅黑;\n"
"    font-size: 14pt; /* 文本字体大小 */\n"
"    text-align:center\n"
"}\n"
"\n"
"QLineEdit:hover { /* 鼠标悬浮在QLineEdit时的状态 */\n"
"    border: 0px solid #298DFF;\n"
"    background: url(./ui/resources/lineEdit_hover.png),transparent;\n"
"    color: #87d8ff;\n"
"    selection-background-color: black;\n"
"    selection-color: white;\n"
"}")
        self.tick_input.setObjectName("tick_input")
        self.threshold_input = QtWidgets.QLineEdit(Setting)
        self.threshold_input.setGeometry(QtCore.QRect(580, 430, 284, 42))
        self.threshold_input.setStyleSheet("QLineEdit {\n"
"    border: 0px solid #A0A0A0;\n"
"    background: url(./ui/resources/lineEdit.png),transparent;\n"
"    color: #5e7884; \n"
"    selection-background-color: #5e7884; \n"
"    selection-color: white; /* 选中文本的颜色 */\n"
"    font-family: 微软雅黑;\n"
"    font-size: 14pt; /* 文本字体大小 */\n"
"    text-align:center\n"
"}\n"
"\n"
"QLineEdit:hover { /* 鼠标悬浮在QLineEdit时的状态 */\n"
"    border: 0px solid #298DFF;\n"
"    background: url(./ui/resources/lineEdit_hover.png),transparent;\n"
"    color: #87d8ff;\n"
"    selection-background-color: black;\n"
"    selection-color: white;\n"
"}")
        self.threshold_input.setObjectName("threshold_input")
        self.score_precision_input = QtWidgets.QLineEdit(Setting)
        self.score_precision_input.setGeometry(QtCore.QRect(580, 480, 284, 42))
        self.score_precision_input.setStyleSheet("QLineEdit {\n"
"    border: 0px solid #A0A0A0;\n"
"    background: url(./ui/resources/lineEdit.png),transparent;\n"
"    color: #5e7884; \n"
"    selection-background-color: #5e7884; \n"
"    selection-color: white; /* 选中文本的颜色 */\n"
"    font-family: 微软雅黑;\n"
"    font-size: 14pt; /* 文本字体大小 */\n"
"    text-align:center\n"
"}\n"
"\n"
"QLineEdit:hover { /* 鼠标悬浮在QLineEdit时的状态 */\n"
"    border: 0px solid #298DFF;\n"
"    background: url(./ui/resources/lineEdit_hover.png),transparent;\n"
"    color: #87d8ff;\n"
"    selection-background-color: black;\n"
"    selection-color: white;\n"
"}")
        self.score_precision_input.setObjectName("score_precision_input")
        self.bg_label.raise_()
        self.bt_back.raise_()
        self.cam_input.raise_()
        self.fire_sound.raise_()
        self.shell_sound.raise_()
        self.hit_sound.raise_()
        self.kill_sound.raise_()
        self.bt_apply.raise_()
        self.tick_input.raise_()
        self.threshold_input.raise_()
        self.score_precision_input.raise_()

        self.retranslateUi(Setting)
        QtCore.QMetaObject.connectSlotsByName(Setting)

    def retranslateUi(self, Setting):
        _translate = QtCore.QCoreApplication.translate
        Setting.setWindowTitle(_translate("Setting", "Form"))
        self.bt_back.setText(_translate("Setting", "返回"))
        self.bt_apply.setText(_translate("Setting", "应用更改"))
