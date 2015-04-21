import json
import time
import sys
import os
from io import BytesIO
from stl_writer import Binary_STL_Writer
from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('printbot.block_model', 'templates'))
from . import png
from nbt import nbt
import numpy as np

THIS_DIR = os.path.dirname(__file__)

RESOURCES_ROOT = os.path.join(os.path.dirname(__file__), "resources")
    
MAX_DIM = 160
    
SIDE_TOP    = 0
SIDE_BOTTOM = 1
SIDE_LEFT   = 2
SIDE_RIGHT  = 3
SIDE_FRONT  = 4
SIDE_BACK   = 5

ALL_SIDES = (0,1,2,3,4,5)

HALFSLAB_BLOCKS = (44, 126)
STAIR_BLOCKS = (53, 67, 108, 109, 114, 128, 134, 135, 136, 156)


STAIR_EAST = 0
STAIR_WEST = 1
STAIR_SOUTH = 2
STAIR_NORTH = 3
STAIR_EAST_UD = 4
STAIR_WEST_UD = 5
STAIR_SOUTH_UD = 6
STAIR_NORTH_UD = 7


#unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
    x = np.linalg.det([[1,a[1],a[2]],
         [1,b[1],b[2]],
         [1,c[1],c[2]]])
    y = np.linalg.det([[a[0],1,a[2]],
         [b[0],1,b[2]],
         [c[0],1,c[2]]])
    z = np.linalg.det([[a[0],a[1],1],
         [b[0],b[1],1],
         [c[0],c[1],1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x/magnitude, y/magnitude, z/magnitude)

#area of polygon poly
def poly_area(poly):
    if len(poly) < 3: # not a plane - no area
        return 0
    total = [0, 0, 0]
    N = len(poly)
    for i in range(N):
        vi1 = poly[i]
        vi2 = poly[(i+1) % N]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result/2)

class MinecraftBlock(object):
    
    def __init__(self, attrs):
        #print attrs
        self.commonname = attrs[0]
        self.block_id = int(attrs[1])
        self.block_data = int(attrs[2]) if attrs[2] != "" else None
        self.name =  attrs[3]
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
            return (self.block_id, self.block_data)
        
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
                id = int(attrs[1])
                block = MinecraftBlock(attrs)
              
                self.lu[block.get_index()] = block
            except ValueError, e:
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
                                ((1, 0, 1), (0, 0, 1), (0, -1))#north
                                )
            
            return missingblockslu[block_data]
            
    def get_tex_uv(self, block, side):
        if side == SIDE_TOP and block.top_uv != None:
            return block.top_uv
        if side == SIDE_BOTTOM and block.bottom_uv != None:
            return block.bottom_uv
        return block.uv
    
    
class ModelAccessor(object):
    
    def get(self, x, y, z):
        return 0, 0
    
    
class PngModelAccessor(object):
    
    def __init__(self, as_png):
        reader = png.Reader(bytes=as_png)
        self.width, self.depth, self.as_array, self.meta = reader.read_flat()
        self.height = 1
    
    def get(self, x, y, z):
        if(x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth):
            return 0, 0
        pixel = self.meta["planes"] * ((z * self.width) + x)
        red_value = self.as_array[pixel]
        block = 2 if red_value == 255 else 43
        data = 0 if red_value == 255 else 4
        return block, data     
          
          
class JsonModelAccessor(object):
    
    def __init__(self, as_json_str):
        self.as_array = json.loads(as_json_str)
        self.width = len(self.as_array)
        self.height = len(self.as_array[0])
        self.depth = len(self.as_array[0][0])
    
    def get(self, x, y, z):
        if(x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth):
            return 0, 0
        block = self.as_array[x][y][z][0]
        data = self.as_array[x][y][z][1]
        return block, data    
    
    
