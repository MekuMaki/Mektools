import bpy

def get_unique_name(base_name, existing_names):
    """Generate a unique name by appending a number if needed."""
    if base_name not in existing_names:
        return base_name
    
    index = 1
    while f"{base_name}.{index:03d}" in existing_names:
        index += 1
    
    return f"{base_name}.{index:03d}"


def safe_hide_set(context, obj, hide):
    """Safely hides objects"""
    if obj and obj.name in context.view_layer.objects:
        obj.hide_set(hide)
        
def create_collection(name="Collection"):
    """Creates a Collection"""
    new_collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(new_collection)
    return new_collection 

def dupe_with_childs(armature):
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    for child in armature.children:
        child.select_set(True)
            
    bpy.ops.object.duplicate_move()