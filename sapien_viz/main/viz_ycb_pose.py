import argparse
import warnings
from pathlib import Path

import numpy as np
import sapien.core as sapien
from natsort import natsorted
from sapien.utils import Viewer

from sapien_viz.utils.ycb_object import SUPPORTED_OBJECT, load_ycb_objects, ID2OBJECT


def parse_args():
    link = "https://github.com/yzqin/viz_utils/tree/master/test_assets/viz_ycb_pose_example_dir"
    hel_str = f"Please see {link}" " for more details about the data format used by this script"
    parser = argparse.ArgumentParser(description=hel_str)
    parser.add_argument('-d', '--directory', action='store', type=str, required=True,
                        help=f"Directory contains pose sequence, example: {link}")
    parser.add_argument('--fps', action='store', type=int, default=2, help="FPS to visualize the trajectory")
    return parser.parse_args()


def visualize_ycb_pose_sequence(directory, fps):
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

    # YCB Objects
    pose_dir = Path(directory)
    if not pose_dir.is_dir():
        raise ValueError(f"{directory} is not a directory")
    print(f"Load object pose from {pose_dir.resolve()}")
    pose_seq_unsorted = []
    file_seq_unsorted = []
    for file in pose_dir.iterdir():
        data = np.load(str(file), allow_pickle=True)
        if isinstance(data, np.ndarray):
            if data.dtype == object:
                data = data[()]
        if not isinstance(data, dict):
            raise RuntimeError(f"Data type {type(data)} is not supported")
        pose_seq_unsorted.append(data)
        file_seq_unsorted.append(str(file.name))
    file_seq_sorted = natsorted(file_seq_unsorted)
    pose_seq = [pose_seq_unsorted[file_seq_unsorted.index(filename)] for filename in file_seq_sorted]

    object_set = set()
    new_pose_seq = []
    for pose_dict in pose_seq:
        new_pose_dict = {}
        if len(pose_dict) == 0:
            continue
        for key in pose_dict:
            if key in SUPPORTED_OBJECT:
                object_set.add(key)
                new_pose_dict.update({key: pose_dict[key]})
            else:
                key_id = str(key).split(".")[0]
                if key_id in ID2OBJECT:
                    object_set.add(ID2OBJECT[key_id])
                    new_pose_dict.update({ID2OBJECT[key_id]: pose_dict[key]})
                else:
                    warnings.warn(f"Object key {key} is not valid")
        new_pose_seq.append(new_pose_dict)

    print(f"Object set has {len(object_set)} objects: {object_set}")
    actors = load_ycb_objects(renderer, scene, list(object_set), static=True)
    scene.step()

    # Viewer
    viewer = Viewer(renderer)
    viewer.set_scene(scene)
    viewer.set_camera_xyz(1, 0, 1)
    viewer.set_camera_rpy(0, -0.6, 3.14)
    viewer.toggle_axes(0)

    render_per_frame = int(60 // fps)
    for k in range(len(new_pose_seq)):
        pose_dict = new_pose_seq[k]
        print(f"Current file: {file_seq_sorted[k]}, current object detected: {pose_dict.keys()}")
        for key, value in pose_dict.items():
            actors[key].set_pose(sapien.Pose.from_transformation_matrix(value))
        for _ in range(render_per_frame):
            scene.update_render()
            viewer.render()

    while not viewer.closed:
        scene.update_render()
        viewer.render()


def main():
    args = parse_args()
    visualize_ycb_pose_sequence(args.directory, args.fps)
