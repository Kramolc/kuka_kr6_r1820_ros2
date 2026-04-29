import os
from pathlib import Path

import FreeCAD
import Import
import Mesh
import Part

STEP_PATH = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/KR6 R1820 HW.stp"
OUT_DIR = Path("/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/grouped_preview")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Manual first-pass grouping based on the exported solid bounding boxes.
# This keeps obvious accessories/cables with their nearest robot body segment,
# but still needs visual RViz validation before treating it as final.
GROUPS = {
    "base_link": [0, 5, 40, 41, 42, 43, 44, 45, 46, 47],
    "link_1": [1, 2, 3, 26, 27, 32, 34, 35],
    "link_2": [6, 7, 8, 9, 21, 28, 29, 30, 31, 33],
    "link_3": [4, 22, 36, 37, 38, 39],
    "link_4": [11, 23, 24, 25],
    "link_5": [10, 16, 17, 18, 19, 20],
    "link_6": [12, 13, 14, 15],
}

doc = FreeCAD.newDocument("kr6_groups")
Import.insert(STEP_PATH, doc.Name)
doc.recompute()

solid_objects = []
for obj in doc.Objects:
    shape = getattr(obj, "Shape", None)
    if shape is None:
        continue
    if len(shape.Solids) == 1 and obj.Label.startswith("COMPOUND"):
        solid_objects.append(obj)

for group_name, indices in GROUPS.items():
    shapes = [solid_objects[i].Shape for i in indices]
    compound = Part.makeCompound(shapes)
    mesh = Mesh.Mesh()
    mesh.addFacets(compound.tessellate(1.0))
    path = OUT_DIR / f"{group_name}.stl"
    mesh.write(str(path))
    bbox = compound.BoundBox
    print(
        f"{group_name}: solids={indices} triangles={mesh.CountFacets} "
        f"bbox_mm=({bbox.XMin:.1f},{bbox.YMin:.1f},{bbox.ZMin:.1f})"
        f"-({bbox.XMax:.1f},{bbox.YMax:.1f},{bbox.ZMax:.1f}) file={path}"
    )
