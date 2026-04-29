import os
import traceback

import FreeCAD
import Import

step_path = "/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/KR6 R1820 HW.stp"
print(f"exists={os.path.exists(step_path)} path={step_path}")

try:
    doc = FreeCAD.newDocument("kr6_inspect")
    Import.insert(step_path, doc.Name)
    doc.recompute()
except Exception:
    traceback.print_exc()
    raise

print(f"document_objects={len(doc.Objects)}")
for index, obj in enumerate(doc.Objects):
    shape = getattr(obj, "Shape", None)
    solids = len(shape.Solids) if shape is not None else 0
    compounds = len(shape.Compounds) if shape is not None else 0
    shells = len(shape.Shells) if shape is not None else 0
    bbox = shape.BoundBox if shape is not None else None
    if bbox is not None:
        print(
            f"{index}: label={obj.Label!r} name={obj.Name!r} type={obj.TypeId} "
            f"solids={solids} compounds={compounds} shells={shells} "
            f"bbox_mm=({bbox.XMin:.1f},{bbox.YMin:.1f},{bbox.ZMin:.1f})"
            f"-({bbox.XMax:.1f},{bbox.YMax:.1f},{bbox.ZMax:.1f})"
        )
    else:
        print(f"{index}: label={obj.Label!r} name={obj.Name!r} type={obj.TypeId}")
