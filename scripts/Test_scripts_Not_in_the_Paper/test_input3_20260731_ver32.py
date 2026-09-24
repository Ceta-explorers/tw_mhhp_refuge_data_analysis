# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:41:06 2026

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


# 鳥類目視最遠距離: 300

# 鳥類: 300 
# 鳥類: 1000

# 鯨+ (望遠鏡): 4000 







#%%

# checklist_taxon
df_taxon = pd.read_csv(os.path.join(input_path, '0_taxon_2025_20260713_1600.csv'), sep=',', low_memory=False)
df_taxon = df_taxon.sort_values(by=['taxonID'], ascending =True)




# mesurement
# open the measurement file
df_measure = pd.read_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260729_1500_with_days.csv'), sep=',', low_memory=False)
df_measure = df_measure.sort_values(by=['occurrenceID'], ascending =True)


# Use a date that conforms to ISO 8601-1:2019.
filter_measure_year = df_measure['year'].isna()
print(df_measure[filter_measure_year])


df_measure['year']= df_measure['year'].astype('str')
df_measure['month']= df_measure['month'].fillna(0)
df_measure['month']= df_measure['month'].astype('Int64')
df_measure['month']= df_measure['month'].astype('str').str.zfill(2)


df_measure['day']= df_measure['day'].fillna(0)
df_measure['day'] = df_measure['day'].astype('Int64')
df_measure['day']= df_measure['day'].astype('str').str.zfill(2)


# set 'verbatimEventDate', set 'eventDate'
df_measure['verbatimEventDate']= df_measure['year'] + '-' + df_measure['month'] + '-' + df_measure['day']
df_measure['measurementDeterminedDate']= df_measure['year'] + '-' + df_measure['month'] + '-' + df_measure['day']
df_measure['measurementDeterminedDate']= df_measure['measurementDeterminedDate'].str.replace('-00-00','')



#型態變回整數
df_measure['year'] = df_measure['year'].astype('Int64')
df_measure['month']= df_measure['month'].astype('Int64')
df_measure['day'] = df_measure['day'].astype('Int64')


#Replace zero in month and day
df_measure['month']= df_measure['month'].replace(0, np.nan)
df_measure['day']= df_measure['day'].replace(0, np.nan)


df_measure['occurrenceID'] =  df_measure['occurrenceID'].str.strip()

df_measure.dtypes
df_measure.columns




#核對occurrenceID
# Open occurrence_file
df_occur1 = pd.read_csv(os.path.join(input_path,
                                     '9_gbif_KL_occurrence_till_20251230_all_20260731_1700_API_name.csv'),
                        sep=',', low_memory=False, keep_default_na= True)

df_occur1['occurrence_newID'] = df_occur1['occurrence_newID'].str.strip()
df_occur1['occurrenceID'] = df_occur1['occurrence_newID']
df_occur1.columns

occurID_measure = set(df_measure['occurrenceID'])
occurID_occur= set(df_occur1['occurrenceID'])

#occurID_measure 需要被包含在 occurID_occur
check_occurID1 = occurID_measure - occurID_occur #有數值即為錯誤
check_occurID2 =  occurID_occur - occurID_measure #len()理應>0




#Save1
filter_chinese_measure = df_measure['occurrenceID'].str.contains(r"[\u4e00-\u9fa5]")
df_measure[filter_chinese_measure]



# df_measure.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260902_1500_with_days.csv'), encoding='utf_8_sig', index= False)

# df_measure_last = df_measure.copy().drop(['scientificName', 'taxonRank', 'vernacularName',
#                               'decimalLongitude', 'decimalLatitude',
#                               'year','month', 'day',
#                               'taxonID','verbatimEventDate','occurrenceID_old'], axis=1)


#df_measure_last.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260729_1500_WO_days.csv'), encoding='utf_8_sig', index= False)



['id','measurementID','occurrenceID',
 'measurementType','measurementValue','measurementUnit',
 'measurementDeterminedDate','measurementDeterminedBy','measurementRemarks']



df0 =  df_occur1.copy()

#%% 開始整理occurrence Table

df0 = df0.sort_values(by=['verbatimEventDate'], ascending =True)


# Use a date that conforms to ISO 8601-1:2019.
df0['year']= df0['year'].astype('str')


