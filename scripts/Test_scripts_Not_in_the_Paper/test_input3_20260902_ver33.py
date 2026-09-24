# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:40:59 2026

@author: cetae
"""


import os
from pathlib import Path
import matplotlib
import pandas as pd
import numpy as np
import json

import math
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap



# Returns the absolute directory of the active script and parent directory
try:
    script_dir = os.path.abspath(__file__)
    scipt_folder = os.path.abspath(os.path.join(script_dir ,'..'))
except: # Jupyter 
    scipt_folder = os.getcwd()
    

#parent directory
root_path = os.path.abspath(os.path.join(scipt_folder, '..'))
print(f'root_path is `{root_path}`')


#example
#root_path = 'C:/Users/cetae/GBIF_IPT/Survey_Data_Mianhua_and_Huaping_Islets_Wildlife_Refuge'


input_path = os.path.join(root_path,'mhhp_inputs/')
output_path = os.path.join(root_path, 'mhhp_outputs/')



# checklist_taxon
df_taxon = pd.read_csv(os.path.join(input_path, '0_taxon_2025_20260713_1600.csv'), sep=',', low_memory=False)
df_taxon = df_taxon.sort_values(by=['taxonID'], ascending =True)


# mesurement
# open the measurement file
df_measure = pd.read_csv(os.path.join(input_path, 'measurement_Fish.csv'), sep='\t', low_memory=False)
df_measure = df_measure.sort_values(by=['occurrenceID'], ascending =True)



df0 = pd.read_csv(os.path.join(input_path, 'v1.35/9_gbif_KL_occurrence_till_20251230_all_20260922_1300_NoMapping.tsv'), sep='\t', low_memory=False)
df0 = df0.sort_values(by=['occurrenceID'], ascending =True)

df0['coordinateUncertaintyInMeters'] = df0['coordinateUncertaintyInMeters'].astype('float')


len(df0.columns)

column_names = ['basisOfRecord', 'dynamicProperties', 'occurrenceID', 'recordedBy',
       'individualCount', 'organismQuantity', 'organismQuantityType',
       'reproductiveCondition', 'behavior', 'georeferenceVerificationStatus',
       'associatedReferences', 'occurrenceRemarks', 'eventDate', 'eventTime',
       'year', 'month', 'day', 'samplingProtocol', 'continent', 'country',
       'countryCode', 'locality', 'minimumDepthInMeters',
       'maximumDepthInMeters', 'decimalLatitude', 'decimalLongitude',
       'geodeticDatum', 'coordinateUncertaintyInMeters', 'coordinatePrecision',
       'taxonID', 'taxonConceptID', 'taxonomicStatus', 'scientificNameID',
       'scientificName', 'verbatimIdentification', 'taxonRank', 'kingdom',
       'vernacularName', 'taxonRemarks', 'identificationQualifier']




#%%
# =============================================================================
# 
# df0['verbatimIdentification_new']= df0['verbatimIdentification']
# 
# 
# a1= df0.groupby(['verbatimIdentification_new']).size()
# a2= df0.groupby(['scientificName']).size()
# a3= df0.groupby(['taxonID']).size()
# 
# 
# # III. 確認'verbatimIdentification_new'沒有多個'vernacularName'
# # 1. 第一步：找出數量大於 1 的異常鑑定名單
# multiple_vernacular_IN = df0.groupby(by=['verbatimIdentification_new'])['vernacularName'].nunique().reset_index(name='count_ID').sort_values(by='count_ID', ascending=False)
# multiple_vernacular_IN_df = multiple_vernacular_IN.loc[multiple_vernacular_IN['count_ID']>1,:]
# 
# # 2. 【效能提升】使用 .isin() 瞬間濾出有問題的原始資料列，取代原本的 for 迴圈
# bad_ident = multiple_vernacular_IN_df['verbatimIdentification_new']
# df_error_IN_ver = df0[df0['verbatimIdentification_new'].isin(bad_ident)]
# 
# # 3. 【關鍵視覺化】把同一個學名對應到的「所有不同的 taxonID」打包成一個列表！
# df_error_goden_IN_vn = df_error_IN_ver.groupby('verbatimIdentification_new')['vernacularName'].unique().reset_index(name='conflicting_vernacularName')
# df_error_goden_IN_vn['conflicting_vernacularName'] = df_error_goden_IN_vn['conflicting_vernacularName'].apply(list)
# df_error_goden_IN_vn['count_VN'] = df_error_goden_IN_vn['conflicting_vernacularName'].apply(len)
# df_error_goden_IN_vn = df_error_goden_IN_vn.sort_values(by='verbatimIdentification_new')
# 
# 
# 
# 
# # I. 確認'verbatimIdentification_new'沒有多個'taxonID'
# # 1. 第一步：找出數量大於 1 的異常鑑定名單
# multiple_taxonID_IN = df0.groupby(by=['verbatimIdentification_new'])['taxonID'].nunique().reset_index(name='count_ID').sort_values(by='count_ID', ascending=False)
# multiple_taxonID_IN_df = multiple_taxonID_IN.loc[multiple_taxonID_IN['count_ID']>1,:]
# 
# # 2. 【效能提升】使用 .isin() 瞬間濾出有問題的原始資料列，取代原本的 for 迴圈
# bad_identifications = multiple_taxonID_IN_df['verbatimIdentification_new']
# df_error_IN = df0[df0['verbatimIdentification_new'].isin(bad_identifications)]
# 
# # 3. 【關鍵視覺化】把同一個學名對應到的「所有不同的 taxonID」打包成一個列表！
# df_error_goden_IN = df_error_IN.groupby('verbatimIdentification_new')['taxonID'].unique().reset_index(name='conflicting_taxonIDs')
# df_error_goden_IN['conflicting_taxonIDs'] = df_error_goden_IN['conflicting_taxonIDs'].apply(list)
# df_error_goden_IN['count_id'] = df_error_goden_IN['conflicting_taxonIDs'].apply(len)
# df_error_goden_IN = df_error_goden_IN.sort_values(by='verbatimIdentification_new')
# 
# # filter_IN_mulipleID = [Iden in multiple_taxonID_IN_df['verbatimIdentification_new'].values for Iden in df0['verbatimIdentification_new'].values]
# # df0_IN_multipleID = df0.loc[filter_IN_mulipleID, 'taxonID'].sort_values().unique()
# 
# 
# 
# # II. 確認'scientificName'沒有多個'taxonID'
# # 1. 第一步：找出數量大於 1 的異常鑑定名單
# multiple_taxonID_SN1 = df0.groupby(by=['scientificName'])['taxonID'].nunique().rename('count_ID').sort_values(ascending=False)
# multiple_taxonID_SN2 = df0.groupby(by=['scientificName'])['taxonID'].nunique().reset_index(name='count_ID').sort_values(by='count_ID', ascending=False)
# multiple_taxonID_SN2_df = multiple_taxonID_SN2.loc[multiple_taxonID_SN2['count_ID']>1,:]
# 
# # 2. 【效能提升】使用 .isin() 瞬間濾出有問題的原始資料列，取代原本的 for 迴圈
# bad_id_SN2 = multiple_taxonID_SN2_df['scientificName']
# df_error_SN = df0[df0['scientificName'].isin(bad_id_SN2)]
# 
# 
# # 3. 【關鍵視覺化】把同一個學名對應到的「所有不同的 taxonID」打包成一個列表！
# df_error_golden_SN = df_error_SN.groupby(by='scientificName')['taxonID'].unique().reset_index(name='conflicting_taxonIDs')
# df_error_golden_SN['conflicting_taxonIDs'] = df_error_golden_SN['conflicting_taxonIDs'].apply(list)
# df_error_golden_SN['count_id'] = df_error_golden_SN['conflicting_taxonIDs'].apply(len)
# df_error_golden_SN= df_error_golden_SN.sort_values(by='scientificName')
# 
# conflict_summary = df_error_golden_SN.sort_values(by='count_id', ascending=False).reset_index(drop=True)
# 
# print(conflict_summary)
# 
# 
# df0['verbatimIdentification']= df0['verbatimIdentification_new']
# 
# 
# =============================================================================


#%%



filter_has_value =  ~(df0['dynamicProperties'].isna())

#鳥類
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('飛行方向','azimuth')

df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('覆蓋度','coverage')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('社會性','sociability')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('1%','0.01')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('株',' plants')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('零星分散','scattered in isolated clusters')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('普通分散或小塊群聚','scattered in groups or small patches')
df0.loc[:,'dynamicProperties'] = df0.loc[:,'dynamicProperties'].str.replace('全面分布','extensive plantings over whole areas')




filter_chinese = df0.loc[:,'dynamicProperties'].str.contains(r"[\u4e00-\u9fa5]", na=False)
a1=df0.loc[filter_chinese]


filter_chinese = df0.loc[:,'dynamicProperties'].str.contains(r"%", na=False)
a1=df0.loc[filter_chinese]




#%%


#鳥類
filter_avian = df0['occurrenceID'].str.contains('Avian')
filter_avian_azimuth = ( (filter_avian) & (~df0['dynamicProperties'].isna()) )
df0_avian_azimuth = df0[filter_avian_azimuth]

df0.loc[filter_avian_azimuth,'dynamicProperties'] = df0.loc[filter_avian_azimuth,'dynamicProperties'].str.replace('飛行方向','azimuth')
df0['dynamicProperties'] = df0['dynamicProperties'].replace("'azimuth': 'X'","'azimuth': 'NA'")

# 中文
# r"[\u4e00-\u9fa5]"



text1 = '{heightInMeters:1, distanceInMeters:300, azimuth:S, angleWithShip:3}'
text1 = '{覆蓋度: null, 社會性: null}'

#更改飛行方向的key
def parse_dict(text1): 
    if pd.isna(text1):
        return np.nan
    text1 = text1.strip()
    text1 = text1.strip('{} ')
    
    result= {}
    for item1 in text1.split(','):
        key1, value1 = item1.strip().split(':',1)
        if value1.strip()=='null':
            continue
        result[key1.strip()] = value1.strip()
        
    if len(result)>0:
        return result
    else:
        np.nan

for i in range(len(df0['dynamicProperties'])):
    parse_dict(df0['dynamicProperties'][i])
    
    
#%%    
    
df0['dynamicProperties2'] = df0['dynamicProperties'].apply(parse_dict)

# 如果您是想提取 'distanceInMeters' (距離)：
df0['distanceInMeters'] = df0['dynamicProperties2'].str.get('distanceInMeters')
df0['distanceInMeters'] = df0['distanceInMeters'].str.replace('NA', '')
df0['distanceInMeters'] = df0['distanceInMeters'].str.replace('>', '')
df0['distanceInMeters'] = df0['distanceInMeters'].str.replace('<', '')
df0['distanceInMeters'] = df0['distanceInMeters'].str.replace('50-100', '100')



# 1. 先把 'distanceInMeters' 的值全部提取出來
temp_distance = df0['dynamicProperties2'].str.get('distanceInMeters')

# 2. 進行「純數字」的篩選測試
# 只要裡面混了英文字母或奇怪符號，都會被 errors='coerce' 變成 NaN
filter_avian = df0['taxonID'].str.contains('Avian', na=False)
is_number_mask = ((pd.to_numeric(temp_distance, errors='coerce').notna()) & (filter_avian))

# 3. 透過遮罩 (mask)，精準地把「確實是阿拉伯數字」的值
# 填入 df0['coordinateUncertaintyInMeters'] 中！
df0.loc[is_number_mask, 'coordinateUncertaintyInMeters'] = temp_distance[is_number_mask]


# 去除一公尺的radius
df0['coordinateUncertaintyInMeters'] =  df0['coordinateUncertaintyInMeters'].astype('int64')
filter_wrong_radius = df0['coordinateUncertaintyInMeters'] <= 1
df0.loc[((filter_avian)&(filter_wrong_radius)),'coordinateUncertaintyInMeters' ] = 300



df0.loc[((filter_avian)&(filter_wrong_radius)),'coordinateUncertaintyInMeters'].unique()



df0.loc[((filter_avian)),'coordinateUncertaintyInMeters'].unique()


#  df0.loc[is_number_mask, 'coordinateUncertaintyInMeters'] = temp_distance[is_number_mask]



# df0.loc[filter_dynamic, 'taxonID'].str[0:8].unique()
# {覆蓋度: null, 社會性: null} : 37
#  {mother-calf pairs:null} : 85


#%% 存檔喔


df0['dynamicProperties'] = df0['dynamicProperties2']
df0 = df0.drop(['dynamicProperties2','distanceInMeters'], axis=1)


# 1. 處理需要變成「整數」的欄位 (例如：深度、座標誤差半徑)
# 注意：要用大寫的 'Int64'，這樣如果欄位裡面有空值(NaN)才不會報錯
int_columns = ['coordinateUncertaintyInMeters', 'maximumDepthInMeters',
               'minimumDepthInMeters', 'individualCount','year', 'month', 'day', 'scientificNameID']
for col in int_columns:
    if col in df0.columns:
        df0[col] = df0[col].astype('Int64')


# 3. 處理需要「小數點後 5 位」的欄位 (例如：經緯度)
float_5_columns = ['decimalLatitude', 'decimalLongitude', 'coordinatePrecision']
for col in float_5_columns:
    if col in df0.columns:
        df0[col] = df0[col].round(5)


df0.to_csv(os.path.join(input_path,
          '9_gbif_KL_occurrence_till_20251230_all_20260923_1731_NoMapping.csv'),
            encoding='utf_8_sig',
            index= False)



print(len(df0.columns))

# .*Fish.*
# .*Benthic.*
