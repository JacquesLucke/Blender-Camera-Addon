import bpy

def getDirectoryToBlends():
    return "F:\\Projekte\\Blender Camera Addon\\Blender Camera Addon\\blends\\"

def add_rotating_camera():
    blendName = "rotating camera.blend"
    groupName = "Rotating Camera Rig Group"
    
    pathToBlend = getDirectoryToBlends() + blendName
    groupsDirectory = pathToBlend + "\\Group\\"
    fileName = "\\" + blendName + "\\Group\\"
    
    print(getCurrentDirectory())
    print(pathToBlend)
    print(groupsDirectory)
    print(fileName)
    
    bpy.ops.wm.link_append(
            link = False, 
            directory = groupsDirectory,
            filename = groupName)
            

class RotationCameraPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Rotating Camera"
    
    def draw(self, context):
        layout = self.layout
        
        split = layout.split()
        col = split.column(align = True)
        
        col.operator("animation.add_rotating_camera")
        
class AddRotatingCameraOperator(bpy.types.Operator):
    bl_idname = "animation.add_rotating_camera"
    bl_label = "Add Rotating Camera"
    
    def execute(self, context):
        add_rotating_camera()
        return{"FINISHED"}

def register():
    bpy.utils.register_class(RotationCameraPanel)
    bpy.utils.register_class(AddRotatingCameraOperator)

def unregister():
    bpy.utils.unregister_class(RotationCameraPanel)
    bpy.utils.unregister_class(AddRotatingCameraOperator)

if __name__ == "__main__":
    register()

