# -*- coding: utf-8 -*-
"""Download the v1.36 Mianhua and Huaping Islets dataset and prepare inputs.

Original author: cetae
Original creation date: September 21, 2026.

Revision 1 groups the existing operations into a few complete tasks. Original
analysis variable names, column names, calculations, and output names are kept
so that each step can be compared with the original script.
"""

# Standard library.
import io
import os
import zipfile
from datetime import datetime

# Third-party packages.
import pandas as pd
import requests


# %% 1. Resolve the repository and input folder.
def setup_paths():
    """Resolve input paths using the original script-location convention.

    Keep the original variable name ``script_folder`` for comparison. When
    ``__file__`` is unavailable, retain the original working-directory fallback.
    """
    try:
        script_dir = os.path.abspath(__file__)
        script_folder = os.path.abspath(os.path.join(script_dir, ".."))
    except:  # Original fallback for interactive environments such as Jupyter.
        script_folder = os.getcwd()

    root_path = os.path.abspath(os.path.join(script_folder, ".."))
    print(f"root_path is `{root_path}`")
    input_path = os.path.join(root_path, "mhhp_inputs/")
    if not os.path.exists(input_path):
        os.mkdir(input_path)
    return root_path, input_path


# %% 2. Download the archive, read its tables, and preserve original conversions.
def download_dataset(input_path, IPT_version='1.37'):
    """Read v1.36 occurrence and measurement tables from the downloaded archive.

    Occurrence integer columns use pandas' nullable Int64 type. Coordinates
    retain the original five-decimal rounding. The measurement table is saved
    as ``measurement_Fish.csv``. The original HTTP-200 condition is retained.
    """
    download_url = (
        "https://ipt.taibif.tw/archive.do?"
        f"r=cetaexplorers_mianhua_huaping_islets&v={IPT_version}"
    )
    print("Downloading dataset...")
    response = requests.get(download_url)
    print(response.status_code)

    target_file = "occurrence.txt"
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z1:
            print(f" Contain Files: {z1.namelist()}")

            with z1.open("occurrence.txt") as f1:
                df0_whole = pd.read_csv(f1, sep="\t", low_memory=False)
                print(f"\n Load {target_file}, Total Rows：{len(df0_whole)}")

                int_columns = [
                    "coordinateUncertaintyInMeters",
                    "maximumDepthInMeters",
                    "minimumDepthInMeters",
                    "individualCount",
                    "year",
                    "month",
                    "day",
                    "scientificNameID",
                ]
                for col in int_columns:
                    if col in df0_whole.columns:
                        df0_whole[col] = df0_whole[col].astype("Int64")

                float_5_columns = [
                    "decimalLatitude",
                    "decimalLongitude",
                    "coordinatePrecision",
                ]
                for col in float_5_columns:
                    if col in df0_whole.columns:
                        df0_whole[col] = df0_whole[col].round(5)
                        
                df0_whole.to_csv(
                    os.path.join(input_path, "occurrence_whole.csv"),
                    encoding="utf_8_sig",
                    index=False,
                    )

            with z1.open("extendedmeasurementorfact.txt") as f2:
                df0_measure = pd.read_csv(f2, sep="\t", low_memory=False)
                
                df0_measure['measurementValue'] = df0_measure['measurementValue'].round(1)
                df0_measure.to_csv(
                    os.path.join(input_path, "measurement_Fish.csv"),
                    encoding="utf_8_sig",
                    index=False,
                )

    return df0_whole, df0_measure


def check_measurement_table(df0_whole, df0_measure):
    
    #. Identify the `occurrenceID`
    df0_measure['occurrenceID'] = df0_measure['occurrenceID'].str.strip()
    df0_whole['occurrenceID'] = df0_whole['occurrenceID'].str.strip()
    
    error_measure_occurID = ~(
        df0_measure['occurrenceID'].isin(df0_whole['occurrenceID'].unique())
        ) 
    df0_error_measure_occurID = df0_measure[error_measure_occurID]
    df0_error_measure_occurID_unique = df0_error_measure_occurID['occurrenceID'].unique()
    

    #. Identify the `measurementRemarks`
    df0_measure['measurementRemarks'] = df0_measure['measurementRemarks'].str.strip()
    df0_whole['scientificName'] = df0_whole['scientificName'].str.strip()
    
    
    error_measure_Remarks = ~(
        df0_measure['measurementRemarks'].isin(df0_whole['scientificName'].unique())
        )
    df0_error_measure_Remarks = df0_measure[error_measure_Remarks]
    df0_error_measure_Remarks_unique = df0_error_measure_Remarks['measurementRemarks'].unique()
    
    return df0_error_measure_occurID_unique, df0_error_measure_Remarks_unique
    



