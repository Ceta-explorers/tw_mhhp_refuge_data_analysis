# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 16:09:30 2026

@author: cetae
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 17:19:59 2026

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





#%%

# checklist_taxon
df_taxon= pd.read_csv(os.path.join(input_path, '0_taxon_2025_20260713_1600.csv'), sep=',', low_memory=False)
df_taxon = df_taxon.sort_values(by=['taxonID'], ascending =True)




# mesurement
# open the measurement file

df_measure = pd.read_csv(os.path.join(input_path, '5_fish_zmeasurement_2025.csv'), sep=',', low_memory=False)





df_measure = df_measure.sort_values(by=['occurrenceID'], ascending =True)

df_measure['measurementRemarks'] = df_measure['scientificName']




# Use a date that conforms to ISO 8601-1:2019.
filter_measure_year= df_measure['year'].isna()
df_measure[filter_measure_year]


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
df_measure['measurementDeterminedDate']=df_measure['measurementDeterminedDate'].str.replace('-00-00','')



#型態變回整數
df_measure['year'] = df_measure['year'].astype('Int64')
df_measure['month']= df_measure['month'].astype('Int64')
df_measure['day'] = df_measure['day'].astype('Int64')


#replace zero in month and day
df_measure['month']= df_measure['month'].replace(0, np.nan)
df_measure['day']= df_measure['day'].replace(0, np.nan)






df_measure['occurrenceID'] =  df_measure['occurrenceID'].str.strip()
df_measure['occurrenceID'] = df_measure['occurrenceID'].str.replace('Censuses','Census')

#開始計算ID的修正
df_measure['occurrenceID_old'] = df_measure['occurrenceID'] 


filter_BRUV = df_measure['occurrenceID'].str.contains('BRUV', na=False)
m1= df_measure[filter_BRUV]


# 刪掉120其他調查的資料 (BRUV+ Roving on 2022-06-04)
filter_value = df_measure['measurementValue'].isna()
df_measure = df_measure.drop(df_measure[filter_value].index)


#更改ID 與 方法學
filter_roving = df_measure['occurrenceID'].str.contains('Roving', na=False)
df_wrong_label_measure = df_measure[filter_roving]

#待做: occur table: 'occurrenceID', "samplingProtocol"




'.*BRUV.*'
'.*Roving.*'




df_measure.dtypes
df_measure.columns

['measurementID', 'taxonID', 'occurrenceID', 'measurementDeterminedDate',
       'scientificName', 'taxonRank', 'vernacularName',
       'measurementDeterminedBy', 'measurementType', 'measurementValue',
       'measurementUnit', 'decimalLongitude', 'decimalLatitude', 'year',
       'month', 'day']


{'measurementID':1,
 'id':1,
 'occurrenceID':1,
 'measurementDeterminedDate':1,
       'measurementDeterminedBy':1,
       'measurementType':1,
       'measurementValue':1,
       'measurementUnit':1,
       'measurementRemarks':1,


       'scientificName':0,
       'taxonRank':0,
       'vernacularName':0,
       'decimalLongitude':0,
       'decimalLatitude':0,
       'year':0,
       'month':0,
       'day':0,
       'taxonID':0,
       'verbatimEventDate':0
       }


'id	measurementID	occurrenceID	measurementType	measurementValue	measurementUnit	measurementDeterminedDate	measurementDeterminedBy, measurementRemarks'








# open the occurrence file
#df_occur1 = pd.read_csv(os.path.join(input_path, '9-gbif-KL_occurrence_till_20251230_all_20260717_ver28.txt'), sep='\t', low_memory=False)
df_occur1 = pd.read_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260715_1700_API_name.csv'),
                        sep=',', low_memory=False, keep_default_na= True)

df_occur1['occurrenceID']=df_occur1['occurrenceID'].str.strip()


#找出對應的錯誤ID in Occur Table
filter_wrong_label_occur = df_occur1['occurrenceID'].isin(df_measure.loc[filter_roving, 'occurrenceID'].values)




#校正錯誤ID in Occur Table
df_occur1.loc[filter_wrong_label_occur, 'occurrenceID'] = df_occur1.loc[filter_wrong_label_occur, 'occurrenceID'].str.replace("_Fish_Roving Diver Method_","_Fish_Underwater Visual Census_")
df_occur1.loc[filter_wrong_label_occur,  "samplingProtocol"]= df_occur1.loc[filter_wrong_label_occur,  "samplingProtocol"].str.replace("Roving Diver Method","'Underwater Visual Census Line Transect'")



#校正錯誤ID in measure Table
df_measure.loc[filter_roving, 'occurrenceID'] = df_measure.loc[filter_roving, 'occurrenceID'].str.replace("_Fish_Roving Diver Method_","_Fish_Underwater Visual Census_")


