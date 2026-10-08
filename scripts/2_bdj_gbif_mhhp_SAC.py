# -*- coding: utf-8 -*-
"""The Survey Data of Mianhua and Huaping Islets Wildlife Refuge.

Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.

@author: Jui-Wen Chang (Ceta explorers Co., Ltd)

Validate survey inputs, calculate annual species statistics, and export tables
and species accumulation figures.
"""

# Standard library.
import argparse
import os
import re
import sys

print(sys.stdin.isatty())


# Third-party packages.
import chardet
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


# %% 1. Configure fonts and resolve input/output paths.
def setup_paths():
    """Return repository paths and create the output folders.

    Figures use Times New Roman with a sans-serif fallback.
    """
    matplotlib.rcParams["font.family"] = ["Times New Roman", "sans-serif"]

    # Resolve paths from this script; interactive sessions use their current folder.
    try:
        script_dir = os.path.abspath(__file__)
        script_folder = os.path.abspath(os.path.join(script_dir, ".."))
    except NameError:  # Interactive sessions without __file__.
        script_folder = os.getcwd()

    root_path = os.path.abspath(os.path.join(script_folder, ".."))
    print(f"root_path is `{root_path}`")

    input_path = os.path.join(root_path, "mhhp_inputs/")
    output_path = os.path.join(root_path, "mhhp_outputs/")

    output_path_counts = os.path.join(output_path, "species_counts_yearly1/")
    output_path_sac = os.path.join(output_path, "species_accumulation_curve1/")

    for folder in [output_path, output_path_counts, output_path_sac]:
        os.makedirs(folder, exist_ok=True)

    return root_path, input_path, output_path, output_path_counts, output_path_sac


# %% 2. Resolve the analysis end year and validate the complete input tables.

def resolve_analysis_year_max(
    df0_whole, IPT_version="1.37", year_max=None, interactive=False
):
    """Show source coverage and select an end year with a fixed 1994 start.

    Blank interactive input and omitted noninteractive input use the dataset
    maximum. The dataset minimum must equal 1994 before analysis can proceed.
    """
    
    
    year_min = 1994
    if "year" not in df0_whole.columns:
        raise ValueError("occurrence_whole.csv requires a year column.")
    try:
        df0_whole = df0_whole[["year"]].astype({"year": "Int64"})
    except (TypeError, ValueError) as error:
        raise ValueError(
            "occurrence_whole.csv: year must contain integers or missing values."
        ) from error
    
    # At least one occurrence record with year value.
    if df0_whole["year"].dropna().empty:
        raise ValueError("The dataset has no known observation years.")


    dataset_year_min = int(df0_whole["year"].min())
    dataset_year_max = int(df0_whole["year"].max())
    print(f"IPT version: {IPT_version}")
    print(f"Dataset year range: {dataset_year_min}\u2013{dataset_year_max}")
    print(f"Start year: {year_min}")
    
    # Count the occurrence records without year value and exclude them in statistics.
    if df0_whole["year"].isna().any():
        print(
            f"Records with missing years: {df0_whole['year'].isna().sum()}; "
            "annual statistics exclude these records."
        )
        
    # Check df0_whole["year"].min() == 1994     
    if dataset_year_min != year_min:
        raise ValueError(
            f"The dataset minimum year is {dataset_year_min}; "
            f"this analysis requires a minimum year of {year_min}."
        )
        
    '''
    # Interactive mode is determined by whether standard input is connected to a terminal.
      If no end year is supplied, interactive mode prompts for a valid year 
      and retries invalid input in a loop. Press Enter to use the dataset's maximum year.
      
    # Noninteractive mode uses the dataset's maximum year without prompting.
      An explicitly supplied invalid end year raises an error without prompting.
    '''
    
    
    # User set the End year by himself/herself if (interactive==True &  year_max is None)
    if year_max is None and interactive:
        while True:
            try:
                year_max_input = input(f"End year in Common Era [defult=={dataset_year_max}]: ").strip()
            # End-of-File Error
            except EOFError:
                year_max_input = ""
                
            try:
                year_max = int(year_max_input) if year_max_input else dataset_year_max
            except ValueError:
                print("Enter an integer year or press Enter to use the default.")
                continue
            
            if year_min <= year_max <= dataset_year_max:
                break
            else:
                print(f"End year must be between {year_min} and {dataset_year_max}.")
    
    # Use the default End year by himself/herself if (interactive==False &  year_max is None)
    elif year_max is None:
        year_max = dataset_year_max
        
    # if (year_max is not None)
    if (not isinstance(year_max, (int, np.integer))) or isinstance(year_max, bool):
        raise ValueError("year_max must be an integer.")
    if not year_min <= year_max <= dataset_year_max:
        raise ValueError(
            f"year_max must be between {year_min} and {dataset_year_max}; "
            f"received {year_max}."
        )
    
    print(f"End year: {year_max}")
    return int(year_max)