# %% 3. Export the original nine taxonomic groups and check record totals.
def split_taxonomic_groups(df0_whole, input_path):
    """Export group CSVs using the original taxonID substring filters.

    Preserve group order and compare the sum of exported rows with the source
    row count. If the totals differ, retain ``df_missing`` for diagnosis.
    """
    taxonomic_groups = [
        "Algae",
        "Avian",
        "BenthicInvertebrate",
        "Cetacean",
        "Fish",
        "Insect",
        "Plant",
        "Spider",
        "Reptile",
    ]

    count_record = 0
    for theTaxonGroup in taxonomic_groups:
        filter_taxonomic = df0_whole["taxonID"].str.contains(theTaxonGroup, na=False)
        df0_group1 = df0_whole.loc[filter_taxonomic, :]
        df0_group1.to_csv(
            os.path.join(input_path, f"occur_{theTaxonGroup}.csv"),
            encoding="utf_8_sig",
            index=False,
        )
        count_record = count_record + len(df0_group1)

    total_record = len(df0_whole)
    if count_record == total_record:
        print(
            " The dataset has successfully been split into multiple "
            "taxonomic group files."
        )
    else:
        print(
            " The dataset has failed to be split into multiple "
            "taxonomic group files."
        )
        pattern = "|".join(taxonomic_groups)
        df_missing = df0_whole[~df0_whole["taxonID"].str.contains(pattern, na=False)]
        print(f"These records aren't included: {df_missing}.")

    return count_record, total_record


# %% 4. Export the taxon table and identify one-to-many field mappings.

def summarize_taxa(df0_whole, input_path, IPT_version='1.37'):
    """Export unique taxon rows and return the original three diagnostic tables.

    1) Checks identify taxonIDs with multiple taxonRemarks,
    2) vernacular names with multiple taxonIDs, 
    3) and taxonIDs with multiple vernacular names. 
    Missing values remain included in each nunique calculation (dropna=False).
    """
    taxon_all_counts = {
        "scientificName": len(df0_whole["scientificName"].unique()),
        "scientificNameID": len(df0_whole["scientificNameID"].unique()),
        "taxonConceptID": len(df0_whole["taxonConceptID"].unique()),
        "taxonID": len(df0_whole["taxonID"].unique()),
        "verbatimIdentification": len(df0_whole["verbatimIdentification"].unique()),
        "vernacularName": len(df0_whole["vernacularName"].unique()),
    }
    print(f"Taxon, Count: {taxon_all_counts}")
    
    
    
    
    df_taxon1 = df0_whole[
        [
            "taxonID",
            "scientificNameID",
            "taxonConceptID",
            "taxonomicStatus",
            "kingdom",
            "scientificName",
            "verbatimIdentification",
            "taxonRank",
            "vernacularName",
            "taxonRemarks",
            "identificationQualifier",
        ]
    ].drop_duplicates()
    print(f"Length in df_taxon1 :{len(df_taxon1)}")
    
    
    year_max = df0_whole['year'].max()
    df_taxon1.to_csv(
        os.path.join(
            input_path,
            f"0_taxon_till_{year_max}1231_ver{IPT_version}.csv",
        ),
        encoding="utf_8_sig",
        index=False,
    )

    # Check 1: Does one taxonID correspond to multiple taxonRemarks?
    multiple_remarks = (
        df_taxon1.groupby(by="taxonID")["taxonRemarks"]
        .nunique(dropna=False)
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    multi_remarks_one_taxonID = multiple_remarks.loc[
        multiple_remarks["count"] > 1, "taxonID"
        ].values
    df_taxon1_wrong1 = df_taxon1.loc[
        df_taxon1["taxonID"].isin(multi_remarks_one_taxonID), :
    ].sort_values(by="taxonID")

    # Check 2: Does one vernacularName correspond to multiple taxonIDs?
    multiple_ID = (
        df_taxon1.groupby(by="vernacularName")["taxonID"]
        .nunique(dropna=False)
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    multi_ID_one_vernacular = multiple_ID.loc[
        multiple_ID["count"] > 1, "vernacularName"
    ].values
    df_taxon1_wrong2 = df_taxon1[
        df_taxon1["vernacularName"].isin(multi_ID_one_vernacular)
    ].sort_values(by="vernacularName", ascending=True)

    # Check 3: Does one taxonID correspond to multiple vernacularNames?
    multiple_vernacular = (
        df_taxon1.groupby(by="taxonID")["vernacularName"]
        .nunique(dropna=False)
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    multi_vernacular_one_taxonID = multiple_vernacular.loc[
        multiple_vernacular["count"] > 1, "taxonID"
    ].values
    df_taxon1_wrong3 = df_taxon1[
        df_taxon1["taxonID"].isin(multi_vernacular_one_taxonID)
    ]

    return df_taxon1, df_taxon1_wrong1, df_taxon1_wrong2, df_taxon1_wrong3


# %% 5. Run the same tasks in their original order.
def main(IPT_version='1.37'):
    """Download inputs, export taxonomic groups, and summarize taxon mappings."""
    root_path, input_path = setup_paths()
    df0_whole, df0_measure = download_dataset(input_path, IPT_version)
    
    (
     df0_error_measure_occurID_unique, 
     df0_error_measure_Remarks_unique
     ) = check_measurement_table(df0_whole, df0_measure)
    
    count_record, total_record = split_taxonomic_groups(df0_whole, input_path)
    print(f"Total Number of grouped records is {count_record}; Total Number of occurrence records is {total_record};")
    df_taxon1, df_taxon1_wrong1, df_taxon1_wrong2, df_taxon1_wrong3 = summarize_taxa(
        df0_whole, input_path, IPT_version
    )


if __name__ == "__main__":
    main('1.37')