df_measure['occurrenceID'] = df_measure['occurrenceID'].str.replace("潛水觀察","Underwater Visual Census")
df_occur1['occurrenceID'] =df_occur1['occurrenceID'].str.replace("潛水觀察","Underwater Visual Census")




occurID_measure = set(df_measure['occurrenceID'])
occurID_occur= set(df_occur1['occurrenceID'])

check_occurID1 = occurID_measure - occurID_occur
check_occurID2 =  occurID_occur - occurID_measure 


filter_chinese_measure = df_measure['occurrenceID'].str.contains(r"[\u4e00-\u9fa5]")






#Save1
df_measure.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260729_1500_with_days.csv'), encoding='utf_8_sig', index= False)

df_measure_last = df_measure.copy().drop(['scientificName', 'taxonRank', 'vernacularName',
                              'decimalLongitude', 'decimalLatitude', 'year',
                              'month', 'day',
                              'taxonID','verbatimEventDate','occurrenceID_old'], axis=1)


df_measure_last.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260729_1500_WO_days.csv'), encoding='utf_8_sig', index= False)




#Save_changed_ID
df_measure_occurID_all = df_measure.loc[:,['occurrenceID_old', 'occurrenceID']]
filter_measure_tochange = df_measure['occurrenceID_old'] != df_measure['occurrenceID']
df_measure_occurID_change = df_measure_occurID_all[filter_measure_tochange] 

df_measure_occurID_change.columns = ['occurrenceID', 'occurrence_newID']
df_measure_occurID_change.to_csv(os.path.join(input_path,
            '9_gbif_KL_occurrenceID_change_20260729.csv'),
            encoding='utf_8_sig',
            index= False,
            header= False)



df0 =  df_occur1.copy()





len(df_measure_occurID_change)
#1557

# len(df0_IDchange_list)
# #12667

# len(df_measure_occurID_change) +len(df0_IDchange_list)
# #14224


#%%



#read data  and compare columns
#df0 = pd.read_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260715_1700_API_name.csv'), sep=',', low_memory=False)
#df0 = pd.read_csv(os.path.join(input_path, '9-gbif-KL-occurrence-till-20251230_all_20260717_ver28.txt'), sep='\t', low_memory=False)



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



# recordedBy
df0['recordedBy'] = df0['recordedBy'].str.replace('研海生態顧問股份有限公司', '研海生態顧問股份有限公司 (Ceta explorers Company Limited)')
df0['recordedBy'] = df0['recordedBy'].str.replace('社團法人基隆市野鳥學會', '社團法人基隆市野鳥學會 (Wild Bird Society of Keelung)')
df0['recordedBy'] = df0['recordedBy'].str.replace('國立臺灣海洋大學', '國立臺灣海洋大學 (National Taiwan Ocean University)')
df0['recordedBy'] = df0['recordedBy'].str.replace('中華民國珊瑚礁學會', '臺灣珊瑚礁學會 (Taiwanese Coral Reef Society)')
df0['recordedBy'] = df0['recordedBy'].str.replace('台灣休閒漁業發展協會', '台灣休閒漁業發展協會 (Taiwan Leisure Fishery Development Association)')
df0['recordedBy'] = df0['recordedBy'].str.replace('陳淯茜', '陳淯茜 (Chen Yu-Chien)')



# samplingProtocol_BenthicInvertebrate

col_benthic_id = []

for occur_ID in df0['occurrenceID'].values:
    occur_ID = str(occur_ID)
    col_benthic_id.append(list(occur_ID.split('_')))
    
df0['method'] = col_benthic_id   
    
    

dict_method_BenthicInvertebrate = {
2018:	'Intertidal Visual Encounter Survey',
2020:	'Snorkeling | Intertidal Visual Encounter Survey',
2022:	'Intertidal Line Transect Survey | Intertidal Quadrat Sampling | Intertidal Qualitative Survey | Roving Diver Method',
2023:	'Intertidal Qualitative Survey | Roving Diver Method',
2024:	'Intertidal Qualitative Survey | Roving Diver Method',
2025:	'Intertidal Qualitative Survey | Roving Diver Method | Quadrat Sediment Survey' 
}



# BenthicInvertebrate_Crab
filter_crab_all = np.logical_or(df0['taxonID'].str.contains('Benthic', na=False), df0['order'].str.contains('Decapoda', na=False))
filter_the_year = np.logical_or(df0['year'] == 2014, df0['year'] == 2017)
filter_crab_year = np.logical_and(filter_crab_all, filter_the_year)
df0.loc[filter_crab_year,'samplingProtocol' ] = 'Intertidal Visual Encounter Survey'


