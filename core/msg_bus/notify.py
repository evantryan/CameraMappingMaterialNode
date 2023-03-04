import bpy

from ..app_handlers import update_all_camera_mapping_nodes


def resolution_change(context):
    update_all_camera_mapping_nodes(context)

def camera_change(context):
    update_all_camera_mapping_nodes(context)



