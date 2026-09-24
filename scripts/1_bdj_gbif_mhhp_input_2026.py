# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 17:54:05 2026

@author: cetae
"""
# import Standard Library
import io
import os
import zipfile
from datetime import datetime

# import Third-party Packages
import pandas as pd
import requests





# =============================================================================
# III. Download Dataset to folder "mhhp_inputs/"
# =============================================================================

# 1. set url
# Returns the absolute directory of the active script and parent directory
try:
    script_dir = os.path.abspath(__file__)
    scipt_folder = os.path.abspath(os.path.join(script_dir ,'..'))
except: # Jupyter 
    scipt_folder = os.getcwd()
    

#parent directory
root_path = os.path.abspath(os.path.join(scipt_folder, '..'))
print(f'root_path is `{root_path}`')

input_path = os.path.join(root_path,'mhhp_inputs/')



download_url = 'https://ipt.taibif.tw/archive.do?r=cetaexplorers_mianhua_huaping_islets&v=1.36'
print("Downloading dataset...")
response = requests.get(download_url)
print(response.status_code)



#%%
# Successfully Download (Status Code 200)
target_file = 'occurrence.txt'
# ['meta.xml', 'extendedmeasurementorfact.txt', 'eml.xml', 'occurrence.txt']

if response.status_code == 200:

    # 2. Read File in RAM
    with zipfile.ZipFile(io.BytesIO(response.content)) as z1:
        print(f' Contain Files: {z1.namelist()}')
        
        # 3. Load as Pandas DataFrame
        with z1.open('occurrence.txt') as f1:
            df0_whole = pd.read_csv(f1, sep='\t', low_memory = False)
            print(f"\n Load {target_file}, Total Rows：{len(df0_whole)}")
            
            # Int64 Types
            int_columns = ['coordinateUncertaintyInMeters', 'maximumDepthInMeters',
                           'minimumDepthInMeters', 'individualCount','year', 'month', 'day', 'scientificNameID']
            for col in int_columns:
                if col in df0_whole.columns:
                    df0_whole[col] = df0_whole[col].astype('Int64')


            # Float Types
            float_5_columns = ['decimalLatitude', 'decimalLongitude', 'coordinatePrecision']
            for col in float_5_columns:
                if col in df0_whole.columns:
                    df0_whole[col] = df0_whole[col].round(5)
                    
        # 3. Load as Pandas DataFrame
        with z1.open('extendedmeasurementorfact.txt') as f2:
            df0_measure = pd.read_csv(f2, sep='\t', low_memory = False)
            df0_measure.to_csv(os.path.join(input_path,  'measurement_Fish.csv'), encoding ='utf_8_sig', index=False )
                     
        
    

#%%


taxonomic_groups = [
 'Algae',
 'Avian',
 'BenthicInvertebrate',
 'Cetacean',
 'Fish',
 'Insect',
 'Plant',
 'Spider',
 'Reptile'
 ]


count_record = 0
for theTaxonGroup in taxonomic_groups:
    filter_taxonomic = df0_whole['taxonID'].str.contains(theTaxonGroup, na=False)
    df0_group1 = df0_whole.loc[filter_taxonomic,:]
    df0_group1.to_csv(os.path.join(input_path,  f'occur_{theTaxonGroup}.csv'), encoding ='utf_8_sig', index=False )
    count_record = count_record+len(df0_group1)


# print(count_record)
if count_record == len(df0_whole):
    print(' The dataset has successfully been split into multiple taxonomic group files.')
else:
    print(' The dataset has failed to be split into multiple taxonomic group files.')
    # Check for missing records 
    pattern = '|'.join(taxonomic_groups)
    df_missing = df0_whole[~df0_whole['taxonID'].str.contains(pattern, na=False)]



#%%


# Check for Taxon Counts, Taxon Consistent, column-mapping
taxon_all_counts = {
'scientificName': len(df0_whole['scientificName'].unique()),
'scientificNameID': len(df0_whole['scientificNameID'].unique()),
'taxonConceptID': len(df0_whole['taxonConceptID'].unique()),
'taxonID': len(df0_whole['taxonID'].unique()),
'verbatimIdentification': len(df0_whole['verbatimIdentification'].unique()),
'vernacularName': len(df0_whole['vernacularName'].unique())
 }
print(f'Taxon, Count: {taxon_all_counts}')





df_taxon1 = df0_whole[['taxonID', 'scientificNameID', 'taxonConceptID','taxonomicStatus', 'kingdom' ,'scientificName','verbatimIdentification','taxonRank', 'vernacularName','taxonRemarks','identificationQualifier']].drop_duplicates()
print(f"Length in df_taxon1 :{len(df_taxon1)}")
df_taxon1.to_csv(os.path.join(input_path,  f"0_taxon_till_20251230_ver{datetime.now().strftime('%Y%m%d')}.csv"), encoding='utf_8_sig', index=False)


#a1=df_taxon1[df_taxon1.duplicated(subset=['taxonID'], keep=False)]

#1.確認'taxonID'沒有對應多個'taxonRemarks' (1對多)
multiple_remarks = df_taxon1.groupby(by='taxonID')['taxonRemarks'].nunique(dropna=False).reset_index(name='count').sort_values(by='count', ascending= False)
multi_remarks_one_taxonID = multiple_remarks.loc[multiple_remarks['count']>1,'taxonID'].values
df_taxon1_wrong1 = df_taxon1.loc[df_taxon1['taxonID'].isin(multi_remarks_one_taxonID),:].sort_values(by='taxonID')
#df0_whole.loc[df0_whole['taxonID']=='KL_BenthicInvertebrate_0000044','taxonRemarks']= '瘤突斜紋蟹 | 礁扁 | 白底仔'
 

#2.確認'vernacularName'沒有對應多個'taxonID' (1對多)
multiple_ID =df_taxon1.groupby(by='vernacularName')['taxonID'].nunique(dropna=False).reset_index(name='count').sort_values(by='count',ascending=False)
multi_ID_one_vernacular = multiple_ID.loc[multiple_ID['count']>1,'vernacularName'].values
df_taxon1_wrong2= df_taxon1[df_taxon1['vernacularName'].isin(multi_ID_one_vernacular)].sort_values(by='vernacularName', ascending= True)
# "Identified to subspecies level based on the known local distribution."


#3.確認'taxonID'沒有對應多個'vernacularName' (1對多)
multiple_vernacular = df_taxon1.groupby(by='taxonID')['vernacularName'].nunique(dropna=False).reset_index(name='count').sort_values(by='count',ascending=False)
multi_vernacular_one_taxonID = multiple_vernacular.loc[multiple_vernacular['count']>1,'taxonID'].values
df_taxon1_wrong3=df_taxon1[df_taxon1['taxonID'].isin(multi_vernacular_one_taxonID)]




