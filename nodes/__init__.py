from .camera_mapping import CameraMappingShaderNode

from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory, CompositorNodeCategory

# could maybe use https://github.com/Secrop/ShaderNodesExtra2.80/blob/master/__init__.py
# to put these into an existing menu. fingers crossed   

node_categories = [
    ShaderNodeCategory("PIPELINENODES", "Mapping Nodes", items=[
        NodeItem("CameraMappingShaderNode"),
    ]),
]

classes = [
    CameraMappingShaderNode
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    register_node_categories("PIPELINENODES", node_categories)

def unregister():
    unregister_node_categories("PIPELINENODES")
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)