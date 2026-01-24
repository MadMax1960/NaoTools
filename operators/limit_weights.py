import bpy

class NaoLimitWeightsOperator(bpy.types.Operator):
    bl_idname = "wm.nao_limit_weights_operator"
    bl_label = "Limit Weights"

    def execute(self, context):
        max_vertex_groups = context.scene.nao_props.max_vertex_groups
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.vertex_group_limit_total(limit=max_vertex_groups)
                bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}
