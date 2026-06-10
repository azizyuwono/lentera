#!/usr/bin/env python3
"""Alpha Radar — Automated Market Intelligence Pipeline"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.report_generator import ReportGenerator

def main() -> None:
    """Execute the full Alpha Radar pipeline."""
    print("=" * 50)
    print("  ALPHA RADAR — Pipeline v1.0")
    print("=" * 50)

    signals = ReportGenerator.run_full_pipeline()
    readme = ReportGenerator.generate_readme(signals)

    # Output to the root README.md, not src/README.md
    readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
    with open(readme_path, "w") as f:
        f.write(readme)

    print("=" * 50)
    print(f"  Assets tracked: {len(signals)}")
    print(f"  README synced : {readme_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
