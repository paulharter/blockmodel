# blockmodel

A python library that converts Minecraft models to various 3D formats

## Usage

First create a BlockModel with one of its classmethods

```python
BlockModel.from_json(as_json, max_size=None)
```
as_json should be a 3D array of block id and block data.

```python   
BlockModel.from_png(cls, as_png, max_size=None)
```

```python
BlockModel.from_sparse_json(cls, as_json, max_size=None)
```

```python  
BlockModel.from_schematic_file(cls, schematic, max_size=None)
```


     
    
 