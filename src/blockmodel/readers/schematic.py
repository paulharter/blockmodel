
from nbt import nbt
from .base import BaseModelReader

class SchematicModelReader(BaseModelReader):

    def __init__(self, schematic_file_path, max_size):

        nbtfile = nbt.NBTFile(schematic_file_path)

        self.width = nbtfile[u"Width"].value
        self.height = nbtfile[u"Height"].value
        self.depth = nbtfile[u"Length"].value
        self.check_size(max_size)
        self.blocks = nbtfile[u"Blocks"]
        self.data = nbtfile[u"Data"]



    def get(self, x, y, z):
        if(x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth):
            return 0, 0
        block = self.blocks[self.width * self.depth * y + self.width * z + x]
        data = self.data[self.width * self.depth * y + self.width * z + x]
        return block, data