import os

import numpy as np
import sapien.core as sapien
from pathlib import Path

_NAME_MAPPING = {
    "allegro": "assets/robot/allegro_hand_description_right.urdf",
    "allegro_left": "assets/robot/allegro_hand_description_left.urdf",
    "allegro_right": "assets/robot/allegro_hand_description_right.urdf",
    "adroit": "assets/robot/adroit_hand_free.urdf",
    "adroit_wrist_free": "assets/robot/adroit_hand_wrist_free.urdf",
}
SUPPORTED_ROBOT = list(_NAME_MAPPING.keys())


def load_robot(renderer: sapien.VulkanRenderer, scene: sapien.Scene, robot_name):
    loader = scene.create_urdf_loader()
    current_dir = Path(__file__) / "../"
    package_dir = (current_dir / "../").resolve()
    filename = str(package_dir / _NAME_MAPPING[robot_name])
    robot_builder = loader.load_file_as_articulation_builder(filename)
    for link_builder in robot_builder.get_link_builders():
        link_builder.set_collision_groups(0, 1, 2, 2)
    robot = robot_builder.build(fix_root_link=True)
    robot.set_qpos(np.zeros([robot.dof]))
    scene.step()
    scene.update_render()

    # Robot specific property
    if 'adroit' in robot_name:
        for link in robot.get_links():
            for geom in link.get_visual_bodies():
                for shape in geom.get_render_shapes():
                    mat_viz = shape.material
                    mat_viz.set_base_color(np.array([0.9, 0.7, 0.5, 1]))
                    mat_viz.set_specular(0.7)
                    mat_viz.set_metallic(0.1)
                    mat_viz.set_roughness(0.1)

    for joint in robot.get_active_joints():
        joint.set_drive_property(1000, 200)

    return robot
