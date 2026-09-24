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


df_measure['occurrenceID']=df_measure['occurrenceID'].str.strip()
df_measure['occurrenceID']=df_measure['occurrenceID'].str.replace('Censuses','Census')



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



df_measure.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260715_1800_with_days.csv'), encoding='utf_8_sig', index= False)



df_measure = df_measure.drop(['scientificName', 'taxonRank', 'vernacularName',
                              'decimalLongitude', 'decimalLatitude', 'year',
                              'month', 'day', 'taxonID','verbatimEventDate'], axis=1)




df_measure.to_csv(os.path.join(input_path, '5_fish_zmeasurement_2025_20260722_1800_WO_days.csv'), encoding='utf_8_sig', index= False)









df_occur1 = pd.read_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260715_1700_WO_API_name.csv'), sep=',', low_memory=False)
df_occur1['occurrenceID']=df_occur1['occurrenceID'].str.strip()



occurID_measure = set(df_measure['occurrenceID'])
occurID_occur= set(df_occur1['occurrenceID'])

check_occurID1 = occurID_measure - occurID_occur
check_occurID2 =  occurID_occur - occurID_measure 





#%%



#read data  and compare columns


df0 = pd.read_csv(os.path.join(input_path, '9-gbif-KL-occurrence-till-20251230_all_20260711_fish.csv'), sep=',', low_memory=False)
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


df0.dtypes



# scientificName
df0['scientificName']=df0['scientificName'].str.strip()


df0['scientificName']=df0['scientificName'].str.replace('Locustella ochotensis','Helopsaltes ochotensis')
df0['scientificName']=df0['scientificName'].str.replace('Saxicola maurus','Saxicola stejnegeri')

#Taxon: delete "KL_BenthicInvertebrate_0000127":"Cocos frillgoby", add "KL_Fish_0000016": "Gymnothorax pictus"





# Intertidal_Algae
filter_coordinate_algae= df0['taxonID'].str.contains("KL_BenthicInvertebrate_0000123", na = False)
df0.loc[filter_coordinate_algae, 'taxonID']= df0.loc[filter_coordinate_algae, 'taxonID'].str.replace("KL_BenthicInvertebrate_0000123", "KL_Algae_0000012")



# df0['occurrenceID'].str.replace('2024-04-01_無脊椎動物_潮間帶調查_棉花嶼_09', '2024-04-01_Algae_潮間帶調查_09')
# df0['occurrenceID'].str.replace('2024-07-31_無脊椎動物_潮間帶調查_棉花嶼_26', '2024-07-31_Algae_潮間帶調查_26')




#filter_fish_record1_Intertidal Survey_Cocos frillgoby
filter_occur_intertidal = df0['taxonID']== "KL_BenthicInvertebrate_0000127"
df0.loc[filter_occur_intertidal,'scientificName']
df0.loc[filter_occur_intertidal,'samplingProtocol']= 'Intertidal Qualitative Survey'
df0.loc[filter_occur_intertidal,'occurrenceID'] = "2024-07-31_Fish_Intertidal Survey_0005"
df0.loc[filter_occur_intertidal,'taxonID'] = "KL_Fish_0000285"


filter_occur_cocos = df0['taxonID']== "KL_Fish_0000285"
df0.loc[filter_occur_cocos,'scientificName']= 'Bathygobius cocosensis'
df0.loc[filter_occur_cocos,'taxonID']= 'KL_Fish_0000166'





#filter_fish_record2_Intertidal Survey_Gymnothorax pictus
filter_occur2 = df0['taxonID']== "KL_BenthicInvertebrate_0000126"
df0.loc[filter_occur2,'scientificName']

df0.loc[filter_occur2,'occurrenceID'] = "2024-07-31_Fish_Intertidal Survey_0004"
df0.loc[filter_occur2,'taxonID'] = "KL_Fish_0000016"
df0.loc[filter_occur2,'samplingProtocol']= 'Intertidal Qualitative Survey'



