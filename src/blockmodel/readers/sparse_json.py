import json

from .base import BaseModelReader


class SparseJsonModelReader(BaseModelReader):

    def __init__(self, as_json_str, max_size):
        self.as_list = json.loads(as_json_str)
        positions = [[b[0],b[1],b[2]] for b in self.as_list]

        xyz = list(zip(*positions))

        self.max_x = max(xyz[0])
        self.min_x = min(xyz[0])
        self.max_y = max(xyz[1])
        self.min_y = min(xyz[1])
        self.max_z = max(xyz[2])
        self.min_z = min(xyz[2])

        self.as_dict = {}

        for b in self.as_list:
            position = (b[0],b[1],b[2])
            block = (b[3],b[4])
            self.as_dict[position] = block

        self.width = (self.max_x - self.min_x) + 1
        self.height = (self.max_y - self.min_y) + 1
        self.depth = (self.max_z - self.min_z) + 1

        self.check_size(max_size)


    def get(self, x, y, z):
        block = self.as_dict.get((x+self.min_x, y+self.min_y, z+self.min_z))
        if block is None:
            return 0, 0
        return block