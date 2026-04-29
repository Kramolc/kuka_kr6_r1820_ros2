import math

import FreeCAD


def placement(xyz, rpy):
    x, y, z = xyz
    roll, pitch, yaw = rpy
    rot_x = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), math.degrees(roll))
    rot_y = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.degrees(pitch))
    rot_z = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), math.degrees(yaw))
    return FreeCAD.Placement(
        FreeCAD.Vector(x * 1000.0, y * 1000.0, z * 1000.0),
        rot_z.multiply(rot_y).multiply(rot_x),
    )


def compose(parent, child):
    return parent.multiply(child)


PI = math.pi
frames = {}
frames["base_link"] = FreeCAD.Placement()
frames["link_1"] = compose(frames["base_link"], placement((0, 0, 0.31), (PI, 0, 0)))
frames["link_2"] = compose(frames["link_1"], placement((0.15, 0.064, -0.14), (PI / 2, 0, 0)))
frames["link_3"] = compose(frames["link_2"], placement((0.85, 0, -0.012), (0, 0, 0)))
frames["link_4"] = compose(frames["link_3"], placement((0.36, -0.20, 0.075), (PI / 2, 0, -PI / 2)))
frames["link_5"] = compose(frames["link_4"], placement((0, -0.041, -0.45), (0, PI / 2, PI / 2)))
frames["link_6"] = compose(frames["link_5"], placement((0.066, 0, 0.041), (PI / 2, 0, -PI / 2)))

for name, frame in frames.items():
    base = frame.Base
    print(f"{name}: xyz_mm=({base.x:.1f}, {base.y:.1f}, {base.z:.1f})")