filter_occur2_method = np.logical_and(df0['taxonID'].str.contains("BenthicInvertebrate", na= False), df0['taxonID'].str.contains("Fish", na= False))
df0.loc[filter_occur2_method,'samplingProtocol']= df0.loc[filter_occur2_method,'samplingProtocol'].str.replace('Intertidal Survey', 'Intertidal Qualitative Survey')




#filter_insect_record1_Diasemia accalis



df0.loc[:,'scientificName']= df0.loc[:,'scientificName'].str.replace('Pycnoscelis surinamensis', 'Pycnoscelus surinamensis')
df0.loc[:,'taxonID']= df0.loc[:,'taxonID'].str.replace('KL_Insect_0000145', 'KL_Insect_0000077')
filter_taxon_insect7 = df0['scientificName']== 'Pycnoscelis surinamensis'
df0.loc[filter_taxon_insect7,'vernacularName'] = '蘇利南潛蠊'




#filter_insect_record1_Diasemia accalis
filter_taxon_insect5 = df0['scientificName']=='Propylea japonoca'
df0.loc[filter_taxon_insect5,'scientificName']= df0.loc[filter_taxon_insect5,'scientificName'].str.replace('Propylea japonoca', 'Propylea japonica')
df0.loc[filter_taxon_insect5, 'taxonID'] = df0.loc[filter_taxon_insect5, 'taxonID'].str.replace('KL_Insect_0000185', 'KL_Insect_0000103')



#filter_insect_record2_Muscidae
filter_taxon_insect1 = df0['taxonID']== 'KL_Insect_0000265'
df0.loc[filter_taxon_insect1,'taxonID'] = df0.loc[filter_taxon_insect1,'taxonID'].str.replace('KL_Insect_0000265', 'KL_Insect_0000169')

filter_taxon_insect2 = df0['taxonID']== 'KL_Insect_0000169'
df0.loc[filter_taxon_insect2,'vernacularName'] = '家蠅科'




#filter_insect_record1_Diasemia accalis
filter_taxon_insect3 = df0['taxonID']== 'KL_Insect_0000181'
df0.loc[filter_taxon_insect3,'scientificName'] = df0.loc[filter_taxon_insect3,'scientificName'].str.replace('Diasemia acalis', 'Diasemia accalis')
df0.loc[filter_taxon_insect3, 'taxonID'] = df0.loc[filter_taxon_insect3, 'taxonID'].str.replace('KL_Insect_0000181','KL_Insect_0000025')

filter_taxon_insect4 = df0['taxonID']== 'KL_Insect_0000025'
df0.loc[filter_taxon_insect4,'vernacularName'] = '褐紋翅野螟蛾'




#filter_record
filter_avian_occur1 = df0['occurrenceID']=='2024-06-14_Avian_棉花嶼_N7_34'
df0.loc[filter_avian_occur1,'scientificName'] = 'Bubulcus ibis'



#filter_rank
df0['taxonRank'] = df0['taxonRank'].str.replace("variety", "varietas")
df0['rank'] = df0['rank'].str.replace("variety", "varietas")


filter_rank = df0['taxonRank'] == df0['rank'].str.lower()
df0[filter_rank]


filter_rank_different =  (df0['taxonRank'] != df0['rank'].str.lower())
a1= df0[filter_rank_different]








df0['countryCode'] = 'TW'




# check 'scientificName'
fiilter_name1 = df0['scientificName'].str.contains(r"^[A-Z].*\s[A-Z]", na=False)
print(df0.loc[fiilter_name1, 'scientificName'])


fiilter_name2 = df0['scientificName'].str.contains(r"^[a-z].*\s[a-z]", na=False)
print(df0.loc[fiilter_name2, 'scientificName'])


df0.loc[df0['taxonID']== 'KL_BenthicInvertebrate_0000014', 'scientificName'] = 'Cypraea arabica'




# check 'lifeStage'
fiilter_name3 = df0['lifeStage'].str.contains(r"^[A-Za-z]", na=False)
df0.loc[fiilter_name3, 'occurrenceRemarks'] = df0.loc[fiilter_name3, 'lifeStage'].values[0][:-1]