def check_data_integrity(input_path, IPT_version="1.37", year_max=None):
    """Validate the selected input files and return their names and occurrences.

    Exactly one dated taxon table must match IPT_version. The explicit file list
    excludes occurrence_whole.csv and unrelated CSV files. 
    Occurrence IDs must be nonblank and unique within and across group files. 
    All records are checked before the analysis end year is applied. 
    The taxon snapshot must use the maximum year of occurrence_whole.csv, rather than the selected analysis year.
    Multiple taxon-table rows for one taxonID are reported for inspection.
    """
    year_min=1994
    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"Input folder does not exist: {input_path}")
    df0_whole = pd.read_csv(
        os.path.join(input_path, "occurrence_whole.csv"),
        encoding="utf-8-sig",
        usecols=["year"],
        dtype={"year": "Int64"},
    )
    
    # At least one occurrence record with year value.
    if df0_whole["year"].dropna().empty:
        raise ValueError("The dataset has no known observation years.")
    dataset_year_min = int(df0_whole["year"].min())
    dataset_year_max = int(df0_whole["year"].max())
    
    if dataset_year_min != year_min:
        raise ValueError("The dataset and analysis minimum year must both equal 1994.")
    if year_max is None:
        year_max = dataset_year_max
    if not year_min <= year_max <= dataset_year_max:
        raise ValueError(f"year_max must be between {year_min} and {dataset_year_max}.")

    # Select the taxon snapshot by IPT version rather than by the plotting range.
    content_taxon = sorted(
        file_name
        for file_name in os.listdir(input_path)
        if re.fullmatch(
            rf"0_taxon_till_\d{{8}}_ver{re.escape(str(IPT_version))}\.csv", file_name
        )
        and os.path.isfile(os.path.join(input_path, file_name))
    )
    
    
    if len(content_taxon) != 1:
        raise ValueError(
            f"Expected exactly one taxon table for IPT version {IPT_version}; "
            f"found {len(content_taxon)}: {content_taxon}. Keep one matching snapshot in mhhp_inputs before running the analysis."
        )
    if content_taxon[0] != f"0_taxon_till_{dataset_year_max}1231_ver{IPT_version}.csv":
        raise ValueError(
            f"{content_taxon[0]}: the taxon snapshot date must use dataset maximum "
            f"year {dataset_year_max}. Recreate the inputs for this IPT version."
        )
    content = [
        content_taxon[0],
        "measurement_Fish.csv",
        "occur_Algae.csv",
        "occur_Avian.csv",
        "occur_BenthicInvertebrate.csv",
        "occur_Cetacean.csv",
        "occur_Fish.csv",
        "occur_Insect.csv",
        "occur_Plant.csv",
        "occur_Reptile.csv",
        "occur_Spider.csv",
    ]
    
    for file_name in content:
        if not os.path.isfile(os.path.join(input_path, file_name)):
            raise FileNotFoundError(f"Required input file is missing: {file_name}")

    data_combined_occur = pd.DataFrame([])
    
    for file_id in range(len(content)):
        with open(os.path.join(input_path, content[file_id]), "rb") as f:
            result = chardet.detect(f.read(10000))
            print(f"{content[file_id]}: {result['encoding']}")
            if result["encoding"] == "Big5":
                encoding_name = "cp950"
            elif result["encoding"] in ["Windows-1252", "Windows-1254"]:
                encoding_name = result["encoding"].replace("Windows-", "cp")
            elif result["encoding"] == "UTF-8-SIG":
                encoding_name = "UTF-8-SIG"
            else:
                encoding_name = "utf-8"
        # Read taxon table
        if file_id == 0:
            data_taxon = pd.read_csv(
                os.path.join(input_path, content[file_id]),
                encoding=encoding_name,
                dtype={"taxonID": "string"},
            )
            if "taxonID" not in data_taxon.columns:
                raise ValueError(
                    f"{content[file_id]}: required column taxonID is missing."
                )
                
            # Check taxonID is na or blank string ("")    
            data_taxon["taxonID"] = data_taxon["taxonID"].str.strip()
            
            if (
                data_taxon["taxonID"].isna().any()
                or data_taxon["taxonID"].astype(str).str.strip().eq("").any()
            ):
                raise ValueError(f"{content[file_id]}: taxonID must not be blank.")
                
            # Check taxonID is na or blank string ("")   
            data_taxon = data_taxon.sort_values(by=["taxonID"])
            
            data_taxon_taxonID = data_taxon.value_counts("taxonID", sort=True)
            data_taxon_taxonID = data_taxon_taxonID.reset_index().sort_values(by=["count"])
            
            if len(data_taxon_taxonID) == len(data_taxon):
                print(f"{content[file_id]}: taxonID is unique.")
            else:
                multiple_taxonID = data_taxon_taxonID.loc[
                    data_taxon_taxonID["count"] > 1, "taxonID"
                ].values
                
                data_taxon_multi_taxonID = data_taxon[
                    data_taxon["taxonID"].isin(multiple_taxonID)
                ].sort_values(by="taxonID", ascending=True)
                print(
                    f"{content[file_id]}: repeated taxonID values require inspection:\n"
                    f"{data_taxon_multi_taxonID}"
                )
        # Read other grouped tables, except taxon table.        
        else:
            data1_check = pd.read_csv(
                os.path.join(input_path, content[file_id]),
                encoding=encoding_name,
                dtype={"occurrenceID": "string", "taxonID": "string"},
            )
            # Read measurement table     
            if content[file_id] == "measurement_Fish.csv":
                if not {"occurrenceID", "measurementType"}.issubset(data1_check.columns):
                    raise ValueError(
                        "measurement_Fish.csv requires occurrenceID and measurementType."
                    )
                continue
            
            # Read taxonomic-grouped occurrence table        
            if not {
                "occurrenceID",
                "taxonID",
                "scientificName",
                "taxonRank",
                "year",
                "month",
                "eventDate",
            }.issubset(data1_check.columns):
                raise ValueError(
                    f"{content[file_id]}: required occurrence columns are missing; "
                    "expected occurrenceID, taxonID, scientificName, taxonRank, "
                    "year, month, and eventDate."
                )
            # Exclude measurement tables 
            if "measurementType" in data1_check.columns:
                raise ValueError(f"{content[file_id]} is not an occurrence-only table.")
                
            # Create group name   
            data1_check["occurrenceID"] = data1_check["occurrenceID"].str.strip()
            data1_check["taxonID"] = data1_check["taxonID"].str.strip()
            taxon_group_name = content[file_id][len("occur_") : -4]
            
            # The substring of `taxonID` in all the records needs to contains {taxon_group_name}
            if (
                not data1_check["taxonID"]
                .str.contains(taxon_group_name, na=False)
                .all()
            ):
                raise ValueError(
                    f"{content[file_id]}: taxonID values do not belong to "
                    f"the expected {taxon_group_name} group."
                )
            # Check for isna and blank in `occurrenceID`
            if (
                data1_check["occurrenceID"].isna().any()
                or data1_check["occurrenceID"].astype(str).str.strip().eq("").any()
            ):
                raise ValueError(f"{content[file_id]}: occurrenceID must not be blank.")
                
            # Check for uniqueness in `occurrenceID`
            data_occurrenceID = data1_check.value_counts("occurrenceID", sort=True)
            if len(data_occurrenceID) != len(data1_check):
                raise ValueError(
                    f"{content[file_id]}: occurrenceID values must be unique."
                ) 
            # Check for isna and blank in `taxonID`  
            if (
                data1_check["taxonID"].isna().any()
                or data1_check["taxonID"].astype(str).str.strip().eq("").any()
            ):
                raise ValueError(f"{content[file_id]}: taxonID must not be blank.")
                
            # Check for year type 
            try:
                data1_check["year"] = data1_check["year"].astype("Int64")
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{content[file_id]}: year must contain integers or missing values."
                ) from error
            
            # Check for year range 
            if (
                data1_check["year"].notna()
                & ~data1_check["year"].between(year_min, dataset_year_max)
            ).any():
                raise ValueError(
                    f"{content[file_id]}: observed years fall outside "
                    f"the complete dataset range {year_min}-{dataset_year_max}. "
                    "Recreate the inputs for this IPT version."
                )
            
            
            data1_check["taxonRank"] = (
                data1_check["taxonRank"]
                .astype("string")
                .str.strip()
                .str.lower()
                .replace("varietas", "variety")
            )
            filter_species = data1_check["taxonRank"].isin(
                ["species", "subspecies", "variety"]
            )
            
            # Check for any "scientificName" in species and infraspecific level, which length is less than two .
            
            if (
                filter_species
                & data1_check["scientificName"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.split()
                .str.len()
                .lt(2)
            ).any():
                raise ValueError(
                    f"{content[file_id]}: species-level scientificName values "
                    "must contain at least a genus and a specific epithet."
                )
                
            data_combined_occur = pd.concat(
                [data_combined_occur, data1_check], ignore_index=True
            )
            print(f"{content[file_id]}: occurrenceID is unique.")

    if data_combined_occur["occurrenceID"].duplicated().any():
        raise ValueError(
            "occurrenceID values are duplicated across occurrence group files."
        )

    # Preserve year-only dates as YYYY-00-00 for sorting without inventing a day.
    data_combined_occur["eventDate"] = data_combined_occur["eventDate"].astype("str")
    filter_only_year = data_combined_occur["eventDate"].str.len() == 4
    data_combined_occur["verbatimEventDate"] = data_combined_occur["eventDate"]
    data_combined_occur.loc[filter_only_year, "verbatimEventDate"] = (
        data_combined_occur.loc[filter_only_year, "verbatimEventDate"] + "-00-00"
    )
    data_combined_occur["verbatimEventDate"] = data_combined_occur[
        "verbatimEventDate"
    ].str.replace("/", "-")

    data_combined_occur_taxonID = data_combined_occur.value_counts("taxonID", sort=True)
    data_combined_occur_taxonID = data_combined_occur_taxonID.reset_index().sort_values(
        by=["taxonID"]
    )
    
    # Compare the taxonID between occur table and taxon table
    count_taxonID_occur = set(data_combined_occur_taxonID["taxonID"].values)
    count_taxonID_taxon = set(data_taxon_taxonID["taxonID"].values)
    
    if count_taxonID_occur == count_taxonID_taxon:
        print("The occurrence and taxon tables contain the same taxonID set.")
    else:
        print("The occurrence and taxon tables contain different taxonID sets.")
        print(
            f"Occurrence taxonIDs absent from the taxon table: {count_taxonID_occur - count_taxonID_taxon}"
        )
        print(
            f"Taxon-table IDs absent from occurrences: {count_taxonID_taxon - count_taxonID_occur}"
        )
        raise ValueError(
            "Taxon and occurrence taxonID sets differ. Recreate the inputs "
            f"for IPT version {IPT_version} before analysing them."
        )
    print(f"Taxonomic ranks: {data_combined_occur['taxonRank'].unique()}")
    return content, data_combined_occur


# %% 3. Prepare each group, calculate annual statistics, and export its SAC.

def calculate_group_statistics(
    input_path, output_path_sac, content, data_combined_occur, year_min, year_max
):
    """Return seven summary tables for the eight analysed occurrence groups.

    Species statistics collapse names to their first two words and retain
    species, subspecies, and variety ranks. Spider records are included.
    
    Known years are restricted to 1994 through year_max. Undated records remain
    in species ratios but do not contribute to annual statistics.
    
    Occurrence counts include all ranks. 
    Individual SAC CSVs contain observed species years; full-year raw tables retain NaN for missing observations.
    
    The returned tables are the species ratio, annual richness, cumulative
    richness, new-species increments, occurrence counts, and two survey indicators.
    """
    
    if year_min != 1994 or year_min > year_max:
        raise ValueError("year_min must equal 1994 and must not exceed year_max.")
    data_annual_species_counts = pd.DataFrame(
        [], index=list(range(year_min, int(year_max + 1), 1))
    )
    data_annual_occur_counts = pd.DataFrame(
        [], index=list(range(year_min, int(year_max + 1), 1))
    )
    data_species_ratio = pd.DataFrame([], index=["species_lower", "taxon_all", "ratio"])

    data_annual_species_cumulative0 = pd.DataFrame(
        [], index=list(range(year_min, int(year_max + 1), 1))
    )

    data_annual_species_increment0 = pd.DataFrame(
        [], index=list(range(year_min, int(year_max + 1), 1))
    )

    # File 0 is the selected taxon table; subsequent files have explicit roles.
    for file_id in range(1, len(content)):
        file_name = content[file_id]
        taxon_group_name = file_name[:-4].split("_")[1]

        # Detect encoding from the complete input file.
        with open(os.path.join(input_path, content[file_id]), "rb") as f:
            result = chardet.detect(f.read())
            print(f"{file_name} : {result['encoding']}")

            if result["encoding"] == "Big5":
                encoding_name = "cp950"
            elif result["encoding"] == "Windows-1252":
                encoding_name = "cp1252"
            elif result["encoding"] == "Windows-1254":
                encoding_name = "cp1254"
            elif result["encoding"] == "UTF-8-SIG":
                encoding_name = "UTF-8-SIG"
            else:
                encoding_name = "utf-8"

        data0 = pd.read_csv(
            os.path.join(input_path, content[file_id]),
            encoding=encoding_name,
            dtype={"occurrenceID": "string", "taxonID": "string"},
        )
        
        # Choose taxonomic-grouped occurrence file and include Spider group (n=1).
        if (
            ("occurrenceID" in list(data0.columns))
            and ("measurementType" not in list(data0.columns))
            #and (not bool(re.search("Spider", content[file_id])))
        ):

            data0["occurrenceID"] = data0["occurrenceID"].str.strip()
            data0["taxonID"] = data0["taxonID"].str.strip()
            
            if (
                not data0["occurrenceID"]
                .isin(data_combined_occur["occurrenceID"])
                .all()
            ):
                raise ValueError(
                    f"{file_name}: occurrence IDs differ from the validated inputs."
                )
                
            data0["year"] = data0["year"].astype("Int64")
            data0["month"] = data0["month"].astype("Int64")
            
            # Keep complete input files; apply the cutoff(year_max) only to analysed records.
            data0 = data0.loc[
                data0["year"].isna() | data0["year"].between(year_min, year_max)
            ].copy()
            data0.sort_values(["year"], ascending=True, ignore_index=True, inplace=True)

            # Sort dates while retaining year-only observations.
            data0["eventDate"] = data0["eventDate"].astype("str")
            filter_only_year = data0["eventDate"].str.len() == 4
            data0["verbatimEventDate"] = data0["eventDate"]
            data0.loc[filter_only_year, "verbatimEventDate"] = (
                data0.loc[filter_only_year, "verbatimEventDate"] + "-00-00"
            )
            data0.sort_values(
                ["verbatimEventDate"], ascending=True, ignore_index=True, inplace=True
            )

            # Count all group occurrences per year using data0, not data1.
            data_annual_occur_counts[taxon_group_name] = np.nan
            
            
            data_yearly_groupOccur_counts = (
                data0.groupby("year")["occurrenceID"]
                .size()
                .to_frame(name=f"{taxon_group_name}")
            )

            # 2.9. Align the observed-year counts to the full-year occurrence table.
            data_annual_occur_counts.loc[
                data_yearly_groupOccur_counts.index, f"{taxon_group_name}"
            ] = data_yearly_groupOccur_counts.loc[
                data_yearly_groupOccur_counts.index, f"{taxon_group_name}"
            ].values


                

            # 3.0. Derive species names and retain species/subspecies/variety.
            # Higher ranks are excluded from species statistics.
            data0["name_split"] = (
                data0["scientificName"].astype("string").str.strip().str.split()
            )

            data0["name_split_2words"] = data0["name_split"].apply(
                lambda x: x[:2] if (isinstance(x, list) and len(x) >= 2) else x
            )

            # Collapse each scientific name to its genus and specific epithet.
            data0["name_species"] = data0["name_split_2words"].str.join(" ")

            # Normalize rank spelling before selecting species and lower ranks.
            data0["taxonRank"] = (
                data0["taxonRank"].astype("string").str.strip().str.lower()
            )

            data0["taxonRank"] = data0["taxonRank"].replace("varietas", "variety")

            filter_species = (
                (data0["taxonRank"] == "species")
                | (data0["taxonRank"] == "subspecies")
                | (data0["taxonRank"] == "variety")
            )

            
            
            # Check for any "scientificName" in species and infraspecific level, which length is less than two.
            # Reject species and infraspecific records whose scientificName has fewer than two words.
            if (
                filter_species
                & data0["scientificName"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.split()
                .str.len()
                .lt(2)
            ).any():  
                raise ValueError(
                    f"{file_name}: species-level scientificName values must contain "
                    "at least a genus and a specific epithet."
                )
            

            # Compare ratio of (retained species-name counts) with (names at all ranks).
            data_species_ratio[taxon_group_name] = [
                data0.loc[filter_species, "name_species"].nunique(),
                data0.loc[:, "name_species"].nunique(),
                (
                    np.round(
                        data0.loc[filter_species, "name_species"].nunique()
                        / data0["name_species"].nunique(),
                        2,
                    )
                    if data0["name_species"].nunique()
                    else np.nan
                ),
            ]

            # Check for at least one "scientificName", which length is >=2 in species and infraspecific level.
            # Check for at least one "name_species" in data0 dataset.
            
            data1 = data0[filter_species].copy()
            if len(data1)<1:
                
                for extension in ("png", "csv"):
                    # Remove previous individual grouped sac figure
                    file_grouped_sac = (
                        f"mhhp_yearly_species_accumulation_curve_"
                        f"{taxon_group_name}.{extension}"
                    )
                    dir_grouped_sac = os.path.join(output_path_sac, file_grouped_sac)
                
                    if os.path.isfile(dir_grouped_sac):
                        os.remove(dir_grouped_sac)
                
                print(f"Skip {taxon_group_name} species analysis because no species or infraspecific record has a scientificName with at least two words.")
                continue
            
            
            # Every analysed group retains a column even when its table is empty.
            data_annual_species_counts[taxon_group_name] = np.nan
            data_annual_species_cumulative0[taxon_group_name] = np.nan
            data_annual_species_increment0[taxon_group_name] = np.nan

            
            # 3.1. Count species observed within each year (not newly recorded species).
            data_taxon_yearly = (
                data1.groupby(["year"])["name_species"].nunique(dropna=True).to_frame()
            )

            # Put into whole-group dataframe
            data_annual_species_counts.loc[
                list(data_taxon_yearly.index), [f"{taxon_group_name}"]
            ] = data_taxon_yearly.loc[list(data_taxon_yearly.index)].values



            # 3.2. Calculate cumulative species for years with retained records.
            taxon_unique_years = np.sort(data1["year"].dropna().unique())
            taxon_cumulative = (
                data1[["name_species", "year"]].dropna().drop_duplicates()
            )

            dict_yearly_groupSpecies_cumulative0 = {y: 0 for y in taxon_unique_years}

            dict_yearly_groupSpecies_count = {}  # Number of species in one year

            for beforeyear in taxon_unique_years:
                dict_yearly_groupSpecies_cumulative0[beforeyear] = taxon_cumulative.loc[
                    taxon_cumulative["year"] <= beforeyear, "name_species"
                ].nunique()  # number of species before "beforeyear"

                dict_yearly_groupSpecies_count[beforeyear] = taxon_cumulative.loc[
                    taxon_cumulative["year"] == beforeyear, "name_species"
                ].nunique()  # number of species in one year


            # 3.3. New species equal the increase since the previous observed year.

            dict_yearly_groupSpecies_increment0 = {}

            for index_year, value_year in enumerate(taxon_unique_years):
                if index_year == 0:
                    dict_yearly_groupSpecies_increment0[value_year] = (
                        dict_yearly_groupSpecies_cumulative0[value_year]
                    )
                elif index_year != 0:
                    year_previous = taxon_unique_years[index_year - 1]
                    dict_yearly_groupSpecies_increment0[value_year] = (
                        dict_yearly_groupSpecies_cumulative0[value_year]
                        - dict_yearly_groupSpecies_cumulative0[year_previous]
                    )

            data_yearly_groupSpecies_cum = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_cumulative0,
                orient="index",
                columns=[f"{taxon_group_name}"],
            )

            data_yearly_groupSpecies_incr = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_increment0,
                orient="index",
                columns=[f"{taxon_group_name}"],
            )


            # Save only one group of SAC
            data_yearly_groupSpecies_cum.to_csv(
                output_path_sac
                + f"mhhp_yearly_species_accumulation_curve_{taxon_group_name}.csv",
                sep=",",
                index=True,
                index_label="Year",
                encoding="utf_8",
            )

            data_yearly_groupSpecies_cum.index = (
                data_yearly_groupSpecies_cum.index.astype("str")
            )


            # 3.4. Align observed-year values to the configured full-year index.
            # Leave years without values as NaN in the exported raw tables.
            
            data_annual_species_cumulative0[f"{taxon_group_name}"] = (
                pd.DataFrame.from_dict(
                    dict_yearly_groupSpecies_cumulative0,
                    orient="index",
                    columns=[f"{taxon_group_name}"],
                )
            )
            data_annual_species_increment0[f"{taxon_group_name}"] = (
                pd.DataFrame.from_dict(
                    dict_yearly_groupSpecies_increment0,
                    orient="index",
                    columns=[f"{taxon_group_name}"],
                )
            )

            # 3.5. Plot only groups with observed species years, and this will removed already existed SAC graphs!
            if data_yearly_groupSpecies_cum.empty:
                # Remove a previous run's curve when this period has no species.
                file_name_curve = os.path.join(
                    output_path_sac,
                    f"mhhp_yearly_species_accumulation_curve_{taxon_group_name}.png",
                )
                if os.path.isfile(file_name_curve):
                    os.remove(file_name_curve)
                print(
                    f"{taxon_group_name}: no dated species observations; individual curve not plotted."
                )
            else:
                fig2_groupSpecies_cum, ax2_groupSpecies_cum = plt.subplots(
                    1, 1, figsize=(6, 4), dpi=300
                )
                size_point = 20
                if taxon_group_name in ["Avian", "Plant", "Insect"]:
                    xlabel_rotate = 90
                elif taxon_group_name in ["Cetacean", "Fish", "BenthicInvertebrate"]:
                    xlabel_rotate = 40
                else:
                    xlabel_rotate = 90

                data_yearly_groupSpecies_cum.plot(ax=ax2_groupSpecies_cum)
                ax2_groupSpecies_cum.scatter(
                    x=list(data_yearly_groupSpecies_cum.index),
                    y=data_yearly_groupSpecies_cum[f"{taxon_group_name}"],
                    s=size_point,
                    marker="o",
                )
                ax2_groupSpecies_cum.set_xticks(
                    range(0, len(data_yearly_groupSpecies_cum))
                )
                ax2_groupSpecies_cum.set_xticklabels(
                    list(data_yearly_groupSpecies_cum.index),
                    rotation=xlabel_rotate,
                    fontsize=15,
                )
                ax2_groupSpecies_cum.set_xlabel("Survey Year", fontsize=18)
                
                ax2_groupSpecies_cum.yaxis.set_major_locator(
                    plt.MaxNLocator(integer=True)
                )
                ax2_groupSpecies_cum.tick_params(axis="y", labelsize=15)
                ax2_groupSpecies_cum.set_ylabel("Species Counts", fontsize=18)
                ax2_groupSpecies_cum.legend([f"{taxon_group_name}"], fontsize=20)
                plt.tight_layout(rect=[0, 0, 1, 1])
                fig2_groupSpecies_cum.savefig(
                    output_path_sac
                    + f"mhhp_yearly_species_accumulation_curve_{taxon_group_name}.png"
                )
                plt.close(fig2_groupSpecies_cum)



        else:
            print(f"Will not process this file: {content[file_id]}")

    # Derive survey indicators after all occurrence groups have been counted.
    data_annual_occur_boolean = (data_annual_occur_counts > 0).astype("int64")
    data_annual_occur_boolean["sum"] = data_annual_occur_boolean.sum(axis=1).values
    drop_index1 = list(
        data_annual_occur_boolean[data_annual_occur_boolean["sum"] == 0].index
    )
    data_yearly_occur_boolean = data_annual_occur_boolean.drop(
        drop_index1, inplace=False
    )

    return (
        data_species_ratio,
        data_annual_species_counts,
        data_annual_species_cumulative0,
        data_annual_species_increment0,
        data_annual_occur_counts,
        data_annual_occur_boolean,
        data_yearly_occur_boolean,
    )


