import sys, os 
sys.path.append(os.path.dirname(__file__)) 


import bpy
from utils import *
import rotating_camera

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
		
		split = layout.split()
		col = split.column(align = True)
		
		col.operator("animation.add_rotating_camera")
			

#registration

def register():
	bpy.utils.register_module(__name__)
	rotating_camera.register()

def unregister():
	bpy.utils.unregister_module(__name__)
	rotating_camera.unregister()

if __name__ == "__main__":
	register()