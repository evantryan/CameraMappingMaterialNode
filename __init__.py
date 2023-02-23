from . import nodes
from .core import app_handlers

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
    #app_handlers.register()

def unregister():
    #app_handlers.unregister()
    nodes.unregister()