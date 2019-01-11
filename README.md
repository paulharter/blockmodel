# blockmodel

A Python library that converts Minecraft models to and from various 3D formats.

blockmodel is the core model creation library used by http://printcraft.org to create models on its servers.

blockmodel supports python 2.7 and 3.7

## Installation

The easiest way to use blockmodel is to install it with pip `pip install blockmodel`

Or you can clone this repo and run the usual `python setup.py install`

## Usage


First create an instance of blockmodel.BlockModel with one of its classmethods

    from_json
    from_png
    from_sparse_json
    from_schematic_file

eg
```python
BlockModel.from_json(as_json, max_size=None)
```
The json has to be a multi-dimensional array of blocks `[x][y][z]` where each block is an array of block ids and data`[id, data]`. For example:
```json
[
[[[3,0],[3,0],[3,0]],[[3,0],[3,0],[3,0]],[[2,0],[2,0],[2,0]]],
[[[3,0],[3,0],[3,0]],[[0,0],[56,0],[3,0]],[[2,0],[2,0],[2,0]]],
[[[3,0],[3,0],[3,0]],[[0,0],[0,0],[3,0]],[[2,0],[2,0],[2,0]]]
]
```
This will create a 9x9 block of dirt with grass on top and a partly exposed block of diamond ore in the middle. (Note this method takes json encoded string not a python array.)

```python   
BlockModel.from_png(as_png, max_size=None)
```
The png reader will create a model one block high in which the block id is taken from the red value of each pixel.

```python
BlockModel.from_sparse_json(as_json, max_size=None)
```
This is an alternative way to define a block model using json. Instead of using a multi-dimensional array you use an array of individual block locations in the form `[x, y, z, id, data]`. For example

```json
[[7, 4, 2, 2, 0],
[8, 4, 2, 2, 0],
[9, 4, 2, 2, 0],
[9, 4, 3, 2, 0],
[9, 4, 4, 2, 0],
[8, 4, 4, 2, 0],
[7, 4, 4, 2, 0],
[7, 4, 3, 2, 0]]

```
This makes a 9x9 ring of grass

```python  
BlockModel.from_schematic_file(schematic_file_path, max_size=None)
```
This uses Minecraft's schematic file format as produced by WorldEdit 

Once you have created a model you can save it in one of five formats

+ obj
+ x3d
+ collada
+ schematic
+ csv

eg

```python  
block_model = BlockModel.from_schematic_file(schematic)
obj = block_model.obj
```

Or you can use the helper methods to save models directly to file

+ save_as_stl(file_path)
+ save_as_obj(file_path)
+ save_as_x3d(file_path)
+ save_as_collada(file_path)
+ save_as_schematic(file_path)

These functions will create obj, x3d and collada files inside a folder with the correct texture

For example:

```python  
earth_json ="""[
    [[[3,0],[3,0],[3,0]],[[3,0],[3,0],[3,0]],[[2,0],[2,0],[2,0]]],
    [[[3,0],[3,0],[3,0]],[[0,0],[56,0],[3,0]],[[2,0],[2,0],[2,0]]],
    [[[3,0],[3,0],[3,0]],[[0,0],[0,0],[3,0]],[[2,0],[2,0],[2,0]]]
    ]
    """
block_model = BlockModel.from_json(earth_json)
block_model.save_as_collada(file_path)
```

This will save out a collada model to file from json.
 
    
 
