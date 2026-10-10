#!/usr/bin/env python3
"""Open a MuJoCo XML/URDF model in the interactive viewer.

Examples:
    python visualize_model.py --robot kinova_gen3
    python visualize_model.py --robot franka_emika_panda
    python visualize_model.py --list
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL_SUFFIXES = {".xml", ".urdf"}


def model_files() -> list[Path]:
    """Return candidate model files, excluding common generated/cache files."""
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in MODEL_SUFFIXES
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and "assets" not in path.parts
    )


def robot_directories() -> dict[str, list[str]]:
    """Return robot directory names grouped by their repository category."""
    categories: dict[str, set[str]] = {}
    for path in model_files():
        robot_dir = path.parent
        category = str(robot_dir.relative_to(ROOT).parent)
        categories.setdefault(category, set()).add(robot_dir.name)
    return {category: sorted(names) for category, names in sorted(categories.items())}


def find_model(value: str) -> Path:
    """Resolve a robot name, path, filename, or unique filename stem."""
    requested = Path(value).expanduser()
    candidates: list[Path] = []

    for path in (requested, ROOT / requested):
        if path.is_file():
            return path.resolve()

    # Robot names are directory names in the repository. Prefer scene.xml,
    # since it usually includes the robot plus its floor, lighting, and camera.
    robot_dirs = sorted(
        path
        for path in ROOT.rglob(value)
        if path.is_dir() and path.name == value and ".git" not in path.parts
    )
    if len(robot_dirs) == 1:
        scene = robot_dirs[0] / "scene.xml"
        if scene.is_file():
            return scene.resolve()
        robot_models = [
            path
            for path in robot_dirs[0].iterdir()
            if path.is_file() and path.suffix.lower() in MODEL_SUFFIXES
        ]
        if len(robot_models) == 1:
            return robot_models[0].resolve()
        if not robot_models:
            raise FileNotFoundError(
                f"Robot {value!r} has no XML or URDF model at {robot_dirs[0]}"
            )
        raise RuntimeError(
            f"Robot {value!r} has multiple model files; add a scene.xml or use --model."
        )
    if len(robot_dirs) > 1:
        matches = "\n  ".join(str(path.relative_to(ROOT)) for path in robot_dirs)
        raise RuntimeError(f"Robot name {value!r} is ambiguous. Choose one of:\n  {matches}")

    for path in model_files():
        if path.name == value or path.stem == value:
            candidates.append(path)

    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"No model matching {value!r} was found.")

    matches = "\n  ".join(str(path.relative_to(ROOT)) for path in candidates)
    raise RuntimeError(f"{value!r} is ambiguous. Choose one of:\n  {matches}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--robot",
        "--model",
        dest="model",
        help="robot directory name (for example kinova_gen3), or an XML/URDF path",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list repository model files and exit",
    )
    args = parser.parse_args()
    if not args.list and not args.model:
        parser.error("--robot is required unless --list is used")
    return args


def main() -> None:
    args = parse_args()

    if args.list:
        print("Available robots (copy and paste a command):")
        for category, robot_names in robot_directories().items():
            print(f"\n[{category}]")
            for name in robot_names:
                print(f"  python visualize_model.py --robot {name}")
        return

    model_path = find_model(args.model)

    try:
        import mujoco
        from mujoco import viewer
    except ImportError as exc:
        raise SystemExit(
            "MuJoCo is not installed. Install it with: python -m pip install mujoco"
        ) from exc

    print(f"Loading {model_path.relative_to(ROOT)}")
    model = mujoco.MjModel.from_xml_path(str(model_path))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    viewer.launch(model, data)


if __name__ == "__main__":
    main()
