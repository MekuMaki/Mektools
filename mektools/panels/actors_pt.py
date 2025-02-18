import bpy
from bpy.types import Panel
from ..addon_preferences import get_addon_preferences 
from ..functions import actors_fn as actors

class ActorItem(bpy.types.PropertyGroup):
    """Stores an armature reference for the UI list"""
    name: bpy.props.StringProperty(name="Armature Name") # type: ignore
    armature: bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore

class UI_UL_Actors(bpy.types.UIList):
    """List UI for displaying armatures"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='OUTLINER_OB_ARMATURE')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OUTLINER_OB_ARMATURE')
            
       
class MEKTOOLS_PT_Actors(Panel):
    bl_idname = "mektools.pt_actors"
    bl_label = "Actors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    @classmethod
    def poll(cls, context):
        return get_addon_preferences().ex_actors == 'ON'
    
    def draw(self, context):
        scene = context.scene
        self.prefs = get_addon_preferences()
      
        layout = self.layout
        box = layout.box()
        row = box.split(factor=0.63)
        row.label(text="Available Actors")
        row.operator("mektools.ot_refresh_actors", icon="FILE_REFRESH", text="Refresh")
            
        row = box.row()
        row.template_list("UI_UL_Actors", "", scene, "actors", scene, "actors_index")

        col = row.column(align=True)
        col.operator("mektools.ot_delete_actor", icon="X", text="")
           

def register():
    bpy.utils.register_class(ActorItem)
    bpy.utils.register_class(UI_UL_Actors)

    bpy.types.Scene.actors = bpy.props.CollectionProperty(type=ActorItem)
    bpy.types.Scene.actors_index = bpy.props.IntProperty()
    bpy.types.Scene.actors_index = bpy.props.IntProperty(update=actors.update_selected_actor)
    
    bpy.utils.register_class(MEKTOOLS_PT_Actors)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_PT_Actors)
    del bpy.types.Scene.actors
    del bpy.types.Scene.actors_index

    bpy.utils.unregister_class(ActorItem)
    bpy.utils.unregister_class(UI_UL_Actors)
    del bpy.types.Scene.orientation_mode
    
    
    
    
    