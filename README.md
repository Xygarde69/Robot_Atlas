# Robot Models

This repository contains MuJoCo robot models organized by category.

## Visualize a robot

Install MuJoCo if needed:

```bash
python -m pip install mujoco
```

Pass the robot directory name to the visualization script. The script automatically loads the robot's `scene.xml` when available:

```bash
python visualize_model.py --robot kinova_gen3
python visualize_model.py --robot franka_emika_panda
```

To see all available model files:

```bash
python visualize_model.py --list
```

The older path-based form is still supported:

```bash
python visualize_model.py --model robotic_arms/kinova_gen3/scene.xml
```

Robot names correspond to the model directory names, such as `kinova_gen3`, `unitree_go1`, and `trossen_vx300s`.
