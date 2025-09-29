import bpy
from bpy.types import Panel
      
class VIEW3D_PT_RigLayer(Panel):
    bl_idname = "VIEW3D_PT_RigLayer"
    bl_label = "Rig Layer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'
    
    def draw(self, context):
        layout = self.layout

        col = layout.column()
        
        row = col.row()
        row.prop(context.active_object.data.collections['Face'], 'is_visible', toggle=True, text='Face')
        row = col.row()
        row.prop(context.active_object.data.collections['Face (Primary)'], 'is_visible', toggle=True, text='(Primary)')
        row.prop(context.active_object.data.collections['Face (Secondary)'], 'is_visible', toggle=True, text='(Secondary)')
        row = col.row()
        row.prop(context.active_object.data.collections['Hair'], 'is_visible', toggle=True, text='Hair')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Torso'], 'is_visible', toggle=True, text='Torso')
        row = col.row()
        row.prop(context.active_object.data.collections['Torso (Tweak)'], 'is_visible', toggle=True, text='(Tweak)')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Fingers'], 'is_visible', toggle=True, text='Fingers')
        row = col.row()
        row.prop(context.active_object.data.collections['Fingers (Detail)'], 'is_visible', toggle=True, text='(Detail)')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Arm.L (IK)'], 'is_visible', toggle=True, text='Arm.L (IK)')
        row.prop(context.active_object.data.collections['Arm.R (IK)'], 'is_visible', toggle=True, text='Arm.R (IK)')
        row = col.row()
        row.prop(context.active_object.data.collections['Arm.L (Tweak)'], 'is_visible', toggle=True, text='(Tweak)')
        row.prop(context.active_object.data.collections['Arm.R (Tweak)'], 'is_visible', toggle=True, text='(Tweak)')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Leg.L (IK)'], 'is_visible', toggle=True, text='Leg.L (IK)')
        row.prop(context.active_object.data.collections['Leg.R (IK)'], 'is_visible', toggle=True, text='Leg.R (IK)')
        row = col.row()
        row.prop(context.active_object.data.collections['Leg.L (Tweak)'], 'is_visible', toggle=True, text='(Tweak)')
        row.prop(context.active_object.data.collections['Leg.R (Tweak)'], 'is_visible', toggle=True, text='(Tweak)')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Tail'], 'is_visible', toggle=True, text='Tail')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['Root'], 'is_visible', toggle=True, text='Root')

        col.separator()

        row = col.row()
        row.prop(context.active_object.data.collections['IVCS'], 'is_visible', toggle=True, text='IVCS')
        row.prop(context.active_object.data.collections['Gear'], 'is_visible', toggle=True, text='Gear')
        row = col.row()
        row.prop(context.active_object.data.collections['Physic'], 'is_visible', toggle=True, text='Physics')
        row.prop(context.active_object.data.collections['Gear (Extra)'], 'is_visible', toggle=True, text='(Extra)')

           

def register():
    bpy.utils.register_class(VIEW3D_PT_RigLayer)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_RigLayer)


