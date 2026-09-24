# -*- coding: utf-8 -*-
"""
The Survey Data of Mianhua and Huaping Islets Wildlife Refuge

Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.

@author: Jui-Wen Chang (Ceta explorers Co., Ltd)

"""



#% conda install -c rpy2
#% conda install -c r-vegan





#%% Import Packages, Input files

# import Standard Library
import os
import re
import sys

# import Third-party Packages
import chardet
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd




# =============================================================================
# II. Path Management and set the fontname of figures
# =============================================================================

matplotlib.rcParams['font.family'] = ['Times New Roman', 'sans-serif']


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
#output_path_csv = os.path.join(output_path, 'csv/')

output_path_counts = os.path.join(output_path, 'species_counts_yearly1/')
output_path_sac = os.path.join(output_path, 'species_accumulation_curve1/')



for folder in [output_path, output_path_sac, output_path_counts]:
    os.makedirs(folder, exist_ok=True)
    


#%% 

# =============================================================================
# III. Data Processing & Ecological Modeling
# =============================================================================

year_min = 1994

year_max = 2025

int(year_max + 1)

#I.Check data integrity
content = os.listdir(input_path)
content = sorted(content)
#os.chdir(input_path)


data_extension=pd.DataFrame([])

#Confirm unique ID
for file_id in range(0,len(content)): #  1 Taxon Table + 1 Measurement Table + 9 taxonomic groups [ range(0,11) ]

    # 1. Detect Encoding
    with open(os.path.join(input_path, content[file_id]), 'rb') as f:
        # read 10000 bytes (10 KB) to detect encoding
        result = chardet.detect(f.read(10000))
        print(result['encoding'])           
        if (result['encoding']=='Big5'):
              encoding_name='cp950'
        elif (result['encoding']=='Windows-1252'):
              encoding_name="ANSI"   
        elif (result['encoding']=='Windows-1254'): 
              #encoding_name="cp1254"        
              #encoding_name="ibm-1254"
              encoding_name="ANSI"
        else:
              encoding_name="utf-8"

    if file_id==0: # Make Sure that taxonID is unique
        data_taxon=pd.read_csv(os.path.join(input_path, content[file_id]), encoding= encoding_name)
        data_taxon=data_taxon.sort_values(by=['taxonID'])
        
        data_taxonID=data_taxon.value_counts('taxonID', sort=True)
        data_taxonID=data_taxonID.reset_index()
        data_taxonID=data_taxonID.sort_values(by=['taxonID'])
        
        
        if len(data_taxonID)==len(data_taxon):
            print(f'{content[file_id]}: taxonID is unique.')
        else:
            print(f'{content[file_id]}: The taxonID is NOT unique!\n')


            # If there is no unique in taxonID, compare it piarwisely.
            for indexID in range(0, min([len(data_taxon),len(data_taxonID)]), 1):
                if not data_taxon.iloc[indexID,3] == data_taxonID.iloc[indexID,0]:
                    print(f'raw data is: {data_taxon.iloc[indexID,:]}\n')
                    
                    print(f'data count is: {data_taxonID.iloc[indexID,0]}')
                    break
  
    else:
        data1_check=pd.read_csv(os.path.join(input_path, content[file_id]), encoding= encoding_name)
        # Make Sure that occurrenceID is unique
        if ('occurrenceID' in list(data1_check.columns)) and ('measurementType' not in list(data1_check.columns)):
            data_occurrenceID = data1_check.value_counts('occurrenceID', sort=True)
            if len(data_occurrenceID) == len(data1_check):
                data_extension = pd.concat([data_extension, data1_check], ignore_index=True)
                print(f'{content[file_id]}: occurrenceID is unique.')
            else:
                print(f'{content[file_id]}: The occurrenceID is NOT unique!\n')
    


# Deal with 'verbatimEventDate' to sort records
filter_only_year = data_extension['eventDate'].str.len()==4
data_extension['verbatimEventDate'] = data_extension['eventDate']
data_extension.loc[filter_only_year,'verbatimEventDate'] = data_extension.loc[filter_only_year,'verbatimEventDate']+"-00-00"
data_extension['verbatimEventDate'] = data_extension['verbatimEventDate'].str.replace('/','-')


# Check for the unique count of `taxonID` in Taxon Table and Occur Table
data_extension_taxon= data_extension.value_counts('taxonID', sort=True)
data_extension_taxon= data_extension_taxon.reset_index().sort_values(by=['taxonID'])
a1=set(data_extension_taxon['taxonID'].values)
a2=set(data_taxonID['taxonID'].values)