# Update: spyder_record
filter_spyder  =df0['taxonID']=='KL_Insect_0000131'
df0.loc[filter_spyder, 'occurrenceID'] = '2008-00-00_Spider_HumanObservation_001'
df0.loc[filter_spyder, 'taxonID'] = 'KL_Spider_0000001'




# 'kingdom'
df0['kingdom'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('kingdom'))
df0['phylum'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('phylum'))
df0['class'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('class'))
df0['order'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('order'))
df0['family'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('family'))
df0['genus'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('genus'))
df0['species'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('species'))
df0['rank'] = df0['Api_name_v1'].apply(lambda x: json.loads(x).get('rank'))




filter_kindom_old = df0['kingdom'].isna()
df0_kingdom_old = df0[filter_kindom_old].copy()


filter_species_old = df0['species'].isna()
df0_species_old = df0[filter_species_old].copy()




dict_taxonID_kindom= {
 'Algae':'Plantae',
 'Avian':'Animalia',
 'Cetacean':'Animalia',
 'BenthicInvertebrate':'Animalia',
 'Fish':'Animalia',
 'Insect':'Animalia',
 'Spider':'Animalia',
 'Plant':'Plantae',
 'Reptile':'Animalia'
}


for name_kingdom in dict_taxonID_kindom.keys():
    filter_group = df0['taxonID'].str.contains(name_kingdom, na=False)
    df0.loc[filter_group,'kingdom']= dict_taxonID_kindom[name_kingdom]


#check "kingdom"
filter_kindom = df0['kingdom'].isna()
df0_kingdom_new = df0[filter_kindom].copy()
a2=df0['kingdom'].value_counts(dropna = False)



# "species_Avian"
filter_group = df0['taxonID'].str.contains('Avian', na=False)
df0.loc[filter_group,'kingdom']= 'Animalia'
df0.loc[filter_group,'phylum']='Chordata'
df0.loc[filter_group,'class']= 'Aves'


# "species_Cetacean"
filter_group = df0['taxonID'].str.contains('Cetacean', na=False)
df0.loc[filter_group,'kingdom']= 'Animalia'
df0.loc[filter_group,'phylum']='Chordata'
df0.loc[filter_group,'class']= 'Mammalia'



# "species_Arachnida (Spider)"
filter_group = df0['taxonID'].str.contains('Spider', na=False)
df0.loc[filter_group,'kingdom']= 'Animalia'
df0.loc[filter_group,'phylum']='Arthropoda'  #節肢動物門 
df0.loc[filter_group,'class']= 'Arachnida'   #蛛形綱


# "species_Insect"
filter_group = df0['taxonID'].str.contains('Insect', na=False)
df0.loc[filter_group,'kingdom']= 'Animalia'
df0.loc[filter_group,'phylum']='Arthropoda'  #節肢動物門 
df0.loc[filter_group,'class']= 'Insecta'   #昆蟲綱


# =============================================================================
# Method 2: Alt Codes (Requires a Numeric Keypad)
# If your keyboard has a dedicated number pad on the right side, you can hold down the Alt key and type a specific numeric code. (Note: You must use the number pad, not the numbers across the top of your keyboard).
# 
# ≥ : Hold Alt and type 242
# 
# ≤ : Hold Alt and type 243
# 
# ≈ : Hold Alt and type 247
# 
# =============================================================================




# Translate_organismQuantity

filter_chinese = df0['organismQuantity'].str.contains(r"[\u4e00-\u9fa5]", na=False)
df0.loc[df0['occurrenceID']=='2019-11-12_Cetacean_HumanObservation_0002', 'organismQuantity'] = '≥2'
df0.loc[df0['occurrenceID']=='2021-08-26_Cetacean_HumanObservation_0014', 'organismQuantity'] = '≥100'


filter_quantity = df0['organismQuantity'].str.contains('約', na=False)
df0.loc[filter_quantity,'organismQuantity'] = df0.loc[filter_quantity,'organismQuantity'].str.replace('約','≈')


