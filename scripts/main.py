"""Download survey inputs and analyse species accumulation from 1994.

Paths are resolved from this file so invocation from the repository root,
the scripts directory, or another directory uses the same child scripts.
Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.
"""

import argparse
from pathlib import Path
import subprocess
import sys


def main(IPT_version="1.37", year_max=None):
    """Prepare complete inputs, then analyse them from 1994 through year_max.

    An omitted end year is resolved by the analysis script after the dataset
    range is available. In a terminal, users can enter it or press Enter to
    use the dataset maximum. Both child scripts use the active interpreter;
    a child failure stops the workflow before the next step.
    """
    year_min = 1994
    if year_max is not None and year_min > year_max:
        raise ValueError("year_max must be greater than or equal to year_min (1994)")


    script_folder = Path(__file__).resolve().parent
    for file_name in [
        "1_bdj_gbif_mhhp_input.py",
        "2_bdj_gbif_mhhp_SAC.py",
    ]:
        if not (script_folder / file_name).is_file():
            raise FileNotFoundError(
                f"Required script not found: {script_folder / file_name}"
            )

    print(f"Running Data Extraction (IPT version {IPT_version})...", flush=True)
    subprocess.run(
        [
            sys.executable,
            str(script_folder / "1_bdj_gbif_mhhp_input.py"),
            "--ipt-version",
            str(IPT_version),
        ],
        cwd=script_folder,
        check=True,
    )

    command = [
        sys.executable,
        str(script_folder / "2_bdj_gbif_mhhp_SAC.py"),
        "--ipt-version",
        str(IPT_version),
    ]
    if year_max is not None:
        command.extend(["--year-max", str(year_max)])
    print(f"Running Species Accumulation Curve (SAC) from year 1994 to {year_max} ...", flush=True)
    subprocess.run(command, cwd=script_folder, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ipt-version", default="1.37", help="TaiBIF IPT archive version."
    )
    parser.add_argument(
        "--year-max",
        type=int,
        default=None,
        help=(
            "Last analysis year, starting from 1994. If omitted, prompt in a "
            "terminal or use the dataset maximum in noninteractive runs."
        ),
    )
    args = parser.parse_args()
    
    main(IPT_version=args.ipt_version, year_max=args.year_max)
    #main(IPT_version=args.ipt_version)








