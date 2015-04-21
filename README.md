# blockmodel

A python library that converts Minecraft models to various 3D formats

## Usage


First create an instance of blockmodel.BlockModel with one of its classmethods

```python
BlockModel.from_json(as_json, max_size=None)
```

```python   
BlockModel.from_png(as_png, max_size=None)
```

```python
BlockModel.from_sparse_json(as_json, max_size=None)
```

```python  
BlockModel.from_schematic_file(schematic, max_size=None)
```

You can then get renditions of the model by accessing these attributes:

+ obj
+ x3d
+ collada
+ schematic
+ csv

eg

```python  
block_model = BlockModel.from_schematic_file(schematic, max_size=None)
obj = block_model.obj
```

     
    
 