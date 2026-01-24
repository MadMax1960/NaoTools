import bpy


def duplicate_and_merge_mesh_with_its_materials():
    selected_objects = bpy.context.selected_objects
    if len(selected_objects) != 1:
        bpy.context.window_manager.popup_menu(warn_no_selection, title="Warning", icon='ERROR')
        return

    selected_mesh = selected_objects[0]

    if selected_mesh.type != 'MESH':
        bpy.context.window_manager.popup_menu(warn_not_mesh, title="Warning", icon='ERROR')
        return

    materials = selected_mesh.data.materials
    new_meshes = []

    for material in materials:
        new_mesh = selected_mesh.copy()
        new_mesh.data = selected_mesh.data.copy()
        new_mesh.data.materials.clear()
        new_mesh.data.materials.append(material)
        bpy.context.collection.objects.link(new_mesh)
        new_meshes.append(new_mesh)

    bpy.context.view_layer.objects.active = selected_mesh
    bpy.ops.object.select_all(action='DESELECT')
    selected_mesh.select_set(True)

    for new_mesh in new_meshes:
        new_mesh.select_set(True)

    bpy.ops.object.join()
    print(f"Duplicated {selected_mesh.name} {len(materials)} times and merged the meshes back into the original.")


def warn_no_selection(self, context):
    self.layout.label(text="Please select exactly one mesh.")


def warn_not_mesh(self, context):
    self.layout.label(text="The selected object must be a mesh.")


class UEMaterialDuplicateOperator(bpy.types.Operator):
    bl_idname = "wm.ue_material_duplicate_operator"
    bl_label = "UE Mat Dupe"
    bl_description = "Duplicate the selected mesh with its materials"

    def execute(self, context):
        duplicate_and_merge_mesh_with_its_materials()
        return {'FINISHED'}
