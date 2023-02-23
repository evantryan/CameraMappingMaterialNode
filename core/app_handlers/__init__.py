import bpy
from ...nodes.camera_mapping import CameraMappingShaderNode

@bpy.app.handlers.persistent
# @override_nodes_app_handler
def depsgraph_update_post(scene, depsgraph):
    for thing in depsgraph.updates:
        print(thing.id)
        if type(thing.id) == CameraMappingShaderNode:
            print(thing.name)
            print(thing.node_tree)

def register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print(e)
    
    register()