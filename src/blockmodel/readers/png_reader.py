
from .base import BaseModelReader
from . import png


class PngModelReader(BaseModelReader):

    def __init__(self, as_png, max_size):
        reader = png.Reader(bytes=as_png)
        self.width, self.depth, self.as_array, self.meta = reader.read_flat()
        self.height = 1
        self.check_size(max_size)


    def get(self, x, y, z):
        if(x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth):
            return 0, 0
        pixel = self.meta["planes"] * ((z * self.width) + x)
        red_value = self.as_array[pixel]
        block = red_value
        data = 0
        return block, data