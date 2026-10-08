# Mianhua and Huaping Islets Wildlife Refuge - Data Analysis

## About

This repository contains Python scripts, input datasets, and analytical outputs for the biodiversity survey data of the Mianhua and Huaping Islets Wildlife Refuge.

The workflow prepares occurrence inputs, calculates annual species counts and newly recorded species, and generates species accumulation curves.

## Repository structure

```text
tw_mhhp_refuge_data_analysis/
├── scripts/
│   ├── main.py
│   ├── 1_bdj_gbif_mhhp_input.py
│   └── 2_bdj_gbif_mhhp_SAC.py
├── mhhp_inputs/
│   ├── occurrence_whole.csv
│   ├── measurement_Fish.csv
│   ├── 0_taxon_till_20251231_ver1.37.csv
│   └── occur_*.csv
├── mhhp_outputs/
│   ├── species_counts_yearly1/
│   └── species_accumulation_curve1/
├── environment.yml
├── requirements.txt
├── LICENSE.txt
└── README.md
```

- `scripts/`: Python scripts for input preparation and analysis.
- `mhhp_inputs/`: Complete occurrence data, taxon and measurement tables, and occurrence files separated by taxonomic group.
- `mhhp_outputs/`: Generated figures and analytical tables.
- `environment.yml`: Conda configuration with pinned Python and direct package versions.
- `requirements.txt`: The same direct Python package versions for installation with pip.


## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Ceta-explorers/tw_mhhp_refuge_data_analysis.git
cd tw_mhhp_refuge_data_analysis
```

Run the following commands from the repository root directory.

### 2. Create and activate the Conda environment

Anaconda or Miniconda is required for this installation method.

```bash
conda env create -f environment.yml
conda activate env_refuge
```

Alternatively, install the Python dependencies into an existing Python 3.12.3 environment:

```bash
python -m pip install -r requirements.txt
```

Use either installation method.

### 3. Download and analyse a dataset

Download the selected IPT archive, prepare the input files, and run the analysis:

```bash
python scripts/main.py --ipt-version 1.37 --year-max 2025
```

### 4. Analyse existing input files

If the required files have already been prepared in `mhhp_inputs/`, run the analysis directly:

```bash
python scripts/2_bdj_gbif_mhhp_SAC.py --ipt-version 1.37 --year-max 2025
```

This command uses the existing input files without downloading or preparing them again. The IPT version must match the dataset used to prepare those files.

## Analysis parameters

- `--ipt-version`: Dataset version; defaults to `1.37`.
- `--year-max`: Final analysis year.
- The analysis start year is fixed at `1994`.
- The dataset's minimum known observation year must equal `1994`.
- The end year must be between `1994` and the dataset's maximum observation year.
- If `--year-max` is omitted, an interactive terminal prompts for an end year. Press Enter to use the dataset maximum.
- In noninteractive runs, an omitted end year uses the dataset maximum.
- The maximum observation year of version `1.37` is `2025`.

## Running in Spyder

Open `scripts/main.py`, then select **Run > Configuration per file** (`Ctrl+F6`).

Enable **Command line options** and enter:

```text
--ipt-version 1.37 --year-max 2025
```

Apply the configuration and run the file.

Supply an explicit end year when running `main.py` in Spyder to avoid waiting for an input prompt in a child process that may not be visible in the Spyder console.

## Outputs

Figures and analytical tables are saved in:

- `mhhp_outputs/species_counts_yearly1/`
- `mhhp_outputs/species_accumulation_curve1/`

Summary CSV filenames include the number of taxonomic groups represented in each table. The `sum` column in the survey-target table is excluded from this group count.

The species-ratio table uses `Metric` as its first-column label. Yearly tables use `Year`.

## Copyright and license

- **Copyright:** Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
- **License:** This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). See [LICENSE.txt](LICENSE.txt) for details.