import bpy
from bpy.app.handlers import persistent

# Import the register/unregister functions from your pins module
from ..operators import pins_ot
from ..panels import pins_pt
from ..addon_preferences import get_addon_preferences

last_state = None

@persistent
def on_file_load(dummy):
    prefs = get_addon_preferences()
    if prefs.ex_pins == 'OFF':
        pins_ot.unregister()
        pins_pt.unregister()
    elif prefs.ex_pins == 'ON':
        pins_ot.register()
        pins_pt.register()

def register():
    bpy.app.handlers.load_post.append(on_file_load)

def unregister():
    if on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_file_load)
