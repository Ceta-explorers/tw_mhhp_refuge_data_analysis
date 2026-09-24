# -*- coding: utf-8 -*-
"""
The Survey Data of Mianhua and Huaping Islets Wildlife Refuge

Copyright (c) 2026 Jui-Wen Chang and Ceta explorers Co., Ltd.
Licensed under the CC BY 4.0 License.

@author: Jui-Wen Chang (Ceta explorers Co., Ltd)

"""



#% conda install -c rpy2
#% conda install -c r-vegan




# =============================================================================
# 
# 
# Oksanen, J., Simpson, G. L., Blanchet, F. G., Kindt, R., Legendre, P., Minchin, P. R., ... & Wagner, H. (2024).
# vegan: Community Ecology Package. R package version 2.6-4. https://CRAN.R-project.org/package=vegan
# 
#
#
#  Sample-based 與 Individual-based
#  Gotelli, N. J., & Colwell, R. K. (2001). Quantifying biodiversity: 
#  procedures and pitfalls in the measurement and comparison of species richness. Ecology Letters, 4(4), 379-391.
# 
#
# 針對 method = "exact" (基於樣本的精確稀疏化公式) 的數學證明：
# Chiarucci, A., Bacaro, G., Rocchini, D., & Fattorini, L. (2008). 
# Discovering and rediscovering the sample-based rarefaction formula in the ecological literature. 
# Community Ecology, 9(1), 121-123.
#
#
#
# =============================================================================




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
# I. R Environment Setup (rpy2)
# =============================================================================

# 1. Create the folder path for R.

# find the path of the environment
conda_prefix = sys.prefix

if os.name =='nt':
    r_path = os.path.join(conda_prefix, 'Lib', 'R' )
else:
    r_path = os.path.join(conda_prefix, 'lib', 'R' )
os.environ['R_HOME'] = r_path
#os.environ['R_HOME'] = r'C:\Users\cetae\anaconda3\envs\env_geo\Lib\R'



# 2. delete variable of 'R_USER' 
if 'R_USER' in os.environ:
    del os.environ['R_USER']
    
# R Environment Setup (rpy2)
try:
    import rpy2.robjects.packages as rpackages
    from rpy2.robjects import pandas2ri
except Exception as error_env:
    print('can not import rpy2')
    print("Make sure to run:  `conda env create -f environment.yml` and activate the envirionment.")
    print(f'Please reaad the error {error_env}')
    sys.exit(1)
    
pandas2ri.activate()
        

# 4). import R packages
try:
    base = rpackages.importr('base')
    base.Sys_setlocale("LC_ALL", "English")
    vegan = rpackages.importr('vegan')
    stats = rpackages.importr('stats')
except Exception as error_import:
    print('can not import R packages')
    print("Make sure you installed `r-vegan` or run the R script `install.R`" )
    print(f'Please reaad the error {error_import}')
    sys.exit(1)



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

output_path_counts = os.path.join(output_path, 'species_counts_yearly/')
output_path_sac = os.path.join(output_path, 'species_accumulation_curve/')
output_path_model = os.path.join(output_path, 'species_accumulation_model/')


for folder in [output_path, output_path_sac, output_path_counts, output_path_model]:
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


# Tabel for SAC Models
data_species_cumulative0_raw = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_species_cumulative0_exact_value = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_species_cumulative0_exact_std = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))
data_species_increment0_exact = pd.DataFrame([],index=list(range(year_min, int(year_max + 1), 1)))




model_name = ["Lomolino", "Asymp", "Michaelis-Menten"]

data_species_cumulative0_aic = pd.DataFrame([],index= model_name )
data_species_cumulative0_pseudoR2 = pd.DataFrame([],index= model_name )
data_species_cumulative0_asym =   pd.DataFrame([],index= model_name )
data_species_cumulative0_unseen_num =  pd.DataFrame([],index= model_name )
data_species_cumulative0_unseen_per =  pd.DataFrame([],index= model_name )
data_species_cumulative0_complete = pd.DataFrame([],index= model_name )
data_species_cumulative0_fit_value = pd.DataFrame([])




