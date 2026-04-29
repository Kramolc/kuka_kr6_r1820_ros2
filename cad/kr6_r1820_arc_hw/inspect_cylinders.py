from pathlib import Path

import FreeCAD
import Import

STEP_PATH = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/KR6 R1820 HW.stp"

GROUPS = {
    "base_link": [0, 5, 40, 41, 42, 43, 44, 45, 46, 47],
    "link_1": [1, 2, 3, 26, 27, 32, 34, 35],
    "link_2": [6, 7, 8, 9, 21, 28, 29, 30, 31, 33],
    "link_3": [4, 22, 36, 37, 38, 39],
    "link_4": [11, 23, 24, 25],
    "link_5": [10, 16, 17, 18, 19, 20],
    "link_6": [12, 13, 14, 15],
}


def vec(v):
    return f"({v.x:.1f},{v.y:.1f},{v.z:.1f})"


doc = FreeCAD.newDocument("kr6_cylinders")
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
    print(f"\n[{group_name}]")
    rows = []
    for index in indices:
        shape = solid_objects[index].Shape
        for face_i, face in enumerate(shape.Faces):
            surface = face.Surface
            if surface.TypeId != "Part::GeomCylinder":
                continue
            rows.append(
                (
                    round(surface.Radius, 3),
                    index,
                    face_i,
                    surface.Center,
                    surface.Axis,
                    face.Area,
                )
            )

    for radius, index, face_i, center, axis, area in sorted(rows, reverse=True)[:30]:
        print(
            f"solid={index:02d} face={face_i:03d} "
            f"r={radius:8.3f} area={area:10.1f} "
            f"center={vec(center)} axis={vec(axis)}"
        )
