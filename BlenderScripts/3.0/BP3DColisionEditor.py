# Copyright (c) 2022, BlockProject 3D
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of BlockProject 3D nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from cgitb import text
import math
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bgl

bl_info = {
    "name" : "Colision Editor",
    "author" : "Yuri6037",
    "description" : "BlockProject 3D Colision Editor",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "BP3D"
}

MAX_POINTS = 48

class Sphere:
    def __init__(self, radius, rings, sectors):
        self.gen_vertices(radius, rings, sectors)
        self.gen_indices(rings, sectors)
    def gen_vertices(self, radius, rings, sectors):
        self.vertices = []
        for r in range(0, rings):
            for s in range(0, sectors):
                u = s / (sectors - 1)
                v = r / (rings - 1)
                phi = math.pi * v
                theta = math.pi * 2.0 * u
                x = math.sin(phi) * math.cos(theta) * radius
                y = math.sin(phi) * math.sin(theta) * radius
                z = math.cos(phi) * radius
                self.vertices.append((x, y, z))
    def gen_indices(self, rings, sectors):
        self.indices = []
        for r in range(0, rings - 1):
            for s in range(0, sectors - 1):
                v1 = r * sectors + s
                v2 = (r + 1) * sectors + s
                v3 = (r + 1) * sectors + (s + 1)
                v4 = r * sectors + (s + 1)
                v5 = r * sectors + s
                v6 = (r + 1) * sectors + (s + 1)
                self.indices.append((v1, v2, v3))
                self.indices.append((v4, v5, v6))
        self.indices

class HalfSphere:
    def __init__(self, radius, rings, sectors, orientation):
        self.gen_vertices(radius, rings, sectors, orientation)
        self.gen_indices(rings, sectors)
    def gen_vertices(self, radius, rings, sectors, orientation):
        self.vertices = []
        for r in range(0, rings):
            for s in range(0, sectors):
                u = s / (sectors - 1)
                v = r / (rings - 1)
                phi = math.pi / 2 * v
                theta = math.pi * 2.0 * u
                x = math.sin(phi) * math.cos(theta) * radius
                y = math.sin(phi) * math.sin(theta) * radius
                z = math.cos(phi) * radius
                if orientation == "Z":
                    self.vertices.append((x, y, z))
                elif orientation == "X":
                    self.vertices.append((z, x, y))
                elif orientation == "Y":
                    self.vertices.append((x, z, y))
    def gen_indices(self, rings, sectors):
        self.indices = []
        for r in range(0, rings - 1):
            for s in range(0, sectors - 1):
                v1 = r * sectors + s
                v2 = (r + 1) * sectors + s
                v3 = (r + 1) * sectors + (s + 1)
                v4 = r * sectors + (s + 1)
                v5 = r * sectors + s
                v6 = (r + 1) * sectors + (s + 1)
                self.indices.append((v1, v2, v3))
                self.indices.append((v4, v5, v6))
        self.indices

class Box:
    def __init__(self, size):
        x = size[0]
        y = size[1]
        z = size[2]
        self.vertices = [
            (-x, -y, z), # 0
            (-x, -y, -z), # 1
            (x, -y, -z), # 2
            (x, -y, z), # 3

            (-x, y, z), # 4
            (-x, y, -z), # 5
            (x, y, -z), # 6
            (x, y, z) # 7
        ]
        # front => -Y
        self.indices = [
            # Face 1 (front)
            (0, 1, 2),
            (0, 2, 3),
            # Face 2 (top)
            (4, 0, 3),
            (4, 3, 7),
            # Face 3 (back)
            (7, 6, 5),
            (7, 5, 4),
            # Face 4 (bottom)
            (1, 5, 6),
            (1, 6, 2),
            # Face 5 (left)
            (4, 5, 1),
            (4, 1, 0),
            # Face 6 (right)
            (3, 2, 6),
            (3, 6, 7)
        ]

class Cylinder:
    def __init__(self, radius, height, points, orientation):
        self.gen_vertices(radius, height, points, orientation)
        self.gen_indices(points)
    def gen_vertices(self, radius, height, points, orientation):
        self.vertices = []
        for p in range(0, points):
            u = p / (points - 1)
            theta = math.pi * 2.0 * u
            x = math.cos(theta) * radius
            y = math.sin(theta) * radius
            if orientation == "Z":
                self.vertices.append((x, y, height))
                self.vertices.append((x, y, -height))
            elif orientation == "X":
                self.vertices.append((height, x, y))
                self.vertices.append((-height, x, y))
            elif orientation == "Y":
                self.vertices.append((x, height, y))
                self.vertices.append((x, -height, y))
    def gen_indices(self, points):
        self.indices = []
        for p in range(0, (points * 2) - 2):
            self.indices.append((p, p + 1, p + 2))

