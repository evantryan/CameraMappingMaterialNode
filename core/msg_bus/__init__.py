import bpy
from . import subscriptions

def register():
    bpy.app.handlers.load_post.append(subscriptions.resolution_change)
    # bpy.app.handlers.load_post.append(subscriptions.camera_change)

def unregister():
    # bpy.app.handlers.load_post.remove(subscriptions.camera_change)
    bpy.app.handlers.load_post.remove(subscriptions.resolution_change)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print(e)
    
    register()