filter_benthic = df0['taxonID'].str.contains('Benthic', na=False)


for year_benthic in dict_method_BenthicInvertebrate.keys():    
    df0.loc[np.logical_and(filter_benthic, df0['year']== year_benthic), 'samplingProtocol'] = dict_method_BenthicInvertebrate[year_benthic]

    
a1= df0.loc[filter_benthic,'method']

b1= df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶調查', na=False)), 'occurrenceID'] 
b2= df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶目視或徒手採集', na=False)), 'occurrenceID'] 
b3= df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('水下調查', na=False)), 'occurrenceID'] 

b4= df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('水下潛水調查', na=False)), 'occurrenceID'] 
b5= df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶樣框調查', na=False)), 'occurrenceID'] 

df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶調查', na=False)), 'samplingProtocol'] = 'Intertidal Qualitative Survey'
df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶目視或徒手採集', na=False)), 'samplingProtocol'] = 'Intertidal Qualitative Survey by Visual and Hand collection'
df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('水下調查', na=False)), 'samplingProtocol'] = 'Roving Diver Method'
df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('水下潛水調查', na=False)), 'samplingProtocol'] = 'Roving Diver Method'
df0.loc[np.logical_and(filter_benthic, df0['occurrenceID'].str.contains('潮間帶樣框調查', na=False)), 'samplingProtocol'] = 'Intertidal Quadrat Sampling'



df0.loc[ df0['samplingProtocol']=='Roving Diver Method', 'minimumDepthInMeters'] = 3
df0.loc[ df0['samplingProtocol']=='Roving Diver Method', 'maximumDepthInMeters']= 10



df0.loc[df0['taxonID'].str.contains('Cetacean', na = False), 'minimumDepthInMeters'] = 0
df0.loc[df0['taxonID'].str.contains('Cetacean', na = False), 'maximumDepthInMeters'] = 0



filter_2023_BRUV = np.logical_and(df0['year']==2023, df0['samplingProtocol'].str.contains('Baited Remote Underwater Video', na = False))
df0.loc[filter_2023_BRUV, 'minimumDepthInMeters'] = 10
df0.loc[filter_2023_BRUV, 'maximumDepthInMeters'] = 20




#%%


filter_fish = df0['taxonID'].str.contains('Fish', na=False)
df0.loc[np.logical_and(filter_fish, df0['samplingProtocol'].str.contains('Intertidal Survey', na=False)), 'samplingProtocol'] = 'Intertidal Qualitative Survey'
df0.loc[np.logical_and(filter_fish, df0['samplingProtocol'].str.contains('Diver Operated Video', na=False)), 'samplingProtocol'] = 'Diver Operated Video (15 m *5 m)'
df0.loc[np.logical_and(filter_fish, df0['samplingProtocol'].str.contains('Underwater Visual Census', na=False)), 'samplingProtocol'] = 'Underwater Visual Census Line Transect'







#uncertainty_in_avian
taxon_group = []

for taxonid in df0['taxonID'].values:
    taxon_group.append(taxonid.split('_')[1])
df0['taxonGroup']= taxon_group
df0['taxonGroup_num']= taxon_group


df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Avian', '1')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Cetacean', '2')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Fish', '3')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('BenthicInvertebrate', '4')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Plant', '5')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Insect', '6')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Reptile', '7')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Spider', '8')
df0['taxonGroup_num'] = df0['taxonGroup_num'].str.replace('Algae', '9')
df0['taxonGroup_num']=df0['taxonGroup_num'].astype('Int64')


np.unique(df0['taxonGroup'])

np.unique(df0['taxonGroup_num'])








col_fixed_lat = []

for fixed_lat in df0['decimalLatitude'].values:
    fixed_lat = str(fixed_lat)
    col_fixed_lat.append(len(fixed_lat.split('.')[1]))
    
np.unique(col_fixed_lat)
df0['PrecisionLat'] = col_fixed_lat

col_fixed_long = []
for fixed_long in df0['decimalLongitude'].values:
    fixed_long = str(fixed_long)
    col_fixed_long.append(len(fixed_long.split('.')[1]))
    
np.unique(col_fixed_long)
df0['PrecisionLong'] = col_fixed_long






df0['decimalLongitude']= np.round(df0['decimalLongitude'],5)
df0['decimalLatitude']= np.round(df0['decimalLatitude'],5)
df0['coordinatePrecision'] = '0.00001'

df0['coordinateUncertaintyInMeters']




viridis = matplotlib.colormaps['viridis'].resampled(8)

filter_avian_rang = np.logical_and(df0['taxonGroup']=='Avian', df0['coordinateUncertaintyInMeters']< 35000)

