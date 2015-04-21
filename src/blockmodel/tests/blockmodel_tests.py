import os
import shutil
import json
import unittest
from lxml import etree

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MADE_DIR = os.path.join(DATA_DIR, "made")

from blockmodel import BlockModel


def data_path(pth):
    return os.path.join(DATA_DIR, pth)


class BlockModelTestCase(unittest.TestCase):

    def setUp(self):
        if not os.path.exists(MADE_DIR):
            os.makedirs(MADE_DIR)

    def tearDown(self):
        shutil.rmtree(MADE_DIR)

    def assertFileMatches(self, ref_path, made_path):

        with open(data_path(ref_path), "rb") as src_f:
            with open(data_path(made_path), "rb") as dst_f:
                self.assertEqual(src_f.read(), dst_f.read(), "Files don't match %s %s" % (ref_path, made_path))

    def test_stl(self):
      
        f = file(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()
        
        blockmodel = BlockModel.from_json(as_json)

        stl = blockmodel.stl
        
        f = file(data_path("made/stl_ref.stl"), "wb")
        f.write(stl)
        f.close()
        
        f = file(data_path("ref/stl_ref.stl"), "r")
        refstl = f.read()
        f.close()

        self.maxDiff = None
        self.assertEqual(refstl, stl)


    def test_schematic(self):

        blockmodel = BlockModel.from_schematic_file(data_path("ref/test.schematic"))

        x3d = blockmodel.x3d

        f = file(data_path("made/x3d_from_schematic.x3d"), "wb")
        f.write(x3d)
        f.close()



    def test_schematic_too_big(self):

        self.assertRaises(Exception, BlockModel.from_schematic_file, data_path("ref/test.schematic"), max=30)


    def test_schematic_steps(self):

        blockmodel = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        obj = blockmodel.obj
        f = file(data_path("made/cup2.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/cup2.obj", "made/cup2.obj")

        x3d = blockmodel.x3d

        f = file(data_path("made/cup2.x3d"), "wb")
        f.write(x3d)
        f.close()

        # self.assertFileMatches("ref/cup2.x3d", "made/cup2.x3d")

        stl = blockmodel.stl

        f = file(data_path("made/cup2.stl"), "wb")
        f.write(stl)
        f.close()

        self.assertFileMatches("ref/cup2.stl", "made/cup2.stl")

        col = blockmodel.collada

        f = file(data_path("made/cup2.dae"), "wb")
        f.write(col)
        f.close()

        # self.assertFileMatches("ref/cup2.dae", "made/cup2.dae")



    def test_sparse_json(self):

        as_list = [[[7, 4, 2], [2, 0]],
                    [[8, 4, 2], [2, 0]],
                    [[9, 4, 2], [2, 0]],
                    [[9, 4, 3], [2, 0]],
                    [[9, 4, 4], [2, 0]],
                    [[8, 4, 4], [2, 0]],
                    [[7, 4, 4], [2, 0]],
                    [[7, 4, 3], [2, 0]]]


        blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
        stl = blockmodel.stl

        f = file(data_path("made/sparse_test.stl"), "w")
        f.write(stl)
        f.close()

        self.assertFileMatches("ref/sparse_test.stl", "made/sparse_test.stl")

        col = blockmodel.collada
        f = file(data_path("made/sparse_test.dae"), "wb")
        f.write(col)
        f.close()


        csv = blockmodel.csv
        f = file(data_path("made/sparse_test.csv"), "wb")
        f.write(csv)
        f.close()

        self.assertFileMatches("ref/sparse_test.csv", "made/sparse_test.csv")


    def test_sparse_json_to_schematic(self):

        as_list = [[[7, 4, 2], [2, 0]],
                    [[8, 4, 2], [2, 0]],
                    [[9, 4, 2], [2, 0]],
                    [[9, 4, 3], [2, 0]],
                    [[9, 4, 4], [2, 0]],
                    [[8, 4, 4], [2, 0]],
                    [[7, 4, 4], [2, 0]],
                    [[7, 4, 3], [2, 0]]]


        blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
        schematic = blockmodel.schematic

        f = file(data_path("made/sparse_2_schematic_test.schematic"), "wb")
        f.write(schematic)
        f.close()

        blockmodel = BlockModel.from_schematic_file(data_path("made/sparse_2_schematic_test.schematic"))

        obj = blockmodel.obj
        f = file(data_path("made/sparse_obj.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/sparse_obj.obj", "made/sparse_obj.obj")



    def test_png_to_schematic(self):

        f = file(data_path("ref/block.png"), "rb")
        as_png = f.read()
        f.close()

        blockmodel = BlockModel.from_png(as_png)

        schematic = blockmodel.schematic

        f = file(data_path("made/png_2_schematic_test.schematic"), "wb")
        f.write(schematic)
        f.close()

        blockmodel = BlockModel.from_schematic_file(data_path("made/png_2_schematic_test.schematic"))

        obj = blockmodel.obj
        f = file(data_path("made/png_2_obj.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/png_2_obj.obj", "made/png_2_obj.obj")


    def test_collada(self):

        f = file(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()

        blockmodel = BlockModel.from_json(as_json)
        col = blockmodel.collada

        f = file(data_path("made/col_ref.dae"), "wb")
        f.write(col)
        f.close()

        f = file(data_path("ref/col_ref.dae"), "r")
        refcol = f.read()
        f.close()

        self.maxDiff = None
        # self.assertMultiLineEqual(refcol, col)

        f = file("collada_schema_1_4_1.xsd", "r")
        xmlschema_doc = etree.parse(f)
        f.close()
        xmlschema = etree.XMLSchema(xmlschema_doc)

        f = file(data_path("made/col_ref.dae"), "r")
        colxml = etree.parse(f)
        f.close()
        xmlschema.validate(colxml)



    def test_x3d(self):

        f = file(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()

        blockmodel = BlockModel.from_json(as_json)
        x3d = blockmodel.x3d

        f = file(data_path("made/x3d_ref.x3d"), "wb")
        f.write(x3d)
        f.close()

        f = file(data_path("ref/x3d_ref.x3d"), "r")
        refx3d = f.read()
        f.close()

        self.maxDiff = None
        # self.assertMultiLineEqual(refx3d, x3d)

        f = file("x3d-3.2.xsd", "r")
        xmlschema_doc = etree.parse(f)
        f.close()
        xmlschema = etree.XMLSchema(xmlschema_doc)

        f = file(data_path("made/x3d_ref.x3d"), "r")
        x3dxml = etree.parse(f)
        f.close()
        xmlschema.validate(x3dxml)


# class BlockModelGeometryTestCase(unittest.TestCase):
#
#
#
#     def test_surface_area(self):
#
#         # surface area in mm
#         as_list = [[[7, 4, 2], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.surface, 24.0)
#
#
#     def test_surface_area_complex(self):
#
#         as_list = [[[7, 4, 2], [2, 0]],
#                     [[8, 4, 2], [2, 0]],
#                     [[9, 4, 2], [2, 0]],
#                     [[9, 4, 3], [2, 0]],
#                     [[9, 4, 4], [2, 0]],
#                     [[8, 4, 4], [2, 0]],
#                     [[7, 4, 4], [2, 0]],
#                     [[7, 4, 3], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.surface, (8 + 8 + 12 + 4) * 4)
#
#
#     def test_dims(self):
#
#         # surface area in mm
#         as_list = [[[7, 4, 2], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.content_depth, 2.0)
#         self.assertEquals(blockmodel.content_width, 2.0)
#         self.assertEquals(blockmodel.content_height, 2.0)
#
#
#     def test_dims_complex(self):
#
#         as_list = [[[7, 4, 2], [2, 0]],
#                     [[8, 4, 2], [2, 0]],
#                     [[9, 4, 2], [2, 0]],
#                     [[9, 4, 3], [2, 0]],
#                     [[9, 4, 4], [2, 0]],
#                     [[8, 4, 4], [2, 0]],
#                     [[7, 4, 4], [2, 0]],
#                     [[7, 4, 3], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.content_depth, 6.0)
#         self.assertEquals(blockmodel.content_width, 6.0)
#         self.assertEquals(blockmodel.content_height, 2.0)
#
#     def test_volume(self):
#
#         # surface area in mm
#         as_list = [[[7, 4, 2], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.volume, 8.0)
#
#
#     def test_volume_complex(self):
#
#         as_list = [[[7, 4, 2], [2, 0]],
#                     [[8, 4, 2], [2, 0]],
#                     [[9, 4, 2], [2, 0]],
#                     [[9, 4, 3], [2, 0]],
#                     [[9, 4, 4], [2, 0]],
#                     [[8, 4, 4], [2, 0]],
#                     [[7, 4, 4], [2, 0]],
#                     [[7, 4, 3], [2, 0]]]
#
#         blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
#
#         self.assertEquals(blockmodel.volume, 64.0)

if __name__ == '__main__':
    unittest.main()