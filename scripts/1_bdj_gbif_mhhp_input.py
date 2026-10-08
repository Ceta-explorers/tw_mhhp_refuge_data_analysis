# -*- coding: utf-8 -*-
"""Download a Mianhua and Huaping Islets archive and prepare analysis inputs.

Original author: cetae
Original creation date: September 21, 2026.
Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
License: Creative Commons Attribution 4.0 International (CC BY 4.0).
See LICENSE.txt in the repository root for the license terms.

Save the complete occurrence table, fish measurements, nine taxonomic group
tables, and a taxon summary in the repository's mhhp_inputs directory.
Report the dataset year range and require its first known year to be 1994.
"""

# Standard library.
import argparse
import io
import os
import zipfile

# Third-party packages.
import pandas as pd
import requests


# %% 1. Resolve the repository and input folder.
def setup_paths():
    """Resolve the repository root and create its analysis input directory.

    In an interactive session without __file__, run from the scripts directory.
    """
    try:
        script_dir = os.path.abspath(__file__)
        script_folder = os.path.abspath(os.path.join(script_dir, ".."))
    except NameError:
        script_folder = os.getcwd()

    root_path = os.path.abspath(os.path.join(script_folder, ".."))
    print(f"root_path is `{root_path}`")
    input_path = os.path.join(root_path, "mhhp_inputs/")
    if not os.path.exists(input_path):
        os.mkdir(input_path)
    return root_path, input_path


