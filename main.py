import os
import sys
import re
import time

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QKeyEvent
from PyQt5.QtCore import Qt, QTimer, QVariantAnimation

from arduino_connection import ArduinoConnection
from museum_image import MuseumImage

# CONFIG
IMAGE_FOLDER = "/home/sergey/PycharmProjects/kilpola_museum/images"
IMAGE_DEFAULT_OPACITY = {"image_0.png": 1.0,
                         "image_1.png": 0.50,
                         "image_2.png": 0.5,
                         }  # List [(image_filename_in_folder, opacity)]
PORT_NAME = "/dev/ttyUSB0"

ard_device = ArduinoConnection(PORT_NAME, 9600)


class MainWindow(QMainWindow):
    def __init__(self, screen):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        # Загружаем список путей к изображениям
        self.image_paths = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ])

        self.images = []
        self.states = []
        self.current_index = 0
        self.load_multiple_images()

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(2000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self.on_opacity_changed)
        self.anim.finished.connect(self.on_animation_finished)

        self.timer.start(50)

    def load_multiple_images(self):
        """Загружает несколько изображений с разной прозрачностью"""
        self.images.clear()
        count = len(self.image_paths)
        self.states = [0] * count
        for i in range(count):
            path = os.path.join(IMAGE_FOLDER, self.image_paths[i])
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            scaled = pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            museum_img = MuseumImage(self.image_paths[i], scaled, IMAGE_DEFAULT_OPACITY.get(self.image_paths[i], 0))
            self.images.append(museum_img)

    def start_transition(self):
        self.opacity = 0.0
        self.anim.start()

    def on_opacity_changed(self, value):
        self.opacity = value
        self.update()

    def on_animation_finished(self):
        self.opacity = 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        for m_img in self.images:
            op = m_img.get_opacity()
            painter.setOpacity(op)
            pixmap = m_img.get_pixmap()
            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
        painter.end()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.timer.stop()
            self.close()
            print("Exit")
        elif event.key() == Qt.Key_Space:
            # self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.update()

    def on_timer(self):
        start = time.time()
        data = int.from_bytes(ard_device.read())
        if data:
            self.states = [bool((1 << i) & data) + 0 for i in range(3)]
            opacity_sum = 1  # sum([m_img.get_default_opacity() * self.states[m_img.get_index()] for m_img in self.images])
            if opacity_sum:
                for m_img in self.images:

                    state = self.states[m_img.get_index()]
                    if state == 0:
                        m_img.set_opacity(0)
                    elif state == 1:
                        m_img.set_opacity(m_img.get_default_opacity() / opacity_sum)
                    else:
                        raise ValueError(f"\"state\" has value \"{state}\", but expected 0 or 1")
            self.update()
        print("Timer tick duration:", round((time.time() - start) * 1000), "ms")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app.primaryScreen())
    window.show()
    sys.exit(app.exec())
