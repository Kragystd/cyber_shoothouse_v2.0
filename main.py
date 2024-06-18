# -*- coding: utf-8 -*-
# @Time    : 2023/6/11 19:11
# @Author  : Kragy
# @File    : main.py
from SR_GUI import *
import sys

app = QApplication(sys.argv)
window = SR_GUI()
window.show()
sys.exit(app.exec_())
