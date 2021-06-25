import argparse

import numpy as np
import sapien.core as sapien
from sapien.utils import Viewer

from sapien_viz.utils.common_robot import load_robot
from sapien_viz.utils.ycb_object import load_ycb_objects


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--affordance-file', action='store', type=str, required=True,
                        help="Filename to save the robot joint trajectory")
    parser.add_argument('--fps', action='store', type=int, default=10, help="FPS to visualize the trajectory")
    parser.add_argument('--object', '-o', type=str, default="tomato_soup_can")
    return parser.parse_args()


def visualize_affordance_state_trajectory(visual_qpos_traj, sim_qpos_traj, fps, object_name):
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

    # Object
    object_actors = load_ycb_objects(renderer, scene, [object_name], static=True)

    # Articulation
    robot_name = "adroit_wrist_free"
    sim_robot = load_robot(renderer, scene, robot_name)
    trajectory_dof = visual_qpos_traj.shape[1]
    if trajectory_dof != sim_robot.dof and trajectory_dof > 0:
        raise ValueError(f"DoF not match: given trajectory has {trajectory_dof} joints"
                         f" while the robot model only has {sim_robot.dof} joints")
    trajectory_dof = sim_qpos_traj.shape[1]
    if trajectory_dof != sim_robot.dof and trajectory_dof > 0:
        raise ValueError(f"DoF not match: given trajectory has {trajectory_dof} joints"
                         f" while the robot model only has {sim_robot.dof} joints")

    viz_robot = load_robot(renderer, scene, robot_name)
    for link in viz_robot.get_links():
        for body in link.get_visual_bodies():
            body.set_visibility(0.5)
    scene.step()

    trajectory_length = sim_qpos_traj.shape[0]

    for i in range(trajectory_length):
        viz_robot.set_qpos(visual_qpos_traj[i])
        sim_robot.set_qpos(sim_qpos_traj[i])
        for _ in range(int(60 / fps)):
            scene.update_render()
            viewer.render()

    while not viewer.closed:
        scene.update_render()
        viewer.render()


def main():
    args = parse_args()
    data = np.load(args.affordance_file, allow_pickle=True)
    affordance = data["affordance"]
    state = data["state"]
    visual_qpos = affordance
    sim_qpos = state[:, :30]
    visualize_affordance_state_trajectory(visual_qpos, sim_qpos, args.fps, args.object)


if __name__ == '__main__':
    main()
