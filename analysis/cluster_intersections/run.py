from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from intersections.cli import main

raise SystemExit(main(["cluster", *sys.argv[1:]]))
