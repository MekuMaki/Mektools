import bpy
import weakref
from bpy.types import Panel
from ..addon_preferences import get_addon_preferences 
from ..libs import actors
from ..custom_icons import preview_collections

class ActorItem(bpy.types.PropertyGroup):
    """Stores an armature reference for the UI list with differentiation"""
    armature: bpy.props.PointerProperty(type=bpy.types.Object)
    
    @property
    def hide_armature(self):
        return self.armature and self.armature.data.get("mektools_actor_hide_armature", False)
    
    @property
    def hide_actor(self):
        return self.armature and self.armature.data.get("mektools_actor_hide_actor", False)  
    
    @property
    def armature_type(self):
        return self.armature and self.armature.data.get("mektools_armature_type", "Unknown")

class UI_UL_Actors(bpy.types.UIList):
    """List UI for displaying categorized armatures"""
    
    def draw_filter(self, context, layout):
        """Draws the filter UI inside the list panel."""
        layout.prop(context.scene, "hide_ghosts", text="Filter Ghosts", toggle=True)
        
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        filtered = []
        order = []
        hide_ghosts = context.scene.hide_ghosts
    
        for i, item in enumerate(items):
            flag = self.bitflag_filter_item  # Default: Show the item

            if hide_ghosts and item.armature not in bpy.context.view_layer.objects.values():
                flag &= ~self.bitflag_filter_item  # Hide the item
        
            filtered.append(flag)
            order.append(i)
    
        return filtered, order
        
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):       
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.armature:
                if item.armature in bpy.context.view_layer.objects.values():
                    if item.armature_type == "mekrig":
                        icon_type = "OUTLINER_OB_ARMATURE"
                    else:
                        icon_type = "MOD_ARMATURE"
                else: 
                    icon_type = "GHOST_DISABLED"

            
                row = layout.row(align=True)
                row.active = not item.hide_actor
                row.label(text=item.armature.name, icon=icon_type)
           
                hide_armature_icon = preview_collections["main"]["BONE_DATA_OFF"].icon_id
                # Hide Armature Button
                if item.hide_armature:
                    op = row.operator("mektools.ot_toggle_actor_visibility", text="", icon_value=hide_armature_icon, emboss=False)
                else:
                    op = row.operator("mektools.ot_toggle_actor_visibility", text="", icon="BONE_DATA", emboss=False)
                op.armature_name = item.armature.name
                op.hide_armature = not item.hide_armature
                op.hide_actor = item.hide_actor

                # Hide Actor Button
                op = row.operator("mektools.ot_toggle_actor_visibility", text="", icon='HIDE_ON' if item.hide_actor else 'HIDE_OFF', emboss=False)
                op.armature_name = item.armature.name
                op.hide_armature = item.hide_armature
                op.hide_actor =  not item.hide_actor
            
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
            
        row = box.row()
        row.template_list("UI_UL_Actors", "", scene, "actors", scene, "actors_index")

        col = row.column(align=True)
        op = col.operator("mektools.ot_set_is_actor", icon="ADD", text="")  # make actor
        op.is_actor = True
        op = col.operator("mektools.ot_set_is_actor", icon="REMOVE", text="")  # make actor
        op.is_actor = False
        
        col.separator(factor=1.0)
        
        if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
            op = col.operator("mektools.ot_rename_actor", icon="GREASEPENCIL", text="") # rename actor 
            op.new_name = scene.actors[scene.actors_index].armature.name if scene.actors[scene.actors_index].armature else ""
            col.operator("mektools.ot_duplicate_actor", icon="DUPLICATE", text="")  # duplicate 
            col.operator("mektools.ot_delete_actor", icon="TRASH", text="")  # delete actor
        
        
           

def register():
    bpy.utils.register_class(ActorItem)
    bpy.utils.register_class(UI_UL_Actors)

    bpy.types.Scene.actors = bpy.props.CollectionProperty(type=ActorItem)
    bpy.types.Scene.actors_index = bpy.props.IntProperty()
    bpy.types.Scene.actors_index = bpy.props.IntProperty(update=actors.update_selected_actor)
    
    bpy.types.Scene.hide_ghosts = bpy.props.BoolProperty(name="Hide Ghosts", default=True)
    
    bpy.utils.register_class(MEKTOOLS_PT_Actors)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_PT_Actors)
    del bpy.types.Scene.actors
    del bpy.types.Scene.actors_index

    bpy.utils.unregister_class(ActorItem)
    bpy.utils.unregister_class(UI_UL_Actors)
    del bpy.types.Scene.orientation_mode
    
    
    
    
    