from __future__ import annotations

import argparse
from pathlib import Path

from generators.generate_01_northwind_starter import generate as generate_01
from generators.generate_blue_ridge import generate_clean as generate_02, generate_messy as generate_03
from generators.generate_04_carolina_home_services import generate as generate_04
from generators.generate_05_piedmont_logistics import generate as generate_05
from generators.generate_06_smart_campus import generate as generate_06
from generators.generate_07_coastal_communications import generate as generate_07


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all synthetic curriculum datasets.")
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="small")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    stages = [
        generate_01(root, args.scale),
        generate_02(root, args.scale),
        generate_03(root, args.scale),
        generate_04(root, args.scale),
        generate_05(root, args.scale),
        generate_06(root, args.scale),
        generate_07(root, args.scale),
    ]
    print("Generated stages:")
    for stage in stages:
        print(f"  - {stage}")


if __name__ == "__main__":
    main()