df0[filter_avian_rang].plot.scatter(x='decimalLongitude', y='decimalLatitude'
                 ,c=[0.267004, 0.004874, 0.329415, 0.5     ],
                 s='coordinateUncertaintyInMeters')




'''
[北二]的鳥類記錄當中，自動相機的調查結果 (n = 7547 )，
其coordinateUncertaintyInMeters大多是10 m (n = 7516 )，
但是有少數筆coordinateUncertaintyInMeters是400 m (n = 31)。
這31筆分布在2022年與2023年，有辦法效對嗎? 還是就算了？

'''

'''
剛剛跟琪萱確認過，[北二]的鯨豚記錄當中，
coordinateUncertaintyInMeters皆為空值，
審稿者叫我改掉。
1).有些紀錄是其他團隊所做: 直接寫一個鯨豚調查的目視最遠距離，4000m。
2).針對我們的紀錄,"最初離船距離"的資料並沒有被彙整進入資料庫當中，我去NAS把他彙整進去。
'''




df0[df0['taxonGroup']=='Avian'].plot.scatter(x='decimalLongitude', y='decimalLatitude'
                 ,c='taxonGroup_num', colormap= 'viridis'
                 ,s='coordinateUncertaintyInMeters')






dict_ceta_uncertainty={
    
"2019-08-22_Cetacean_HumanObservation_0001":4000,
"2019-11-12_Cetacean_HumanObservation_0002":4000,
    
"2020-06-08_Cetacean_HumanObservation_0003":4000,
"2020-07-03_Cetacean_HumanObservation_0004":4000,
"2020-08-19_Cetacean_HumanObservation_0005":4000,
"2020-09-14_Cetacean_HumanObservation_0008":4000,
"2020-09-14_Cetacean_HumanObservation_0006":4000,
"2020-09-14_Cetacean_HumanObservation_0009":4000,
"2020-09-14_Cetacean_HumanObservation_0007":4000,



"2021-03-30_Cetacean_HumanObservation_0010": 4000,
"2021-07-11_Cetacean_HumanObservation_0011": 300,
"2021-07-11_Cetacean_HumanObservation_0012": 300,
"2021-07-11_Cetacean_HumanObservation_0013": 300,
"2021-08-26_Cetacean_HumanObservation_0014": 1000,
"2021-08-26_Cetacean_HumanObservation_0015": 4000,

"2021-09-21_Cetacean_HumanObservation_0016": 300,
"2021-09-21_Cetacean_HumanObservation_0017": 300,



"2022-03-15_Cetacean_HumanObservation_0018": 300,
"2022-03-15_Cetacean_HumanObservation_0019": 500,
"2022-03-15_Cetacean_HumanObservation_0020": 300,
"2022-03-15_Cetacean_HumanObservation_0021": 300,
"2022-03-15_Cetacean_HumanObservation_0022": 300,
"2022-03-15_Cetacean_HumanObservation_0023": 300,



'2022-06-04_Cetacean_HumanObservation_0024': 300,
'2022-06-04_Cetacean_HumanObservation_0025': 500,
"2022-06-04_Cetacean_HumanObservation_0026": 500,
"2022-06-04_Cetacean_HumanObservation_0027": 300,
"2022-06-04_Cetacean_HumanObservation_0028": 300,
"2022-06-04_Cetacean_HumanObservation_0029": 700,
"2022-06-04_Cetacean_HumanObservation_0030": 300,



"2022-07-26_Cetacean_HumanObservation_0031": 300,
"2022-07-26_Cetacean_HumanObservation_0032": 300,
"2022-07-26_Cetacean_HumanObservation_0033": 300,
"2022-07-26_Cetacean_HumanObservation_0034": 300,
"2022-07-26_Cetacean_HumanObservation_0035": 300,
"2022-07-26_Cetacean_HumanObservation_0036": 800,
"2022-07-26_Cetacean_HumanObservation_0037": 300,


"2022-07-27_Cetacean_HumanObservation_0038":4000,
"2022-07-27_Cetacean_HumanObservation_0039":300,
"2022-07-27_Cetacean_HumanObservation_0040":4000,
"2022-09-30_Cetacean_HumanObservation_0041": 300,


"2023-04-11_Cetacean_HumanObservation_0005": 300,
"2023-04-11_Cetacean_HumanObservation_0004": 300,
"2023-04-11_Cetacean_HumanObservation_0003": 300,
"2023-04-11_Cetacean_HumanObservation_0002": 300,
"2023-04-11_Cetacean_HumanObservation_0001": 350,

"2023-07-11_Cetacean_HumanObservation_0006": 300,
"2023-07-11_Cetacean_HumanObservation_0007": 300,
"2023-07-11_Cetacean_HumanObservation_0008": 300,
"2023-07-11_Cetacean_HumanObservation_0009": 4000,
"2023-07-11_Cetacean_HumanObservation_0010": 300,
"2023-07-11_Cetacean_HumanObservation_0011": 300,
"2023-07-11_Cetacean_HumanObservation_0012": 300,
"2023-07-11_Cetacean_HumanObservation_0013": 300,

"2023-08-21_Cetacean_HumanObservation_0014": 800,
"2023-08-21_Cetacean_HumanObservation_0016": 600,
"2023-08-21_Cetacean_HumanObservation_0015": 900,


"2023-09-18_Cetacean_HumanObservation_0017": 300,
"2023-09-18_Cetacean_HumanObservation_0018": 300,
"2023-09-18_Cetacean_HumanObservation_0019": 500,
"2023-09-18_Cetacean_HumanObservation_0020": 300,



"2024-05-27_Cetacean_HumanObservation_0001": 300,
"2024-05-27_Cetacean_HumanObservation_0002": 300,
"2024-05-27_Cetacean_HumanObservation_0003": 300,
"2024-05-27_Cetacean_HumanObservation_0004": 300,

"2024-07-31_Cetacean_HumanObservation_0005": 300,
"2024-07-31_Cetacean_HumanObservation_0006": 300,
"2024-07-31_Cetacean_HumanObservation_0007": 300,
"2024-07-31_Cetacean_HumanObservation_0008": 300,
"2024-07-31_Cetacean_HumanObservation_0009": 300,
"2024-07-31_Cetacean_HumanObservation_0010": 300,

"2024-09-12_Cetacean_HumanObservation_0011": 300,
"2024-09-12_Cetacean_HumanObservation_0012": 300,


"2025-04-08_Cetacean_HumanObservation_0001": 300,
"2025-07-16_Cetacean_HumanObservation_0002": 300,
"2025-07-16_Cetacean_HumanObservation_0003": 300,
"2025-08-19_Cetacean_HumanObservation_0004": 300,
"2025-08-19_Cetacean_HumanObservation_0005": 300
 }