df0['month']=df0['month'].fillna(0)
df0['month']= df0['month'].astype('Int64')
df0['month']= df0['month'].astype('str').str.zfill(2)


df0['day']= df0['day'].fillna(0)
df0['day'] = df0['day'].astype('Int64')
df0['day']= df0['day'].astype('str').str.zfill(2)


# set 'verbatimEventDate', set 'eventDate'
df0['verbatimEventDate']= df0['year'] + '-' + df0['month'] + '-' + df0['day']
df0['eventDate']= df0['year'] + '-' + df0['month'] + '-' + df0['day']
df0['eventDate']=df0['eventDate'].str.replace('-00-00','')



#型態變回整數
df0['year'] = df0['year'].astype('Int64')
df0['month']= df0['month'].astype('Int64')
df0['day'] = df0['day'].astype('Int64')


#replace zero in month and day
df0['month']= df0['month'].replace(0, np.nan)
df0['day']= df0['day'].replace(0, np.nan)


df0['individualCount'] = df0['individualCount'].astype('Int64')
# scientificName
df0['scientificName']=df0['scientificName'].str.strip()

#%% 
# 1. 定義一個解析這種特殊格式的函數
def parse_custom_dict(text):
    # 遇到空值 (NaN) 直接回傳空字典
    if pd.isna(text) or not str(text).strip():
        return np.nan
    
    # 移除頭尾的 {} 與空白
    clean_text = str(text).strip('{} ')
    if not clean_text:
        return np.nan
    
    result = {}
    # 用逗號切開每一組鍵值對
    for item in clean_text.split(','):
        if ':' in item:
            # 用冒號切分為 key 和 value，並清除多餘空白
            k, v = item.split(':', 1)
            result[k.strip()] = v.strip()
            
    return str(result)

# 2. 假設您的資料表叫做 df，直接套用到整個 'dynamicProperties' 欄位
df0['parsed_properties'] = df0['dynamicProperties'].apply(parse_custom_dict)
df0_property = df0.loc[(~df0['parsed_properties'].isna()),'parsed_properties']


#%% 

# .*Avian.*

df0['dynamicProperties3'] = df0['dynamicProperties2'].str.strip()
df0_property = df0.loc[(~df0['dynamicProperties2'].isna()),'dynamicProperties2']



#鳥類
filter_avian = df0['occurrenceID'].str.contains('Avian')
filter_avian_azimuth= ( (filter_avian) & (~df0['parsed_properties'].isna()) )

#更改飛行方向的key
df0['dynamicProperties']
text1 = '{heightInMeters:1, distanceInMeters:300, azimuth:S, angleWithShip:3}'

def parse_dict(text1): 
    if pd.isna(text1):
        return np.nan
    text1 = text1.strip()
    text1 = text1.strip('{} ')
    
    result= {}
    for item1 in text1.split(','):
        key1, value1 = item1.strip().split(':',1)
        result[key1.strip()] = value1.strip()
    return result

for i in range(len(df0['dynamicProperties'])):
    parse_dict(df0['dynamicProperties'][i])
    
df0['dynamicProperties2'] = df0['dynamicProperties'].apply(parse_dict)    



a1 = df0.loc[filter_avian_azimuth,'parsed_properties']





















#%%

#%% Save File


df0.to_csv(os.path.join(input_path,
            '9_gbif_KL_occurrence_till_20251230_all_20260902_1700_API_name.csv'),
            encoding='utf_8_sig',
            index= False)



'''
# remove columns :['lifeStage', 'associatedMedia']
# add columns :['id', 'kingdom', 'countryCode', 'verbatimIdentification']

'''





df0 = df0.drop(['Api_name_v2','Api_name_v1', 'higherClassification', 'rank', 'status','confidence', 'matchType',
                'phylum', 'class', 'order', 'family','genus', 'species'], axis=1)

df0 = df0.drop(['lifeStage', 'associatedMedia'], axis=1)
df0 = df0.drop(['PrecisionLong','PrecisionLat',
                'taxonGroup','taxonGroup_num',
                'method','occurrence_newID'], axis=1)

if 'id' in  df0.columns:
    df0 = df0.drop(['id'], axis=1)
    



df0.to_csv(os.path.join(input_path,
          '9_gbif_KL_occurrence_till_20251230_all_20260902_1700_WO_API_occurrenceID.csv'),
            encoding='utf_8_sig',
            index= False)

