import bpy

class NaoRenameMaterialsListOperator(bpy.types.Operator):
    bl_idname = "wm.nao_rename_materials_list_operator"
    bl_label = "Rename Materials for Aigis (051)"
    bl_description = "Renames Aigis's mats to match her mat slot ids"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object.")
            return {'CANCELLED'}

        target_names = [
            "M_00_FuMeMk_00",
            "M_00_FuBaMk_00",
            "M_02_FuBaMk_00",
            "M_00_FuBaMk_00_OlMk",
            "M_02_FuBaMk_00_OlMk",
            "M_00_FuMeMk_65_OlMk",
            "M_00_FuMeMk_60_OlMk",
            "M_00_FuBaMk_65",
            "M_00_FuBaMk_60",
            "M_00_FuMeMk_65",
            "M_00_FuMeMk_60"
        ]

        # Iterate through slots and assign names based on the list
        for i, slot in enumerate(obj.material_slots):
            if i >= len(target_names):
                break
            
            target_name = target_names[i]
            
            if slot.material:
                new_mat = slot.material.copy()
                new_mat.name = target_name
                slot.material = new_mat
            else:
                new_mat = bpy.data.materials.new(name=target_name)
                slot.material = new_mat

        self.report({'INFO'}, f"Renamed {min(len(obj.material_slots), len(target_names))} materials.")
        return {'FINISHED'}