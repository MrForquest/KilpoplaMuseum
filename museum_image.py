import re


class MuseumImage:
    def __init__(self, filename, pixmap, default_opacity):
        self.filename = filename
        self.pixmap = pixmap
        self.filename = filename
        self.default_opacity = default_opacity
        self.current_opacity = default_opacity
        pattern = r"image_(?P<index>\d+)*"
        match = re.match(pattern, filename)
        ## todo refactoring
        assert match, "Wrong filename of image"
        self.index = int(match.group("index"))

    def set_opacity(self, opacity):
        self.current_opacity = opacity

    def get_opacity(self):
        return self.current_opacity

    def get_default_opacity(self):
        return self.default_opacity

    def get_pixmap(self):
        return self.pixmap

    def get_index(self):
        return self.index

# class LayersPreset:
#     def __init__(self, ):
