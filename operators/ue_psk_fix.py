import bpy

class UEPskFixOperator(bpy.types.Operator):
    bl_idname = "wm.ue_psk_fix_operator"
    bl_label = "UE Psk Fix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'ARMATURE':
            # Step 1: Scale up by 100 and apply the transformation
            obj.scale = (100, 100, 100)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            self.report({'INFO'}, f"Scaled armature '{obj.name}' up by 100 and applied scale.")

            # Step 2: Scale down to 0.01 without applying the transformation
            obj.scale = (0.01, 0.01, 0.01)
            self.report({'INFO'}, f"Scaled armature '{obj.name}' down to 0.01 on all axes (without applying).")

            # Step 3: Rename the armature object to 'Armature'
            obj.name = "Armature"
            self.report({'INFO'}, "Renamed armature object to 'Armature'.")

            # Step 4: Rename the armature data block (the `.ad`) to 'Armature'
            armature_data = obj.data
            armature_data.name = "Armature"
            self.report({'INFO'}, "Renamed armature data block to 'Armature'.")

            # Step 5: Keep the root bone as is, without renaming it
            root_bone = next((bone for bone in armature_data.bones if bone.parent is None), None)
            if root_bone:
                self.report({'INFO'}, f"Root bone is '{root_bone.name}' (not renamed).")
            else:
                self.report({'WARNING'}, "No root bone found in the armature.")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Please select an armature object.")
            return {'CANCELLED'}
