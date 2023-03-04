import bpy

from . import notify

# do we need to separate this out to allow for updates on unsaved files? - probably give the user a warning if bpy.data.filepath == ''

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