data_extension['taxonRank'].unique()
filter_rank = data_extension['taxonRank'].isin(['kingdom', 'phylum', 'class', 'order', 'family', 'subfamily', 'genus', 'species' ,'subspecies', 'variety' ])
data_extension[filter_rank]


#%% #II. Statistics of the data



#os.chdir(input_path)


# Tabel for Taxon Yearly Counts , Table for Species Accumulation Model (SAC)
data_yearly_taxon_counts = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_yearly_occur_counts = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_species_ratio = pd.DataFrame([],index=['species_lower', 'taxon_all', 'ratio'])
data_species_cumulative0 = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_species_increment0=  pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))


# To store ecological metrics for final reporting

# 2. Load Data
for file_id in range(1,len(content)): #range(0,len(sheet_name)-1)
    file_name = content[file_id]
    taxon_group_name = file_name[:-4].split('_')[1]
    
    #check the encoding format
    with open(os.path.join(input_path, content[file_id]), 'rb') as f:
        result = chardet.detect(f.read())
        print(f"{file_name} : {result['encoding']}")    
        
        if (result['encoding']=='Big5'):
              encoding_name='cp950'
        elif (result['encoding']=='Windows-1252'):
              encoding_name="ANSI"   
        elif (result['encoding']=='Windows-1254'): 
              #encoding_name="cp1254"        
              #encoding_name="ibm-1254"
              encoding_name="ANSI"
        else:
              encoding_name="utf-8"
              
              

    data0 = pd.read_csv(os.path.join(input_path, content[file_id]), encoding= encoding_name)

    if ('occurrenceID' in list(data0.columns)) and ('measurementType' not in list(data0.columns)) and (not bool(re.search('Spider', content[file_id]))):
        
        data0['year'] = data0['year'].astype('Int64')  #型別
        data0['month'] = data0['month'].astype('Int64')
        data0.sort_values(['year'],ascending=True, ignore_index=True, inplace=True) #將年份排序
        
        # Sort by 'eventDate' and 'verbatimEventDate'
        data0['eventDate'] = data0['eventDate'].astype('str')
        filter_only_year = data0['eventDate'].str.len()==4
        data0['verbatimEventDate'] = data0['eventDate']
        data0.loc[filter_only_year,'verbatimEventDate'] = data0.loc[filter_only_year,'verbatimEventDate']+"-00-00"
        data0.sort_values(['verbatimEventDate'],ascending=True, ignore_index=True, inplace=True) 
        
        # =============================================================================
        #         Goal: Filter the occurrences with taxonRank euqals species.
        #         edit the occurrences with taxonRank lower than species (subspecies, 'variety' ) into species.
        #         remove the occurrences with taxonRank higher than species
        # =============================================================================
        
        
        # 3. Data Wrangling (Clean and Filter)
        data0['name_split'] = data0['scientificName'].str.strip().str.split()

        #data0['name_split_2words'] = [[a1[0], a1[1]] if len(a1)>=2 else [a1[0]] for a1 in  data0['name_split']   ]
        data0['name_split_2words'] = data0['name_split'].apply(lambda x: x[:2] if (isinstance(x, list) and len(x)>=2 ) else x)
        
        # Extract Binomial Nomenclature (Genus + Specific epithet)
        data0['name_species'] = data0['name_split_2words'].str.join(' ')
        

        
        #Assign data1 : Filter the occurrences with taxonRank euqals species.
        data0['taxonRank'] = data0['taxonRank'].str.strip().str.lower()
        data_extension['taxonRank'] = data_extension['taxonRank'].replace('varietas', 'variety')
        
        # Filter for species/subspecies level  # "20260921": "add variety"
        
        # filter_species1 = np.logical_or(data0['taxonRank']=='species', data0['taxonRank']=='subspecies')
        # filter_species1 = np.logical_or(filter_species1, data0['taxonRank']=='variety')
        
        # filter_species2= ((data0['taxonRank']=='species') | (data0['taxonRank']=='subspecies') | (data0['taxonRank']=='variety'))
        # filter_species3 = data0['taxonRank'].isin(['species', 'subspecies', 'variety'])
        filter_species = ((data0['taxonRank']=='species') | (data0['taxonRank']=='subspecies') | (data0['taxonRank']=='variety'))
        

        
        # Count the Ratio between (species with lower rank counts) and (all taxon counts).!
        data_species_ratio[taxon_group_name] = [data0.loc[filter_species, "name_species"].nunique(),
                                                data0.loc[:, "name_species"].nunique(),
                                                np.round(data0.loc[filter_species, "name_species"].nunique()/data0["name_species"].nunique(), 2) ]
        data1 = data0[filter_species].copy()
        


        #3-1. Annual Species Counts
        data_taxon_yearly = data1.groupby(['year'])['name_species'].nunique(dropna=True).to_frame()
        # X axis is Years.
        #data_yearly_taxon_counts[f'{taxon_group_name}']=0   #index is "Year"，匯入總整理資料
        data_yearly_taxon_counts.loc[list(data_taxon_yearly.index), [f'{taxon_group_name}'] ] = data_taxon_yearly.loc[list(data_taxon_yearly.index)].values
        
        
        #3-2_Python. Yearly Species Accumulation Curve (SAC)        
        taxon_unique_years = np.sort(data1['year'].dropna().unique())