# %% 4. Export summary tables and yearly survey-target indicators.


def export_summary_tables(
    output_path_counts,
    output_path_sac,
    data_species_ratio,
    data_annual_species_counts,
    data_annual_species_cumulative0,
    data_annual_species_increment0,
    data_yearly_occur_boolean,
):
    """Export five summary CSVs and return a completion message.

    Summary tables use Year index labels and retain NaN values. 
    Survey-target indicators use occurrences at all ranks and omit years with no surveyed group (yearly counts).
    """
    # Export species ratios and annual observed-species counts.
    data_species_ratio.to_csv(
        output_path_counts + "mhhp_yearly_species_ratio_8_groups.csv",
        sep=",",
        index=True,
        index_label="Year",
        encoding="utf_8",
    )

    data_annual_species_counts.to_csv(
        output_path_counts + "mhhp_yearly_species_counts_8_groups.csv",
        sep=",",
        index=True,
        index_label="Year",
        encoding="utf_8",
    )

    # Export cumulative counts and new-species increments with NaN intact.
    data_annual_species_cumulative0.to_csv(
        output_path_sac + "mhhp_yearly_species_accumulation_8_groups_richness_raw.csv",
        sep=",",
        index=True,
        index_label="Year",
        encoding="utf_8",
    )

    data_annual_species_increment0.to_csv(
        output_path_sac + "mhhp_yearly_species_increments_8_groups_richness.csv",
        sep=",",
        index=True,
        index_label="Year",
        encoding="utf_8",
    )

    # A positive occurrence count marks a surveyed group for that year (0 | 1).
    data_yearly_occur_boolean.to_csv(
        output_path_counts + "mhhp_yearly_survey_targets_boolean_8_groups.csv",
        sep=",",
        index=True,
        index_label="Year",
        encoding="utf_8",
    )

    return "All the tables have been exported"


