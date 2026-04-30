# KUKA KR 6 R1820 arc HW ROS 2 description

ROS 2 workspace for building and debugging a KUKA KR 6 R1820 arc hollow-wrist robot description.

The repository combines:

- a ROS 2 `kuka_robot_descriptions` workspace,
- a custom `kr6_r1820_arc_hw` model under `kuka_cybertech_support`,
- CAD helper scripts for extracting and grouping meshes from the original STEP file,
- a current visual/kinematic debug workflow for aligning the robot joint frames.

## Repository Layout

```text
.
|-- cad/
|   `-- kr6_r1820_arc_hw/
|       |-- KR6 R1820 HW.stp
|       |-- exported_solids/
|       |-- grouped_preview/
|       |-- grouped_local_frames/
|       |-- *.py
|       `-- NOTES.md
`-- src/
    `-- kuka_robot_descriptions/
        |-- kuka_cybertech_support/
        |-- kuka_kr_moveit_config/
        `-- ...
```

The active robot model is here:

```text
src/kuka_robot_descriptions/kuka_cybertech_support/urdf/kr6_r1820_arc_hw.urdf.xacro
src/kuka_robot_descriptions/kuka_cybertech_support/urdf/kr6_r1820_arc_hw_macro.xacro
```

The current debug notes are here:

```text
cad/kr6_r1820_arc_hw/NOTES.md
```

## Quick Start

Build the workspace:

```bash
cd /home/luka/kuka_kr6_r1820_ros2
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Open the KR 6 R1820 arc HW model in RViz:

```bash
ros2 launch kuka_cybertech_support test_kr6_r1820_arc_hw.launch.py
```

This starts:

- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`

Use `joint_state_publisher_gui` to move individual joints and inspect whether each child link rotates around the expected physical axis.

## Validate The URDF

For a fast syntax/tree check without RViz:

```bash
cd /home/luka/kuka_kr6_r1820_ros2
source /opt/ros/jazzy/setup.bash
source install/setup.bash
xacro src/kuka_robot_descriptions/kuka_cybertech_support/urdf/kr6_r1820_arc_hw.urdf.xacro mode:=mock use_gpio:=false > /tmp/kr6_r1820_arc_hw.urdf
check_urdf /tmp/kr6_r1820_arc_hw.urdf
```

Expected result:

```text
Successfully Parsed XML
```

## Current Debug State

The model is intentionally in a visual debug state:

- `joint_1` and `joint_2` are treated as accepted.
- `base_link`, `link_1`, and `link_2` visuals are visible and semi-transparent.
- `link_3` through `link_6` visuals are temporarily hidden.
- `joint_3` is currently tuned for the A3 center.
- `joint_4` is simplified to isolate the next frame placement.

Important current values in `kr6_r1820_arc_hw_macro.xacro`:

```xml
<joint name="${prefix}joint_3" type="revolute">
  <parent link="${prefix}link_2"/>
  <child link="${prefix}link_3"/>
  <origin xyz="0.81 0 -0.012" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
</joint>

<joint name="${prefix}joint_4" type="revolute">
  <parent link="${prefix}link_3"/>
  <child link="${prefix}link_4"/>
  <origin xyz="0.36 0 0" rpy="1.5707963267948966 0 -1.5707963267948966"/>
  <axis xyz="0 0 1"/>
</joint>
```

## How URDF/Xacro Pieces Work

`link` defines a rigid body.

```xml
<link name="${prefix}link_2">
  ...
</link>
```

`visual` defines only how that body is drawn in RViz.

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <mesh filename="${mesh_path}/link_2.stl" scale="${mesh_scale}"/>
  </geometry>
</visual>
```

Changing `visual/origin` moves only the displayed mesh inside the link frame. It does not change the kinematic model.

`joint` defines where the child link frame attaches to the parent link frame.

```xml
<joint name="${prefix}joint_3" type="revolute">
  <parent link="${prefix}link_2"/>
  <child link="${prefix}link_3"/>
  <origin xyz="0.81 0 -0.012" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
</joint>
```

Changing `joint/origin` moves the child link and everything after it in the kinematic chain.

`axis` is expressed in the joint frame after the `origin rpy` rotation is applied. Most KUKA joints in this model use:

```xml
<axis xyz="0 0 1"/>
```

and rely on `origin rpy` to orient that local Z axis correctly.

## CAD Helper Scripts

The CAD tools live in:

```text
cad/kr6_r1820_arc_hw/
```

They use FreeCAD Python APIs. Run them with a FreeCAD-capable Python environment, for example:

```bash
freecadcmd cad/kr6_r1820_arc_hw/inspect_kr6_step.py
```

Current scripts:

| Script | Purpose |
| --- | --- |
| `inspect_kr6_step.py` | Loads the STEP file and prints object names, solid counts, and bounding boxes. Use this first to understand the raw CAD structure. |
| `export_kr6_solids.py` | Exports each individual STEP solid into `exported_solids/` as a separate STL. Useful for identifying which CAD solids belong to each robot link. |
| `group_kr6_solids.py` | Groups selected solid indices into one STL per robot link in the original CAD/world placement. Output goes to `grouped_preview/`. |
| `group_kr6_solids_local_frames.py` | Groups solids and transforms them into each link's local URDF frame. Output goes to `grouped_local_frames/`. These are the meshes used for the ROS model workflow. |
| `inspect_cylinders.py` | Finds cylindrical faces in grouped CAD solids. Useful for locating likely joint axes and bearing/shaft centers. |
| `print_urdf_frames.py` | Computes and prints URDF frame positions from the current hand-written joint transforms. Useful as a quick transform sanity check. |

Note: several CAD scripts currently contain absolute paths from the original local workspace, such as:

```text
/home/luka/ros2_ws/cad/kr6_r1820_arc_hw/...
```

If the scripts are run from this repository, update those constants to:

```text
/home/luka/kuka_kr6_r1820_ros2/cad/kr6_r1820_arc_hw/...
```

before regenerating meshes.

## Meshes

The current KR 6 R1820 visual meshes are installed under:

```text
src/kuka_robot_descriptions/kuka_cybertech_support/meshes/kr6_r1820_arc_hw/visual/
```

The source CAD-derived local-frame meshes are under:

```text
cad/kr6_r1820_arc_hw/grouped_local_frames/
```

STL files define geometry only. Changing URDF joint origins does not shorten, stretch, or cut STL geometry.

## MoveIt

The generic KUKA KR MoveIt config includes `kr6_r1820_arc_hw` in:

```text
src/kuka_robot_descriptions/kuka_kr_moveit_config/CMakeLists.txt
```

Joint velocity limits are defined in:

```text
src/kuka_robot_descriptions/kuka_cybertech_support/config/kr6_r1820_arc_hw_joint_limits.yaml
```

## Development Workflow

Recommended order for debugging:

1. Keep later link visuals hidden.
2. Validate one joint at a time from base to flange.
3. Check the center of rotation in RViz with TF enabled.
4. Move `joint/origin xyz` only when the kinematic frame is wrong.
5. Move `visual/origin` only when the mesh is visually offset inside an otherwise correct frame.
6. Re-run `xacro` and `check_urdf` after every meaningful change.
7. Commit small, understandable steps.