for occurID in dict_ceta_uncertainty.keys():
    df0.loc[df0['occurrenceID']== occurID, 'coordinateUncertaintyInMeters'] = dict_ceta_uncertainty[occurID]





df0.loc[df0['occurrenceID']=="2024-07-31_Cetacean_HumanObservation_0008", 'decimalLongitude'] = 122.20149
df0.loc[df0['occurrenceID']=="2022-03-15_Cetacean_HumanObservation_0023", 'decimalLongitude'] = 121.89828



dict_ceta_eventTime={

"2021-03-30_Cetacean_HumanObservation_0010": '11:06:00',
"2021-07-11_Cetacean_HumanObservation_0011": '06:15:00',
"2021-07-11_Cetacean_HumanObservation_0012": '09:34:00',
"2021-07-11_Cetacean_HumanObservation_0013": '14:22:00',
"2021-08-26_Cetacean_HumanObservation_0014": '11:08:00',
"2021-08-26_Cetacean_HumanObservation_0015": '11:31:00',
"2021-09-21_Cetacean_HumanObservation_0016": '07:21:00',
"2021-09-21_Cetacean_HumanObservation_0017": '12:42:00',



"2022-03-15_Cetacean_HumanObservation_0018": "15:41:00",
"2022-03-15_Cetacean_HumanObservation_0019": "06:58:00",
"2022-03-15_Cetacean_HumanObservation_0020": "10:10:00",
"2022-03-15_Cetacean_HumanObservation_0021": '12:50:00',
"2022-03-15_Cetacean_HumanObservation_0022": '15:27:00',
"2022-03-15_Cetacean_HumanObservation_0023": '14:50:00',



'2022-06-04_Cetacean_HumanObservation_0024': "07:46:00",
'2022-06-04_Cetacean_HumanObservation_0025': "09:20:00",
"2022-06-04_Cetacean_HumanObservation_0026": "09:28:00",
"2022-06-04_Cetacean_HumanObservation_0027": "09:41:00",
"2022-06-04_Cetacean_HumanObservation_0028": "10:16:00",
"2022-06-04_Cetacean_HumanObservation_0029": "11:52:00",
"2022-06-04_Cetacean_HumanObservation_0030": "14:49:00",



"2022-07-26_Cetacean_HumanObservation_0031": "10:02:00",
"2022-07-26_Cetacean_HumanObservation_0032": "15:36:00",
"2022-07-26_Cetacean_HumanObservation_0033": "11:04:00",
"2022-07-26_Cetacean_HumanObservation_0034": "14:42:00",
"2022-07-26_Cetacean_HumanObservation_0035": "15:00:00",
"2022-07-26_Cetacean_HumanObservation_0036": "15:20:00",
"2022-07-26_Cetacean_HumanObservation_0037": "11:04:00",



"2022-07-27_Cetacean_HumanObservation_0038": "13:31:00",
"2022-07-27_Cetacean_HumanObservation_0039": "12:36:00",
"2022-07-27_Cetacean_HumanObservation_0040": "14:08:00",
"2022-09-30_Cetacean_HumanObservation_0041": "08:25:00",



"2023-04-11_Cetacean_HumanObservation_0005": '11:18:00',
"2023-04-11_Cetacean_HumanObservation_0004": '10:41:00',
"2023-04-11_Cetacean_HumanObservation_0003": '09:08:00',
"2023-04-11_Cetacean_HumanObservation_0002": '07:46:00',
"2023-04-11_Cetacean_HumanObservation_0001": '07:21:00',


"2023-07-11_Cetacean_HumanObservation_0006": '05:23:00',
"2023-07-11_Cetacean_HumanObservation_0007": '05:23:00',
"2023-07-11_Cetacean_HumanObservation_0008": '06:42:00',
"2023-07-11_Cetacean_HumanObservation_0009": '07:11:00',
"2023-07-11_Cetacean_HumanObservation_0010": '10:12:00',
"2023-07-11_Cetacean_HumanObservation_0011": '10:31:00',
"2023-07-11_Cetacean_HumanObservation_0012": '13:25:00',
"2023-07-11_Cetacean_HumanObservation_0013": '15:39:00',

"2023-08-21_Cetacean_HumanObservation_0014": '09:47:00',
"2023-08-21_Cetacean_HumanObservation_0015": '11:03:00',
"2023-08-21_Cetacean_HumanObservation_0016": '13:36:00',

"2023-09-18_Cetacean_HumanObservation_0017": '06:23:00',
"2023-09-18_Cetacean_HumanObservation_0018": '07:34:00',
"2023-09-18_Cetacean_HumanObservation_0019": '07:34:00',
"2023-09-18_Cetacean_HumanObservation_0020": '09:52:00',



"2024-05-27_Cetacean_HumanObservation_0001": '05:29:00',
"2024-05-27_Cetacean_HumanObservation_0002": '14:09:00',
"2024-05-27_Cetacean_HumanObservation_0003": '14:09:00',
"2024-05-27_Cetacean_HumanObservation_0004": '14:31:00',

"2024-07-31_Cetacean_HumanObservation_0005":'08:54:00',
"2024-07-31_Cetacean_HumanObservation_0006":'09:12:00',
"2024-07-31_Cetacean_HumanObservation_0007":'09:31:00',
"2024-07-31_Cetacean_HumanObservation_0008":'10:28:00',
"2024-07-31_Cetacean_HumanObservation_0009":'10:35:00',
"2024-07-31_Cetacean_HumanObservation_0010":'10:52:00',

"2024-09-12_Cetacean_HumanObservation_0011": '06:50:00',
"2024-09-12_Cetacean_HumanObservation_0012": '12:22:00',




"2025-04-08_Cetacean_HumanObservation_0001": '14:27:00',
"2025-07-16_Cetacean_HumanObservation_0002": '07:14:00',
"2025-07-16_Cetacean_HumanObservation_0003": '15:29:00',
"2025-08-19_Cetacean_HumanObservation_0004": '06:15:00',
"2025-08-19_Cetacean_HumanObservation_0005": '12:58:00',

}