filter_quantity = df0['organismQuantity'].str.contains('無法判斷', na=False)
df0.loc[filter_quantity,'organismQuantity'] = df0.loc[filter_quantity,'organismQuantity'].str.replace('無法判斷','undetermined')


filter_chinese = df0['organismQuantity'].str.contains(r"[\u4e00-\u9fa5]", na=False)
df0.loc[filter_chinese , :] 




#%%


# samplingProtocol_Plant





# Year >= 2021
#filter_method_plant = np.logical_and(df0['taxonID'].str.contains("Plant", na=False), df0['samplingProtocol'].str.contains(r"[\u4100-\u9fa5]", na=False))

filter_method_plant = np.logical_and(df0['taxonID'].str.contains("Plant", na=False), df0['year']>= 2021)
df0.loc[filter_method_plant,'samplingProtocol'] = df0.loc[filter_method_plant,'samplingProtocol'].str.replace('穿越線', 'Line Transect Survey')
df0.loc[filter_method_plant,'samplingProtocol'] = df0.loc[filter_method_plant,'samplingProtocol'].str.replace('樣區調查', 'Quadrat Sampling')


filter_method_plant_burned_area = np.logical_and(filter_method_plant,  df0['locality'].str.contains("火災", na=False))
df0.loc[filter_method_plant_burned_area,'samplingProtocol']= df0.loc[filter_method_plant_burned_area,'samplingProtocol'].str.replace('Quadrat Sampling', 'Quadrat Sampling (10*10 m\u00b2 Quadrat)')


filter_method_plant_general_area = np.logical_and(filter_method_plant,  df0['locality'].str.contains("火災", na=False) == False)
df0.loc[filter_method_plant_general_area,'samplingProtocol']= df0.loc[filter_method_plant_general_area,'samplingProtocol'].str.replace('Quadrat Sampling', 'Quadrat Sampling (5*5 m\u00b2 Quadrat)')





# Year < 2021
dict_method_plant = {
1994:	'Line Transect Survey | Quadrat Sampling (10*10 m²)',
1997:	'The survey was conducted without a description of the methods.',
2005:	'The survey was conducted without a description of the methods.',
2008:	'Line Transect Survey | Quadrat Sampling (5*5 m²)',
2009:	'The survey was conducted without a description of the methods.',
2010:	'The survey was conducted without a description of the methods.',
2011:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2012:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2013:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2014:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2015:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2016:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2017:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2018:	'Line Transect Survey | Quadrat Sampling (Twelve 5*5 m² Quadrats)',
2019:	'Line Transect Survey',
2020:	'Quadrat Sampling (Twelve 5*5 m² Quadrats)'
#2021:	'Quadrat Sampling (Twelve 5*5 m² Quadrats)',
#2022:	'Quadrat Sampling (Twelve 5*5 m² Quadrats) | Quadrat Sampling in a burned area (10*10 m² Quadrat) | Line Transect Survey',
#2023:	'Quadrat Sampling in a burned area (10*10 m² Quadrat) | Line Transect Survey'
 }


for year_plant in dict_method_plant.keys():
    filter_method_plant_year = np.logical_and(df0['taxonID'].str.contains("Plant", na=False), df0['year']==year_plant)
    df0.loc[filter_method_plant_year,'samplingProtocol']= dict_method_plant[year_plant]







# samplingProtocol_avian


# year, locality, basisOfRecord

# basisOfRecord (1)

# basisOfRecord (0), year, locality,


filter_method_avian = df0['taxonID'].str.contains("Avian", na=False)
df0[filter_method_avian]



filter_method_avian_machine = np.logical_and(df0['taxonID'].str.contains("Avian", na=False), df0['basisOfRecord'].str.contains("MachineObservation", na=False))
df0.loc[filter_method_avian_machine,'samplingProtocol'] = 'Camera trap'
df0[filter_method_avian_machine]