# %% 5. Export individual annual-count figures and the six-panel figure.


def plot_annual_species_counts(
    data_annual_species_counts, output_path_counts, year_max
):
    """Export annual-count figures and return the plotting table, colors, and label.

    Missing values are filled with zero for plotting only. The six-panel figure
    places groups down each column in the configured group order.
    """

    
    data_annual_counts_fig = data_annual_species_counts.copy()
    data_annual_counts_fig = data_annual_counts_fig.fillna(0).astype("int")
    ylabel_name = "Species Counts"
    
    #range(1995, 2026, 1)
    
    tick_years = list(
        range(
            ((int(data_annual_counts_fig.index.min()) + 4) // 5) * 5,
            int(year_max) + 1,
            5,
        )
    )
    if not tick_years:
        tick_years = [int(data_annual_counts_fig.index.min())]

    color_category = {
        "Algae": "#6ccb59",
        "Avian": "#ff9a03",
        "BenthicInvertebrate": "#46859c",
        "Cetacean": "#6ccbef",
        "Fish": "#4685ff",
        "Plant": "#077148",
        "Reptile": "#61396e",
        "Insect": "#613901",
    }



    # 5.1. Export individual annual count figures for the eight analysed groups.
    for category1 in [
        "Algae",
        "Avian",
        "BenthicInvertebrate",
        "Cetacean",
        "Fish",
        "Plant",
        "Reptile",
        "Insect",
    ]:
        
        
        # Use a readable group name in the legend.
        
        group_label = (
            "Benthic Invertebrate"
            if category1 == "BenthicInvertebrate"
            else category1
            )

        file_annual_counts = (
            f"mhhp_yearly_species_counts_{group_label}.png"
            )
        dir_annual_counts = os.path.join(output_path_counts, file_annual_counts)
        

        if category1 not in data_annual_counts_fig.columns:
            

            # Remove previous annual count figures           
            if os.path.isfile(dir_annual_counts):
                os.remove(dir_annual_counts)
                
            #Go to another group
            continue


        fig0_annual_counts, axis0_annual_counts = plt.subplots(1, 1, dpi=300)

        bar0_annual_counts = axis0_annual_counts.bar(
            data_annual_counts_fig.index,
            data_annual_counts_fig[category1],
            color=color_category[category1],
        )


        bar0_annual_counts.set_label(group_label)
        axis0_annual_counts.legend(prop={"size": 25})

        # Show integer species-count ticks.
        axis0_annual_counts.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Set tick-label sizes.
        axis0_annual_counts.tick_params(axis="y", labelsize=15)
        axis0_annual_counts.tick_params(axis="x", labelsize=15)

        axis0_annual_counts.set_xlabel("Year", fontsize=20)
        axis0_annual_counts.set_ylabel(ylabel_name, fontsize=20)
        
        if len(data_annual_counts_fig.index) == 1:
            axis0_annual_counts.set_xticks(tick_years)
        plt.tight_layout()
        
        fig0_annual_counts.savefig(dir_annual_counts)
        plt.close(fig0_annual_counts)


    # 5.2. Fill this specific six-panel figure down each column in the configured group order.
    fig_row_counts = 3

    fig1_groupSpecies_annual_counts, axis1_groupSpecies_annual_counts = plt.subplots(
        3, 2, dpi=300, figsize=(11.69, 8.27)
    )
    turn = 0
    
    for category1 in [
        "Avian",
        "Fish",
        "Insect",
        "Cetacean",
        "BenthicInvertebrate",
        "Plant",
    ]:
        
        # Reserve a fixed panel position for every configured group.
        row1_panel = np.mod(turn, fig_row_counts)
        column1_panel = int(np.floor(turn / fig_row_counts))
        turn = turn + 1
        
        # Remove previous annual count six-panel figure
        if category1 not in data_annual_counts_fig.columns:
            
            axis1_panel = axis1_groupSpecies_annual_counts[
                row1_panel, column1_panel
            ]
            group_label = (
                "Benthic Invertebrate"
                if category1 == "BenthicInvertebrate"
                else category1
            )

            # Keep the frame without displaying numeric ticks.
            axis1_panel.set_xticks([])
            axis1_panel.set_yticks([])

            axis1_panel.text(
                0.5, 0.65, group_label,
                transform=axis1_panel.transAxes,
                ha="center", va="center",
                fontsize=22,
            )
            axis1_panel.text(
                0.5, 0.45, f"No species or infraspecies records from 1994 to {year_max}",
                transform=axis1_panel.transAxes,
                ha="center", va="center",
                fontsize=16,
                fontfamily="Times New Roman",
            )
            continue

        
        
        
        data_annual_counts_fig[category1] = data_annual_counts_fig[category1].astype(
            "Int64"
        )

        bar1_groupSpecies_annual_counts = axis1_groupSpecies_annual_counts[
            row1_panel, column1_panel
        ].bar(
            data_annual_counts_fig.index,
            data_annual_counts_fig[category1],
            color=color_category[category1],
        )

        # Use a readable group name in the legend.
        if category1 == "BenthicInvertebrate":
            category1 = "Benthic Invertebrate"
            
        # set legend
        bar1_groupSpecies_annual_counts.set_label(category1)
        # set legend fontsize 
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].legend(prop={"size": 22})

        # Show integer species-count ticks.
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].yaxis.set_major_locator(
            MaxNLocator(integer=True)
        )
        # Set tick-label sizes.
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].tick_params(
            axis="y", labelsize=20
        )
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].set_xlabel(
            "Year", fontsize=20
        )
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].set_ylabel(
            ylabel_name, fontsize=20
        )

        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].set_xticks(tick_years)
        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].set_xticklabels(
            tick_years, fontsize=20
        )

        axis1_groupSpecies_annual_counts[row1_panel, column1_panel].tick_params(
            axis="y", labelsize=15
        )


    plt.tight_layout()
    fig1_groupSpecies_annual_counts.savefig(
        output_path_counts + "mhhp_yearly_species_counts_6subplots.png"
    )
    plt.close(fig1_groupSpecies_annual_counts)

    return data_annual_counts_fig, color_category, ylabel_name


