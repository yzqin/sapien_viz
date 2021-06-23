import argparse

import numpy as np
import sapien.core as sapien
from sapien.utils import Viewer

from sapien_viz.utils.common_robot import SUPPORTED_ROBOT, load_robot


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--robot', action='store', type=str, required=True, help="Name of the robot")
    parser.add_argument('-j', '--joint-pos', nargs='+', type=float,
                        help="Single frame joint pos. For joint trajectory visualization, please use numpy file")
    parser.add_argument('-f', '--joint-file', action='store', type=str, required=False,
                        help="Filename to save the robot joint trajectory")
    parser.add_argument('--fps', action='store', type=int, default=10, help="FPS to visualize the trajectory")
    parser.add_argument('-s', '--smooth', action="store_true", default=False,
                        help="Whether to use drive to generate trajectory (simulate but not animate)")
    parser.add_argument('--dict-key', action='store', type=str,
                        help="Key name for joint pos if the given file is a dict")
    return parser.parse_args()


def visualize_articulation(robot_name, qpos_array=np.zeros([0, 0]), fps=10, smooth=False):
    # Setup
    engine = sapien.Engine()
    renderer = sapien.VulkanRenderer(offscreen_only=False)
    engine.set_renderer(renderer)
    config = sapien.SceneConfig()
    config.gravity = np.array([0, 0, 0])
    scene = engine.create_scene(config=config)
    scene.set_timestep(1 / 125)
    visual_material = renderer.create_material()
    visual_material.set_base_color(np.array([132, 131, 101, 255]) / 255)
    visual_material.set_roughness(0.8)
    scene.add_ground(-1, render_material=visual_material)

    # Lighting
    render_scene = scene.get_renderer_scene()
    render_scene.set_ambient_light(np.array([0.6, 0.6, 0.6]))
    render_scene.add_directional_light(np.array([1, -1, -1]), np.array([0.5, 0.5, 0.5]))
    render_scene.add_point_light(np.array([2, 2, 2]), np.array([1, 1, 1]))
    render_scene.add_point_light(np.array([2, -2, 2]), np.array([1, 1, 1]))
    render_scene.add_point_light(np.array([-2, 0, 2]), np.array([1, 1, 1]))

    # Viewer
    viewer = Viewer(renderer)
    viewer.set_scene(scene)
    viewer.set_camera_xyz(1, 0, 1)
    viewer.set_camera_rpy(0, -0.6, 3.14)
    viewer.toggle_axes(0)

    # Articulation
    robot = load_robot(renderer, scene, robot_name)
    trajectory_dof = qpos_array.shape[1]
    if trajectory_dof != robot.dof and trajectory_dof > 0:
        raise ValueError(f"DoF not match: given trajectory has {trajectory_dof} joints"
                         f" while the robot model only has {robot.dof} joints")

    # Visualization Loop
    trajectory_length = qpos_array.shape[0]
    scene.step()
    scene.update_render()

    for i in range(trajectory_length):
        if smooth:
            robot.set_drive_target(qpos_array[i])
            robot.set_qpos(qpos_array[i])
        else:
            robot.set_qpos(qpos_array[i])
        for _ in range(int(fps)):
            scene.update_render()
            viewer.render()
    if trajectory_length > 0:
        print(f"Finish visualize robot trajectory with {trajectory_length} trajectory points.")

    while not viewer.closed:
        scene.update_render()
        viewer.render()


def main():
    args = parse_args()
    if args.robot not in SUPPORTED_ROBOT:
        raise ValueError(
            f"Robot name {args.robot} not supported. List of supported robots are shown below: \n{SUPPORTED_ROBOT}")

    qpos = args.joint_pos
    if qpos is not None:
        qpos_array = np.array(qpos)[None, :]
    else:
        qpos_array = np.zeros([0, 0])

    if args.joint_pos is not None and args.joint_file is not None:
        raise RuntimeError(f"Joint position and joint filename are both given, conflict!")

    if args.joint_file is not None:
        joint_pos = np.load(args.joint_file, allow_pickle=True)
        if isinstance(joint_pos, dict):
            if args.dict_key is None:
                raise RuntimeError(f"File {args.joint_file} is a dict but dict key is not given."
                                   f" Do not know which dict key to use.")
            joint_pos = np.array(joint_pos[args.dict_key])
        elif isinstance(joint_pos, np.ndarray):
            pass
        elif isinstance(joint_pos, list):
            joint_pos = np.array(joint_pos)
        else:
            raise TypeError(f"Unsupported data type {type(joint_pos)}")

        if len(joint_pos.shape) == 1:
            qpos_array = joint_pos[None, :]
        elif len(joint_pos.shape) > 2:
            raise ValueError(f"Joint pos in file {args.joint_pos} has not supported shape {joint_pos.shape}")
        else:
            qpos_array = joint_pos[:, :]

    visualize_articulation(args.robot, qpos_array, args.fps, args.smooth)


if __name__ == '__main__':
    main()
