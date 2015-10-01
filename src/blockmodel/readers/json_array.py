import json
from .base import BaseModelReader


class JsonModelReader(BaseModelReader):

    def __init__(self, as_json_str, max_size):
        self.as_array = json.loads(as_json_str)
        self.width = len(self.as_array)
        self.height = len(self.as_array[0])
        self.depth = len(self.as_array[0][0])
        self.check_size(max_size)

    def get(self, x, y, z):
        if x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth:
            return 0, 0
        block = self.as_array[x][y][z][0]
        data = self.as_array[x][y][z][1]
        return block, data