class Capsule:
    def __init__(self, radius, height, rings, sectors, points, orientation):
        ball = HalfSphere(radius, rings, sectors, orientation)
        base = Cylinder(radius, height, points, orientation)
        top_vertices = []
        bottom_vertices = []
        for (x, y, z) in ball.vertices:
            if orientation == "Z":
                top_vertices.append((x, y, z + height))
                bottom_vertices.append((x, y, -z - height))
            elif orientation == "X":
                top_vertices.append((x + height, y, z))
                bottom_vertices.append((-x - height, y, z))
            elif orientation == "Y":
                top_vertices.append((x, y + height, z))
                bottom_vertices.append((x, -y - height, z))
        self.indices = []
        for (v1, v2, v3) in base.indices:
            self.indices.append((v1, v2, v3))
        l = len(base.vertices)
        for (v1, v2, v3) in ball.indices:
            self.indices.append((l + v1, l + v2, l + v3))
        l = l + len(ball.vertices)
        for (v1, v2, v3) in ball.indices:
            self.indices.append((l + v1, l + v2, l + v3))
        self.vertices = base.vertices + bottom_vertices + top_vertices

class Renderer:
    def __init__(self):
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    def load_mesh(self, obj):
        doubled_indices = []
        for (v1, v2, v3) in obj.indices:
            doubled_indices.append((v1, v2))
            doubled_indices.append((v2, v3))
            doubled_indices.append((v3, v1))
            # Recompute triangle indices into edge indices
            # (my guess is batch_for_shader works in an unexpected way:
            # it assumes edges instead of triangles like any low-level rendering routine should accept)
        return batch_for_shader(self.shader, 'LINES', {"pos": obj.vertices}, indices = doubled_indices)
    def lock(self):
        bgl.glLineWidth(5)
        self.shader.bind()
    def set_green(self):
        self.shader.uniform_float("color", (0, 1, 0, 1))
    def set_red(self):
        self.shader.uniform_float("color", (1, 0, 0, 1))
    def unlock(self):
        bgl.glLineWidth(1)
    def render(self, mesh):
        mesh.draw(self.shader)

draw_handler = None

r = Renderer()

def draw():
    r.lock()
    settings = bpy.context.scene.bp3d_collision_settings
    components = settings.components
    active = settings.active_component
    for (index, component) in enumerate(components):
        if (component.enabled):
            if (index == active):
                r.set_red()
            else:
                r.set_green()
            component.draw(r)
    r.unlock()

def toggle_view(self, _):
    global draw_handler
    if (draw_handler == None):
        draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')
    else:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
        draw_handler = None
    return None

class CollisionComponent(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        items = [
            ("Sphere", "Sphere", "Sphere"),
            ("Box", "Box", "Box"),
            ("Cylinder", "Cylinder", "Cylinder"),
            ("Capsule", "Capsule", "Capsule"),
            ("Convex", "Convex", "Convex")
        ],
        name = "Type",
        default = "Sphere",
        description = "Collision component type"
    )
    enabled: bpy.props.BoolProperty(
        name = "Enabled",
        description = "Show in 3D view",
        default = True
    )
    pos: bpy.props.FloatVectorProperty(
        name = "Position",
        subtype = "TRANSLATION",
        description = "Collision component position",
        default = (0.0, 0.0, 0.0)
    )
    radius: bpy.props.FloatProperty(
        name = "Radius",
        description = "Radius of sphere, cylinder or capsule",
        default = 1.0
    )
    height: bpy.props.FloatProperty(
        name = "Height",
        description = "Height of cylinder or capsule",
        default = 1.0
    )
    size: bpy.props.FloatVectorProperty(
        name = "Size",
        subtype = "XYZ",
        description = "Size of box",
        default = (1.0, 1.0, 1.0)
    )
    mesh: bpy.props.StringProperty(
        name = "Mesh name",
        description = "Name of mesh in scene tree to use for a convex collision component",
        default = ""
    )
    orientation: bpy.props.EnumProperty(
        items = [
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z")
        ],
        name = "Orientation",
        description = "Orientation of capsule or cylinder",
        default = "Z"
    )

    gpu_mesh = None

    def get_mesh(self, r):
        if (self.gpu_mesh == None):
            if self.type == "Sphere":
                self.gpu_mesh = r.load_mesh(Sphere(self.radius, 10, 10))
            elif self.type == "Box":
                self.gpu_mesh = r.load_mesh(Box(self.size))
            elif self.type == "Cylinder":
                self.gpu_mesh = r.load_mesh(Cylinder(self.radius, self.height, 10, self.orientation))
            elif self.type == "Capsule":
                self.gpu_mesh = r.load_mesh(Capsule(self.radius, self.height, 10, 10, 10, self.orientation))
        return self.gpu_mesh

    def draw(self, r):
        mesh = self.get_mesh(r)
        gpu.matrix.push()
        gpu.matrix.translate(self.pos)
        r.render(mesh)
        gpu.matrix.pop()