# =============================================================================
#     #3-2_python: Calculate number of species before "beforeyear" of 8 Groups
        
        taxon_cumulative = data1[['name_species','year']].dropna().drop_duplicates()   
        
        species_cumulative0 = {y : 0 for y in taxon_unique_years }  
        taxon_sample_yearly_times = {} # Number of species in one year
        #beforeyear=2025
        
        for beforeyear in taxon_unique_years:   #np.array(data1['year'].unique())
            # taxon_beforeyear=taxon_cumulative.loc[taxon_cumulative['year']<=beforeyear,'name_species'].value_counts()
            # len(taxon_beforeyear)      
            species_cumulative0[beforeyear] = taxon_cumulative.loc[taxon_cumulative['year'] <= beforeyear,'name_species'].nunique()         # number of species before "beforeyear"
            taxon_sample_yearly_times[beforeyear] = taxon_cumulative.loc[taxon_cumulative['year'] == beforeyear,'name_species'].nunique()    # number of species in one year



        #3-3: Calculate the increment in SAC.
        species_increment0={}
        for i, y in enumerate(taxon_unique_years) :
            if i==0:
                species_increment0[y] = species_cumulative0[y]
            elif i!=0 :
                year_previous = taxon_unique_years[i-1]
                species_increment0[y] = species_cumulative0[y] - species_cumulative0[year_previous]


        data_species_sample_year_cum = pd.DataFrame.from_dict(species_cumulative0 , orient='index',columns=[f'{taxon_group_name}'])
        data_species_sample_year_incr = pd.DataFrame.from_dict(species_increment0, orient='index', columns=[f'{taxon_group_name}'])  
        
        data_species_sample_year_cum.to_csv(output_path_sac + f'mhhp_yearly_species_accumulation_curve_{taxon_group_name}.csv', 
                                                sep=',', index=True, index_label='Year', encoding='utf_8')
        
        
        data_species_sample_year_cum.index = data_species_sample_year_cum.index.astype("str")
        
        
        
        
        # From year_min To year_max (1994-2025)
        data_species_cumulative0[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_cumulative0 , orient='index',columns=[f'{taxon_group_name}'])
        data_species_increment0[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_increment0, orient='index', columns=[f'{taxon_group_name}'])  
        

        
        # Plot: yearly_species_accumulation_curve in Survey Year Order
        
        fig2,ax2 = plt.subplots(1,1, figsize=(6,4), dpi=300)
        size_point=20 #the size of the point
        if  taxon_group_name in ['Avian','Plant','Insect']:
            xlabel_rotate = 90
        elif taxon_group_name in ['Cetacean','Fish','BenthicInvertebrate']:
            xlabel_rotate = 40
        else:
            xlabel_rotate = 90
        
        data_species_sample_year_cum.plot(ax=ax2)
        ax2.scatter(x = list(data_species_sample_year_cum.index) , y = data_species_sample_year_cum[f'{taxon_group_name}'],
                          s=size_point, marker='o')
        
        ax2.set_xticks(range(0,len(data_species_sample_year_cum)))
        ax2.set_xticklabels(list(data_species_sample_year_cum.index) , rotation= xlabel_rotate, fontsize=15)
        ax2.set_xlabel('Survey Year', fontsize=18)
        
        # if file_id==4:
        #     ax2.set_yticks(range(0,data_species_sample_year_cum.max().values[0]+2, 1) )
        #     ax2.set_yticklabels(range(0, data_species_sample_year_cum.max().values[0]+2, 1), fontsize=15 )
        
        #set the y label as interger value
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        ax2.tick_params(axis='y', labelsize=15)      
        ax2.set_ylabel('Species Counts', fontsize=18)
        ax2.legend([f'{taxon_group_name}'], fontsize=20)
        
        plt.tight_layout(rect= [0, 0, 1, 1])
        fig2.savefig(output_path_sac + f'mhhp_yearly_species_accumulation_curve_{taxon_group_name}.png')        


