from __future__ import annotations

import argparse
from pathlib import Path

from generators.generate_01_northwind_starter import generate as generate_01
from generators.generate_blue_ridge import generate_clean as generate_02, generate_messy as generate_03
from generators.generate_04_carolina_home_services import generate as generate_04
from generators.generate_05_piedmont_logistics import generate as generate_05
from generators.generate_06_smart_campus import generate as generate_06
from generators.generate_07_coastal_communications import generate as generate_07

GENERATORS = {
    "01": generate_01,
    "02": generate_02,
    "03": generate_03,
    "04": generate_04,
    "05": generate_05,
    "06": generate_06,
    "07": generate_07,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one curriculum dataset stage.")
    parser.add_argument("stage", choices=GENERATORS.keys())
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="small")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    path = GENERATORS[args.stage](Path(args.root).resolve(), args.scale)
    print(path)


if __name__ == "__main__":
    main()