for occurID in dict_ceta_eventTime.keys():
    df0.loc[df0['occurrenceID']== occurID, 'eventTime'] = dict_ceta_eventTime[occurID]




df0.loc[df0['occurrenceID']== '2021-07-11_Cetacean_HumanObservation_0011', 'decimalLatitude'] = 25.20195
df0.loc[df0['occurrenceID']== '2021-07-11_Cetacean_HumanObservation_0011', 'decimalLongitude'] = 121.81463	





#%%



df0['geodeticDatum']= df0['geodeticDatum'].str.replace('WGS84','EPSG:4326')
df0['geodeticDatum']='EPSG:4326'


df0['coordinateUncertaintyInMeters'].unique()

filter_uncetain = df0['coordinateUncertaintyInMeters'].isna()
a1=df0[filter_uncetain]



#%%


#Behavior_ceta

dict_behavior_ceta = {
"覓食、游走":"feeding | travelling",
"游走、社交":"travelling | socialising",
"繞圈徘徊、覓食": "milling | feeding",
"繞圈徘徊；社交": "milling | socialising",
"覓食(疑似)；游走" :"feeding (probable) | travelling",
"遊走；其他(浮窺、全身跳出1次)" : "travelling | spyhopping | breaching",
'feeding；travelling': 'feeding | travelling',
"覓食":"feeding",
"游走":"travelling",
"社交":"socialising",
"繞圈徘徊": "milling",
"不知":"",
"未知":""}



