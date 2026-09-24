# \# Mianhua and Huaping Islets Wildlife Refuge - Data Analysis

## About
This repository contains the Python scripts, input datasets, and output figures for analyzing the biodiversity survey data of the **Mianhua and Huaping Islets Wildlife Refuge**. The analysis utilizes GBIF occurrence datasets to generate species accumulation curves, perform ecological modeling, and calculate annual species counts across various taxonomic groups.


## Repository 

* `scripts/`: Contains the Python scripts for data processing.
* `mhhp_inputs/`: Contains the GBIF occurrence dataset used for this analysis.
* `mhhp_outputs/`: Contains the generated figures (e.g., species accumulation curves) used in the manuscript.
* `environment.yml`: List of dependencies required to run the scripts,including Python and R packages.
* `requirements.txt`: List of Python dependencies required to run the scripts.

## Repository Structure

```text
tw_mhhp_refuge_data_analysis/
|
├── scripts/              <- Directory containing Python scripts
│   └── (e.g., main.py)
│
├── mhhp_inputs/          <- Directory containing the GBIF occurrence dataset
│   └── (e.g., 2_Avian_2025_20260408.csv)
│
├── mhhp_outputs/   <- Directory containing the generated figures and tables
|          ├──species_counts_yearly
|          └──species_accumulation_curve
│                   ├── (e.g., mhhp_yearly_species_accumulation_curve_Avian.png)
│                   └── (e.g., mhhp_yearly_species_accumulation_curve_Avian.csv)
│
├── environment.yml       <- Conda environment configuration (Python & R packages)
|── requirements.txt      <- Python dependencies required to reproduce the analysis
|── install.R             <- R dependencies required to reproduce the analysis
├── LICENSE.txt           <- License for the code and data (e.g., CC BY 4.0)
└── README.md             <- The top-level README for reviewers and developers


```

## Getting started
### Prerequisites
Ensure you have Anaconda or Miniconda installed.

### 1. Clone the repository <br> 
`git clone https://github.com/Ceta-explorers/tw_mhhp_refuge_data_analysis.git`

### 2. Create and activate the environment in Conda Shell <br> 
This project relies on both Python and R packages (via rpy2). You can set up the exact environment using the provided environment.yml<br>
`conda env create -f environment.yml`<br> `conda activate env_refuge`

### 3. Run the analysis in the activated environment<br>
`python ./scripts/main.py` <br>
All generated figures and analytical tables will be automatically saved in the mhhp_outputs/ directory.


## <sup>©</sup> Copyright and License

* **Copyright:** Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
* **License:** This project is licensed under the **Creative Commons Attribution 4.0 International License** (CC BY 4.0). See the [LICENSE](LICENSE) file for details.

