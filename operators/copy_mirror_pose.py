import bpy

class NaoCopyMirrorPoseOperator(bpy.types.Operator):
    bl_idname = "wm.nao_copy_mirror_pose_operator"
    bl_label = "Copy & Mirror Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def find_mirror_name(self, name, left_suffix, right_suffix):
        if name.endswith(left_suffix):
            return name[:-len(left_suffix)] + right_suffix
        elif name.endswith(right_suffix):
            return name[:-len(right_suffix)] + left_suffix
        elif f" {left_suffix}" in name:
            return name.replace(f" {left_suffix}", f" {right_suffix}")
        elif f" {right_suffix}" in name:
            return name.replace(f" {right_suffix}", f" {left_suffix}")
        return None

    def execute(self, context):
        armature = context.active_object
        active_bone = context.active_pose_bone
        if not armature or not active_bone:
            self.report({'WARNING'}, "No active pose bone selected.")
            return {'CANCELLED'}

        left_suffix = context.scene.nao_left_suffix
        right_suffix = context.scene.nao_right_suffix
        mirror_name = self.find_mirror_name(active_bone.name, left_suffix, right_suffix)

        if mirror_name and mirror_name in armature.pose.bones:
            mirror_bone = armature.pose.bones[mirror_name]
            mirror_bone.location = (active_bone.location[0], active_bone.location[1], active_bone.location[2])

            active_bone.rotation_mode = 'XYZ'
            mirror_bone.rotation_mode = 'XYZ'
            mirror_bone.rotation_euler = (-active_bone.rotation_euler[0], -active_bone.rotation_euler[1], active_bone.rotation_euler[2])
            mirror_bone.scale = active_bone.scale

            self.report({'INFO'}, f"Pose values from {active_bone.name} have been effectively not inverted and copied to {mirror_bone.name}.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Mirror bone not found.")
            return {'CANCELLED'}
