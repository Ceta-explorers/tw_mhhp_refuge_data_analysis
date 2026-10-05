"""Run the v1.36 download and analysis scripts in their original order.

Paths are resolved from this file so invocation from the repository root,
the scripts directory, or another directory uses the same child scripts.
Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.
"""

from pathlib import Path
import subprocess
import sys


def main():
    """Use the active Python interpreter and stop if either child fails."""
    script_folder = Path(__file__).resolve().parent

    print("Running Data Extraction...", flush=True)
    subprocess.run(
        [sys.executable, str(script_folder / "1_bdj_gbif_mhhp_input_20261005.py")],
        cwd=script_folder,
        check=True,
    )

    print("Running Species Accumulation Curve (SAC)...", flush=True)
    subprocess.run(
        [sys.executable, str(script_folder / "2_bdj_gbif_mhhp_SAC_20261005.py")],
        cwd=script_folder,
        check=True,
    )


if __name__ == "__main__":
    main()


