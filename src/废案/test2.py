import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from src.wasted.core_optimized import ShootingRange


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sr = ShootingRange('http://192.168.137.203:4747/videos', '../imgs/st.png')

        self.setWindowTitle("Camera Capture")
        self.setGeometry(100, 100, 1000, 600)

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 390, 580)
        self.label2 = QLabel(self)
        self.label2.setGeometry(400, 10, 390, 580)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)  # 1 ms 捕获一帧

    def update_frame(self):
        frameData = self.sr.getCurrentData()
        frame = frameData[0]

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height()))

        target = frameData[1]
        if target is not None:
            image = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            image = QImage(target.data, target.shape[1], target.shape[0], target.shape[1] * target.shape[2],
                           QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label2.setPixmap(pixmap.scaled(self.label2.width(), self.label2.height()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