#data_species_cumulative0_model = pd.DataFrame([],index=list(range(0,3,1)))


                                                              


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
        
        #將日期排序
        data0['eventDate'] = data0['eventDate'].astype('str')
        filter_only_year = data0['eventDate'].str.len()==4
        data0['verbatimEventDate'] = data0['eventDate']
        data0.loc[filter_only_year,'verbatimEventDate'] = data0.loc[filter_only_year,'verbatimEventDate']+"-00-00"
        data0.sort_values(['verbatimEventDate'],ascending=True, ignore_index=True, inplace=True) 
        
        # =============================================================================
        #         Goal: Filter the occurrences with taxonRank euqals species.
        #         edit the occurrences with taxonRank lower than species (subspecies) into species.
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
        #data_yearly_taxon_counts[f'{taxon_group_name}']=0   #index是年分，匯入總整理資料
        data_yearly_taxon_counts.loc[list(data_taxon_yearly.index), [f'{taxon_group_name}'] ] = data_taxon_yearly.loc[list(data_taxon_yearly.index)].values
        
        
        #3-2_Python. Yearly Species Accumulation Curve (SAC)        
        
        taxon_unique_years = np.sort(data1['year'].dropna().unique())

        

        #  3-2). Model of Sample-based species accumulation curve (SAC) in R scripts.
        # 1). convert table from long table (occurrence table) to  wide table (community matrix).
        data1_community_quan = pd.crosstab(data1['year'], data1['name_species'])
        data1_community_boolean = (data1_community_quan>0).astype('int')

        
        # 2). species accumulation curve of different methods. (random/exact/collector) in R code
        # Don't analysis "Algae , Reptile , Spider, or  less than 1 year survey" in SAC
        taxon_no_model = ['Algae','Reptile','Spider']
        taxon_no_model_re = '|'.join(taxon_no_model)        
        if len(data1_community_boolean)>1 and (not bool(re.search(taxon_no_model_re, content[file_id] ))): 
            
            sp1 = vegan.specaccum(data1_community_boolean, method= 'random')
            sp2 = vegan.specaccum(data1_community_boolean, method= 'collector')
            sp3 = vegan.specaccum(data1_community_boolean, method= 'exact')


            # 3)：Extract results of R, and convert to  Numpy Array.
            # ==========================================
            # exreact elements by using .rx2(), and convert to np.array().
            x_sites1 = np.array(sp1.rx2('sites'))
            y_richness1 = np.array(sp1.rx2('richness'))
            y_sd1 = np.array(sp1.rx2('sd'))
    
    
            x_sites2 = np.array(sp2.rx2('sites'))
            y_richness2 = np.array(sp2.rx2('richness'))
            #y_sd2 = np.array(sp2.rx2('sd'))        
            
            
            x_sites3 = np.array(sp3.rx2('sites'))
            y_richness3 = np.array(sp3.rx2('richness'))
            y_sd3 = np.array(sp3.rx2('sd'))
        
            y_mena3 = np.mean(y_richness3)
            TSS = np.sum( (y_richness3 -  y_mena3)**2 )


            # save results to Dataframe.
            sac_results = {
                'Years': taxon_unique_years,
                'NumYears': x_sites1,
                'Richness_coll': y_richness2,
                'Richness_exac': y_richness3,
                'SD_exact': y_sd3
            }
            
            
            species_cumulative0_raw = {}
            for yea, val in zip(taxon_unique_years, y_richness2) :
                species_cumulative0_raw[yea] = val
                
            
            species_cumulative0_exact_value = {}
            for yea, val in zip(taxon_unique_years, y_richness3) :
                species_cumulative0_exact_value[yea] = val            
            
            species_cumulative0_exact_std = {}
            for yea, val in zip(taxon_unique_years, y_sd3) :
                species_cumulative0_exact_std[yea] = val               
            
            
            # Calculate the increment in SAC.
            species_increment0={}
            for i, y in enumerate(taxon_unique_years) :
                if i==0:
                    species_increment0[y] = species_cumulative0_exact_value[y]
                elif i!=0 :
                    year_previous = taxon_unique_years[i-1]
                    species_increment0[y] = species_cumulative0_exact_value[y] - species_cumulative0_exact_value[year_previous]
    


            
            data_species_cumulative0_raw[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_cumulative0_raw , orient='index',columns=[f'{taxon_group_name}'])
            data_species_cumulative0_exact_value[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_cumulative0_exact_value, orient='index', columns=[f'{taxon_group_name}'])  
            data_species_cumulative0_exact_std[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_cumulative0_exact_std, orient='index', columns=[f'{taxon_group_name}']) 
            
            data_species_increment0_exact[f'{taxon_group_name}'] = pd.DataFrame.from_dict(species_increment0, orient='index', columns=[f'{taxon_group_name}'])  
            


            
            
            # ==========================================
            # 4：Fit with different Models
            # ==========================================
            
            try:
                mod1 = vegan.fitspecaccum(sp3, "lomolino")
                coeffs1 = stats.coef(mod1)
                Asym1 = coeffs1[0]
                xmid = coeffs1[1]
                slope = coeffs1[2]
                fit_mod1 = mod1.rx2('fitted')
                #res_mod1 = mod1.rx2('residuals')
                
                
                AIC1 = stats.AIC(mod1)[0]
                RSS_1 = np.sum( (y_richness3 - fit_mod1)**2)
                #RSS_1 = np.sum( mod1.rx2('residuals')**2)
                Pseudo1 = 1 - (RSS_1/TSS)
                unseen_num1 = Asym1 - fit_mod1[-1]
                unseen_per1 = ((Asym1 - fit_mod1[-1])/Asym1)*100
                survey_comp1 = (fit_mod1[-1]/Asym1) *100
                
                
                asym_mod1 = np.repeat(Asym1, len(fit_mod1), axis=0)
                predict_mod1 = stats.predict(mod1, newdata = np.arange(0,50,1))
                
            except Exception as error1:
                mod1 = np.nan
                coeffs1= np.nan
                Asym1 = np.nan
                fit_mod1 = np.nan
                
                AIC1 = np.nan
                RSS_1 = np.nan
                Pseudo1 = np.nan
                unseen_num1 = np.nan
                unseen_per1 = np.nan
                survey_comp1 = np.nan
                
                asym_mod1= np.nan
                predict_mod1 = np.nan

                print(error1)
                print(f"The model lomolino in {taxon_group_name} fails: mod1")

            try:
                mod2 = vegan.fitspecaccum(sp3, "asymp")
                coeffs2 = stats.coef(mod2)
                AIC2 = stats.AIC(mod2)[0]
                Asym2 = coeffs2[0]
                R0 = coeffs2[1]
                lrc = coeffs2[2]
                
                fit_mod2 = mod2.rx2('fitted')
                predict_mod2 = stats.predict(mod2, newdata = np.arange(0,50,1))
                asym_mod2 = np.repeat(Asym2, len(fit_mod2), axis=0)
                
                
                RSS_2 = np.sum( (y_richness3 - fit_mod2)**2)
                Pseudo2 = 1 - (RSS_2/TSS)
                
                unseen_num2 = Asym2 - fit_mod2[-1]
                unseen_per2 = ((Asym2 - fit_mod2[-1])/Asym2)*100
                survey_comp2 = (fit_mod2[-1]/Asym2) *100
     
                
            except Exception as error1:
                print(error1)             
                print(f"The model asymp in {taxon_group_name} fails: mod2")
                
            try:
                mod3 = vegan.fitspecaccum(sp3, "michaelis-menten")
                coeffs3 = stats.coef(mod3)
                AIC3 = stats.AIC(mod3)[0]
                Asym3 = coeffs3[0]
                Khalf = coeffs3[1]
                
                fit_mod3 = mod3.rx2('fitted')
                predict_mod3 = stats.predict(mod3, newdata = np.arange(0,50,1))
                asym_mod3 = np.repeat(Asym3, len(fit_mod3), axis=0)
                RSS_3 = np.sum( (y_richness3 - fit_mod3)**2)
                Pseudo3 = 1 - (RSS_3/TSS)
            
            
                unseen_num3 = Asym3 - fit_mod3[-1]
                unseen_per3 = ((Asym3 - fit_mod3[-1])/Asym3)*100
                survey_comp3 = (fit_mod3[-1]/Asym3) *100
                
            except Exception as error1:
                print(error1)            
                print(f"The model michaelis-menten in {taxon_group_name} fails: mod3")

            data_species_cumulative0_aic[f'{taxon_group_name}'] = [AIC1, AIC2, AIC3]
            data_species_cumulative0_pseudoR2[f'{taxon_group_name}'] =  [Pseudo1, Pseudo2, Pseudo3]
            data_species_cumulative0_asym[f'{taxon_group_name}'] =[Asym1, Asym2, Asym3]
            
            data_species_cumulative0_unseen_num[f'{taxon_group_name}'] = [unseen_num1, unseen_num2, unseen_num3]
            data_species_cumulative0_unseen_per[f'{taxon_group_name}'] =  [unseen_per1, unseen_per2, unseen_per3]
            data_species_cumulative0_complete[f'{taxon_group_name}'] =  [survey_comp1, survey_comp2, survey_comp3]
            
            

                


            # ==========================================
            # 5-1：check RSS and AIC
            # ==========================================              
            
            models = {
                "Lomolino": mod1,
                "Asymp": mod2,
                "Michaelis-Menten": mod3
            }
            colors = {"Lomolino": "purple", "Asymp": "blue", "Michaelis-Menten": "green"}

            figfit, axfit = plt.subplots(nrows=1, ncols=1, figsize= (8.27, 5.83), dpi=300)
            #figfit.suptitle(f'Model Fit for the Species Accumulation Curve of {taxon_group_name}', fontsize= 16, fontweight='bold', y=0.95)
            
            max_left_y = np.max(y_richness3)
            max_right_y = 0

            
            # Rarefaction curve (black points)
            axfit.plot(x_sites2, y_richness2, color='black', marker='o', linewidth=3, label='Species Accumulation in Survey Order')
            
            #axfit.scatter(x_sites3, y_richness3, color='red', alpha=0.2, label= 'Species Rarefaction of Expected Values', zorder=5)
            axfit.plot(x_sites3, y_richness3, color='red', alpha=0.4, marker='s', linewidth=2, label= 'Species Rarefaction of Expected Values')
            axfit.fill_between(x_sites3, 
                              y_richness3 - 2*y_sd3, 
                              y_richness3 + 2*y_sd3, 
                              color='red', alpha=0.2, label='± 2 Standard Deviation')
        
            #row = 0
            #col = 0
            
            num_predict = 50
            num_asym = 20
            for name, mod in models.items():
                try:
                    # 從 R 物件中提取「預測值」與「殘差」
                    y_fit = np.array(mod.rx2('fitted'))
                    coeffs = stats.coef(mod)
                    Asym = coeffs[0]
                    residuals = np.array(mod.rx2('residuals'))
                    predict_mod = stats.predict(mod, newdata = np.arange(0, num_predict, 1))
                    asym_mod = np.repeat(Asym, num_asym, axis=0)
                    
                    max_left_y = np.max([max_left_y, np.max(predict_mod), Asym])

                    
                    # --- Ledft Panel：Predict curve vs Rarefaction curve ---
                    ax_curve = axfit
                    
                    
                    #fit model
                    ax_curve.plot(np.arange(1, num_predict+1, 1), predict_mod, color= colors[name], marker='', linewidth=2.5, linestyle='--', label= f'{name} Fit')
                    
                    #save fitting value
                    data_species_cumulative0_fit_value[f'{taxon_group_name}_{name}'] = predict_mod
                    
                    #fit asymtptoc line
                    #ax_curve.plot(np.arange(1, num_asym+1, 1), asym_mod, color= colors[name], marker='', linewidth=2.5, linestyle='-' ) 


                    #ax_curve.set_title(f'{name} - Fitted Curve of {taxon_group_name}', fontsize=12)
                    ax_curve.set_xlabel('Number of Sampling Year', fontsize=20)
                    ax_curve.set_ylabel('Cumulative Species Counts', fontsize=20)
                                        
                    #ax_curve.legend(title=f'{taxon_group_name}', title_fontsize= 25 , prop={'size':17} )
                    

                    if 'Avian' in f'{taxon_group_name}':
                        ax_curve.legend(title=f'{taxon_group_name}', loc='lower right' ,title_fontsize= 20, prop={'size':15})
                        
                    else:
                        ax_curve.legend([f'{taxon_group_name}'], loc='lower right' , fontsize= 20 )

                except Exception as e:
                    data_species_cumulative0_fit_value[f'{taxon_group_name}_{name}'] = np.nan 
                    # If the model fails
                    print(f"Can not plot {name}: {e}")
                    
                # === 【新增】迴圈結束後，統一設定所有子圖的 Y 軸極限 ===
                for i in range(3):
                    # 左圖 Y 軸統一：從 0 開始，上限為整體最大值的 1.05 倍 (保留 5% 頂部空白空間)
                    ax_curve.set_ylim(0, max_left_y * 1.05)
                    
            
            ax_curve.tick_params(axis='y', labelsize= 20)
            ax_curve.tick_params(axis='x', labelsize= 20)
            #set the y label as interger value
            plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            plt.tight_layout(rect= [0, 0, 1, 1] )

            #plt.show()
            
            
            figfit.savefig(output_path_model + f'mhhp_yearly_species_accumulation_curve_model_{taxon_group_name}.png',
                           dpi= 500)  


            
            # ==========================================
            # 5-2：check RSS and AIC
            # ==========================================              
            
            models = {
                "Lomolino": mod1,
                "Asymp": mod2,
                "Michaelis-Menten": mod3
            }
            colors = {"Lomolino": "purple", "Asymp": "blue", "Michaelis-Menten": "green"}
            
            # "Lomolino": "#1A74A8"

            
            fig, axes = plt.subplots(nrows=3, ncols=2, figsize= (8.27, 11.69), dpi=300)
            fig.suptitle(f'Model Fit and Residual Analysis for Species Accumulation of {taxon_group_name}', fontsize=16, fontweight='bold', y=0.95)
            
            max_left_y = np.max(y_richness3)
            max_right_y = 0
            

            row = 0
            for name, mod in models.items():
                try:
                    # extract values in R objects
                    y_fit = np.array(mod.rx2('fitted'))
                    coeffs = stats.coef(mod)
                    Asym = coeffs[0]
                    residuals = np.array(mod.rx2('residuals'))
                    predict_mod = stats.predict(mod, newdata = np.arange(0,50,1))
                    
                    asym_mod = np.repeat(Asym, num_predict , axis=0)
                    
                    max_left_y = np.max([max_left_y, np.max(predict_mod), Asym])
                    max_right_y = np.max([max_right_y, np.max(np.abs(residuals))])
                    
                    
                    # --- Left： Prediction ---
                    ax_curve = axes[row, 0]
                    
                    # plot collector curve (black points)
                    ax_curve.plot(x_sites2, y_richness2, color='black', marker='o', linewidth=3, label='Species Accumulation in Survey Order')
                    #ax_curve.scatter(x_sites3, y_richness3, color='red', alpha=0.2, label='Species Rarefaction of Expected Values', zorder=5)
                    ax_curve.plot(x_sites3, y_richness3, color='red', alpha=0.2, marker='s', linewidth=2, label= 'Species Rarefaction of Expected Values')
                    
                    ax_curve.fill_between(x_sites3, 
                                      y_richness3 - 2*y_sd3, 
                                      y_richness3 + 2*y_sd3, 
                                      color='red', alpha=0.2, label='± 2 Standard Deviation')
                    
                    
                    # plot Prediction Curve with different color
                    ax_curve.plot(np.arange(1, num_predict+1, 1), predict_mod, color= colors[name], marker='', linewidth=2.5, linestyle='--', label=f'Model Fit of {name}') #fit model
                    
                    
                    ax_curve.plot(np.arange(1, num_predict+1, 1), asym_mod, color= colors[name], marker='', linewidth=2.5, linestyle='-') # label = f'The Saturation of {name}'
            
            
                    
                    ax_curve.set_title(f'{name} - Fitted Curve', fontsize=12)
                    ax_curve.set_xlabel('Years (Sampling Effort)')
                    ax_curve.set_ylabel('Species Richness')
                    ax_curve.legend()
                    ax_curve.grid(True, linestyle='--', alpha=0.5)
            
            

                    # --- Right：(Residual Plot) ---
                    ax_res = axes[row, 1]
                    # Residual Plot
                    ax_res.scatter(x_sites3, residuals, color=colors[name], alpha=0.7)
                    # Plot:  Y=0 
                    ax_res.axhline(0, color='black', linestyle='--', linewidth=1.5)
                    # (Lollipop Residual Plot)
                    ax_res.vlines(x_sites3, 0, residuals, color=colors[name], alpha=0.4)
                    
                    ax_res.set_title(f'{name} - Residuals of {taxon_group_name}', fontsize=12)
                    ax_res.set_xlabel('Years (Sampling Effort)')
                    ax_res.set_ylabel('Residuals (Observed - Predicted)')
                    ax_res.grid(True, linestyle='--', alpha=0.5)
                    
                except Exception as e:
                    # error
                    axes[row, 0].text(0.5, 0.5, f"{name} Model Failed", ha='center', fontsize=14, color='red')
                    axes[row, 1].text(0.5, 0.5, "No Residuals", ha='center', fontsize=14, color='red')
                    print(f"Can not plot {name}: {e}")
                    
                row += 1

            # === After loop，set Y Limit ===
            for i in range(3):
                # 左圖 Y 軸統一：從 0 開始，上限為整體最大值的 1.05 倍 (保留 5% 頂部空白空間)
                axes[i, 0].set_ylim(0, max_left_y * 1.05)
                
                # 右圖 Y 軸統一：以 0 為中心對稱，上下限為最大殘差絕對值的 1.1 倍 (保留 10% 空白空間)
                # 這樣 Y=0 的基準虛線就永遠會完美落在圖表的正中央！
                axes[i, 1].set_ylim(-max_right_y * 1.1, max_right_y * 1.1)
                
            plt.tight_layout(rect= [0, 0, 1, 0.95])
            #plt.show()
            
            fig.savefig(output_path_model + f'mhhp_yearly_species_accumulation_curve_fitting_{taxon_group_name}.png')  


            
            # ==========================================
            # 6：Plot smoothed SAC with Matplotlib
            # ==========================================            
    
            figr, axr = plt.subplots(1,1, figsize= (8.27, 5.83), dpi=500)
            
            # plot curve in Random Method
            # axr.plot(x_sites1, y_richness1, color='brown', marker='o', linewidth=2, label='Species Accumulation with Permutations.')
            
            
            # Plot Collector curve on the SAME effort axis (x_exact) so they align perfectly
            axr.plot(x_sites2, y_richness2, color= 'black', marker='o', linewidth=3, label='Species Accumulation in Survey Order')
            
            # plot curve in Exact Method
            axr.plot(x_sites3, y_richness3, color= 'red', alpha=0.4, marker='s', linewidth=4, label='Species Rarefaction of Expected Values') 
            
            
            
            
            # # plot Prediction Curve with completeness.
            axr.plot(np.arange(1, len(fit_mod2)+1, 1), stats.predict(mod2, newdata = np.arange(1, len(fit_mod2)+1, 1)) ,
                     color= 'blue', marker='', linewidth=2, linestyle='--', label='Model Fit of Asymp') #fit model
            
            axr.plot(x_sites2, asym_mod2, color= 'blue', marker='', linewidth=2.5, linestyle='-', label='The Saturation of Asymp') #fit model
            
            axr.text(2, Asym2*0.9, f' y = { int( np.round(Asym2, 0)) }', color= 'blue', fontsize = 30) #fit model
            
            
            
            # try:
            #     axr.plot(np.arange(0,50,1), predict_mod1, color= 'red', marker='', linewidth=2.5, linestyle='--', label='Model Fit of Lomolino') #fit model
            #     axr.plot(x_sites1, asym_mod1, color= '#1A74A8', marker='', linewidth=2.5, linestyle='-', label='The Saturation of Lomolino') #fit model
            # except Exception as error2:
            #     print(error2)
                  
           
            # axr.plot(np.arange(0,50,1), predict_mod3, color= 'blue', marker='', linewidth=2.5, linestyle='--', label='Model Fit of Michaelis-Menten') #fit model
            # axr.plot(x_sites3, asym_mod3, color= 'green', marker='', linewidth=2.5, linestyle='-', label='The Saturation of Michaelis-Menten') #fit model
            
            
            
            # dark blue: #154A89, # dark green: #30748A, light blue: #1f77b4
            
            # Plot Confidence Interval
            # plot confidence range of Permutations method.
            # axr.fill_between(x_sites1, 
            #                  y_richness1 - 2*y_sd1, 
            #                  y_richness1 + 2*y_sd1, 
            #                  color='#1f77b4', alpha=0.2, label='± 2 Standard Deviation')
            
            # plot confidence range of Exact method.
            axr.fill_between(x_sites3, 
                              y_richness3 - 2*y_sd3, 
                              y_richness3 + 2*y_sd3, 
                              color='red', alpha=0.2, label='± 2 Standard Deviation')
            
            
            #axr.xaxis.set_major_locator(MaxNLocator(integer = True))
            axr.set_xticks(x_sites3)
            axr.set_xticklabels([str(int(yr)) for yr in taxon_unique_years], rotation= 50, fontsize=15)
            
            
            #axr.set_title(f'The Species Accumulation Curve of {taxon_group_name}', fontsize=14, pad= 20)
            axr.set_xlabel('Actual Survey Year', fontsize=14, labelpad= 10)

            axr.set_ylabel(f'Cumulative Species Counts of {taxon_group_name}', fontsize=15)
            
            
            # Axis 2 (Top X-axis): Actual Survey Year Labels
            axr2 = axr.twiny() 
            # Step 1: Force axr2 to share the exact same axis limits as ax1
            axr2.set_xlim(axr.get_xlim())
            
            # Step 2: Set the tick positions to match the exact effort numbers (1, 2, 3...)
            axr2.set_xticks(x_sites2)            
            
            # Step 3: Replace the tick numbers with the actual string of the survey years
            axr2.set_xticklabels(x_sites3, rotation= 0, fontsize=15)
            axr2.set_xlabel('Number of Sampling Years', fontsize= 14, labelpad=12)
            # Configure top axis (axr2)
            
            
            
            # set axis as integer.
            #plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            
            # set legend
            #plt.grid(True, linestyle='--', alpha=0.6)
            axr.tick_params(axis='y', labelsize=15)
            #axr.legend(title=f'{taxon_group_name}', loc='lower right' , fontsize=9 )
            
            if 'Avian' in f'{taxon_group_name}':
                axr.legend(title=f'{taxon_group_name}', loc='lower right' ,title_fontsize= 17 , prop= {'size':14})
                
            else:
                axr.legend([f'{taxon_group_name}'], loc='lower right' , fontsize= 17 )
                
            
            plt.tight_layout(rect= [0, 0, 1, 1])
            #plt.show()
            figr.savefig(output_path_model + f'mhhp_yearly_species_accumulation_curve_complete_{taxon_group_name}.png',
                         dpi= 500,  pad_inches=0.1)     
            
            

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



