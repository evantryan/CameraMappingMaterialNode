from .camera_mapping import CameraMappingShaderNode

from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory, CompositorNodeCategory

node_categories = [
    ShaderNodeCategory("SH_TESTING_NODES", "Testing Nodes", items=[
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

    register_node_categories("SH_TESTING_NODES", node_categories)

def unregister():
    unregister_node_categories("SH_TESTING_NODES")
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)