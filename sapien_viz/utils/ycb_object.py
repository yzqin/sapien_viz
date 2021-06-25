import os
from pathlib import Path

import sapien.core as sapien

_YCB_OBJECT_MAPPING = {"master_chef_can": "002", "cracker_box": "003", "sugar_box": "004", "tomato_soup_can": "005",
                       "mustard_bottle": "006", "potted_meat_can": "010", "banana": "011", "bleach_cleanser": "021",
                       "bowl": "024", "mug": "025", "large_clamp": "051"}

SUPPORTED_OBJECT = list(_YCB_OBJECT_MAPPING.keys())


def load_ycb_objects(renderer: sapien.VulkanRenderer, scene: sapien.Scene, object_names, static=False):
    asset_root = Path(__file__) / "../" / "../" / "assets"
    ycb_dir = asset_root / "ycb"
    actors = {}

    for object_name in object_names:
        if object_name not in SUPPORTED_OBJECT:
            raise ValueError(f"Object name {object_name} is not supported.")
        visual_file = ycb_dir / "visual" / f"{_YCB_OBJECT_MAPPING[object_name]}_{object_name}" / "textured_simple.obj"
        builder = scene.create_actor_builder()
        builder.add_visual_from_file(filename=str(visual_file.resolve()), scale=[1] * 3)
        collision_dir = ycb_dir / "collision" / f"{_YCB_OBJECT_MAPPING[object_name]}_{object_name}"
        for collision_file in collision_dir.resolve().iterdir():
            if str(collision_file).endswith(("stl", "obj")) and 'convex' not in str(collision_file):
                builder.add_collision_from_file(filename=str(collision_file))

        if static:
            actor = builder.build_static(object_name)
        else:
            actor = builder.build(object_name)
        actors[object_name] = actor

    return actors
