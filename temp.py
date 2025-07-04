import re

filename = "image_110sada.jpgdadasdads"
pattern = r"image_(?P<index>\d+)*"
match = re.match(pattern, filename)
if match:
    print(type(match.group("index")))