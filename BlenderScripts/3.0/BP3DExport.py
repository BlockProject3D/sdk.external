# Copyright (c) 2020, BlockProject
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
#     * Neither the name of BlockProject nor the names of its contributors
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

bl_info = {
    "name" : "Export",
    "author" : "Yuri6037",
    "description" : "BlockProject 3D Export tool",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "BP3D"
}

import bpy
import bmesh
from bpy.utils import register_class
from bpy.utils import unregister_class
from bpy_extras.io_utils import ExportHelper

def getParts(obj): 
    parts = []
    parts.append(obj)
    for o in bpy.data.objects:
        if o.parent == obj:
            parts.append(o)
    return parts

def objectToTriangulatedMesh(obj, context):
    dg = context.evaluated_depsgraph_get()
    o1 = obj.evaluated_get(dg)
    mesh = o1.to_mesh()
    mat = obj.matrix_world
    if (mat.determinant() < 0):
        mesh.flip_normals()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.transform(bm, matrix=mat)
    bm.to_mesh(mesh)
    bm.free()
    return (mesh)

def key2d(v):
    return (v[0], v[1])

def key3d(v):
    return (v.x, v.y, v.z)

def writeArmatureFile(armature, fileName):
    fileName = fileName[0:len(fileName) - len(".bp3d.obj")] + ".armature.bp3d.obj"
    boneMap = {}
    count = 1
    file = open(fileName, "w", encoding="utf8", newline="\n")
    file.write("## BlockProject 3D Object Armature\n")
    file.write("\n")
    for bone in armature.bones:
        # The "bone" command takes bone name, bone head position x3 and bone tail position x3
        file.write("bone {} {} {} {} {} {} {}\n".format(bone.name, bone.head[0], bone.head[1], bone.head[2], bone.tail[0], bone.tail[1], bone.tail[2]))
        boneMap[bone.name] = count
        count += 1
    return (boneMap, file)

def writeAnimationFile(scene, boneMap, armatureWeird, fileName):
    fileName = fileName[0:len(fileName) - len(".bp3d.obj")] + ".animation.bp3d.obj"
    with open(fileName, "w", encoding="utf8", newline="\n") as file:
        file.write("## BlockProject 3D Object Animation\n")
        file.write("\n")
        for f in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(f)
            # The "frame" command takes the frame number
            file.write("frame {}\n".format(f))
            for pbone in armatureWeird.pose.bones:
                # The "transform" command takes the target bone id, the target bone position x3, the target bone scale x3 and the target bone rotation quaternion x4
                boneId = boneMap[pbone.name]
                file.write("transform {} {} {} {} {} {} {} {} {} {} {}\n".format(boneId, pbone.location.x, pbone.location.y, pbone.location.z, pbone.scale.x, pbone.scale.y, pbone.scale.z, pbone.rotation_quaternion.w, pbone.rotation_quaternion.x, pbone.rotation_quaternion.y, pbone.rotation_quaternion.z))
    scene.frame_set(0)