class SparseJsonModelAccessor(object):
    
    def __init__(self, as_json_str):
        self.as_list = json.loads(as_json_str)
        positions, _blocks = zip(*self.as_list)
        
        xyz = zip(*positions)

        self.max_x = max(xyz[0])
        self.min_x = min(xyz[0])
        self.max_y = max(xyz[1])
        self.min_y = min(xyz[1])
        self.max_z = max(xyz[2])
        self.min_z = min(xyz[2])

        self.as_dict = {}
        
        for position, block in self.as_list:
            self.as_dict[tuple(position)] = tuple(block)

        self.width = (self.max_x - self.min_x) + 1
        self.height = (self.max_y - self.min_y) + 1
        self.depth = (self.max_z - self.min_z) + 1
    
    def get(self, x, y, z):
        block = self.as_dict.get((x+self.min_x, y+self.min_y, z+self.min_z))
        if block is None:
            return 0, 0
        return block
    
    
class SchematicModelAccessor(object):
    
    def __init__(self, schematic_file_path):

        nbtfile = nbt.NBTFile(schematic_file_path)
            
        self.width = nbtfile[u"Width"].value
        self.height = nbtfile[u"Height"].value
        self.depth = nbtfile[u"Length"].value      

        
        if self.width > MAX_DIM or self.height > MAX_DIM or self.depth > MAX_DIM:
            raise Exception("model too big")
        
        self.blocks = nbtfile[u"Blocks"]
        self.data = nbtfile[u"Data"]

 
    def get(self, x, y, z):
        if(x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.depth):
            return 0, 0
        block = self.blocks[self.width * self.depth * y + self.width * z + x]
        data = self.data[self.width * self.depth * y + self.width * z + x]
        return block, data  
    
    

