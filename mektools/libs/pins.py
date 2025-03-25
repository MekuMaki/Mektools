import bpy
suppress_pin_callback = False

def select_pin(self, context):
    """Updates selection based on selected pins index"""
    global suppress_pin_callback
    if suppress_pin_callback:
        return
    
    scene = context.scene
    if len(scene.pins) > 0 and 0 <= scene.pins_index < len(scene.pins):
        if scene.pins_index >= 0:
            pin = scene.pins[scene.pins_index]
            if pin.object:
                previous_mode = context.mode
                if context.view_layer.objects.active:
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.ops.object.select_all(action='DESELECT')
                pin.object.select_set(True)
                context.view_layer.objects.active = pin.object
                
                try:
                    bpy.ops.object.mode_set(mode=previous_mode)
                except RuntimeError:
                    bpy.ops.object.mode_set(mode='OBJECT')

def sync_list_with_viewport_selection(scene):
    """Updates the active actor index based on selection."""
    global suppress_pin_callback
    suppress_pin_callback = True
    active_obj = bpy.context.view_layer.objects.active
    new_index = -1
    for i, pin in enumerate(scene.pins):
        if pin.object == active_obj:
            new_index = i
            break
    
    # Only update if the index has changed to prevent recursion
    if scene.pins_index != new_index:     
        scene.pins_index = new_index    
    
    suppress_pin_callback = False                    
                
def cleanup_pin_list(scene):
    """Removes pins from the list if the object is no longer in the viewport.""" 
    to_remove = []
    
    for i, pin in enumerate(scene.pins):
        if pin.object and pin.object not in bpy.context.view_layer.objects.values():
            to_remove.append(i)  
    
    for i in reversed(to_remove):
        scene.pins.remove(i)
        

def on_update_callback(scene):
    """Callback function triggered when Blender's update operation is called."""
    remove_callback()  # Temporarily disable callback
    sync_list_with_viewport_selection(scene) 
    #cleanup_pin_list(scene)
    add_callback()  # Re-enable callback
    
def add_callback():
    """Ensures the callback is only added once."""
    global suppress_pin_callback
    suppress_pin_callback = False
    
    if on_update_callback not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_update_callback)

def remove_callback():
    """Removes the callback to prevent infinite recursion."""
    global suppress_pin_callback
    suppress_pin_callback = True
    
    if on_update_callback in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_update_callback)


        