filter_ceta = df0['taxonID'].str.contains('Cetacean')
df0.loc[filter_ceta, 'behavior'].unique()

for behavior1 in dict_behavior_ceta.keys():
    df0.loc[filter_ceta, 'behavior']= df0.loc[filter_ceta, 'behavior'].str.replace(behavior1, dict_behavior_ceta[behavior1])
    
df0.loc[filter_ceta, 'behavior'].unique()


    
    
#%%

#Behavior_avian

df0.loc[df0['occurrenceID']=='2023-09-18_Avian_基隆海域_314', 'occurrenceRemarks'] = 'stoppong the ship'
df0.loc[df0['occurrenceID']=='2023-09-18_Avian_基隆海域_294', 'occurrenceRemarks'] = 'stoppong the ship'

    
    
    
dict_behavior_avian = {
"飛行/海上漂浮": "flying | floating",
"盤旋/覓食/海上漂浮": "hovering | feeding | floating",
"停棲在海漂物":"perching on floating debris",
"停棲在其他海漂物":"perching on floating debris",
"停棲在漂浮物":"perching on floating debris",
"停棲海面":"perching above the ocean",
"覓食": "feeding",
"飛行": "flying",
"海上漂浮": "floating",
"盤旋": "hovering",
"停船": "",
"備註": ""
 }
    


filter_avian = df0['taxonID'].str.contains('Avian')
df0.loc[filter_avian, 'behavior'].unique()


for behavior1 in dict_behavior_avian.keys():
    df0.loc[filter_avian, 'behavior']= df0.loc[filter_avian, 'behavior'].str.replace(behavior1, dict_behavior_avian[behavior1])

df0.loc[filter_avian, 'behavior'].unique()



df0['behavior'].unique()

#%%

# 'occurrenceID' in Chinese ( 12624 >> 1623 >> 506)

df0['occurrence_newID'] = df0['occurrenceID']
filter_chinese_occur = df0['occurrence_newID'].str.contains('[\u4e00-\u9fa5]')
df0_chinese = df0[filter_chinese_occur]
print(len(df0_chinese))

df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Avian_棉花嶼', 'Avian_Mianhua Islet')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Avian_花瓶嶼', 'Avian_Huaping Islet')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Avian_彭佳嶼', 'Avian_Pengjia Islet')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Avian_基隆海域', 'Avian_waters off Keelung')

filter_chinese_occur = df0['occurrence_newID'].str.contains('[\u4e00-\u9fa5]')
df0_chinese = df0[filter_chinese_occur]
print(len(df0_chinese))

df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('棉花嶼_植物_全島', 'Plant_Mianhua Islet')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('棉花嶼_植物_火災樣區', 'Plant_MianhuaIslet_PostFire')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('棉花嶼_植物', 'Plant_MianhuaIslet')

filter_plant = df0['taxonID'].str.contains('PLant')
df0.loc[filter_plant, 'locality']=df0.loc[filter_plant, 'locality'].str.replace('MianhuaIslet_Plant_', 'MianhuaIslet_')




df0['occurrence_newID']=df0['occurrence_newID'].str.replace('2024-04-01_無脊椎動物_潮間帶調查_棉花嶼_09', '2024-04-01_Algae_Intertidal Qualitative Survey_09')
df0['occurrence_newID']=df0['occurrence_newID'].str.replace('2024-07-31_無脊椎動物_潮間帶調查_棉花嶼_26', '2024-07-31_Algae_Intertidal Qualitative Survey_26')
df0['occurrence_newID']=df0['occurrence_newID'].str.replace('藻類調查', 'Algae_Survey')







filter_chinese_occur = df0['occurrence_newID'].str.contains('[\u4e00-\u9fa5]')
df0_chinese = df0[filter_chinese_occur]
print(len(df0_chinese))



df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物_水下調查_棉花嶼', 'BenthicInvertebrate_Roving Diver Method')

df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物_水下潛水調查_棉花嶼', 'BenthicInvertebrate_Roving Diver Method')

df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace(r'(.*)_無脊椎動物_水下潛水調查_([0-9]*)',
                                                    r'\1_BenthicInvertebrate_Roving Diver Method_\2',
                                                    regex = True)



df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物_潮間帶樣框調查', 'BenthicInvertebrate_Intertidal Quadrat Sampling')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物_潮間帶調查_棉花嶼', 'BenthicInvertebrate_Intertidal Qualitative Survey')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物調查_棉花嶼', 'BenthicInvertebrate_')