class BlockModel(object):
    
    def __init__(self, accessor, name, label):
        self.vertices = {}
        self.faces = []
        self.name = name
        self.label = label
        self.texUvMappingsArray = []
        self.volume = 0
        self.surface = 0
    
        lines = []
        
        for y in range(33):
            for x in range(33):
                lines.append("vt %.5f %.5f" % (x/32.0, y/32.0))
                self.texUvMappingsArray.append((x/32.0, y/32.0))
        self.uv_mappings = "\n".join(lines)
    
        self.accessor = accessor
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000000", time.gmtime())
        self.width = self.accessor.width
        self.height = self.accessor.height
        self.depth = self.accessor.depth
        self.max_x =  None
        self.min_x =  None
        self.max_y =  None
        self.min_y =  None
        self.max_z =  None
        self.min_z =  None
        self.scale = 2
        self.stl_scale = 2.0
        self.xoffset = -self.width/2.0
        self.yoffset = 0
        self.zoffset = -self.depth/2.0
        self.faces = []
        self.stl_faces = []
        self.block_mapper = MinecraftBlockMapper()
        self._process()
        self._make_stl()

        
        
    @classmethod
    def from_json(cls, as_json, name="", label=""):
        return cls(JsonModelAccessor(as_json), name, label)
    
    @classmethod
    def from_png(cls, as_png, name="", label=""):
        return cls(PngModelAccessor(as_png), name, label)
    
    @classmethod
    def from_sparse_json(cls, as_json, name="", label=""):
        return cls(SparseJsonModelAccessor(as_json), name, label)
        
    @classmethod
    def from_schematic(cls, schematic, name="", label=""):
        return cls(SchematicModelAccessor(schematic), name, label)
    
        
    def _is_blank_quadrant(self, x, y, z, xd, yd, zd, side):
        
        q = 0.5
        x1 = x
        y1 = y
        z1 = z
        xd1 = xd
        yd1 = yd
        zd1 = zd

        if side == SIDE_TOP:
            if (y + yd == self.height - q):return True
            if yd == 0.0:
                yd1 = 0.5
            if yd == 0.5:
                yd1 = 0.0
                y1 = y + 1
        if side == SIDE_BOTTOM:
            if (y + yd == 0):return True
            if yd == 0.0:
                yd1 = 0.5
                y1 = y - 1
            if yd == 0.5:
                yd1 = 0.0
        if side == SIDE_RIGHT:
            if (x + xd == self.width - q):return True
            if xd == 0.0:
                xd1 = 0.5
            if xd == 0.5:
                xd1 = 0.0
                x1 = x + 1
        if side == SIDE_LEFT:
            if (x + xd == 0):return True
            if xd == 0.0:
                x1 = x - 1
                xd1 = 0.5
            if xd == 0.5:
                xd1 = 0.0
        if side == SIDE_FRONT:
            if (z + zd == self.depth - q):return True
            if zd == 0.0:
                zd1 = 0.5
            if zd == 0.5:
                zd1 = 0.0
                z1 = z + 1
        if side == SIDE_BACK:
            if (z + zd == 0):return True
            if zd == 0.0:
                zd1 = 0.5
                z1 = z - 1
            if zd == 0.5:
                zd1 = 0.0
                
        return self.block_mapper.is_blank(x1, y1, z1, xd1, yd1, zd1, self.accessor) 
        
        
    def _render_partial_face(self, block, x, y, z, side):
        
        d = 0.5
        
        if side == SIDE_TOP:
            xd1 = 0.0
            yd1 = 0.5
            zd1 = 0.0
            xd2 = 0.0
            yd2 = 0.5
            zd2 = 0.5
            xd3 = 0.5
            yd3 = 0.5
            zd3 = 0.0
            xd4 = 0.5
            yd4 = 0.5
            zd4 = 0.5
            
        if side == SIDE_BOTTOM:
            xd1 = 0.0
            yd1 = 0.0
            zd1 = 0.0
            xd2 = 0.0
            yd2 = 0.0
            zd2 = 0.5
            xd3 = 0.5
            yd3 = 0.0
            zd3 = 0.0
            xd4 = 0.5
            yd4 = 0.0
            zd4 = 0.5
            
        if side == SIDE_RIGHT:
            xd1 = 0.5
            yd1 = 0.0
            zd1 = 0.0
            xd2 = 0.5
            yd2 = 0.5
            zd2 = 0.0
            xd3 = 0.5
            yd3 = 0.0
            zd3 = 0.5
            xd4 = 0.5
            yd4 = 0.5
            zd4 = 0.5
            
        if side == SIDE_LEFT:
            xd1 = 0.0
            yd1 = 0.0
            zd1 = 0.0
            xd2 = 0.0
            yd2 = 0.5
            zd2 = 0.0
            xd3 = 0.0
            yd3 = 0.0
            zd3 = 0.5
            xd4 = 0.0
            yd4 = 0.5
            zd4 = 0.5
            
        if side == SIDE_FRONT:
            xd1 = 0.0
            yd1 = 0.0
            zd1 = 0.5
            xd2 = 0.5
            yd2 = 0.0
            zd2 = 0.5
            xd3 = 0.0
            yd3 = 0.5
            zd3 = 0.5
            xd4 = 0.5
            yd4 = 0.5
            zd4 = 0.5
            
        if side == SIDE_BACK:
            xd1 = 0.0
            yd1 = 0.0
            zd1 = 0.0
            xd2 = 0.5
            yd2 = 0.0
            zd2 = 0.0
            xd3 = 0.0
            yd3 = 0.5
            zd3 = 0.0
            xd4 = 0.5
            yd4 = 0.5
            zd4 = 0.0

        self._render_face_quadrant(block, x, y, z, xd1, yd1, zd1, side, d)
        self._render_face_quadrant(block, x, y, z, xd2, yd2, zd2, side, d)
        self._render_face_quadrant(block, x, y, z, xd3, yd3, zd3, side, d)
        self._render_face_quadrant(block, x, y, z, xd4, yd4, zd4, side, d)

    def _renderface(self, block, x, y, z, side):
        
        if side == SIDE_TOP:
            other_block = self._get_block(x, y+1, z)
        if side == SIDE_BOTTOM:
            other_block = self._get_block(x, y-1, z)
        if side == SIDE_RIGHT:
            other_block = self._get_block(x+1, y, z)
        if side == SIDE_LEFT:
            other_block = self._get_block(x-1, y, z)
        if side == SIDE_FRONT:
            other_block = self._get_block(x, y, z+1)
        if side == SIDE_BACK:
            other_block = self._get_block(x, y, z-1)

        if block.block_type == "cube":
            if other_block is None:
                self._add_face(self._get_face_corners(x, y, z, side), block, side)
            else:
                if other_block.block_type != "cube":
                    self._render_partial_face(block, x, y, z, side)
        else:
            self._render_partial_face(block, x, y, z, side)
            
            
    def _get_face_corners(self, x, y, z, side):
        if side == SIDE_TOP:
            return ((x, y + 1, z), (x, y + 1, z + 1), (x + 1, y + 1, z + 1), (x + 1, y + 1, z))
        if side == SIDE_BOTTOM:
            return ((x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1), (x, y , z))
        if side == SIDE_RIGHT:
            return ((x + 1, y + 1, z + 1) , (x + 1, y, z + 1), (x + 1, y, z), (x + 1, y + 1 , z))
        if side == SIDE_LEFT:
            return ((x, y + 1 , z) , (x, y, z), (x, y, z + 1), (x, y + 1, z + 1))
        if side == SIDE_FRONT:
            return ((x, y + 1 , z + 1), (x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1))
        if side == SIDE_BACK:
            return ((x + 1, y + 1, z), (x + 1, y, z), (x, y, z), (x, y + 1 , z))
  
            
    def _get_block(self, x, y, z):
        return self.block_mapper.get_block(x, y, z, self.accessor)

        
    def _render_block(self, block, x, y, z):

        block_volume = self.stl_scale ** 3

        if block.block_type == "cube":
            self.volume += block_volume
            for side in ALL_SIDES:
                self._renderface(block, x, y, z, side)
        else:

            if block.block_type == "halfslab":
                self.volume += block_volume/2.0

            if block.block_type == "stair":
                self.volume += (block_volume * 3.0)/4.0

            self._render_block_sub_blocks(block, x, y, z)


    def _get_quadrant_corners_quads(self, x, y, z, xd, yd, zd, side, d):
        xx = x + xd
        yy = y + yd
        zz = z + zd
        #top
        if side == SIDE_TOP:
            A = (xx, yy + d, zz)
            B = (xx, yy + d, zz + d)
            C = (xx + d, yy + d, zz + d)
            D = (xx + d, yy + d, zz)
            quad_x = int(xd * 2.0)
            quad_y = 1 - int(zd * 2.0)
        #bottom
        if side == SIDE_BOTTOM:
            A = (xx + d, yy, zz)
            B = (xx + d, yy, zz + d)
            C = (xx, yy, zz + d)
            D = (xx, yy, zz)
            quad_x = 1 - int(xd * 2.0)
            quad_y = 1 - int(zd * 2.0)
        #right
        if side == SIDE_RIGHT:
            A = (xx + d, yy + d, zz + d)
            B = (xx + d, yy, zz + d)
            C = (xx + d, yy, zz)
            D = (xx + d, yy + d, zz)
            quad_x = 1 - int(zd * 2.0)
            quad_y = int(yd * 2.0)
        #left
        if side == SIDE_LEFT:
            A = (xx, yy + d, zz)
            B = (xx, yy, zz)
            C = (xx, yy, zz + d)
            D = (xx, yy + d, zz + d)
            quad_x = int(zd * 2.0)
            quad_y = int(yd * 2.0)
        #front
        if side == SIDE_FRONT:
            A = (xx, yy + d, zz + d)
            B = (xx, yy, zz + d)
            C = (xx + d, yy, zz + d)
            D = (xx + d, yy + d, zz + d)
            quad_x = int(xd * 2.0)
            quad_y = int(yd * 2.0)
        #back
        if side == SIDE_BACK:
            A = (xx + d, yy + d, zz)
            B = (xx + d, yy, zz)
            C = (xx, yy, zz)
            D = (xx, yy + d, zz)
            quad_x = 1 - int(xd * 2.0)
            quad_y = int(yd * 2.0)

        return (A, B, C, D), quad_x, quad_y
    

    def _render_face_quadrant(self, block, x, y, z, xd, yd, zd, side, d):
        if not self._is_blank_quadrant(x, y, z, xd, yd, zd, side):
            return
        corners, quad_x, quad_y = self._get_quadrant_corners_quads(x, y, z, xd, yd, zd, side, d)
        self._add_face(corners, block, side, quad_x, quad_y)


    def _render_block_sub_blocks(self, block, x, y, z):
        d = 0.5
        for xd in (0.0, d):
            for yd in  (0.0, d):
                for zd in  (0.0, d):
                    if self.block_mapper.is_blank(x, y, z, xd, yd, zd, self.accessor):continue
                    for side in ALL_SIDES:
                        self._render_face_quadrant(block, x, y, z, xd, yd, zd, side, d)


    def _check_min_max(self, points):

        for p in points:
            x, y, z = p
            if self.max_x is None or x > self.max_x:
                self.max_x = x
            if self.min_x is None or x < self.min_x:
                self.min_x = x

            if self.max_y is None or y > self.max_y:
                self.max_y = y
            if self.min_y is None or y < self.min_y:
                self.min_y = y

            if self.max_z is None or z > self.max_z:
                self.max_z = z
            if self.min_z is None or z < self.min_z:
                self.min_z = z


    def _add_face(self, corners, block, side, quad_x=None, quad_y=None):

        scaled_stl = [((c[0] + self.xoffset) * self.stl_scale, -(c[2] + self.zoffset) * self.stl_scale, c[1] * self.stl_scale) for c in corners]
        self.surface += poly_area(scaled_stl)
        self._check_min_max(scaled_stl)

        scaled_obj = [((c[0] + self.xoffset) * self.scale, c[1] * self.scale, (c[2] + self.zoffset) * self.scale) for c in corners] 
        tex_x, tex_y = self.block_mapper.get_tex_uv(block, side)
        self._add_corners(scaled_obj, tex_x, tex_y, quad_x, quad_y)
        self.stl_faces.append(scaled_stl)
        
    def _process(self):
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    block = self._get_block(x, y, z)
                    if block is not None:
                        self._render_block(block, x, y, z)
                           
                                      
    def _make_stl(self):
        output = BytesIO()
        stlwriter = Binary_STL_Writer(output)
        stlwriter.add_faces(self.stl_faces)
        stlwriter.close()
        stl = output.getvalue()
        output.close()
        self.stl = stl
        

    def _get_ordered_vertices(self):
        ordered_vertices = [None] * len(self.vertices)
        for k, v in self.vertices.iteritems():
            ordered_vertices[v] = k
        return ordered_vertices
    
    
    def _as_x3d_faces(self):
        
        attrs = {}
        ordered_vertices = self._get_ordered_vertices()
        vertix_lines = ["%.5g %.5g %.5g" % v for v in ordered_vertices]
        coordIndex = ["%i %i %i %i %i %i %i %i" % (f[0] - 1, f[2] - 1, f[4] - 1, -1, f[0] - 1, f[4] - 1, f[6] - 1, -1) for f in self.faces]
        texCoordIndex =  ["%i %i %i %i %i %i %i %i" % (f[1] - 1, f[3] - 1, f[5] - 1, -1, f[1] - 1, f[5] - 1, f[7] - 1, -1) for f in self.faces]
        
        attrs["coordinate_point"] = " ".join(vertix_lines)
        attrs["coord_index"] = " ".join(coordIndex)
        attrs["tex_coord_index"] = " ".join(texCoordIndex)
        attrs["timestamp"] = self.timestamp
        template = jinja_env.get_template("x3d_faces.xml")
        as_x3d = template.render(attrs)

        return str(as_x3d)
    
    
    def _as_x3d_triangles(self):
        
        attrs = {}
        ov = self._get_ordered_vertices()
        tx = self.texUvMappingsArray

        # each face is a pair of triangles
        index = [ str(i) for i in range(len(self.faces) * 6)]
        
        allTheCoordPoints = []
        allTheTexCoordPoints = []
        
        for f in self.faces:
            allTheCoordPoints.append(ov[f[0] - 1])
            allTheCoordPoints.append(ov[f[2] - 1])
            allTheCoordPoints.append(ov[f[4] - 1])
            allTheCoordPoints.append(ov[f[0] - 1])
            allTheCoordPoints.append(ov[f[4] - 1])
            allTheCoordPoints.append(ov[f[6] - 1])
            
            allTheTexCoordPoints.append(tx[f[1] - 1])
            allTheTexCoordPoints.append(tx[f[3] - 1])
            allTheTexCoordPoints.append(tx[f[5] - 1])
            allTheTexCoordPoints.append(tx[f[1] - 1])
            allTheTexCoordPoints.append(tx[f[5] - 1])
            allTheTexCoordPoints.append(tx[f[7] - 1])
            
        coordPoints =  ["%.5g %.5g %.5g" % cp for cp in allTheCoordPoints]
        texCoordPoints =  ["%.5g %.5g" % tp for tp in allTheTexCoordPoints]

        attrs["coordinate_point"] = " ".join(coordPoints)
        attrs["index"] = " ".join(index)
        attrs["tex_coord_point"] = " ".join(texCoordPoints)
        attrs["timestamp"] = self.timestamp
        template = jinja_env.get_template("x3d_triangles.xml")
        as_x3d = template.render(attrs)

        return str(as_x3d)


    def _as_csv(self):
        lines = []
        for z in range(self.depth + 1):
            blocks = []
            for x in range(self.width + 1):
                for y in range(self.height + 1):
                    block_id, block_data = self.accessor.get(x, self.height - y, z)
                    
                    if block_id != 0:
                        blocks.append("%s:%s" % (block_id, block_data))
                        continue
                blocks.append(",")
            lines.append("".join(blocks))
            lines.append("\n")
        
        return "".join(lines)

        
    def _as_schematic(self):
        
        nbtfile = nbt.NBTFile()
        
        nbtfile.name = "Schematic"
        
        nbtfile.tags.append(nbt.TAG_Short(name="Height", value=self.height))
        nbtfile.tags.append(nbt.TAG_Short(name="Width", value=self.width))
        nbtfile.tags.append(nbt.TAG_Short(name="Length", value=self.depth))
        
        nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetX", value=-1))
        nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetY", value=0))
        nbtfile.tags.append(nbt.TAG_Int(name="WEOffsetZ", value=-1))
        nbtfile.tags.append(nbt.TAG_Int(name="WEOriginX", value=0))
        nbtfile.tags.append(nbt.TAG_Int(name="WEOriginY", value=0))
        nbtfile.tags.append(nbt.TAG_Int(name="WEOriginZ", value=0))
        
        # YZX ordering
       
        data = bytearray()
        blocks = bytearray()
      
        for y in range(self.height):
            for z in range(self.depth):
                for x in range(self.width):
                    block_id, block_data = self.accessor.get(x, y, z)
                    blocks.append(block_id)
                    data.append(block_data)
           
        blocks_tag = nbt.TAG_Byte_Array()
        blocks_tag.value = blocks

        data_tag = nbt.TAG_Byte_Array()
        data_tag.value = data
        
        nbtfile["Blocks"] = blocks_tag
        nbtfile["Data"] = data_tag
        
        nbtfile.tags.append(nbt.TAG_String(name="Materials", value=u"Alpha"))
        nbtfile["Entities"] = nbt.TAG_List(type=nbt.TAG_Compound)
        nbtfile["TileEntities"] = nbt.TAG_List(type=nbt.TAG_Compound)
        
        output = BytesIO()
        nbtfile.write_file(fileobj = output)
        as_nbt = output.getvalue()
        output.close()
        
        return as_nbt
        

    def _as_collada(self):
        
        attrs = {}
        ordered_vertices = self._get_ordered_vertices()
        vertix_lines = ["%.5g %.5g %.5g" % v for v in ordered_vertices]
        zeroindexfaces = [[x-1 for x in f] for f in self.faces]
        face_lines = ["%i %i %i %i %i %i %i %i" % tuple(f) for f in zeroindexfaces]
        attrs["obj_vertex_source_array"] = " ".join(vertix_lines)
        attrs["obj_vertex_source_array_accessor_count"] = str( len(ordered_vertices))
        attrs["obj_vertex_source_array_count"] = str(len(ordered_vertices) * 3)
        attrs["obj_uv_source_array"] = " ".join(["%.5g %.5g" % uv for uv in self.texUvMappingsArray])
        attrs["polylist_p"] = " ".join(face_lines)
        attrs["vcount"] = " ".join("4" * len(self.faces))
        attrs["polylist_count"] = str(len(self.faces))
        attrs["timestamp"] = self.timestamp
        template = jinja_env.get_template("collada2.xml")
        as_col = template.render(attrs)
        return str(as_col)


    def _as_obj(self):
        
        ordered_vertices = self._get_ordered_vertices()
        vertix_lines = ["v %.5f %.5f %.5f" % v for v in ordered_vertices]
        face_lines = ["f %i/%i %i/%i %i/%i %i/%i" % tuple(f) for f in self.faces]
        
        objstr = "#A printcraft model\n"
        objstr += "mtllib printcraft.mtl\n"
        objstr += "o printcraft-model\n"
        objstr += "\n".join(vertix_lines)
        objstr += "\n"
        objstr += self.uv_mappings
        objstr += "\ng blocks\n"
        objstr += "usemtl minecraftblocks\n"
        objstr += "s off\n"
        objstr += "\n".join(face_lines)
        return objstr
    

    def _add_corners(self, corners, tex_x, tex_y, quad_x=None, quad_y=None):
        faceinfo = []
        for counter, corner in enumerate(corners):
            i = self.vertices.get(corner)
            if i is None:
                i = len(self.vertices)
                self.vertices[corner] = i
            faceinfo.append(i + 1)
            faceinfo.append(self._get_vt_index(counter, tex_x, tex_y, quad_x, quad_y))
        self.faces.append(faceinfo)
        
        
    def _get_vt_index(self, corner, blockx, blocky, quad_x=None, quad_y=None):

        x = blockx * 2
        y = blocky * 2
        if quad_x: x += quad_x
        if quad_y: y += quad_y
        
        if quad_x == None:
            if corner == 0:
                return ((y + 2) * 33) + x + 1
            if corner == 1:
                return ((y) * 33) + x + 1
            if corner == 2:
                return ((y) * 33) + x + 3
            if corner == 3:
                return ((y + 2) * 33) + x + 3
        
        elif quad_x == 0.5:
            if corner == 0:
                return ((y + 1) * 33) + x + 1
            if corner == 1:
                return ((y) * 33) + x + 1
            if corner == 2:
                return ((y) * 33) + x + 2
            if corner == 3:
                return ((y + 1) * 33) + x + 2
        else:
            if corner == 0:
                return ((y + 1) * 33) + x + 1
            if corner == 1:
                return ((y) * 33) + x + 1
            if corner == 2:
                return ((y) * 33) + x + 2
            if corner == 3:
                return ((y + 1) * 33) + x + 2  


    def _get_content_width(self):
        return self.max_x - self.min_x


    def _get_content_height(self):
        return self.max_y - self.min_y


    def _get_content_depth(self):
        return self.max_z - self.min_z


    obj = property(_as_obj)
    x3d = property(_as_x3d_triangles)
    x3d_triangles = property(_as_x3d_triangles)
    x3d_faces = property(_as_x3d_faces)
    collada = property(_as_collada)
    csv = property(_as_csv)
    schematic = property(_as_schematic)
    content_width = property(_get_content_width)
    content_height = property(_get_content_height)
    content_depth = property(_get_content_depth)