class Settings(bpy.types.PropertyGroup):
    enable_view: bpy.props.BoolProperty(
        name = "Enable Collision View",
        description = "Enable Collision View",
        default = False,
        update = toggle_view
    )
    components: bpy.props.CollectionProperty(
        type = CollisionComponent,
        name = "Collision components",
        description = "List of collision components"
    )
    active_component: bpy.props.IntProperty(
        name = "Active component",
        description = "Current active collision component for editing"
    )

class COLLISION_UL_component(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text = item.type)
        layout.prop(item, "enabled")

class COLLISION_OP_add(bpy.types.Operator):
    bl_label = "Add collision component"
    bl_idname = "collision.add"

    def invoke(self, context, _):
        settings = context.scene.bp3d_collision_settings
        settings.components.add()
        return {'FINISHED'}

class COLLISION_OP_remove(bpy.types.Operator):
    bl_label = "Remove collision component"
    bl_idname = "collision.remove"

    def invoke(self, context, _):
        settings = context.scene.bp3d_collision_settings
        index = settings.active_component
        settings.components.remove(index)
        return {'FINISHED'}

class COLLISION_PT_panel(bpy.types.Panel):
    bl_label = "BP3D Colision Editor"
    bl_category = "BP3D Colision Editor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        settings = context.scene.bp3d_collision_settings
        self.layout.prop(settings, "enable_view", text="Enable Collision View")
        self.layout.separator()
        row = self.layout.row()
        row.label(text = "Collision components: ")
        row.prop(settings, "components")
        self.layout.template_list("COLLISION_UL_component", "", settings, "components", settings, "active_component")
        self.layout.operator("collision.add", text="Add new component")
        self.layout.operator("collision.remove", text="Remove component")
        self.layout.separator()
        if (settings.active_component >= 0 and settings.active_component < len(settings.components)):
            row = self.layout.row()
            row.label(text = "Active component")
            component = settings.components[settings.active_component]
            row.label(text = component.type)

            # Render type selector
            col = self.layout.column()
            row = col.split()
            row.label(text = "Type")
            row.prop(component, "type", text = "")

            # Render orientation selector
            if component.type == "Capsule" or component.type == "Cylinder":
                col = self.layout.column()
                row = col.split()
                row.label(text = "Orientation")
                row.prop(component, "orientation", text = "")

            # Render position
            col = self.layout.column()
            col.prop(component, "pos")

            # Render radius and height
            if component.type == "Capsule" or component.type == "Cylinder" or component.type == "Sphere":
                self.layout.prop(component, "radius")
            if component.type == "Capsule" or component.type == "Cylinder":
                self.layout.prop(component, "height")

            # Render box size
            if component.type == "Box":
                col = self.layout.column()
                col.prop(component, "size")

            # Render convex mesh name
            if component.type == "Convex":
                box = self.layout.box()
                col = box.column()
                col.label(text = "Mesh name")
                col.prop(component, "mesh", text = "")
        else:
            self.layout.label(text = "No active component")

CLASS = [CollisionComponent, Settings, COLLISION_OP_add, COLLISION_OP_remove, COLLISION_PT_panel, COLLISION_UL_component]

def register():
    for cl in CLASS:
        bpy.utils.register_class(cl)
    bpy.types.Scene.bp3d_collision_settings = bpy.props.PointerProperty(type=Settings)

def unregister():
    global draw_handler
    for cl in CLASS:
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.bp3d_collision_settings
    if draw_handler != None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
        draw_handler = None

if __name__ == "__main__":
    register()