df0.loc[filter_method_avian,'locality'] = df0.loc[filter_method_avian,'locality'].str.replace('棉花嶼','Mianhua Islet')
df0.loc[filter_method_avian,'locality'] = df0.loc[filter_method_avian,'locality'].str.replace('花瓶嶼','Huaping Islet')
df0.loc[filter_method_avian,'locality'] = df0.loc[filter_method_avian,'locality'].str.replace('彭佳嶼','Pengjia Islet')
df0.loc[filter_method_avian,'locality'] = df0.loc[filter_method_avian,'locality'].str.replace('基隆海域','waters off Keelung')







#俗名>> ID>> scientific name




filter_method_avian_human = np.logical_and(df0['taxonID'].str.contains("Avian", na=False), df0['basisOfRecord'].str.contains("HumanObservation", na=False))


filter_method_avian_human_locality2 = np.logical_and(filter_method_avian_human, df0['locality'].str.contains("Huaping Islet", na=False))
df0.loc[filter_method_avian_human_locality2, 'samplingProtocol'] = 'Route Survey'



filter_method_avian_human_locality1 = np.logical_and(filter_method_avian_human, df0['locality'].str.contains("waters off Keelung", na=False))
df0.loc[filter_method_avian_human_locality1, 'samplingProtocol'] = 'Route Survey'


dict_method_avian_pengjia = {
1994:	'Route Survey',
2002:	'Route Survey',
2003:	'Route Survey',
2005:	'The survey was conducted without a description of the methods.',
2008:	'Line Transect Survey',
2009:	'The survey was conducted without a description of the methods.',
2010:	'Line Transect Survey',
2011:	'Area Search Method',
2012:	'Area Search Method',
2013:	'Area Search Method',
2014:	'Line Transect Survey',
2015:	'Line Transect Survey',
2016:	'Line Transect Survey',
2017:	'Line Transect Survey',
2018:	'Line Transect Survey',
2020:	'Line Transect Survey'
 }

filter_method_year_avian_human_pengjia = np.logical_and(filter_method_avian_human, df0['locality'].str.contains("Pengjia", na=False))

df0[filter_method_year_avian_human_pengjia]


for year_avian in dict_method_avian_pengjia.keys():
    df0.loc[np.logical_and(filter_method_year_avian_human_pengjia, df0['year']== year_avian), 'samplingProtocol'] = dict_method_avian_pengjia[year_avian]
    print(df0.loc[np.logical_and(filter_method_year_avian_human_pengjia , df0['year']== year_avian), ['year','samplingProtocol']] )




dict_method_avian_mianhua ={
1994:	'Point Count Survey',
2002:	'Route Survey',
2003:	'Route Survey',
2005:	'The survey was conducted without a description of the methods.',
2008:	'Line Transect Survey',
2009:	'The survey was conducted without a description of the methods.',
2010:	'Line Transect Survey | Point Count Survey | Area Search Method',
2011:	'Line Transect Survey | Point Count Survey | Area Search Method',
2012:	'Line Transect Survey | Point Count Survey | Area Search Method',
2013:	'Line Transect Survey | Point Count Survey | Area Search Method',
2014:	'Line Transect Survey | Point Count Survey | Area Search Method',
2015:	'Line Transect Survey | Point Count Survey | Area Search Method',
2016:	'Line Transect Survey | Area Search Method',
2017:	'Line Transect Survey | Area Search Method',
2018:	'Line Transect Survey | Area Search Method',
2019:	'Line Transect Survey',
2020:	'Line Transect Survey | Area Search Method',
2021:	'Area Search Method',
2022:	'Area Search Method',
2023:	'Area Search Method',
2024:	'Area Search Method',
2025:	'Area Search Method'
 }




filter_method_year_avian_human_mianhua = np.logical_and(filter_method_avian_human, df0['locality'].str.contains("Mianhua", na=False))

df0[filter_method_year_avian_human_mianhua]


for year_avian in dict_method_avian_mianhua.keys():
    df0.loc[np.logical_and(filter_method_year_avian_human_mianhua, df0['year']== year_avian), 'samplingProtocol'] = dict_method_avian_mianhua[year_avian]
    print(df0.loc[np.logical_and(filter_method_year_avian_human_mianhua , df0['year']== year_avian), ['year','samplingProtocol']] )



