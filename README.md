# viz_utils

## Installation

```bash
# Install SAPIEN from Python PYPI
pip3 install sapien 
```

Then install the visualization utils, including robot model:

```bash
git clone https://github.com/yzqin/viz_utils
cd viz_utils
pip3 install .
```

## Usage

```bash
usage: viz_robot [-h] -r ROBOT [-j JOINT_POS [JOINT_POS ...]] [-f JOINT_FILE] [--fps FPS] [-s] [--dict-key DICT_KEY]

optional arguments:
  -h, --help            show this help message and exit
  -r ROBOT, --robot ROBOT
                        Name of the robot
  -j JOINT_POS [JOINT_POS ...], --joint-pos JOINT_POS [JOINT_POS ...]
                        Single frame joint pos. For joint trajectory visualization, please use numpy file
  -f JOINT_FILE, --joint-file JOINT_FILE
                        Filename to save the robot joint trajectory
  --fps FPS             FPS to visualize the trajectory
  -s, --smooth          Whether to use drive to generate trajectory (simulate but not animate)
  --dict-key DICT_KEY   Key name for joint pos if the given file is a dict
```

For example, use the test data in this repo:

```bash
viz_robot -f test_assets/obj_id_37.pkl -r adroit_free --dict-key retarget_qpos -s
viz_hand_object -f test_assets/142517.pkl -r adroit_free
```
