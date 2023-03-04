from . import nodes
from .core import app_handlers, msg_bus

bl_info = {
    "name": "CameraMappingMaterialNode",
    "author": "Evan Ryan",
    "version": (0, 0, 0),
    "blender": (3, 3, 3),
    "location": "Node Editor",
    "category": "Node",
    "description": "Camera projection mapping material node",
    "warning": ""
}

VERSION = 'v0.0.0' 

def register():
    nodes.register()
    app_handlers.register()
    msg_bus.register()

def unregister():
    msg_bus.unregister()
    app_handlers.unregister()
    nodes.unregister()