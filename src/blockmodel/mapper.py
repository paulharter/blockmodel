import os
from blockmodel.constants import *

THIS_DIR = os.path.dirname(__file__)
RESOURCES_ROOT = os.path.join(os.path.dirname(__file__), "resources")


class MinecraftBlock(object):

    def __init__(self, attrs):
        #print attrs
        self.commonname = attrs[0]
        self.block_id = int(attrs[1])
        self.block_data = int(attrs[2]) if attrs[2] != "" else None
        self.name = attrs[3]
        self.uv = (int(attrs[5]), int(attrs[6]))
        self.texname = attrs[7]
        self.top_uv = (int(attrs[9]), int(attrs[10])) if attrs[9] != "" else None
        self.top_texname = attrs[11] if attrs[11] != "" else None
        self.bottom_uv = (int(attrs[13]), int(attrs[14])) if attrs[13] != "" else None
        self.bottom_texname = attrs[15] if attrs[15] != "" else None

    def get_index(self):
        if self.block_data is None:
            return self.block_id
        else:
            return self.block_id, self.block_data

    def get_block_type(self):
        if self.block_id in HALFSLAB_BLOCKS:
            return "halfslab"
        if self.block_id in STAIR_BLOCKS:
            return "stair"
        return "cube"

    def __str__(self):
        return "%s block" % self.commonname

    block_type = property(get_block_type)


class MinecraftBlockMapper(object):

    def __init__(self):
        self.lu = {}

        blocks_csv = os.path.join(RESOURCES_ROOT, "blocks.csv")
        f = open(blocks_csv, "r")

        for b in f.readlines():
            attrs = b.split(",")
            try:
                block = MinecraftBlock(attrs)
                self.lu[block.get_index()] = block
            except ValueError:
                #print "fucked up %s %s" % (attrs, e)
                pass
        f.close()

    def can_render(self, block_id, block_data):
        block = self.lu.get(block_id)
        if not block:
            block = self.lu.get((block_id, block_data))
        return block is not None

    def get_block(self, x, y, z, accessor):
        block_id, block_data = accessor.get(x, y, z)
        block = self.lu.get(block_id)
        if not block:
            block = self.lu.get((block_id, block_data))
        return block

    def is_blank(self, x, y, z, xd, yd, zd, accessor):

        block_id, block_data = accessor.get(x, y, z)
        #print block_id, block_data
        block = self.lu.get(block_id)

        if not block:
            block = self.lu.get((block_id, block_data))

        #print "block", block
        if not block:
            #print "failed to find %s %s" % (block_id, block_data)
            #print self.lu.keys()
            return True

        if block.block_type == "cube":
            return False

        if block.block_type == "halfslab":
            if block_data < 8:
                return yd == 0.5
            else:
                return yd == 0.0

        if block.block_type == "stair":

            xx = int(2.0 * xd)
            yy = int(2.0 * yd)
            zz = int(2.0 * zd)

            missingblocks = self.get_missing_blocks(block_data)
            behindx = missingblocks[2][0]
            behindz = missingblocks[2][1]

            ##now horrid messing around to do the corners
            if (xx, yy, zz) in missingblocks:
                blank = True
                blockbehind_id, blockbehind_data = accessor.get(x - behindx, y, z - behindz)
                if blockbehind_id in STAIR_BLOCKS:
                    #if they are the same way up
                    if (block_data < 4) == (blockbehind_data < 4):
                        #see if the block quadrant behind is solid
                        behindmissingblocks = self.get_missing_blocks(blockbehind_data)
                        if (xx + behindx, yy, zz + behindz) not in behindmissingblocks:
                            blank = False
            else:
                blank = False
                blockbehind_id, blockbehind_data = accessor.get(x + behindx, y, z + behindz)
                if blockbehind_id in STAIR_BLOCKS:
                    #if they are the same way up
                    if (block_data < 4) == (blockbehind_data < 4):
                        #see if the block quadrant behind is blank
                        behindmissingblocks = self.get_missing_blocks(blockbehind_data)
                        if (xx - behindx, yy, zz - behindz) in behindmissingblocks:
                            blank = True
            return blank
        return True

    def get_missing_blocks(self, block_data):

            missingblockslu = (((0, 1, 0), (0, 1, 1), (1, 0)),#east
                                ((1, 1, 1), (1, 1, 0), (-1, 0)),#west
                                ((0, 1, 0), (1, 1, 0), (0, 1)),#south
                                ((1, 1, 1), (0, 1, 1), (0, -1)),#north
                                ((0, 0, 0), (0, 0, 1), (1, 0)),#east
                                ((1, 0, 1), (1, 0, 0), (-1, 0)),#west
                                ((0, 0, 0), (1, 0, 0), (0, 1)),#south
                                ((1, 0, 1), (0, 0, 1), (0, -1)))

            return missingblockslu[block_data]

    def get_tex_uv(self, block, side):
        if side == SIDE_TOP and block.top_uv is not None:
            return block.top_uv
        if side == SIDE_BOTTOM and block.bottom_uv is not None:
            return block.bottom_uv
        return block.uv