# =============================================================================


        #I.計算這個種類的生物在整年份的目擊分布>>使用所有的taxon occurrences(data0)
        data_year = data0.groupby('year')['occurrenceID'].size().to_frame(name=f'{taxon_group_name}')
        
        #單一物種整年份的目擊分布>>彙整至全部種類整年份的分布
        #data_yearly_occur_counts[f'{taxon_group_name}']=0  

        # index is years: Inset into yearly tables.
        data_yearly_occur_counts.loc[data_year.index, f'{taxon_group_name}']=data_year.loc[data_year.index, f'{taxon_group_name}'].values
        
        # index is not years: Inset into yearly tables.
        #data_yearly_occur_counts.loc[data_year['year'].values, f'{taxon_group_name}'] = data_year.loc[data_year['year']==data_year['year'].values, f'{taxon_group_name}'].values
        

    else:
        print(f'Will not process this file: {content[file_id]}')
        
        
     
        
# I.Save the Table: yearly_species_counts_8_groups    
data_species_ratio.to_csv(output_path_counts + 'mhhp_yearly_species_ratio_8_groups.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')

data_yearly_taxon_counts.to_csv(output_path_counts + 'mhhp_yearly_species_counts_8_groups.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')


# II. Save the Table: yearly_species_accumulation_curves_8_groups
data_species_cumulative0.to_csv(output_path_sac +'mhhp_yearly_species_accumulation_8_groups_richness_raw.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')

data_species_increment0.to_csv(output_path_sac +'mhhp_yearly_species_increments_8_groups_richness.csv',sep=',',
                               index=True, index_label='Year', encoding='utf_8')




#%% 2-2. Count the boolean of survey targets in each year (0 | 1).



# "data_yearly_occur_counts" is the number of occurrences of the survey targets in each year.
# Count the boolean of survey targets in each year (0 | 1).

data_year_category_group = data_yearly_occur_counts>0
data_year_category_group = data_year_category_group.astype('int64')

# Delete it : If there isn't any survey targets in that year.
data_year_category_group['sum'] = data_year_category_group.sum(axis=1).values
drop_index1=list(data_year_category_group[data_year_category_group['sum']==0].index)
data_year_category_group.drop(drop_index1, inplace=True)
data_year_category_group.to_csv(output_path_counts +'mhhp_yearly_survey_targets_boolean_8_groups.csv',
                                sep=',',index=True, index_label='Year', encoding='utf_8')



#%% III. Visualizations 



 #3-1.Export 8 figures of mhhp_annual_species_counts
# Use the Variable to plot
data_yearly_counts_fig = data_yearly_taxon_counts.copy()


data_yearly_counts_fig = data_yearly_counts_fig.fillna(0).astype('int')
ylabel_name='Species Counts'


# data_yearly_counts_fig.columns
#['Algae', 'Avian', 'Benthic Invertebrate', 'Cetacean', 'Fish', 'Plant', 'Reptile', 'Insect']


color_category={
 'Algae':'#6ccb59',
 'Avian':'#ff9a03',
 'BenthicInvertebrate':'#46859c',
 'Cetacean':'#6ccbef',
 'Fish':'#4685ff',
 'Plant':'#077148',
 'Reptile':'#61396e',
 'Insect':'#613901'}


data_yearly_counts_fig.columns
['Algae', 'Avian', 'BenthicInvertebrate', 'Cetacean', 'Fish', 'Insect',
       'Plant', 'Reptile']