# %% 2. Download and read the occurrence and measurement tables.
def download_dataset(IPT_version="1.37"):
    """Return occurrence and measurement tables from the selected IPT version.

    Occurrence integer columns use pandas' nullable Int64 type. Coordinates
    are rounded to five decimal places; measurement values to one decimal.
    No CSV files are written until the table relationships have been checked.
    """
    download_url = (
        "https://ipt.taibif.tw/archive.do?"
        f"r=cetaexplorers_mianhua_huaping_islets&v={IPT_version}"
    )
    print(f"\nDownloading dataset version {IPT_version}...")
    response = requests.get(download_url, timeout=(30, 180))
    response.raise_for_status()

    target_file = "occurrence.txt"
    with zipfile.ZipFile(io.BytesIO(response.content)) as z1:
        required_tables = {"occurrence.txt", "extendedmeasurementorfact.txt"}
        missing_tables = required_tables.difference(z1.namelist())
        if missing_tables:
            raise ValueError(
                "The downloaded archive is missing required tables: "
                + ", ".join(sorted(missing_tables))
            )
        print(f"Archive files: {z1.namelist()}")

        with z1.open(target_file) as f1:
            df0_whole = pd.read_csv(
                f1,
                sep="\t",
                low_memory=False,
                dtype={
                    "occurrenceID": "string",
                    "taxonID": "string",
                    "scientificName": "string",
                },
            )

        with z1.open("extendedmeasurementorfact.txt") as f2:
            df0_measure = pd.read_csv(
                f2,
                sep="\t",
                low_memory=False,
                dtype={"occurrenceID": "string", "measurementRemarks": "string"},
            )

    required_columns = {
        "occurrence.txt": {
            "occurrenceID",
            "taxonID",
            "scientificName",
            "scientificNameID",
            "taxonConceptID",
            "taxonomicStatus",
            "kingdom",
            "verbatimIdentification",
            "taxonRank",
            "vernacularName",
            "taxonRemarks",
            "identificationQualifier",
            "year",
            "month",
            "eventDate",
        },
        "extendedmeasurementorfact.txt": {
            "occurrenceID",
            "measurementType",
            "measurementValue",
            "measurementRemarks",
        },
    }
    for target_file, df0_table in (
        ("occurrence.txt", df0_whole),
        ("extendedmeasurementorfact.txt", df0_measure),
    ):
        missing_columns = required_columns[target_file].difference(df0_table.columns)
        if missing_columns:
            raise ValueError(
                f"{target_file} is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )
    if df0_whole.empty:
        raise ValueError("The occurrence table contains no records.")
    print(f"\t● Loaded occurrence.txt: {len(df0_whole)} rows.")
    print(f"\t● Loaded extendedmeasurementorfact.txt: {len(df0_measure)} rows.")

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

    df0_measure["measurementValue"] = df0_measure["measurementValue"].round(1)

    return df0_whole, df0_measure


def check_measurement_table(df0_whole, df0_measure):
    
    """Normalize IDs and names in place and return measurement discrepancies.

    occurrenceID must identify one occurrence uniquely. measurementRemarks
    must equal the scientificName of that occurrence after whitespace removal.
    The returned arrays contain unknown occurrenceIDs and mismatched names.
    """
    df0_measure["occurrenceID"] = (
        df0_measure["occurrenceID"].astype("string").str.strip()
    )
    df0_whole["occurrenceID"] = df0_whole["occurrenceID"].astype("string").str.strip()
    
    
    # Check "occurrenceID" is none or duplicated.
    if (df0_whole["occurrenceID"].isna() | df0_whole["occurrenceID"].eq("")).any():
        raise ValueError(
            "The occurrence table contains missing or blank occurrenceIDs."
        )
    if df0_whole["occurrenceID"].duplicated().any():
        raise ValueError("The occurrence table contains duplicate occurrenceIDs.")

    # Each measurement must reference an existing occurrence.
    error_measure_occurID = ~(
        df0_measure["occurrenceID"].isin(df0_whole["occurrenceID"].unique())
    )
    df0_error_measure_occurID = df0_measure[error_measure_occurID]
    df0_error_measure_occurID_unique = df0_error_measure_occurID[
        "occurrenceID"
    ].unique()


    # Compare names using the referenced occurrence, rather than all species.
    df0_measure["measurementRemarks"] = (
        df0_measure["measurementRemarks"].astype("string").str.strip()
    )
    df0_whole["scientificName"] = (
        df0_whole["scientificName"].astype("string").str.strip()
    )
    scientificName_by_occurrenceID = df0_whole.set_index("occurrenceID")[
        "scientificName"
    ]
    
    ''' 
    "occurrenceID" column can be mapped,
    yet "measurementRemarks" column in df0_measure can not be mapped to "scientificName" column in df0_whole.
    
    '''
    error_measure_Remarks = ~error_measure_occurID & (
        df0_measure["measurementRemarks"].isna()
        | df0_measure["measurementRemarks"].eq("")
        | df0_measure["measurementRemarks"].ne(
            df0_measure["occurrenceID"].map(scientificName_by_occurrenceID)
        )
    ).fillna(True)
    
    df0_error_measure_Remarks = df0_measure[error_measure_Remarks]
    df0_error_measure_Remarks_unique = df0_error_measure_Remarks[
        "measurementRemarks"
    ].unique()

    return df0_error_measure_occurID_unique, df0_error_measure_Remarks_unique


def export_input_tables(df0_whole, df0_measure, input_path):
    """Save the complete occurrence and measurement tables after validation."""
    df0_whole.to_csv(
        os.path.join(input_path, "occurrence_whole.csv"),
        encoding="utf_8_sig",
        index=False,
    )
    df0_measure.to_csv(
        os.path.join(input_path, "measurement_Fish.csv"),
        encoding="utf_8_sig",
        index=False,
    )



# %% 3. Validate and export the nine taxonomic groups.

def split_taxonomic_groups(df0_whole, input_path):
    """Export groups using taxonID substring filters and return record totals.

    Every occurrence must match exactly one group before group files are saved.
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

    group_membership_count = pd.Series(0, index=df0_whole.index, dtype="int64")
    for theTaxonGroup in taxonomic_groups:
        filter_taxonomic = (
            df0_whole["taxonID"].astype("string").str.contains(theTaxonGroup, na=False)
        )
        group_membership_count = group_membership_count + filter_taxonomic.astype(
            "int64"
        )
    
    # Check for records are not included in taxonomic_groups.
    
    if not group_membership_count.eq(1).all():
        pattern = "|".join(taxonomic_groups)
        df_missing = df0_whole[
            ~df0_whole["taxonID"].astype("string").str.contains(pattern, na=False)
        ]
        df_overlapping = df0_whole[group_membership_count.gt(1)]
        raise ValueError(
            "Taxonomic group assignment is not a partition: "
            f"{len(df_missing)} unassigned records and "
            f"{len(df_overlapping)} records matching multiple groups. "
            f"Unassigned occurrenceIDs: {df_missing['occurrenceID'].tolist()}; "
            f"overlapping occurrenceIDs: {df_overlapping['occurrenceID'].tolist()}."
        )


    # Split the whole occurrence file.
    count_record = 0
    for theTaxonGroup in taxonomic_groups:
        filter_taxonomic = (
            df0_whole["taxonID"].astype("string").str.contains(theTaxonGroup, na=False)
        )
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
            "The dataset has successfully been split into multiple "
            "taxonomic group files."
        )
    else:
        raise RuntimeError(
            "The grouped record total does not match the occurrence table."
        )

    return count_record, total_record




# %% 4. Export the taxon table and identify one-to-many field mappings.


def summarize_taxa(df0_whole, input_path, IPT_version="1.37"):
    """Export unique taxon rows and return the summary and diagnostic tables.
    
    0) Checks identify taxonIDs with multiple `identificationQualifier`,
    1) Checks identify taxonIDs with multiple `taxonRemarks`,
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
    print(f"\nTaxon Count: {taxon_all_counts}")

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
    print(f"Length in df_taxon1: {len(df_taxon1)}")

    year_max = df0_whole["year"].max()
    if pd.isna(year_max) or not float(year_max).is_integer():
        raise ValueError(
            "A nonmissing integer year is required for the taxon filename."
        )
    year_max = int(year_max)
    
    # The filename identifies the coverage year, rather than the last event date.
    df_taxon1.to_csv(
        os.path.join(
            input_path,
            f"0_taxon_till_{year_max}1231_ver{IPT_version}.csv",
        ),
        encoding="utf_8_sig",
        index=False,
    )



    # Check 0: Does one taxonID correspond to multiple taxonRemarks?
    multiple_remarks = (
        df_taxon1.groupby(by="taxonID")["taxonRemarks"]
        .nunique(dropna=False)
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    multi_remarks_one_taxonID = multiple_remarks.loc[
        multiple_remarks["count"] > 1, "taxonID"
    ].values
    
    df_taxon1_wrong0 = df_taxon1.loc[
        df_taxon1["taxonID"].isin(multi_remarks_one_taxonID), :
    ].sort_values(by="taxonID")
        
        
    # Check 1: Does one taxonID correspond to multiple taxonRemarks?
    multiple_qualifier = (
        df_taxon1.groupby(by="taxonID")["identificationQualifier"]
        .nunique(dropna=False)
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )
    multi_qualifier_one_taxonID = multiple_qualifier.loc[
        multiple_qualifier["count"] > 1, "taxonID"
    ].values
    
    df_taxon1_wrong1 = df_taxon1.loc[
        df_taxon1["taxonID"].isin(multi_qualifier_one_taxonID), :
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

    return df_taxon1, df_taxon1_wrong0, df_taxon1_wrong1, df_taxon1_wrong2, df_taxon1_wrong3


# %% 5. Prepare validated inputs and summarize taxon mappings.
def main(IPT_version="1.37"):
    """Validate the dataset's fixed start year and export complete inputs."""
    root_path, input_path = setup_paths()
    df0_whole, df0_measure = download_dataset(IPT_version)

    df0_error_measure_occurID_unique, df0_error_measure_Remarks_unique = (
        check_measurement_table(df0_whole, df0_measure)
    )

    print(
        "Check! Measurement occurrenceID discrepancies: "
        f"{df0_error_measure_occurID_unique.tolist()}"
    )
    print(
        "Check! Measurement measurementRemarks discrepancies: "
        f"{df0_error_measure_Remarks_unique.tolist()}"
    )
    if len(df0_error_measure_occurID_unique) or len(df0_error_measure_Remarks_unique):
        raise ValueError(
            "Error! Measurement relationships failed validation; no inputs were exported."
        )
    if df0_whole["year"].dropna().empty:
        raise ValueError(
            "Error! At least one known observation year is required to export inputs."
        )

    year_min = 1994
    year_max = int(df0_whole["year"].max())
    print(f"\n\t● IPT version: {IPT_version}")
    print(
        f"\t● Dataset year range: {int(df0_whole['year'].min())}\u2013{year_max}"
    )

    

    # Check records with missing year
    if df0_whole["year"].isna().any():
        print(f"Warning! Records with missing years: {df0_whole['year'].isna().sum()}")
        
    # Check df0_whole["year"].min() == 1994
    if df0_whole["year"].min() != year_min:
        raise ValueError(
            f"Error! The dataset's first known year must be {year_min}; "
            f"found {int(df0_whole['year'].min())}. No inputs were exported."
        )

    export_input_tables(df0_whole, df0_measure, input_path)
    count_record, total_record = split_taxonomic_groups(df0_whole, input_path)
    print(
        f"Check! Total grouped records: {count_record};\n"
        f"total occurrence records: {total_record}."
    )
    df_taxon1, df_taxon1_wrong0, df_taxon1_wrong1, df_taxon1_wrong2, df_taxon1_wrong3 = summarize_taxa(
        df0_whole, input_path, IPT_version
    )
    
   
    
    print(f"Check! TaxonIDs with multiple taxonRemarks: {len(df_taxon1_wrong0)} taxon rows.")
    print(f"Check! TaxonIDs with multiple identificationQualifier: {len(df_taxon1_wrong1)} taxon rows.")
    print(
        f"Check! TaxonIDs with multiple vernacular names: {len(df_taxon1_wrong3)} taxon rows."
    ) 
    
    print(
        f"Check! Vernacular names with multiple taxonIDs: {len(df_taxon1_wrong2)} taxon rows."
    )

#%%

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ipt-version",
        default="1.37",
        help="IPT archive version to download (default: 1.37).",
    )
    args = parser.parse_args()
    main(args.ipt_version)
