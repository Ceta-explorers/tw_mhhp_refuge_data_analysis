# -*- coding: utf-8 -*-
"""The Survey Data of Mianhua and Huaping Islets Wildlife Refuge.

Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.

@author: Jui-Wen Chang (Ceta explorers Co., Ltd)

Revision 1 preserves the original analysis variable names, DataFrame columns,
calculations, missing-value rules, file names, and figure styles.
"""

# Standard library.
import os
import re
import sys

# Third-party packages.
import chardet
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


# %% 1. Configure the original font and resolve input/output paths.
def setup_paths():
    """Configure paths and create output folders using the original convention.

    The original working-directory fallback and ``script_folder`` name are kept.
    Figure fonts remain Times New Roman with sans-serif as the second choice.
    """
    matplotlib.rcParams["font.family"] = ["Times New Roman", "sans-serif"]

    # Returns the absolute directory of the active script and parent directory
    try:
        script_dir = os.path.abspath(__file__)
        script_folder = os.path.abspath(os.path.join(script_dir, ".."))
    except:  # Jupyter
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


#root_path, input_path, output_path, output_path_counts, output_path_sac = (     setup_paths() )



# %% 2. Check identifiers and build the combined occurrence table.
def check_data_integrity(input_path, IPT_version='1.37', year_max = 2025):
    """Check identifiers and return sorted input filenames and data_combined_occur.

    File 0 is treated as the taxon table. Other tables are concatenated only if
    they contain occurrenceID, do not contain measurementType, and have unique
    occurrenceIDs.
    
    Original encoding choices and date preparation are retained.
    The taxonID sets (count_taxonID_taxon/count_taxonID_occur) and rank filter remain available inside this step for
    inspection; as in the original, they do not filter the analysis tables.
    """
    # File position remains based on sorted directory contents; file 0 is the taxon table.
    #content = os.listdir(input_path)
    content = [
    f"0_taxon_till_{year_max}1231_ver{IPT_version}.csv",
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
    
    content = sorted(content)

    data_combined_occur = pd.DataFrame([])

    # Check identifiers independently within each input file.
    for file_id in range(
        0, len(content)
    ):  #  1 Taxon Table + 1 Measurement Table + 9 taxonomic groups [ range(0,11) ]

        # 1. Detect Encoding
        with open(os.path.join(input_path, content[file_id]), "rb") as f:
            # read 10000 bytes (10 KB) to detect encoding
            result = chardet.detect(f.read(10000))
            print(result["encoding"])
            if result["encoding"] == "Big5":
                encoding_name = "cp950"
            elif result["encoding"] == "Windows-1252":
                encoding_name = "ANSI"
            elif result["encoding"] == "Windows-1254":
                encoding_name = "ANSI"
            elif result["encoding"] == "UTF-8-SIG":
                encoding_name = "UTF-8-SIG"      
            else:
                encoding_name = "utf-8"

        if file_id == 0:  # Make Sure that taxonID is unique
            data_taxon = pd.read_csv(
                os.path.join(input_path, content[file_id]), encoding=encoding_name
            )
            data_taxon = data_taxon.sort_values(by=["taxonID"])

            data_taxon_taxonID = data_taxon.value_counts("taxonID", sort=True)
            data_taxon_taxonID = data_taxon_taxonID.reset_index()
            data_taxon_taxonID = data_taxon_taxonID.sort_values(by=["count"])

            if len(data_taxon_taxonID) == len(data_taxon):
                print(f"{content[file_id]}: taxonID is unique.")
            else:
                print(f"{content[file_id]}: The taxonID is NOT unique!\n")
                
                # Diagnose of duplicate taxonID.
                multiple_taxonID = data_taxon_taxonID.loc[data_taxon_taxonID['count']>1,'taxonID'].values
                data_taxon_multi_taxonID = data_taxon[
                    data_taxon["taxonID"].isin(multiple_taxonID)
                    ].sort_values(by="taxonID",  ascending= True)
                print(f"These taxonID appears duplicate: {data_taxon_multi_taxonID} .")
                


        else:
            data1_check = pd.read_csv(
                os.path.join(input_path, content[file_id]), encoding=encoding_name
            )
            # Make Sure that occurrenceID is unique
            if ("occurrenceID" in list(data1_check.columns)) and (
                "measurementType" not in list(data1_check.columns)
            ):
                data_occurrenceID = data1_check.value_counts("occurrenceID", sort=True)
                if len(data_occurrenceID) == len(data1_check):
                    data_combined_occur = pd.concat(
                        [data_combined_occur, data1_check], ignore_index=True
                    )
                    print(f"{content[file_id]}: occurrenceID is unique.")
                else:
                    print(f"{content[file_id]}: The occurrenceID is NOT unique!\n")

    # Represent year-only dates with "-00-00", and normalize date separators.
    filter_only_year = data_combined_occur["eventDate"].str.len() == 4
    data_combined_occur["verbatimEventDate"] = data_combined_occur["eventDate"]
    data_combined_occur.loc[filter_only_year, "verbatimEventDate"] = (
        data_combined_occur.loc[filter_only_year, "verbatimEventDate"] + "-00-00"
    )
    data_combined_occur["verbatimEventDate"] = data_combined_occur[
        "verbatimEventDate"
    ].str.replace("/", "-")

    # Prepare taxonID sets for comparing the taxon and occurrence tables.
    data_combined_occur_taxonID = data_combined_occur.value_counts("taxonID", sort=True)
    data_combined_occur_taxonID = data_combined_occur_taxonID.reset_index().sort_values(
        by=["taxonID"]
    )
    
    count_taxonID_taxon = set(data_taxon_taxonID["taxonID"].values)
    count_taxonID_occur = set(data_combined_occur_taxonID["taxonID"].values)
    
    if count_taxonID_occur == count_taxonID_taxon:
        print('The number of taxonID in occurrence table is equal to the number of taxonID in taxon table.')
    else:
        print('The number of taxonID in occurrence table is NOT equal to the number of taxonID in taxon table!')
        
    

    
    data_combined_occur["taxonRank"] = data_combined_occur["taxonRank"].replace(
                "varietas", "variety"
            )
    print(f'The unique taxonRank value included {data_combined_occur["taxonRank"].unique()}')
    
    filter_rank = data_combined_occur["taxonRank"].isin(
        [
            "kingdom",
            "phylum",
            "class",
            "order",
            "family",
            "subfamily",
            "genus",
            "species",
            "subspecies",
            "variety"
        ]
    )

    return content, data_combined_occur


# %% 3. Prepare each group, calculate annual statistics, and export its SAC.
def calculate_group_statistics(
    input_path, output_path_sac, content, data_combined_occur, year_min, year_max
):
    """Return the original five summary tables after processing each group.
    Individual SAC CSVs use observed years; full-year tables retain NaN. 
    
    Occurrence counts use data0,
    whereas species statistics use data1,
    which includes: Spider exclusion, 
    name_species as the first two name words, and
    filtering to species/subspecies/variety. 
    
    The varietas replacement deliberately still targets data_combined_occur, matching the original script.
    """
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

    # Read every table after the first sorted file (the taxon table).
    for file_id in range(1, len(content)):
        file_name = content[file_id]
        taxon_group_name = file_name[:-4].split("_")[1]

        # Detect encoding using the whole file, as in the original group loop.
        with open(os.path.join(input_path, content[file_id]), "rb") as f:
            result = chardet.detect(f.read())
            print(f"{file_name} : {result['encoding']}")

            if result["encoding"] == "Big5":
                encoding_name = "cp950"
            elif result["encoding"] == "Windows-1252":
                encoding_name = "ANSI"
            elif result["encoding"] == "Windows-1254":
                encoding_name = "ANSI"
            elif result["encoding"] == "UTF-8-SIG":
                encoding_name = "UTF-8-SIG"    
            else:
                encoding_name = "utf-8"
                
        data0 = pd.read_csv(
            os.path.join(input_path, content[file_id]), encoding=encoding_name
        )

        ''' Analyse each occurrence table of specific group, inclding:
            "Algae",
            "Avian",
            "BenthicInvertebrate",
            "Cetacean",
            "Fish",
            "Plant",
            "Reptile",
            "Insect".
        '''
    
        if (
            ("occurrenceID" in list(data0.columns))
            and ("measurementType" not in list(data0.columns))
            and (not bool(re.search("Spider", content[file_id])))
        ):

            data0["year"] = data0["year"].astype("Int64")  
            data0["month"] = data0["month"].astype("Int64")
            data0.sort_values(
                ["year"], ascending=True, ignore_index=True, inplace=True
            )  

            # Sort by 'eventDate' and 'verbatimEventDate'
            data0["eventDate"] = data0["eventDate"].astype("str")
            filter_only_year = data0["eventDate"].str.len() == 4
            data0["verbatimEventDate"] = data0["eventDate"]
            data0.loc[filter_only_year, "verbatimEventDate"] = (
                data0.loc[filter_only_year, "verbatimEventDate"] + "-00-00"
            )
            data0.sort_values(
                ["verbatimEventDate"], ascending=True, ignore_index=True, inplace=True
            )

            # 3.0. Derive species names and retain species/subspecies/variety.
            # Higher ranks are excluded from species statistics.
            data0["name_split"] = data0["scientificName"].str.strip().str.split()

            data0["name_split_2words"] = data0["name_split"].apply(
                lambda x: x[:2] if (isinstance(x, list) and len(x) >= 2) else x
            )

            # Extract Binomial Nomenclature (Genus + Specific epithet)
            data0["name_species"] = data0["name_split_2words"].str.join(" ")

            # Normalize rank spelling before applying the original rank filter.
            data0["taxonRank"] = data0["taxonRank"].str.strip().str.lower()
            
            # Preserve the original target: this replaces values in data_combined_occur.
            data0["taxonRank"] = data0["taxonRank"].replace(
                "varietas", "variety"
            )

            filter_species = (
                (data0["taxonRank"] == "species")
                | (data0["taxonRank"] == "subspecies")
                | (data0["taxonRank"] == "variety")
            )

            # Compare retained species-name counts with names at all ranks.
            data_species_ratio[taxon_group_name] = [
                data0.loc[filter_species, "name_species"].nunique(),
                data0.loc[:, "name_species"].nunique(),
                np.round(
                    data0.loc[filter_species, "name_species"].nunique()
                    / data0["name_species"].nunique(),
                    2,
                ),
            ]
            data1 = data0[filter_species].copy()

            # 3.1. Count species observed within each year (not newly recorded species).
            
            data_taxon_yearly = (
                data1.groupby(["year"])["name_species"].nunique(dropna=True).to_frame()
            )
            

            
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
                    dict_yearly_groupSpecies_increment0[value_year] = dict_yearly_groupSpecies_cumulative0[value_year]
                elif index_year != 0:
                    year_previous = taxon_unique_years[index_year - 1]
                    dict_yearly_groupSpecies_increment0[value_year] = (
                        dict_yearly_groupSpecies_cumulative0[value_year] - dict_yearly_groupSpecies_cumulative0[year_previous]
                    )
            

            
            data_yearly_groupSpecies_cum = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_cumulative0, orient="index", columns=[f"{taxon_group_name}"]
            )
            
            
            data_yearly_groupSpecies_incr = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_increment0, orient="index", columns=[f"{taxon_group_name}"]
            )

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


            # 3.4. Align survey-year values to the full 1994-2025 index.
            # Leave years without values as NaN in the exported raw tables.
            data_annual_species_cumulative0[f"{taxon_group_name}"] = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_cumulative0, orient="index", columns=[f"{taxon_group_name}"]
            )
            data_annual_species_increment0[f"{taxon_group_name}"] = pd.DataFrame.from_dict(
                dict_yearly_groupSpecies_increment0, orient="index", columns=[f"{taxon_group_name}"]
            )

            # 3.5. Export the individual-group curve in observed survey-year order.

            
            fig2_groupSpecies_cum, ax2_groupSpecies_cum = plt.subplots(1, 1, figsize=(6, 4), dpi=300)
            size_point = 20  # the size of the point
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

            ax2_groupSpecies_cum.set_xticks(range(0, len(data_yearly_groupSpecies_cum)))
            ax2_groupSpecies_cum.set_xticklabels(
                list(data_yearly_groupSpecies_cum.index),
                rotation=xlabel_rotate,
                fontsize=15,
            )
            ax2_groupSpecies_cum.set_xlabel("Survey Year", fontsize=18)

            # First, keep integer tick positions for species counts.
            plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            
            # Second, set the fontsize
            ax2_groupSpecies_cum.tick_params(axis="y", labelsize=15)
            ax2_groupSpecies_cum.set_ylabel("Species Counts", fontsize=18)
            ax2_groupSpecies_cum.legend([f"{taxon_group_name}"], fontsize=20)

            plt.tight_layout(rect=[0, 0, 1, 1])
            
            fig2_groupSpecies_cum.savefig(
                output_path_sac
                + f"mhhp_yearly_species_accumulation_curve_{taxon_group_name}.png"
            )

            
            # 3.6. Count all group occurrences per year using data0, not data1.
            data_yearly_groupOccur_counts = (
                data0.groupby("year")["occurrenceID"]
                .size()
                .to_frame(name=f"{taxon_group_name}")
            )

            # Align the observed-year counts to the full-year occurrence table.
            data_annual_occur_counts.loc[data_yearly_groupOccur_counts.index, f"{taxon_group_name}"] = (
                data_yearly_groupOccur_counts.loc[data_yearly_groupOccur_counts.index, f"{taxon_group_name}"].values
            )
            
            
            # A positive occurrence count marks a surveyed group for that year (0 | 1).
            data_annual_occur_boolean = data_annual_occur_counts > 0
            data_annual_occur_boolean = data_annual_occur_boolean.astype("int64")
            
            # Remove years with no surveyed groups.
            data_annual_occur_boolean["sum"] = data_annual_occur_boolean.sum(axis=1).values
            
            drop_index1 = list(
                data_annual_occur_boolean[data_annual_occur_boolean["sum"] == 0].index
            )
            data_yearly_occur_boolean = data_annual_occur_boolean.drop(drop_index1, inplace=False)

        else:
            print(f"Will not process this file: {content[file_id]}")

    return (
        data_species_ratio,
        data_annual_species_counts,
        data_annual_species_cumulative0,
        data_annual_species_increment0,
        data_annual_occur_counts,
        data_annual_occur_boolean,
        data_yearly_occur_boolean
    )




