import bpy

class NaoClearUnusedWeightsOperator(bpy.types.Operator):
    bl_idname = "wm.nao_clear_unused_weights_operator"
    bl_label = "Clear Unused Weights"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            vertex_groups = obj.vertex_groups[:]
            groups_to_remove = []

            for group in vertex_groups:
                is_used = False
                for vertex in obj.data.vertices:
                    for group_info in vertex.groups:
                        if group_info.group == group.index:
                            is_used = True
                            break
                    if is_used:
                        break
                if not is_used:
                    groups_to_remove.append(group.name)

            for group_name in groups_to_remove:
                obj.vertex_groups.remove(obj.vertex_groups[group_name])

            self.report({'INFO'}, f"Removed {len(groups_to_remove)} unused vertex groups.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Please select a mesh object.")
            return {'CANCELLED'}
