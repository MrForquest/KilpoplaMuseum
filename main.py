import os
import sys
import re
import time
from typing import List, Dict

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QKeyEvent
from PyQt5.QtCore import Qt, QTimer, QVariantAnimation

from arduino_connection import ArduinoConnection
from museum_image import MuseumImage, LayersPreset

# CONFIG
IMAGE_FOLDER: str = "/home/sergey/PycharmProjects/kilpola_museum/images"

IMAGES: List[MuseumImage] = [
    MuseumImage(os.path.join(IMAGE_FOLDER, "image_0.png"), "russian_layer"),
    MuseumImage(os.path.join(IMAGE_FOLDER, "image_1.png"), "finland_layer"),
    MuseumImage(os.path.join(IMAGE_FOLDER, "image_2.png"), "soviet_layer"),
]

IMGS_DICT: Dict[str, MuseumImage] = {img.layer_name: img for img in IMAGES}

PRESETS: Dict[int, LayersPreset] = {
    0: LayersPreset({"russian_layer": (1, 0.0), "finland_layer": (2, 0.0), "soviet_layer": (3, 0.0)}),
    1: LayersPreset({"russian_layer": (1, 1.0), "finland_layer": (2, 0.0), "soviet_layer": (3, 0.0)}),
    2: LayersPreset({"russian_layer": (1, 0.0), "finland_layer": (2, 1.0), "soviet_layer": (3, 0.0)}),
    3: LayersPreset({"russian_layer": (1, 1.0), "finland_layer": (2, 0.5), "soviet_layer": (3, 0.5)}),
    4: LayersPreset({"russian_layer": (1, 0.0), "finland_layer": (2, 0.0), "soviet_layer": (3, 1.0)}),
    5: LayersPreset({"russian_layer": (1, 1.0), "finland_layer": (2, 0.0), "soviet_layer": (3, 0.5)}),
    6: LayersPreset({"russian_layer": (1, 1.0), "finland_layer": (2, 0.5), "soviet_layer": (3, 0)}),
    7: LayersPreset({"russian_layer": (1, 1.0), "finland_layer": (2, 0.5), "soviet_layer": (3, 0.5)}),
}

PORT_NAME: str = "/dev/ttyUSB0"

ard_device: ArduinoConnection = ArduinoConnection(PORT_NAME, 9600)


def load_qpixmap(imgs: List[MuseumImage]) -> None:
    for img in imgs:
        img.load_image()


class MainWindow(QMainWindow):
    def __init__(self, screen) -> None:
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(screen.geometry())
        self.showFullScreen()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer)

        self.image_paths: List[str] = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ])

        self.images = []
        self.states = []
        self.current_index = 0
        self.next_index = 0

        load_qpixmap(IMAGES)

        self.current_preset = PRESETS[self.current_index]
        self.next_preset = PRESETS[self.current_index]

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(1000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self.on_opacity_changed)
        self.anim.finished.connect(self.on_animation_finished)
        self.timer.start(50)

    def start_transition(self) -> None:
        for layer_name in self.current_preset.layers:
            self.current_preset.layer_current_opacities[layer_name] = self.current_preset.layer_default_opacities[
                layer_name]
            self.next_preset.layer_current_opacities[layer_name] = 0.0
        self.anim.start()

    def on_opacity_changed(self, value: float) -> None:
        for layer_name in self.current_preset.layers:
            # self.current_preset.layer_current_opacities[layer_name] = (1 - value) * \
            #                                                           self.current_preset.layer_default_opacities[
            #                                                               layer_name]
            self.next_preset.layer_current_opacities[layer_name] = value * self.next_preset.layer_default_opacities[
                layer_name]
        self.update()

    def on_animation_finished(self) -> None:
        for layer_name in self.current_preset.layers:
            self.current_preset.layer_current_opacities[layer_name] = 0.0
            self.next_preset.layer_current_opacities[layer_name] = self.next_preset.layer_default_opacities[layer_name]
        self.current_index = self.next_index
        self.current_preset = self.next_preset
        self.update()

    def draw_preset(self) -> None:
        # preset: LayersPreset = PRESETS[7]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        # print(self.current_preset.layer_current_opacities)
        for layer_name in self.current_preset.layers:
            m_img: MuseumImage = IMGS_DICT[layer_name]
            painter.setOpacity(self.current_preset.layer_current_opacities[layer_name])
            pixmap: QPixmap = m_img.get_pixmap()
            x: int = (self.width() - pixmap.width()) // 2
            y: int = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)

        for layer_name in self.next_preset.layers:
            m_img: MuseumImage = IMGS_DICT[layer_name]
            painter.setOpacity(self.next_preset.layer_current_opacities[layer_name])
            pixmap: QPixmap = m_img.get_pixmap()
            x: int = (self.width() - pixmap.width()) // 2
            y: int = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)

        painter.end()

    def paintEvent(self, event) -> None:
        self.draw_preset()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.timer.stop()
            self.close()
            print("Exit")
        elif event.key() == Qt.Key_Space:
            self.next_index = (self.current_index + 1) % 8
            self.next_preset = PRESETS[self.next_index]
            # if not self.anim.state() == self.anim.Running:
            print("aaa")
            self.start_transition()

    def on_timer(self) -> None:
        start = time.time()
        data = int.from_bytes(ard_device.read())
        if data:  # todo обработка data=0 (напрмиер, смена 0 на -1 на Arduino)
            print(data)
            self.next_index = data
            self.next_preset = PRESETS[self.next_index]
            # if not self.anim.state() == self.anim.Running:
            self.start_transition()
            # self.update()

        print("Timer tick duration:", round((time.time() - start) * 1000), "ms")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app.primaryScreen())
    window.show()
    sys.exit(app.exec())