# %% 4. Export summary tables and yearly survey-target indicators.

def export_summary_tables(
    output_path_counts,
    output_path_sac,
    data_species_ratio,
    data_annual_species_counts,
    data_annual_species_cumulative0,
    data_annual_species_increment0,
    data_yearly_occur_boolean
):
    """Export the original summary CSVs and return data_annual_occur_boolean.

    Summary tables preserve their original Year index labels and NaN values.
    Survey-target indicators use all occurrence counts and remove years with
    no surveyed group, exactly as in the original.
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

def plot_annual_species_counts(data_annual_species_counts, output_path_counts, year_max):
    """Plot original yearly species counts and return the plotting table/colors.

    Only plotting data are filled with zero. Group order, colors, fonts, bar
    labels, filenames, and the original column-first six-panel layout are kept.
    """
    
    data_annual_counts_fig = data_annual_species_counts.copy()
    data_annual_counts_fig = data_annual_counts_fig.fillna(0).astype("int")
    ylabel_name = "Species Counts"

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

    # 5.1. Export all eight individual annual-count figures in the original order.
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

        
        fig0_annual_counts, axis0_annual_counts = plt.subplots(1, 1, dpi=300)
        
        
        bar0_annual_counts = axis0_annual_counts.bar(
            data_annual_counts_fig.index,
            data_annual_counts_fig[category1],
            color=color_category[category1],
        )

        # set the legend
        if category1 == "BenthicInvertebrate":
            category1 = "Benthic Invertebrate"

        bar0_annual_counts.set_label(category1)
        axis0_annual_counts.legend(prop={"size": 25})

        # Set the Y interval to integer.
        axis0_annual_counts.yaxis.set_major_locator(MaxNLocator(integer=True))
        # Set the fontsize of Y label
        axis0_annual_counts.tick_params(axis="y", labelsize=15)
        axis0_annual_counts.tick_params(axis="x", labelsize=15)

        axis0_annual_counts.set_xlabel("Year", fontsize=20)
        axis0_annual_counts.set_ylabel(ylabel_name, fontsize=20)
        plt.tight_layout()
        fig0_annual_counts.savefig(output_path_counts + f"mhhp_yearly_species_counts_{category1}.png")


    # 5.2. Fill the six-panel figure down each column in the original group order.
    fig_row_counts = 3
    


    
    fig1_groupSpecies_annual_counts, axis1_groupSpecies_annual_counts = plt.subplots(3, 2, dpi=300, figsize=(11.69, 8.27))
    turn = 0
    for category1 in [
        "Avian",
        "Fish",
        "Insect",
        "Cetacean",
        "BenthicInvertebrate",
        "Plant",
    ]:
        
        
        row1_panel = np.mod(turn, fig_row_counts)
        column1 = int(np.floor(turn / fig_row_counts))
        data_annual_counts_fig[category1] = data_annual_counts_fig[category1].astype(
            "Int64"
        )
        
        
        bar1_groupSpecies_annual_counts = axis1_groupSpecies_annual_counts[row1_panel, column1].bar(
            data_annual_counts_fig.index,
            data_annual_counts_fig[category1],
            color=color_category[category1],
        )

        # set the legend
        if category1 == "BenthicInvertebrate":
            category1 = "Benthic Invertebrate"
        bar1_groupSpecies_annual_counts.set_label(category1)
        axis1_groupSpecies_annual_counts[row1_panel, column1].legend(prop={"size": 25})

        # Set the Y interval to integer.
        axis1_groupSpecies_annual_counts[row1_panel, column1].yaxis.set_major_locator(MaxNLocator(integer=True))
        # Set the fontsize of Y label
        axis1_groupSpecies_annual_counts[row1_panel, column1].tick_params(axis="y", labelsize=20)
        axis1_groupSpecies_annual_counts[row1_panel, column1].set_xlabel("Year", fontsize=20)
        axis1_groupSpecies_annual_counts[row1_panel, column1].set_ylabel(ylabel_name, fontsize=20)

        axis1_groupSpecies_annual_counts[row1_panel, column1].set_xticks(range(1995, int(year_max + 1), 5))
        axis1_groupSpecies_annual_counts[row1_panel, column1].set_xticklabels(
            range(1995, int(year_max + 1), 5), fontsize=20
        )

        axis1_groupSpecies_annual_counts[row1_panel, column1].tick_params(axis="y", labelsize=15)

        turn = turn + 1

    plt.tight_layout()
    fig1_groupSpecies_annual_counts.savefig(output_path_counts + "mhhp_yearly_species_counts_6subplots.png")

    return data_annual_counts_fig, color_category, ylabel_name


# %% 6. Export the original combined accumulation curve for six groups.

def plot_combined_accumulation_curve(
    data_annual_species_increment0, color_category, output_path_sac, year_max
):
    """Plot increments filled with zero and accumulated over the full year index.

    The displayed six-group order and all figure styling are retained. Return
    data_species_cumulative_fig so the plotted values can be checked directly.
    """
    # For this combined figure, fill missing increments with zero before cumsum.
    # This retains the original distinction from the raw cumulative CSV.
    data_species_cumulative_fig = (
        data_annual_species_increment0.fillna(0).cumsum().astype("int")
    )
        
    
    fig2_combined_groupSpecies_cum, axis2_combined_groupSpecies_cum = plt.subplots(1, 1, dpi=300, figsize=(6, 4))
    for category2 in [
        "Avian",
        "Fish",
        "Insect",
        "Cetacean",
        "BenthicInvertebrate",
        "Plant",
    ]:


        (line2_groupSpecies,) = axis2_combined_groupSpecies_cum.plot(
            data_species_cumulative_fig.index,
            data_species_cumulative_fig[category2],
            color=color_category[category2],
            linewidth=2,
        )

        # set the legend
        if category2 == "BenthicInvertebrate":
            category2 = "Benthic Invertebrate"
        line2_groupSpecies.set_label(category2)

        axis2_combined_groupSpecies_cum.set_xlabel("Year", fontsize=15)
        axis2_combined_groupSpecies_cum.set_ylabel("Cumulative Species Counts", fontsize=15)

        axis2_combined_groupSpecies_cum.set_xticks(range(1995, int(year_max + 1), 5))
        axis2_combined_groupSpecies_cum.set_xticklabels(range(1995, int(year_max + 1), 5), fontsize=15)

        axis2_combined_groupSpecies_cum.tick_params(axis="y", labelsize=15)

    axis2_combined_groupSpecies_cum.legend(frameon=False, prop={"size": 10})
    plt.tight_layout()
    fig2_combined_groupSpecies_cum.savefig(
        output_path_sac + "mhhp_yearly_species_accumulation_curves_6_groups_raw.png"
    )

    return data_species_cumulative_fig


# %% 7. Run the same tasks in their original order.
def main(IPT_version='1.37', year_max = 2025,  year_min = 1994 ):
    """Run identifier checks, annual calculations, CSV exports, and figures."""
    
    # 1. set the paths
    root_path, input_path, output_path, output_path_counts, output_path_sac = (
        setup_paths()
    )
    
    # 2. check data
    content, data_combined_occur = check_data_integrity(input_path, IPT_version)
    
    # 3. group statistics
    (
        data_species_ratio,
        data_annual_species_counts,
        data_annual_species_cumulative0,
        data_annual_species_increment0,
        data_annual_occur_counts,
        data_annual_occur_boolean,
        data_yearly_occur_boolean
    ) = calculate_group_statistics(
        input_path, output_path_sac, content, data_combined_occur, year_min, year_max
    )

    # 4. export tables
    export_tables_success = export_summary_tables(
    output_path_counts,
    output_path_sac,
    data_species_ratio,
    data_annual_species_counts,
    data_annual_species_cumulative0,
    data_annual_species_increment0,
    data_yearly_occur_boolean
    )
    print(export_tables_success)
    
    data_annual_counts_fig, color_category, ylabel_name = plot_annual_species_counts(
        data_annual_species_counts, output_path_counts, year_max
    )
    data_species_cumulative_fig = plot_combined_accumulation_curve(
        data_annual_species_increment0, color_category, output_path_sac, year_max
    )


if __name__ == "__main__":
    main('1.37')
    
    
