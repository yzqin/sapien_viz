import argparse
import itertools

import numpy as np
import sapien.core as sapien
from sapien.utils import Viewer

from sapien_viz.utils.common_robot import SUPPORTED_ROBOT, load_robot
from sapien_viz.utils.ycb_object import SUPPORTED_OBJECT, load_ycb_objects


def parse_args():
    hand_object_file_help = """
    Hand Object File should be a dict contains the information of retargeted robot qpos and object pose
    It should be {
        "retarget_qpos" : List[np.ndarray], "object_pose": List[Dict[str: np.ndarray]]
    }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--robot', action='store', type=str, required=True, help="Name of the robot")
    parser.add_argument('-f', '--hand-object-file', type=str, required=True, help=hand_object_file_help)
    parser.add_argument('--fps', action='store', type=int, default=20, help="FPS to visualize the trajectory")
    return parser.parse_args()


def visualize_articulation(robot_name, fps, hand_object_data):
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

    qpos_array = hand_object_data["retarget_qpos"]
    object_pose = hand_object_data["object_pose"]
    trajectory_length = len(qpos_array)

    # Object
    object_name_seq = [list(object_pose[i].keys()) for i in range(trajectory_length)]
    object_name_seq = list(itertools.chain.from_iterable(object_name_seq))
    object_name_exist = list(np.unique(object_name_seq))
    for object_name in object_name_exist:
        if object_name not in SUPPORTED_OBJECT:
            raise ValueError(
                f"Robot name {object_name} not supported. "
                f"List of supported robots are shown below: \n{SUPPORTED_OBJECT}")
    objects = load_ycb_objects(renderer, scene, object_name_exist)

    scene.step()
    scene.update_render()

    # Visualization Loop
    for i in range(trajectory_length):
        robot.set_drive_target(qpos_array[i])
        robot.set_qpos(qpos_array[i])
        for object_name, pose in object_pose[i].items():
            objects[object_name].set_pose(sapien.Pose.from_transformation_matrix(pose))

        for _ in range(int(fps)):
            scene.update_render()
            viewer.render()
    if trajectory_length > 0:
        print(f"Finish visualize trajectory with {trajectory_length} trajectory points.")

    while not viewer.closed:
        scene.update_render()
        viewer.render()


def main():
    args = parse_args()
    if args.robot not in SUPPORTED_ROBOT:
        raise ValueError(
            f"Robot name {args.robot} not supported. List of supported robots are shown below: \n{SUPPORTED_ROBOT}")

    hand_object_data = np.load(args.hand_object_file, allow_pickle=True)
    if "retarget_qpos" not in hand_object_data or "object_pose" not in hand_object_data:
        raise RuntimeError(f"Hand object data loaded from {args.hand_object_file} does not contains necessary field.")
    if len(hand_object_data["retarget_qpos"]) != len(hand_object_data["object_pose"]):
        raise RuntimeError(f"Hand and object sequence loaded from {args.hand_object_file} does not have same length.")
    visualize_articulation(args.robot, args.fps, hand_object_data)


if __name__ == '__main__':
    main()