df0.loc[filter_method_avian_human,'samplingProtocol']
df0.loc[filter_method_avian,'locality'].value_counts(dropna=False)



 

# samplingProtocol_ceta

dict_method_ceta = {
2019:	'Route Survey',
2020:	'Route Survey',
2021:	'Route Survey',
2022:	'Route Survey | Line Transect Survey',
2023:	'Route Survey',
2024:	'Route Survey',
2025:	'Route Survey'
}



filter_method_year_ceta_year = df0['taxonID'].str.contains("Cetacean", na=False)

df0[filter_method_year_ceta_year]

for year_ceta in dict_method_ceta.keys():
    df0.loc[np.logical_and(filter_method_year_ceta_year, df0['year']== year_ceta), 'samplingProtocol'] = dict_method_ceta[year_ceta]
    print(df0.loc[np.logical_and(filter_method_year_ceta_year, df0['year']== year_ceta), ['year','samplingProtocol']] )



# samplingProtocol_spyder

dict_method_spyder = {
2008:	'Opportunistic observation during other taxonomic surveys'
}

filter_method_spyder_year = df0['taxonID'].str.contains("Spider", na=False)

for year_spyder in dict_method_spyder.keys():
    df0.loc[np.logical_and(filter_method_spyder_year, df0['year']== year_spyder), 'samplingProtocol'] = dict_method_spyder[year_spyder]
    print(df0.loc[np.logical_and(filter_method_spyder_year, df0['year']== year_spyder), ['year','samplingProtocol']] )





# samplingProtocol_insect

dict_method_insect = {1994:	'The survey was conducted without a description of the methods.',
1997:	'',
2002:	'',
2003:	'',
2005:	'',
2008:	'Line Transect Survey | Aerial Netting | Host Plant Recognition | Hand Sorting Method | Bait Method',
2009:	'The survey was conducted without a description of the methods.',
2010:	'The survey was conducted without a description of the methods.',
2011:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2012:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2013:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2014:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2015:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2016:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2017:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2018:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2019:	'Visual Search Method | Sweeping Net Method',
2020:	'Aerial Netting | Sweeping Net Method | Beat Sheet Method | Sieving Method | Aquatic Sieving | Visual Search Method | Trap Method | Bait Method',
2021:	'Aerial Netting | Sweeping Net Method | Hand Sorting Method | Sieving Method',
2022:	'Aerial Netting | Sweeping Net Method | Hand Sorting Method | Sieving Method',
2023:	'Line Transect Survey (Aerial Netting | Sweeping Net Method | Hand Sorting Method | Sieving Method)',
2024:	'Line Transect Survey (Aerial Netting | Sweeping Net Method | Hand Sorting Method | Sieving Method)',
2025:	'Line Transect Survey (Aerial Netting | Sweeping Net Method | Hand Sorting Method | Sieving Method)'
}





filter_method_insect_year = df0['taxonID'].str.contains("Insect", na=False)

for year_insect in dict_method_insect.keys():
    df0.loc[np.logical_and(filter_method_insect_year, df0['year']== year_insect), 'samplingProtocol'] = dict_method_insect[year_insect]
    print(df0.loc[np.logical_and(filter_method_insect_year, df0['year']== year_insect), ['year','samplingProtocol']] )






# samplingProtocol_Fish


dict_method_fish = {
2011:	'Line Transect Survey (30 m * 5 m)',
2020:	'Snorkeling'
}


filter_fish = df0['taxonID'].str.contains('Fish', na=False)


for year_fish in dict_method_fish.keys():    
    df0.loc[np.logical_and(filter_fish , df0['year']== year_fish), 'samplingProtocol'] = dict_method_fish[year_fish]
    print(df0.loc[np.logical_and(filter_fish , df0['year']== year_fish), ['year','samplingProtocol']] )
    


a1_fish = df0.loc[filter_fish, 'samplingProtocol']



# samplingProtocol_BenthicInvertebrate


