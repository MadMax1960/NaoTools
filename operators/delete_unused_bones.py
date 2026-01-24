import bpy

class NaoDeleteUnusedBonesOperator(bpy.types.Operator):
    bl_idname = "wm.nao_delete_unused_bones_operator"
    bl_label = "Delete Unused Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        arm_obj = context.active_object
        if not arm_obj or arm_obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an armature object.")
            return {'CANCELLED'}

        used_bones = set()
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == arm_obj:
                        for vg in obj.vertex_groups:
                            used_bones.add(vg.name)
                        break

        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = arm_obj.data.edit_bones
        bones_to_remove = [bone for bone in edit_bones if bone.name not in used_bones]
        for bone in bones_to_remove:
            edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, f"Removed {len(bones_to_remove)} unused bones.")
        return {'FINISHED'}