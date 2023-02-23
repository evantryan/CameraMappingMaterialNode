from . import nodes

bl_info = {
    "name": "CameraProjectionMaterial",
    "author": "Evan Ryan",
    "version": (0, 0, 0),
    "blender": (3, 3, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "Camera projection mapping material node",
    "warning": ""
}

VERSION = 'v0.0.0' 

def register():
    nodes.register()

def unregister():
    nodes.unregister()