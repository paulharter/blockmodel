# blockmodel

A python library that converts Minecraft models to various 3D formats

## Usage


First create an instance of blockmodel.BlockModel with one of its classmethods

```python
BlockModel.from_json(as_json, max_size=None)
```
as_json should be a 3D array of block id and block data.

```python   
BlockModel.from_png(as_png, max_size=None)
```
Uses the red values in the png to set block ids.

```python
BlockModel.from_sparse_json(as_json, max_size=None)
```

```python  
BlockModel.from_schematic_file(schematic, max_size=None)
```


     
    
 