for category1 in [
  'Algae',
  'Avian',
  'BenthicInvertebrate',
  'Cetacean',
  'Fish',
  'Plant',
  'Reptile',
  'Insect']:

    fig0, axis0=plt.subplots(1,1, dpi=300)
    bar0=axis0.bar(data_yearly_counts_fig.index, data_yearly_counts_fig[category1], color= color_category[category1])
    

        
    #set the legend
    if category1== 'BenthicInvertebrate':
        category1 = 'Benthic Invertebrate'
        
    bar0.set_label(category1)
    axis0.legend(prop = {"size":25})

    
    #Set the Y interval to integer.
    axis0.yaxis.set_major_locator(MaxNLocator(integer=True))
    # Set the fontsize of Y label
    axis0.tick_params(axis='y',labelsize=15)
    axis0.tick_params(axis='x',labelsize=15)
    
    
    
    
    axis0.set_xlabel('Year', fontsize=20)
    axis0.set_ylabel(ylabel_name, fontsize=20)
    plt.tight_layout()
    fig0.savefig(output_path_counts + f'mhhp_yearly_species_counts_{category1}.png')




#%% 3-2.Export 1 figure of annual_species_counts_8_subplots


fig_row_counts = 3


fig1,axis1=plt.subplots(3,2, dpi=300, figsize=(11.69, 8.27))
turn=0
for category1 in [
# 'Algae',
 'Avian',
 'Fish',
 'Insect',
 'Cetacean',
 'BenthicInvertebrate',
 'Plant',
# 'Reptile',
# 'Spider'
 ]:
    
    row1=np.mod( turn, fig_row_counts)
    column1=int( np.floor(turn/fig_row_counts) )
    data_yearly_counts_fig[category1]=data_yearly_counts_fig[category1].astype('Int64')
    
    #line1,=axis1[row1,column1].plot(data_yearly_counts_fig['year'], data_yearly_counts_fig[category1], color='black')
    bar1=axis1[row1,column1].bar(data_yearly_counts_fig.index, data_yearly_counts_fig[category1], color=color_category[category1])
   
    #set the legend
    if category1== 'BenthicInvertebrate':
        category1 = 'Benthic Invertebrate'
    bar1.set_label(category1)
    axis1[row1,column1].legend(prop={"size":25})
    
    #Set the Y interval to integer.
    axis1[row1,column1].yaxis.set_major_locator(MaxNLocator(integer=True))
    # Set the fontsize of Y label
    axis1[row1,column1].tick_params(axis='y',labelsize=20)
    axis1[row1,column1].set_xlabel('Year', fontsize=20)
    axis1[row1,column1].set_ylabel(ylabel_name, fontsize=20)
    
    axis1[row1,column1].set_xticks(range(1995, int(year_max + 1), 5))
    axis1[row1,column1].set_xticklabels(range(1995, int(year_max + 1), 5) ,fontsize=20)
    
    axis1[row1,column1].tick_params(axis='y', labelsize = 15)

    
    turn=turn+1

plt.tight_layout()
fig1.savefig(output_path_counts + 'mhhp_yearly_species_counts_6subplots.png')
#plt.show()





#%% 3-3. Export 1 figure of 1 subplot of 8 species_accumulation_curves



data_species_cumulative_fig = data_species_increment0.fillna(0).cumsum().astype('int')



# data_species_cumulative_fig.columns=['year',
#  'Algae',
#  'Avian',
#  'Benthic Invertebrate',
#  'Cetacean',
#  'Fish',
#  'Plant',
#  'Reptile',
#  'Insect']



fig2, axis2=plt.subplots(1,1, dpi=300, figsize=(6, 4))
for category2 in [
# 'Algae',
 'Avian',
 'Fish',
 'Insect',
 'Cetacean',
 'BenthicInvertebrate',
 'Plant',
# 'Reptile'
 ]:

    
    line2,= axis2.plot(data_species_cumulative_fig.index, data_species_cumulative_fig[category2],
                      color=color_category[category2], linewidth=2)
    
    #set the legend
    if category2 == 'BenthicInvertebrate':
        category2 = 'Benthic Invertebrate'    
    line2.set_label(category2)
    
    axis2.set_xlabel('Year', fontsize=15)
    axis2.set_ylabel('Cumulative Species Counts', fontsize=15)
    
    axis2.set_xticks(range(1995, int(year_max + 1), 5))
    axis2.set_xticklabels(range(1995, int(year_max + 1), 5) , fontsize=15)
    
    axis2.tick_params(axis='y', labelsize=15)


#axis2.legend(title='8 Groups',title_fontsize=12 ,prop={'size':11})
axis2.legend(frameon=False, prop={'size':10})
plt.tight_layout()
fig2.savefig(output_path_sac + 'mhhp_yearly_species_accumulation_curves_6_groups_raw.png')

#plt.show()



#%%   

