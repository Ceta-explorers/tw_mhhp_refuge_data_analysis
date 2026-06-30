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

#read data  and compare columns


df0 = pd.read_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260630.csv'), sep=',', low_memory=False)
df0 = df0.sort_values(by=['verbatimEventDate'], ascending =True)


df0.dtypes

df0['year']= df0['year'].astype('str')


df0['month']=df0['month'].fillna(0)
df0['month']= df0['month'].astype('Int64')
df0['month']= df0['month'].astype('str').str.zfill(2)


df0['day']= df0['day'].fillna(0)
df0['day'] = df0['day'].astype('Int64')
df0['day']= df0['day'].astype('str').str.zfill(2)


df0['verbatimEventDate']= df0['year'] + '-' + df0['month'] + '-' + df0['day']
df0['eventDate']= df0['year'] + '-' + df0['month'] + '-' + df0['day']
df0['eventDate']=df0['eventDate'].str.replace('-00-00','')



#型態變回整數
df0['month']= df0['month'].astype('Int64')
df0['day'] = df0['day'].astype('Int64')

df0['individualCount'] = df0['individualCount'].astype('Int64')


df0.to_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_ver20260630_correct.csv'), encoding='utf_8_sig', index= False)





#%%
#移除欄位'occurrenceStatus'
df0 = df0.drop(['occurrenceStatus', 'sex', 'vitality'],axis=1)
#df0.to_csv(os.path.join(input_path, 'occurrence_new.csv'), encoding='utf_8_sig', index= False)


# df0_indx = df0.dropna(axis = 'index', how ='all')
# df0_column = df0.dropna(axis = 'columns', how ='all')





# update欄位'associatedMedia'
df0['associatedMedia']= df0['associatedMedia'].astype('str')
filter_manta = np.logical_and(df0['scientificName']== 'Manta birostris', df0['eventDate']== '2022-06-04')
df0.loc[filter_manta, 'associatedMedia'] =  'https://arpha.pensoft.net/zoomed_fig/14217697'



# update欄位'reproductiveCondition'
df0['reproductiveCondition']= df0['reproductiveCondition'].astype('str')
filter_streaked = (df0['scientificName']== 'Calonectris leucomelas') & (df0['basisOfRecord']== 'MachineObservation') & (df0['eventTime'].notnull()) 
a2= df0.loc[filter_streaked ,:]
df0.loc[filter_streaked ,'reproductiveCondition'] = 'Possible breeder'


#a1 = df0.loc[df0['scientificName']== 'Calonectris leucomelas']
#a1.to_csv(os.path.join(input_path, 'KL_Streaked_Shearwater.csv'), encoding='utf_8_sig')


df0[df0['eventTime'].notnull()]



# update turtle

filter_tirtle = (df0['scientificName']== 'Chelonia mydas') & (df0['occurrenceRemarks'].str.strip()=='遭漁業垃圾纏繞')
a3 = df0.loc[filter_tirtle ,:]
df0.loc[filter_tirtle ,'eventDate'] = '2022-07-26'
df0.loc[filter_tirtle ,'verbatimEventDate'] = '2022-07-26'
df0.loc[filter_tirtle , 'occurrenceID'] = '2022-07-26_Reptile_HumanObservation_0015'
df0.loc[filter_tirtle ,'year'] = int(2022)
df0.loc[filter_tirtle ,'month']= int(7)
df0.loc[filter_tirtle ,'day']= int(26)


# update欄位'individualCount'
df0['individualCount']= df0['individualCount'].astype('Int64')




df0_indx = df0.dropna(axis = 'index', how ='all')
df0_column = df0.dropna(axis = 'columns', how ='all')


col_df0 = set(df0.columns)
col_dfc = set(df0_column.columns)
print(col_df0 - col_dfc)
#df0.to_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_ver20260629.csv'), encoding='utf_8_sig', index= False)



'''
凡是簡訊相機拍攝的大水薙鳥 (有日期與時間)，他的'reproductiveCondition' = 'Possible breeder'

欄位的變動：
delete these columns： 'sex', 'vitality', 'occurrenceStatus'.
update these columns： 'associatedMedia', 'reproductiveCondition'.
change the occurrenceID of one record： From '2022-06-04_Reptile_HumanObservation_0015' to '2022-07-26_Reptile_HumanObservation_0015'.

'''




#%%

print(f'The backend of graphic is {matplotlib.get_backend()}')
# Returns the absolute directory of the active script
script_dir = Path(__file__).resolve().parent
print(script_dir)


print(f'script_dir is {script_dir}')
print(f'realpath is {os.path.realpath(__file__)}')
print(f'abspath is {os.path.abspath(__file__)}')



try:
    script_dir = os.path.abspath(__file__)
except:
    script_dir = os.getcwd()
    
    
root_path = os.path.abspath(os.path.join(script_dir, '..'))

print(f'root_path  is {root_path }')
