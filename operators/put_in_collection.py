import bpy

class NaoPutInCollectionOperator(bpy.types.Operator):
    bl_idname = "wm.nao_put_in_collection_operator"
    bl_label = "Put in Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        if not selected_armatures:
            self.report({'WARNING'}, "Please select at least one armature.")
            return {'CANCELLED'}

        for armature in selected_armatures:
            collection_name = f"{armature.name}_Collection"
            collection = bpy.data.collections.get(collection_name)
            if not collection:
                collection = bpy.data.collections.new(collection_name)
                context.scene.collection.children.link(collection)

            attached_meshes = []
            for obj in context.scene.objects:
                if obj.type == 'MESH':
                    if obj.parent == armature:
                        attached_meshes.append(obj)
                        continue
                    for mod in obj.modifiers:
                        if mod.type == 'ARMATURE' and mod.object == armature:
                            attached_meshes.append(obj)
                            break

            objects_to_link = [armature] + attached_meshes
            for obj in objects_to_link:
                if collection not in obj.users_collection:
                    collection.objects.link(obj)

        return {'FINISHED'}