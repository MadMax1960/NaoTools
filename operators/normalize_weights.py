import bpy

class NaoNormalizeOperator(bpy.types.Operator):
    bl_idname = "wm.nao_normalize_operator"
    bl_label = "Normalize Weights"

    def execute(self, context):
        for obj in bpy.context.visible_objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.vertex_group_normalize_all()
        return {'FINISHED'}