df0.loc[:, 'samplingProtocol'] = df0.loc[:, 'samplingProtocol'].str.replace('Intertidal Qualitative Survey by Visual and Hand collection',
                                                                            'Intertidal Qualitative Survey by Visual or Hand collection')



df0.loc[filter_chinese_occur, 'occurrence_newID'] = df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物_潮間帶目視或徒手採集', 'BenthicInvertebrate_Intertidal Qualitative Survey by Visual or Hand collection')
df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('無脊椎動物調查', 'BenthicInvertebrate')




df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Fish_BRUV',
                                                                                                                 'Fish_Baited Remote Underwater Video')


df0.loc[:, 'samplingProtocol'] = df0.loc[:, 'samplingProtocol'].str.replace('Line Transect Survey (30 m * 5 m)',
                                                                            'Underwater Visual Census Line Transect (30 m * 5 m)')

df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Fish_潛水調查',
                                                                                                                 'Fish_Underwater Visual Census')


df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Fish_浮潛',
                                                                                                                 'Fish_Snorkeling')


df0.loc[filter_chinese_occur, 'occurrence_newID']= df0.loc[filter_chinese_occur, 'occurrence_newID'].str.replace('Fish_陸域巡護',
                                                                                                                 'Fish_Terrestrial Patrol')

filter_DOV = df0['samplingProtocol'].str.contains( 'Diver Operated Video', na= False)
df0.loc[filter_DOV , 'occurrence_newID']= df0.loc[filter_DOV , 'occurrence_newID'].str.replace('Fish_Underwater Visual Census','Fish_Diver Operated Video')








filter_chinese_occur = df0['occurrence_newID'].str.contains('[\u4e00-\u9fa5]')
df0_chinese = df0[filter_chinese_occur]
print(len(df0_chinese))






df0_occurID = df0.loc[:,['occurrenceID','occurrence_newID']]

filter_occur_tochange = df0_occurID['occurrenceID'] != df0_occurID['occurrence_newID']

df0_IDchange_list = df0_occurID[filter_occur_tochange] 

df0_IDchange_list_new = pd.concat([df_measure_occurID_change, df0_IDchange_list], ignore_index=True)


df0_IDchange_list_new.to_csv(os.path.join(input_path,
            '9_gbif_KL_occurrenceID_change_new_20260729.csv'),
            encoding='utf_8_sig',
            index= False,
            header= False)



# 1. 處理需要變成「整數」的欄位 (例如：深度、座標誤差半徑)
# 注意：要用大寫的 'Int64'，這樣如果欄位裡面有空值(NaN)才不會報錯
int_columns = ['coordinateUncertaintyInMeters', 'maximumDepthInMeters',
               'minimumDepthInMeters', 'individualCount','year', 'month', 'day']
for col in int_columns:
    if col in df0.columns:
        df0[col] = df0[col].astype('Int64')


# 3. 處理需要「小數點後 5 位」的欄位 (例如：經緯度)
float_5_columns = ['decimalLatitude', 'decimalLongitude', 'coordinatePrecision']
for col in float_5_columns:
    if col in df0.columns:
        df0[col] = df0[col].round(5)
        
        
        
# Missing data items have been left blank.
df0['samplingProtocol'] = df0['samplingProtocol'].replace('The survey was conducted without a description of the methods.', '')
df0['behavior'] = df0['behavior'].replace('unknown', '')
df0['dynamicProperties'] = df0['dynamicProperties'].replace('{mother-calf pairs:unknown}', '')




#%%


df0.to_csv(os.path.join(input_path,
            '9_gbif_KL_occurrence_till_20251230_all_20260731_1700_API_name.csv'),
            encoding='utf_8_sig',
            index= False)



'''
# remove columns :['lifeStage', 'associatedMedia']
# add columns :['id', 'kingdom', 'countryCode', 'verbatimIdentification']

'''



#Remove columns
df0['occurrenceID'] = df0['occurrence_newID']

df0 = df0.drop(['Api_name_v2','Api_name_v1', 'higherClassification', 'rank', 'status','confidence', 'matchType',
                'phylum', 'class', 'order', 'family','genus', 'species'], axis=1)

df0 = df0.drop(['lifeStage', 'associatedMedia'], axis=1)
df0 = df0.drop(['PrecisionLong','PrecisionLat',
                'taxonGroup','taxonGroup_num',
                'method','occurrence_newID'], axis=1)

if 'id' in  df0.columns:
    df0 = df0.drop(['id'], axis=1)
    



df0.to_csv(os.path.join(input_path,
          '9_gbif_KL_occurrence_till_20251230_all_20260731_1700_WO_API_occurrenceID.csv'),
            encoding='utf_8_sig',
            index= False)










