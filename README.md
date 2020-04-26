# BlockProject 3D Blender Export Scripts
Export scripts for Blender. Currently only Blender 2.8 is supported.

## Intermediate format
All 3D modelling tools are expected to export to an intermediate format. OBJ was chosen for it's simple use and Open Source.
Because OBJ does not support animations and armatures, BlockProject 3D Object file has been designed based on OBJ format and is retrocompatible with any OBJ reader assuming it can correctly skip comments.
The BlockProject 3D Object is designed in 3 files:
- The main .bp3d.obj which contains the core model with cuts for models supporting multi-material.
- The .armature.bp3d.obj stores all vertex weights, vertex bone indices and actual bone information.
- The .animation.bp3d.obj stores all the frames recorded in the timeline

This intermediate format is intended to be parsed by the ModelCompiler in order to generate rendering API and platform independent data. ModelCompiler will generate a BPX type M file for both OBJ and BP3D OBJ formats.