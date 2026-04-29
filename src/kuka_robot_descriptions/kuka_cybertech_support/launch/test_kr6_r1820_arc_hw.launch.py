# Copyright 2026
#
# Licensed under the Apache License, Version 2.0.

from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("kuka_cybertech_support"),
                    "urdf",
                    "kr6_r1820_arc_hw.urdf.xacro",
                ]
            ),
            " ",
            "mode:=mock",
            " ",
            "use_gpio:=false",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("kuka_resources"), "config", "view_6_axis_urdf.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_launch",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[robot_description],
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="log",
    )

    return LaunchDescription([robot_state_publisher, rviz_node, joint_state_publisher_gui])
