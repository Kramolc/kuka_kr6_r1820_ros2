import math
from pathlib import Path

import FreeCAD
import Import
import Mesh
import Part

STEP_PATH = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/KR6 R1820 HW.stp"
OUT_DIR = Path("/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/grouped_local_frames")
OUT_DIR.mkdir(parents=True, exist_ok=True)

GROUPS = {
    "base_link": [0, 5, 40, 41, 42, 43, 44, 45, 46, 47],
    "link_1": [1, 2, 3, 26, 27, 32, 34, 35],
    "link_2": [6, 7, 8, 9, 21, 28, 29, 30, 31, 33],
    "link_3": [4, 22, 36, 37, 38, 39],
    "link_4": [11, 23, 24, 25],
    "link_5": [10, 16, 17, 18, 19, 20],
    "link_6": [12, 13, 14, 15],
}


def placement(xyz, rpy):
    x, y, z = xyz
    roll, pitch, yaw = rpy
    rot_x = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), math.degrees(roll))
    rot_y = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.degrees(pitch))
    rot_z = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.degrees(yaw))
    # URDF rpy is fixed-axis roll, pitch, yaw: R = Rz * Ry * Rx.
    return FreeCAD.Placement(
        FreeCAD.Vector(x * 1000.0, y * 1000.0, z * 1000.0),
        rot_z.multiply(rot_y).multiply(rot_x),
    )


def compose(parent, child):
    return parent.multiply(child)


def joint_z(angle):
    return FreeCAD.Placement(
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.degrees(angle)),
    )


PI = math.pi
# The KUKA STEP file is exported in a mastering-like pose, not the URDF
# zero pose. These reference angles align the imported CAD solids with the
# URDF link frames before each mesh is written in its local frame.
Q_REF = {
    "joint_1": 0.0,
    "joint_2": -PI / 2,
    "joint_3": PI / 2,
    "joint_4": 0.0,
    "joint_5": 0.0,
    "joint_6": 0.0,
}

T = {}
T["base_link"] = FreeCAD.Placement()
T["link_1"] = compose(compose(T["base_link"], placement((0, 0, 0.31), (PI, 0, 0))), joint_z(Q_REF["joint_1"]))
T["link_2"] = compose(compose(T["link_1"], placement((0.15, 0.064, -0.14), (PI / 2, 0, 0))), joint_z(Q_REF["joint_2"]))
T["link_3"] = compose(compose(T["link_2"], placement((0.85, 0, -0.012), (0, 0, 0))), joint_z(Q_REF["joint_3"]))
T["link_4"] = compose(compose(T["link_3"], placement((0.36, -0.20, 0.075), (PI / 2, 0, -PI / 2))), joint_z(Q_REF["joint_4"]))
T["link_5"] = compose(compose(T["link_4"], placement((0, -0.041, -0.45), (0, PI / 2, PI / 2))), joint_z(Q_REF["joint_5"]))
T["link_6"] = compose(compose(T["link_5"], placement((0.066, 0, 0.041), (PI / 2, 0, -PI / 2))), joint_z(Q_REF["joint_6"]))

doc = FreeCAD.newDocument("kr6_groups_local")
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
    local_shapes = []
    inv = T[group_name].inverse()
    for index in indices:
        shape = solid_objects[index].Shape.copy()
        shape.Placement = inv.multiply(shape.Placement)
        local_shapes.append(shape)

    compound = Part.makeCompound(local_shapes)
    mesh = Mesh.Mesh()
    mesh.addFacets(compound.tessellate(1.0))
    path = OUT_DIR / f"{group_name}.stl"
    mesh.write(str(path))
    bbox = compound.BoundBox
    print(
        f"{group_name}: solids={indices} triangles={mesh.CountFacets} "
        f"local_bbox_mm=({bbox.XMin:.1f},{bbox.YMin:.1f},{bbox.ZMin:.1f})"
        f"-({bbox.XMax:.1f},{bbox.YMax:.1f},{bbox.ZMax:.1f}) file={path}"
    )
