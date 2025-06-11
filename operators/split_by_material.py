import bpy

class NaoSplitByMaterialOperator(bpy.types.Operator):
    bl_idname = "wm.nao_split_by_material_operator"
    bl_label = "Split by Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' and obj.data.materials:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='MATERIAL')
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
