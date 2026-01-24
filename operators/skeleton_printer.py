import bpy

class SkeletonPrinterOperator(bpy.types.Operator):
    bl_idname = "wm.skeleton_printer_operator"
    bl_label = "Skeleton Printer"
    bl_options = {'REGISTER', 'UNDO'}

    def print_hierarchy(self, bone, level=0):
        print("\t" * level + bone.name)
        for child in bone.children:
            self.print_hierarchy(child, level + 1)

    def execute(self, context):
        selected_obj = context.active_object
        if selected_obj and selected_obj.type == 'ARMATURE':
            print("Hierarchy for Armature:", selected_obj.name)
            for bone in selected_obj.data.bones:
                if not bone.parent:
                    self.print_hierarchy(bone, 1)
            return {'FINISHED'}
        else:
            print("Please select an armature object.")
            self.report({'WARNING'}, "Please select an armature object.")
            return {'CANCELLED'}
