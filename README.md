# \# tw\_mhhp\_refuge\_data\_analysis

## 

## Repository

* `scripts/`: Contains the Python scripts for data processing.
* `mhhp_inputs/`: Contains the GBIF occurrence dataset used for this analysis.
* `mhhp_outputs/`: Contains the generated figures (e.g., species accumulation curves) used in the manuscript.
* `requirements.txt`: List of Python dependencies required to run the scripts.

## Repository Structure

```text
.
├── scripts/              <- Directory containing Python scripts
│   └── (e.g., bdj_gbif_mhhp_data_2026.py)
│
├── mhhp_inputs/          <- Directory containing the GBIF occurrence dataset
│   └── (e.g., 2_Avian_2025_20260408.csv)
│
├── mhhp_outputs/sac         <- Directory containing the generated figures for the manuscript
│   ├── (e.g., mhhp_yearly_species_accumulation_curve_Avian.png)
│   └── (e.g., mhhp_yearly_species_accumulation_curve_Avian.csv)
│
├── LICENSE.txt           <- License for the code and data (e.g., CC BY 4.0)
├── README.md             <- The top-level README for reviewers and developers
└── requirements.txt      <- Python dependencies required to reproduce the analysis

```

## Create an environment and activate it
run `conda env create -f environment.yml` in Conda Shell
run `activate env_refuge`
run `python ./scripts/bdj_gbif_mhhp_data_2026.py`

## Copyright and License

* **Copyright:** Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
* **License:** This project is licensed under the **Creative Commons Attribution 4.0 International License** (CC BY 4.0). See the [LICENSE](LICENSE) file for details.