# III. Save the Table: yearly_smoothed_species_accumulation_curves_6_groups

data_species_cumulative0_raw.to_csv(output_path_sac +'mhhp_yearly_species_accumulation_6_groups_richness_raw.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')


data_species_cumulative0_exact_value.to_csv(output_path_model +'mhhp_yearly_species_accumulation_6_groups_richness_expect.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')


# Save the Table: yearly_smoothed_species_accumulation_curves_6_groups
data_species_cumulative0_exact_std.to_csv(output_path_model +'mhhp_yearly_species_accumulation_6_groups_richness_expect_std.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')



# Save the Table: yearly_species_counts_increments_6_groups  
data_species_increment0_exact.to_csv(output_path_model +'mhhp_yearly_species_increments_6_groups_richness_except.csv',sep=',',
                               index=True, index_label='Year', encoding='utf_8')



# IV.Save model statistics
data_species_cumulative0_fit_value.index = np.arange(1, num_predict+1, 1)
data_species_cumulative0_fit_value.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_value.csv',sep=',',
                                index=True, index_label='x_axis', encoding='utf_8')



data_species_cumulative0_aic.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_aic.csv',sep=',',
                                index=True, index_label='Model', encoding='utf_8')


data_species_cumulative0_pseudoR2.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_pseudoR2.csv',sep=',',
                                index=True, index_label='Model', encoding='utf_8')


data_species_cumulative0_asym.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_AsymValue.csv',sep=',',
                                index=True, index_label='Model', encoding='utf_8')


data_species_cumulative0_unseen_num.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_unseenNum.csv',sep=',',
                                index=True, index_label='Model', encoding='utf_8')


data_species_cumulative0_complete.to_csv(output_path_model +'mhhp_yearly_sac_6_groups_fit_completeness.csv',sep=',',
                                index=True, index_label='Model', encoding='utf_8')





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



#data_species_cumulative_fig = data_species_increment0.fillna(0).cumsum().astype('int')


data_species_cumulative_fig = data_species_increment0_exact.fillna(0).cumsum().astype('int')


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
fig2.savefig(output_path_sac + 'mhhp_yearly_species_accumulation_curves_6_groups.png')

#plt.show()



#%%   