class BP3D_Export(bpy.types.Operator, ExportHelper):
    """Export as BlockProject 3D modified Object format"""
    bl_idname = "b3d.export" # Not called bp3d as Blender refuses to respect case
    bl_label = "BlockProject 3D Export"
    filename_ext = ".bp3d.obj"

    def execute(self, context):
        filepath = self.filepath
        armature = None
        armWeird = None
        for mod in context.object.modifiers:
            if (mod.type == "ARMATURE"):
                armature = mod.object.data
                armWeird = mod.object
        parts = getParts(context.object)
        print("BP3D OBJ #parts: {}".format(len(parts)))
        boneMap = None
        armFile = None
        if (armature != None):
            boneMap, armFile = writeArmatureFile(armature, filepath)
            writeAnimationFile(context.scene, boneMap, armWeird, filepath)
        with open(filepath, "w", encoding="utf8", newline="\n") as file:
            file.write("## BlockProject 3D Object\n")
            file.write("#version 1\n")
            if (armature != None):
                file.write("#use ArmatureAnimation")
            useMultiMaterial = False
            if (len(parts) > 1):
                useMultiMaterial = True
                file.write("#use MultiMaterial\n")
                file.write("#AllocMat {}\n".format(len(parts)))
            file.write("\n")
            sd = 0
            vcount = 1
            ncount = 1
            uvcount = 1
            for part in parts:
                print(part.type)
                file.write("\n")
                #SubMaterial (index of sub material, number to subtract to vertex id, number to subtract to uv id, number to subtract to normal id)
                if (useMultiMaterial):
                    file.write("#SubMaterial {} {} {} {}\n".format(sd, vcount, uvcount, ncount))
                mesh = objectToTriangulatedMesh(part, context)
                uvlayer = None
                if (len(mesh.uv_layers) > 0):
                    uvlayer = mesh.uv_layers.active.data[:]
                facePairs = [(face, index) for index, face in enumerate(mesh.polygons)]
                mesh.calc_normals_split()
                file.write("## Vertices\n")
                for v in mesh.vertices:
                    file.write("v {} {} {}\n".format(v.co.x, v.co.y, v.co.z))
                    if (armature != None):
                        cmd = "vb"
                        cmd1 = "vw"
                        for group in v.groups:
                            boneId = boneMap[part.vertex_groups[group.group].name]
                            cmd += " {}".format(boneId)
                            cmd1 += " {}".format(group.weight)
                        cmd += "\n"
                        cmd1 += "\n"
                        armFile.write(cmd)
                        armFile.write(cmd1)
                file.write("## Normals\n")
                normalMap = {}
                loopsToNormals = [0] * len(mesh.loops)
                nsubcount = 0
                for f, id in facePairs:
                    for lid in f.loop_indices:
                        key = key3d(mesh.loops[lid].normal)
                        val = normalMap.get(key)
                        if (val is None):
                            val = nsubcount
                            normalMap[key] = val
                            nsubcount += 1
                            file.write("vn {} {} {}\n".format(key[0], key[1], key[2]))
                        loopsToNormals[lid] = val
                file.write("## UVs\n")
                uvMap = {}
                uvToFace = [None] * len(facePairs)
                uvsubcount = 0
                for f, fid in facePairs:
                    uvlist = []
                    uvToFace[fid] = uvlist
                    for uvid, lid in enumerate(f.loop_indices):
                        uv = uvlayer[lid].uv
                        key = (mesh.loops[lid].vertex_index, key2d(uv))
                        val = uvMap.get(key)
                        if (val is None):
                            val = uvsubcount
                            uvMap[key] = val
                            uvsubcount += 1
                            file.write("vt {} {}\n".format(uv.x, uv.y))
                        uvlist.append(val)
                file.write("## Faces\n")
                for f, fid in facePairs:
                    file.write("f")
                    faces = [(vi, mesh.vertices[vid], lid) for vi, (vid, lid) in enumerate(zip(f.vertices, f.loop_indices))]
                    for vi, v, li in faces:
                        file.write(" {}/{}/{}".format(vcount + v.index, uvcount + uvToFace[fid][vi], ncount + loopsToNormals[li]))
                    file.write("\n")
                vcount += len(mesh.vertices)
                uvcount += uvsubcount
                ncount += nsubcount
                sd += 1
        if (armFile != None):
            armFile.close()
        return {'FINISHED'}

def exportMenuEntry(self, nwjerptbm):
    self.layout.operator(BP3D_Export.bl_idname, text="BlockProject 3D")

def register():
    register_class(BP3D_Export)
    bpy.types.TOPBAR_MT_file_export.append(exportMenuEntry)

def unregister():
    unregister_class(BP3D_Export)
    bpy.types.TOPBAR_MT_file_export.remove(exportMenuEntry)

if __name__ == "__main__":
    register()
