# KR6 R1820 arc HW URDF debug notes

## Current approach

We debug the robot from the base toward the flange, one joint at a time.
`joint_1` and `joint_2` are treated as already aligned. Visual meshes for
`link_3` through `link_6` are temporarily hidden in the xacro so the next joint
can be added back and checked without visual clutter.

## Rules

- `link` defines a rigid body.
- `link/visual/origin` moves only the displayed mesh inside that link frame.
- `joint/origin` defines where the child link frame is attached to the parent
  link frame.
- `joint/axis` defines the rotation axis in the joint frame, after
  `joint/origin rpy` has oriented that frame.
- STL files define geometry only. Changing joint origins does not shorten,
  stretch, or cut STL geometry.

## Current chain

| Joint | Parent | Child | Status |
| --- | --- | --- | --- |
| joint_1 | base_link | link_1 | accepted |
| joint_2 | link_1 | link_2 | accepted |
| joint_3 | link_2 | link_3 | accepted for current debug view |
| joint_4 | link_3 | link_4 | simplified frame, visual hidden for now |
| joint_5 | link_4 | link_5 | hidden for now |
| joint_6 | link_5 | link_6 | hidden for now |

## Current key values

```xml
<joint name="${prefix}joint_3" type="revolute">
  <parent link="${prefix}link_2"/>
  <child link="${prefix}link_3"/>
  <origin xyz="0.81 0 -0.012" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
</joint>
```

`joint_4` is currently simplified to isolate the next attachment frame:

```xml
<joint name="${prefix}joint_4" type="revolute">
  <parent link="${prefix}link_3"/>
  <child link="${prefix}link_4"/>
  <origin xyz="0.36 0 0" rpy="1.5707963267948966 0 -1.5707963267948966"/>
  <axis xyz="0 0 1"/>
</joint>
```

To continue debugging, first add back only the visual mesh for `link_3`, then check:

- the center of rotation is at the physical A3 axis,
- rotating `joint_3` moves `link_3` around the correct axis,
- `link_3` mesh sits in the expected frame without using joint changes to fix
  mesh-only visual offsets.
