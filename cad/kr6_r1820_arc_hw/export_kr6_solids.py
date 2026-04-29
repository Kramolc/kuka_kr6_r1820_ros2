import os

import FreeCAD
import Import
import Mesh

step_path = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/KR6 R1820 HW.stp"
out_dir = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/exported_solids"
os.makedirs(out_dir, exist_ok=True)

doc = FreeCAD.newDocument("kr6_export")
Import.insert(step_path, doc.Name)
doc.recompute()

solid_objects = []
for obj in doc.Objects:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        continue
    if len(shape.Solids) != 1:
        continue
    if not obj.Label.startswith("COMPOUND"):
        continue
    solid_objects.append(obj)

print(f"exporting_solids={len(solid_objects)}")
for index, obj in enumerate(solid_objects):
    shape = obj.Shape
    bbox = shape.BoundBox
    mesh = Mesh.Mesh()
    mesh.addFacets(shape.tessellate(0.75))
    filename = os.path.join(out_dir, f"solid_{index:02d}_{obj.Label}.stl")
    mesh.write(filename)
    print(
        f"{index:02d} {obj.Label} triangles={mesh.CountFacets} "
        f"bbox_mm=({bbox.XMin:.1f},{bbox.YMin:.1f},{bbox.ZMin:.1f})"
        f"-({bbox.XMax:.1f},{bbox.YMax:.1f},{bbox.ZMax:.1f}) "
        f"file={filename}"
    )