dict_method_BenthicInvertebrate = {
2018:	'Intertidal Visual Encounter Survey',
2020:	'Snorkeling | Intertidal Visual Encounter Survey',
2022:	'Intertidal Line Transect Survey | Intertidal Qualitative Survey | Roving Diver Method',
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
    print(df0.loc[np.logical_and(filter_benthic, df0['year']== year_benthic), ['year','samplingProtocol']] )
    

a1_benthic = df0.loc[filter_benthic, 'samplingProtocol']







# Translate_samplingProtocol_Reptiles

filter_method_reptile_year = df0['taxonID'].str.contains("Reptile", na=False)

#filter_method_reptile_year = np.logical_and(df0['year']>=2011, df0['year']<=2011)

for year_reptile in [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2020]:
    df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), 'samplingProtocol'] ='Line Transect Survey'
    print(df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), ['year','samplingProtocol']] )



for year_reptile in [2021, 2022, 2023, 2024, 2025]:
    df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), 'samplingProtocol'] = 'Opportunistic observation during other taxonomic surveys'
    print(df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), ['year','samplingProtocol']] )


for year_reptile in [1994, 2008, 2009, 2010]:
    df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), 'samplingProtocol'] = 'The survey was conducted without a description of the methods.'
    print(df0.loc[np.logical_and(filter_method_reptile_year, df0['year']== year_reptile), ['year','samplingProtocol']] )



filter_coordinate_null_reptile1 =  np.logical_and( df0['decimalLongitude'].isna(),  df0['scientificName'].str.contains('Gekko hokouensis', na = False))
df0.loc[filter_coordinate_null_reptile1,'decimalLongitude'] = 122.105349
df0.loc[filter_coordinate_null_reptile1,'decimalLatitude'] = 25.484834
df0.loc[filter_coordinate_null_reptile1,'coordinateUncertaintyInMeters'] =  400


filter_coordinate_null = df0['decimalLongitude'].isna()
df0.loc[filter_coordinate_null,'decimalLongitude'] = 122.105349
df0.loc[filter_coordinate_null,'decimalLatitude'] = 25.484834
df0.loc[filter_coordinate_null,'coordinateUncertaintyInMeters'] =  600






dict_method_algae = {
2020:	'The survey was conducted without a description of the methods.',
2024:	'Intertidal Qualitative Survey'
}

for year_algae in dict_method_algae.keys():
    filter_method_algae = np.logical_and( df0['taxonID'].str.contains('Algae', na = False), df0['year']==year_algae)
    df0.loc[filter_method_algae, 'samplingProtocol'] = dict_method_algae[year_algae]




# Reclassify
filter_name1 =np.logical_and(df0['scientificName']=='Gallinago', df0['taxonRank'].str.contains('family', na=False))
df0.loc[filter_name1,'taxonRank'] = 'genus'


filter_name2 =np.logical_and(df0['scientificName']=='Geometridae', df0['taxonRank'].str.contains('genus', na=False))
df0.loc[filter_name2,'taxonRank'] = 'family'


filter_name3 =np.logical_and(df0['scientificName']=='Lepismatidae', df0['taxonRank'].str.contains('genus', na=False))
df0.loc[filter_name3,'taxonRank'] = 'family'


filter_name4 =np.logical_and(df0['scientificName']=='Ichneumonidae', df0['taxonRank'].str.contains('genus', na=False))
df0.loc[filter_name4,'taxonRank'] = 'family'

filter_name5 =np.logical_and(df0['scientificName']=='Ornebius bimaculatus', df0['taxonRank'].str.contains('genus', na=False))
df0.loc[filter_name5,'taxonRank'] = 'species'


filter_name6 =np.logical_and(df0['scientificName']=='Scymnus fuscatus', df0['taxonRank'].str.contains('genus', na=False))
df0.loc[filter_name6,'taxonRank'] = 'species'


filter_name7 =np.logical_and(df0['scientificName']=='Cellana toreuma', df0['taxonRank'].str.contains('subspecies', na=False))
df0.loc[filter_name7,'taxonRank'] = 'species'





