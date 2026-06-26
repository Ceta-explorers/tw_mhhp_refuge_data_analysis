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
#read data


df0 = pd.read_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260408.csv'), sep='\t', low_memory=False)
df0 = df0.sort_values(by=['verbatimEventDate'], ascending =True)


#移除欄位'occurrenceStatus'
df0 = df0.drop(['occurrenceStatus'],axis=1)
#df0.to_csv(os.path.join(input_path, 'occurrence_new.csv'), encoding='utf_8_sig', index= False)


df0_indx = df0.dropna(axis = 'index', how ='all')
df0_column = df0.dropna(axis = 'columns', how ='all')





#update欄位'associatedMedia'
df0['associatedMedia']= df0['associatedMedia'].astype('str')


filter_manta = np.logical_and(df0['scientificName']== 'Manta birostris', df0['eventDate']== '2022-06-04')
df0.loc[filter_manta, 'associatedMedia'] =  'https://arpha.pensoft.net/zoomed_fig/14217697'


filter_streaked = np.logical_and(df0['scientificName']== 'Calonectris leucomelas', df0['eventDate']== '2023-11-07')
a1 = df0.loc[df0['scientificName']== 'Calonectris leucomelas']
#a1.to_csv(os.path.join(input_path, 'KL_Streaked_Shearwater.csv'), encoding='utf_8_sig')



# df0.loc[filter_streaked, :]
# df0.loc[filter_streaked, 'associatedMedia'] =  'https://arpha.pensoft.net/zoomed_fig/14295127'





col_df0 = set(df0.columns)
col_dfc = set(df0_column.columns)
col_df0 - col_dfc





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
