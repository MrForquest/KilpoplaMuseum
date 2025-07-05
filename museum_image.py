from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize


class MuseumImage:
    def __init__(self, path: str, layer_name: str) -> None:
        self.path = path
        self.pixmap = None
        self.layer_name = layer_name

    def load_image(self, size: QSize):
        pixmap = QPixmap(self.path)
        pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.pixmap = pixmap

    def get_pixmap(self) -> QPixmap:
        return self.pixmap


class LayersPreset:
    def __init__(self,
                 layer_params: dict[str, tuple[int, float]],
                 ) -> None:
        layer_order = dict()
        self.layers = sorted(layer_order.keys(), key=lambda k: layer_order[k])
        self.layer_default_opacities = dict()
        self.layer_current_opacities = dict()
        for key, values in layer_params.items():
            self.layer_default_opacities[key] = values[1]
            self.layer_current_opacities[key] = values[1]
            layer_order[key] = values[0]
        self.layers = sorted(layer_order.keys(), key=lambda k: layer_order[k])
