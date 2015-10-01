import os
import shutil
import json
import unittest
from lxml import etree
# import xml.etree.ElementTree as ET

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MADE_DIR = os.path.join(DATA_DIR, "made")

import blockmodel
from blockmodel import BlockModel


def data_path(pth):
    return os.path.join(DATA_DIR, pth)


class BlockModelTestCase(unittest.TestCase):

    def setUp(self):
        if not os.path.exists(MADE_DIR):
            os.makedirs(MADE_DIR)

    def tearDown(self):
        pass
        # shutil.rmtree(MADE_DIR)

    def assertFileMatches(self, ref_path, made_path):

        with open(data_path(ref_path), "rb") as src_f:
            with open(data_path(made_path), "rb") as dst_f:
                self.assertEqual(src_f.read(), dst_f.read(), "opens don't match %s %s" % (ref_path, made_path))

    def test_stl(self):
      
        f = open(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()
        
        blockmodel = BlockModel.from_json(as_json)

        stl = blockmodel.stl
        
        f = open(data_path("made/stl_ref.stl"), "wb")
        f.write(stl)
        f.close()
        
        f = open(data_path("ref/stl_ref.stl"), "rb")
        refstl = f.read()
        f.close()

        self.maxDiff = None
        self.assertEqual(refstl, stl)


    def test_schematic(self):

        blockmodel = BlockModel.from_schematic_file(data_path("ref/test.schematic"))

        x3d = blockmodel.x3d

        f = open(data_path("made/x3d_from_schematic.x3d"), "w")
        f.write(x3d)
        f.close()


    def test_schematic_2(self):

        blockmodel = BlockModel.from_schematic_file(data_path("ref/new5.schematic"))

        x3d = blockmodel.x3d

        f = open(data_path("made/bum.x3d"), "w")
        f.write(x3d)
        f.close()





    def test_schematic_too_big(self):

        self.assertRaises(Exception, BlockModel.from_schematic_file, data_path("ref/test.schematic"), max=30)


    def test_schematic_steps(self):

        blockmodel = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        obj = blockmodel.obj
        f = open(data_path("made/cup2.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/cup2.obj", "made/cup2.obj")

        x3d = blockmodel.x3d

        f = open(data_path("made/cup2.x3d"), "w")
        f.write(x3d)
        f.close()

        stl = blockmodel.stl

        f = open(data_path("made/cup2.stl"), "wb")
        f.write(stl)
        f.close()

        self.assertFileMatches("ref/cup2.stl", "made/cup2.stl")

        col = blockmodel.collada

        f = open(data_path("made/cup2.dae"), "w")
        f.write(col)
        f.close()

        # self.assertFileMatches("ref/cup2.dae", "made/cup2.dae")



    def test_sparse_json(self):

        as_list = [[7, 4, 2, 2, 0],
                    [8, 4, 2, 2, 0],
                    [9, 4, 2, 2, 0],
                    [9, 4, 3, 2, 0],
                    [9, 4, 4, 2, 0],
                    [8, 4, 4, 2, 0],
                    [7, 4, 4, 2, 0],
                    [7, 4, 3, 2, 0]]


        blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
        stl = blockmodel.stl

        f = open(data_path("made/sparse_test.stl"), "wb")
        f.write(stl)
        f.close()

        self.assertFileMatches("ref/sparse_test.stl", "made/sparse_test.stl")

        col = blockmodel.collada
        f = open(data_path("made/sparse_test.dae"), "w")
        f.write(col)
        f.close()


        csv = blockmodel.csv
        f = open(data_path("made/sparse_test.csv"), "w")
        f.write(csv)
        f.close()

        self.assertFileMatches("ref/sparse_test.csv", "made/sparse_test.csv")


    def test_sparse_json_to_schematic(self):

        as_list = [[7, 4, 2, 2, 0],
                    [8, 4, 2, 2, 0],
                    [9, 4, 2, 2, 0],
                    [9, 4, 3, 2, 0],
                    [9, 4, 4, 2, 0],
                    [8, 4, 4, 2, 0],
                    [7, 4, 4, 2, 0],
                    [7, 4, 3, 2, 0]]


        blockmodel = BlockModel.from_sparse_json(json.dumps(as_list))
        schematic = blockmodel.schematic

        f = open(data_path("made/sparse_2_schematic_test.schematic"), "wb")
        f.write(schematic)
        f.close()

        blockmodel = BlockModel.from_schematic_file(data_path("made/sparse_2_schematic_test.schematic"))

        obj = blockmodel.obj
        f = open(data_path("made/sparse_obj.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/sparse_obj.obj", "made/sparse_obj.obj")



    def test_png_to_schematic(self):

        f = open(data_path("ref/block.png"), "rb")
        as_png = f.read()
        f.close()

        blockmodel = BlockModel.from_png(as_png)

        schematic = blockmodel.schematic

        f = open(data_path("made/png_2_schematic_test.schematic"), "wb")
        f.write(schematic)
        f.close()

        blockmodel = BlockModel.from_schematic_file(data_path("made/png_2_schematic_test.schematic"))

        obj = blockmodel.obj
        f = open(data_path("made/png_2_obj.obj"), "w")
        f.write(obj)
        f.close()

        self.assertFileMatches("ref/png_2_obj.obj", "made/png_2_obj.obj")


    def test_collada(self):

        f = open(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()

        blockmodel = BlockModel.from_json(as_json)
        col = blockmodel.collada

        f = open(data_path("made/col_ref.dae"), "w")
        f.write(col)
        f.close()

        f = open(data_path("ref/col_ref.dae"), "r")
        refcol = f.read()
        f.close()

        self.maxDiff = None
        # self.assertMultiLineEqual(refcol, col)

        f = open("collada_schema_1_4_1.xsd", "rb")
        col_str = f.read()
        xmlschema_doc = etree.fromstring(col_str)
        f.close()
        xmlschema = etree.XMLSchema(xmlschema_doc)

        f = open(data_path("made/col_ref.dae"), "r")
        colxml = etree.parse(f)
        f.close()
        xmlschema.validate(colxml)



    def test_x3d(self):

        f = open(data_path("ref/073985f1c3e2f26c5be4a01073de42d3"), "r")
        as_json = f.read()
        f.close()

        blockmodel = BlockModel.from_json(as_json)
        x3d = blockmodel.x3d

        f = open(data_path("made/x3d_ref.x3d"), "w")
        f.write(x3d)
        f.close()

        f = open(data_path("ref/x3d_ref.x3d"), "r")
        refx3d = f.read()
        f.close()

        self.maxDiff = None
        # self.assertMultiLineEqual(refx3d, x3d)

        f = open("x3d-3.2.xsd", "rb")
        xmlschema_doc = etree.parse(f)
        f.close()
        xmlschema = etree.XMLSchema(xmlschema_doc)

        f = open(data_path("made/x3d_ref.x3d"), "r")
        x3dxml = etree.parse(f)
        f.close()
        xmlschema.validate(x3dxml)


class BlockModelFilesTestCase(unittest.TestCase):

    def setUp(self):
        if not os.path.exists(MADE_DIR):
            os.makedirs(MADE_DIR)

    def tearDown(self):
        shutil.rmtree(MADE_DIR)

    def assertFileMatches(self, ref_path, made_path):
        with open(data_path(ref_path), "rb") as src_f:
            with open(data_path(made_path), "rb") as dst_f:
                self.assertEqual(src_f.read(), dst_f.read(), "opens don't match %s %s" % (ref_path, made_path))

    def test_save_stl(self):
        model = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        made_file_path = data_path("made/test.stl")
        model.save_as_stl(made_file_path)
        self.assertFileMatches("ref/cup2.stl", "made/test.stl")

    def test_save_x3d(self):
        model = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        made_file_path = data_path("made/test.x3d")
        model.save_as_x3d(made_file_path)
        self.assertTrue(os.path.exists(data_path("made/test_x3d/test.x3d")))



    def test_save_collada_from_json(self):
        earth_json ="""[
            [[[3,0],[3,0],[3,0]],[[3,0],[3,0],[3,0]],[[2,0],[2,0],[2,0]]],
            [[[3,0],[3,0],[3,0]],[[0,0],[56,0],[3,0]],[[2,0],[2,0],[2,0]]],
            [[[3,0],[3,0],[3,0]],[[0,0],[0,0],[3,0]],[[2,0],[2,0],[2,0]]]
            ]
            """

        model = BlockModel.from_json(earth_json)
        made_file_path = data_path("made/earth.dae")
        model.save_as_collada(made_file_path)
        self.assertTrue(os.path.exists(data_path("made/earth_dae/earth.dae")))




    def test_save_collada(self):
        model = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        made_file_path = data_path("made/test.dae")
        model.save_as_collada(made_file_path)
        self.assertTrue(os.path.exists(data_path("made/test_dae/test.dae")))

    def test_save_obj(self):
        model = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        made_file_path = data_path("made/test.obj")
        model.save_as_obj(made_file_path)
        self.assertTrue(os.path.exists(data_path("made/test_obj/test.obj")))

    def test_save_csv(self):
        model = BlockModel.from_schematic_file(data_path("ref/cup2.schematic"))
        made_file_path = data_path("made/test.csv")
        model.save_as_csv(made_file_path)
        self.assertTrue(os.path.exists(data_path("made/test.csv")))


if __name__ == '__main__':
    unittest.main()