# %% 6. Export the combined accumulation curve for six groups.


def plot_combined_accumulation_curve(
    data_annual_species_increment0, color_category, output_path_sac, year_max
):
    """Plot increments filled with zero and accumulated over the full year index.

    Return data_species_cumulative_fig so the plotted values can be checked.
    """
    # For this combined figure, fill missing increments with zero before cumsum.
    # The raw cumulative CSV retains NaN in years without species observations.
    data_species_cumulative_fig = (
        data_annual_species_increment0.fillna(0).cumsum().astype("int")
    )
    
    
    
    tick_years = list(
        range(
            ((int(data_species_cumulative_fig.index.min()) + 4) // 5) * 5,
            int(year_max) + 1,
            5,
        )
    )
    if not tick_years:
        tick_years = [int(data_species_cumulative_fig.index.min())]
        
        

    fig2_combined_groupSpecies_cum, axis2_combined_groupSpecies_cum = plt.subplots(
        1, 1, dpi=300, figsize=(6, 4)
    )
    
    # Remove previous combined_sac file
    content_output = np.array(sorted(os.listdir(output_path_sac)))
    filter_combined_sac =["_groups_raw.png" in figname for figname in content_output]
    for file_combined_sac in content_output[filter_combined_sac]:
        dir_combined_sac = os.path.join(output_path_sac, file_combined_sac)
    
        if os.path.isfile(dir_combined_sac):
            os.remove(dir_combined_sac)    
    
    
    
    for category2 in [
        "Avian",
        "Fish",
        "Insect",
        "Cetacean",
        "BenthicInvertebrate",
        "Plant",
    ]:
        
        if category2 in data_species_cumulative_fig.columns:
            pass
        else:
            continue

        (line2_groupSpecies,) = axis2_combined_groupSpecies_cum.plot(
            data_species_cumulative_fig.index,
            data_species_cumulative_fig[category2],
            color=color_category[category2],
            linewidth=2,
        )

        # Use a readable group name in the legend.
        if category2 == "BenthicInvertebrate":
            category2 = "Benthic Invertebrate"
        line2_groupSpecies.set_label(category2)

        axis2_combined_groupSpecies_cum.set_xlabel("Year", fontsize=15)
        axis2_combined_groupSpecies_cum.set_ylabel(
            "Cumulative Species Counts", fontsize=15
        )

        axis2_combined_groupSpecies_cum.set_xticks(tick_years)
        axis2_combined_groupSpecies_cum.set_xticklabels(tick_years, fontsize=15)

        axis2_combined_groupSpecies_cum.tick_params(axis="y", labelsize=15)


    curve_count = len(axis2_combined_groupSpecies_cum.get_lines())
    if curve_count > 0:
        axis2_combined_groupSpecies_cum.legend(
        frameon=False, prop={"size": 10} )
    
    plt.tight_layout()
    
    fig2_combined_groupSpecies_cum.savefig(
        output_path_sac + f"mhhp_yearly_species_accumulation_curves_{curve_count}_groups_raw.png"
    )
    plt.close(fig2_combined_groupSpecies_cum)

    return data_species_cumulative_fig


# %% 7. Validate inputs, calculate statistics, and export results.
def main(IPT_version="1.37", year_max=None):
    """Analyse from 1994 through a selected or dataset-derived maximum year."""
    year_min = 1994

    # 1. Resolve repository paths.
    root_path, input_path, output_path, output_path_counts, output_path_sac = (
        setup_paths()
    )

    # 2. Show full dataset coverage and choose the analysis end year.
    df0_whole = pd.read_csv(
        os.path.join(input_path, "occurrence_whole.csv"),
        encoding="utf-8-sig",
        usecols=["year"],
        dtype={"year": "Int64"},
    )
    
    year_max = resolve_analysis_year_max(
        df0_whole, IPT_version, year_max, interactive=sys.stdin.isatty()
    )

    # 3. Validate the complete input files before selecting analysis records.
    content, data_combined_occur = check_data_integrity(
        input_path, IPT_version, year_max
    )

    # 4. Calculate statistics through the selected end year.
    (
        data_species_ratio,
        data_annual_species_counts,
        data_annual_species_cumulative0,
        data_annual_species_increment0,
        data_annual_occur_counts,
        data_annual_occur_boolean,
        data_yearly_occur_boolean,
    ) = calculate_group_statistics(
        input_path, output_path_sac, content, data_combined_occur, year_min, year_max
    )

        
    # 5. Export summary tables and figures.
    export_tables_success = export_summary_tables(
        output_path_counts,
        output_path_sac,
        data_species_ratio,
        data_annual_species_counts,
        data_annual_species_cumulative0,
        data_annual_species_increment0,
        data_yearly_occur_boolean,
    )
    print(export_tables_success)

    data_annual_counts_fig, color_category, ylabel_name = plot_annual_species_counts(
        data_annual_species_counts, output_path_counts, year_max
    )
    data_species_cumulative_fig = plot_combined_accumulation_curve(
        data_annual_species_increment0, color_category, output_path_sac, year_max
    )



#%%

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate annual species statistics and accumulation curves."
    )
    parser.add_argument(
        "--ipt-version", default="1.37", help="IPT version of the input taxon snapshot."
    )
    parser.add_argument(
        "--year-max",
        type=int,
        default=None,
        help=(
            "Last analysis year; the first year is fixed at 1994. "
            "If omitted, prompt in a terminal or use the dataset maximum."
        ),
    )
    args = parser.parse_args()
    main(args.ipt_version, args.year_max)

#%%
