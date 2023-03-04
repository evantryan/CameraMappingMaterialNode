import bpy

from . import notify

@bpy.app.handlers.persistent
def resolution_change(scene, depsgraph):
    '''this should register to load_post. Uses msgbus to trigger on socket change'''

    subscribe_tuples = [
        (bpy.types.RenderSettings, 'resolution_x'),
        (bpy.types.RenderSettings, 'resolution_y'),
        ]

    for subscribe_to in subscribe_tuples:
        #handle = object()
        handle = bpy

        bpy.msgbus.subscribe_rna(
            key=subscribe_to,
            owner=handle,
            args=((bpy.context,)),
            notify=notify.resolution_change,
        )

@bpy.app.handlers.persistent
def camera_change(scene, depsgraph):
    '''this should register to load_post. Uses msgbus to trigger on socket change'''

    subscribe_tuples = [
        (bpy.types.Camera, 'lens'),
        (bpy.types.Camera, 'sensor_fit'),
        (bpy.types.Camera, 'sensor_height'),
        (bpy.types.Camera, 'sensor_width'),
        ]

    for subscribe_to in subscribe_tuples:
        #handle = object()
        handle = bpy

        bpy.msgbus.subscribe_rna(
            key=subscribe_to,
            owner=handle,
            args=((bpy.context,)),
            notify=notify.camera_change,
        )