# abbreviation

filter_abbrev = df0['samplingProtocol'].str.contains('BRUV', na=False)
df0.loc[filter_abbrev, 'samplingProtocol']= df0.loc[filter_abbrev, 'samplingProtocol'].str.replace('BRUV','Baited Remote Underwater Video')




# df0.loc[filter_group,'order']= 'Cetacea'  #鯨目
# df0.loc[filter_group,'order']='Cetartiodactyla' #鯨偶蹄目


df0['samplingProtocol']=df0['samplingProtocol'].str.strip()



#Taxon_verbatimIdentification
df0['verbatimIdentification'] = df0['scientificName'] 
filter_taxon_avian1= df0['vernacularName'] == '極北柳鶯複合群'
df0.loc[filter_taxon_avian1,'taxonID'] 
df0.loc[filter_taxon_avian1,'scientificName'] 
df0.loc[filter_taxon_avian1,'verbatimIdentification'] = 'Phylloscopus xanthodryas | borealis | examinandus'


filter_taxon_avian2 = df0['vernacularName'] == '冠紋柳鶯複合群'
df0.loc[filter_taxon_avian2,'taxonID'] 
df0.loc[filter_taxon_avian2,'scientificName'] 
df0.loc[filter_taxon_avian2,'verbatimIdentification'] = 'Phylloscopus reguloides | claudiae | goodsoni'

filter_taxon_avian= df0['vernacularName'] == '柳鶯屬'
df0.loc[filter_taxon_avian,'taxonID'] 
df0.loc[filter_taxon_avian,'scientificName'] 




# samplingProtocol
filter_coordinate_null = df0['samplingProtocol'].isna()
a1 = df0.loc[filter_coordinate_null,:] 






# Locality

df0['locality'] = df0['locality'].str.replace('棉花嶼周圍海域', 'waters surrounding Mianhua Islet')
df0['locality'] = df0['locality'].str.replace('棉花嶼周邊海域', 'waters surrounding Mianhua Islet')

df0['locality'] = df0['locality'].str.replace('基隆到北方三島的海域', 'waters off Keelung')
df0['locality'] = df0['locality'].str.replace('基隆嶼至棉花嶼的海域', 'waters off Keelung')

df0['locality'] = df0['locality'].str.replace('棉花嶼_植物_火災樣區', 'MianhuaIslet_Plant_PostFire')
df0['locality'] = df0['locality'].str.replace('棉花嶼_植物', 'MianhuaIslet_Plant')
df0['locality'] = df0['locality'].str.replace('棉花嶼', 'Mianhua Islet')

a1=df0['locality'].unique()








df0.to_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260722_1500_API_name.csv'), encoding='utf_8_sig', index= False)



'''
# remove columns :['lifeStage', 'associatedMedia']
# add columns :['id', 'kingdom', 'countryCode', 'verbatimIdentification']

'''



#Remove columns
df0 = df0.drop(['Api_name_v2','Api_name_v1', 'higherClassification', 'rank', 'status','confidence', 'matchType', 'phylum', 'class', 'order', 'family','genus', 'species'], axis=1)
df0 = df0.drop(['lifeStage', 'associatedMedia'], axis=1)

#df0.to_csv(os.path.join(input_path, '9_gbif_KL_occurrence_till_20251230_all_20260722_1500_WO_API_name.csv'), encoding='utf_8_sig', index= False)





df0_indx = df0.dropna(axis = 'index', how ='all')
df0_column = df0.dropna(axis = 'columns', how ='all')


col_df0 = set(df0.columns)
col_dfc = set(df0_column.columns)
print(col_df0 - col_dfc)







#%%


occur_taxonID = df0['taxonID'].unique()
occur_scientificName = df0['scientificName'].unique()


taxon_taxonID = df_taxon['taxonID'].unique()
taxon_scientificName= df_taxon['scientificName'].unique()



differ_scientificName = set(taxon_scientificName) - set(occur_scientificName)

differ_taxonID= set(taxon_taxonID) - set(occur_taxonID)






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
