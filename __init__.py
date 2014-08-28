import sys, os, bpy
sys.path.append(os.path.dirname(__file__)) 
import rotating_camera, target_camera
from utils import *


bl_info = {
    "name":        "Camera Tools",
    "description": "A tool to make good camera animations faster",
    "author":      "Jacques Lucke",
    "version":     (0, 1, 0),
    "blender":     (2, 7, 1),
    "location":    "View 3D > Tool Shelf",
    "warning":     "Alpha",
    "category":    "3D View"
    }
	
	
# interface

class CameraToolsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_label = "Camera Tools"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		col.operator("camera_tools.add_rotating_camera")
		col.operator("camera_tools.insert_target_camera")
		
		col = layout.column(align = True)
		col.operator("camera_tools.set_active_camera")
		col.operator("camera_tools.seperate_text")
		col.operator("camera_tools.text_to_name")
		
		
# operators

class SetActiveCameraOperator(bpy.types.Operator):
	bl_idname = "camera_tools.set_active_camera"
	bl_label = "Set Active Camera"
	
	def execute(self, context):
		bpy.context.scene.camera = getActive()
		return{"FINISHED"}
		
class TextToNameOperator(bpy.types.Operator):
	bl_idname = "camera_tools.text_to_name"
	bl_label = "Text to Name"
	
	def execute(self, context):
		textToName()
		return{"FINISHED"}
		
class SeperateTextOperator(bpy.types.Operator):
	bl_idname = "camera_tools.seperate_text"
	bl_label = "Seperate Text"
	
	def execute(self, context):
		active = getActive()
		if isTextObject(active):
			seperateTextObject(active)
			delete(active)
		
		return{"FINISHED"}
			

#registration

def register():
	bpy.utils.register_module(__name__)
	rotating_camera.register()
	target_camera.register()

def unregister():
	bpy.utils.unregister_module(__name__)
	rotating_camera.unregister()
	target_camera.unregister()

if __name__ == "__main__":
	register()