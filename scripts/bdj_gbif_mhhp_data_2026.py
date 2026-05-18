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

import os
import numpy as np
import pandas as pd
import chardet

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# 1. 強制設定 R_HOME 為你 Conda 虛擬環境中的 R 資料夾
# (注意前面的 r 不能省略，這能避免 Windows 反斜線 \ 造成的路徑辨識錯誤)
os.environ['R_HOME'] = r'C:\Users\cetae\anaconda3\envs\env_geo\Lib\R'

# 2. 清除可能干擾的 R_USER 變數 (如果有設定的話，讓它重置)
if 'R_USER' in os.environ:
    del os.environ['R_USER']


# 在 Python 裡面直接召喚 R 的 vegan！
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri



matplotlib.rcParams['font.family'] = 'Times New Roman'



print(f" Current Working Directory (CWD) : {os.getcwd()}")
root_path0 = input("Input the complete path of the folder 'Survey_Data_Mianhua_and_Huaping_Islets_Wildlife_Refuge' if the CWD is not this \n or Enter:")  or str(os.getcwd()) 
root_path = root_path0.strip()
if (root_path[-1] == '/'):
    root_path = root_path[:-1]

#example
#root_path = 'C:/Users/cetae/GBIF_IPT/Survey_Data_Mianhua_and_Huaping_Islets_Wildlife_Refuge'



input_path = os.path.join(root_path,'mhhp_inputs/')
output_path = os.path.join(root_path, 'mhhp_outputs/')
output_path_csv = os.path.join(output_path, 'csv/')
output_path_sac = os.path.join(output_path, 'species_accumulation_curve/')
output_path_counts = os.path.join(output_path, 'species_counts_yearly/')


if not os.path.exists(output_path):
    os.mkdir(output_path)

# if not os.path.exists(output_path_csv):
#     os.mkdir(output_path_csv)

if not os.path.exists(output_path_sac):
    os.mkdir(output_path_sac)


if not os.path.exists(output_path_counts):
    os.mkdir(output_path_counts)




#%% I.Check data integrity
content=os.listdir(input_path)
content=sorted(content)
os.chdir(input_path)



data_extension=pd.DataFrame([])

#Confirm unique ID
for file_id in range(0,10): #range(0,len(sheet_name)-1)

    #check the encoding format
    with open(content[file_id], 'rb') as f:
        result = chardet.detect(f.read())
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
        data_taxon=pd.read_csv(content[file_id], encoding= encoding_name)
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
        data1_check=pd.read_csv(content[file_id], encoding= encoding_name)
        # Make Sure that occurrenceID is unique
        if ('occurrenceID' in list(data1_check.columns)) and ('measurementType' not in list(data1_check.columns)):
            data_occurrenceID=data1_check.value_counts('occurrenceID', sort=True)
            if len(data_occurrenceID)==len(data1_check):
                data_extension=pd.concat([data_extension,data1_check], ignore_index=True)
                print(f'{content[file_id]}: occurrenceID is unique.')
            else:
                print(f'{content[file_id]}: The occurrenceID is NOT unique!\n')
    





data_extension['verbatimEventDate'] = data_extension['verbatimEventDate'].str.replace('/','-')



data_extension_taxon=data_extension.value_counts('taxonID', sort=True)
data_extension_taxon=data_extension_taxon.reset_index().sort_values(by=['taxonID'])
a1=set(data_extension_taxon['taxonID'].values)
a2=set(data_taxonID['taxonID'].values)



#%% #II. Statistics of the data



os.chdir(input_path)



data_yearly_taxon_counts = pd.DataFrame([],index=list(range(1994,2026,1)))
data_yearly_occur_counts = pd.DataFrame([],index=list(range(1994,2026,1)))


data_species_cumulative0 = pd.DataFrame([],index=list(range(1994,2026,1)))
data_species_increment0 = pd.DataFrame([],index=list(range(1994,2026,1)))




for file_id in range(1,10): #range(0,len(sheet_name)-1)

    #check the encoding format
    with open(content[file_id], 'rb') as f:
        result = chardet.detect(f.read())
        print(f"{content[file_id]} : {result['encoding']}")    
        
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
              
              

    data0 = pd.read_csv(content[file_id], encoding= encoding_name)


    if ('occurrenceID' in list(data0.columns)) and ('measurementType' not in list(data0.columns)):
        
        data0['year'] = data0['year'].astype('Int64')  #型別
        data0['month'] = data0['month'].astype('Int64')
        data0.sort_values(['year'],ascending=True, ignore_index=True, inplace=True) #將年份排序
        data0.sort_values(['verbatimEventDate'],ascending=True, ignore_index=True, inplace=True) #將年份排序
        
        # =============================================================================
        #         Goal: Filter the occurrences with taxonRank euqals species.
        #         edit the occurrences with taxonRank lower than species (subspecies) into species.
        #         remove the occurrences with taxonRank higher than species
        # =============================================================================
        

        data0['name_split']=data0['scientificName'].str.strip().str.split()
        
        
        #data0['name_split_2words'] = [[a1[0], a1[1]] if len(a1)>=2 else [a1[0]] for a1 in  data0['name_split']   ]
        data0['name_split_2words']=data0['name_split'].apply(lambda x: x[:2] if (isinstance(x, list) and len(x)>=2 ) else x)
        data0['name_species'] = data0['name_split_2words'].str.join(' ')
        

        
        #Assign data1 : Filter the occurrences with taxonRank euqals species.
        data0['taxonRank'] = data0['taxonRank'].str.strip().str.lower()
        filter_species= np.logical_or(data0['taxonRank']=='species', data0['taxonRank']=='subspecies')
        len(data0[filter_species])/len(data0)
        data1 = data0[filter_species].copy()
        
        
        
        
        
        
        #Sample-based accumulation curve ()
        data1_community_quan = pd.crosstab(data1['year'],data1['name_species'])
        data1_community_boolean = (data1_community_quan>0).astype('int')


        # 1).Convert from pandas to R
        pandas2ri.activate()
        
        # 2). import 'vegan' package
        vegan = rpackages.importr('vegan')
        stats = rpackages.importr('stats')
        
        
        # 3). species accumulation curve_random/exact
        if len(data1_community_boolean)>1:
            sp1 = vegan.specaccum(data1_community_boolean, method= 'random')
            sp2 = vegan.specaccum(data1_community_boolean, method= 'collector')
            sp3 = vegan.specaccum(data1_community_boolean, method= 'exact')
            
        #plot(sp1, ci.type="poly", col="blue", lwd=2, ci.lty=0, ci.col="lightblue")
        
        
        # 步驟 4：把 R 的結果萃取出來，轉成 Python 的 Numpy 陣列
        # ==========================================
        # 使用 .rx2() 抓出特定元素，並用 np.array() 把它們變成純數值
        x_sites1 = np.array(sp1.rx2('sites'))
        y_richness1 = np.array(sp1.rx2('richness'))
        y_sd1 = np.array(sp1.rx2('sd'))

        x_sites2 = np.array(sp2.rx2('sites'))
        y_richness2 = np.array(sp2.rx2('richness'))
        y_sd2 = np.array(sp2.rx2('sd'))        
        
        
        x_sites3 = np.array(sp3.rx2('sites'))
        y_richness3 = np.array(sp3.rx2('richness'))
        y_sd3 = np.array(sp3.rx2('sd'))
        
        
        

        # ==========================================
        # 步驟 5：變成 Pandas DataFrame 方便檢視與輸出
        # ==========================================
        sac_results = pd.DataFrame({
            'Years': x_sites1,
            'Richness': y_richness1,
            'SD': y_sd1
        })
        
        print("==== 物種累積曲線計算結果 ====")
        print(sac_results.head()) # 先偷看前五筆資料
        
        # ==========================================
        # 步驟 6：使用 Matplotlib 畫出帶有標準差的 SAC 圖
        # ==========================================

        figr, axr = plt.subplots(1,1,figsize=(10, 6))
        
        # plot curve
        axr.plot(x_sites1, y_richness1, color='#1f77b4', marker='o', linewidth=2, label='Species Accumulation with Permutations.')
        axr.plot(x_sites2, y_richness2, color='black', marker='o', linewidth=2, label='Species Accumulation in Survey Order')
        axr.plot(x_sites3, y_richness3, color='black', marker='o', linewidth=2, label='Species Accumulation in Exact Mode.')
        
        
        mod1 = vegan.fitspecaccum(sp3, "lomolino")
        
        mod2 = vegan.fitspecaccum(sp3, "asymp")
        
        mod3 = vegan.fitspecaccum(sp3, "michaelis-menten")
        
        #stats.sapply(mods1.models, AIC)
        
        coeffs1 = stats.coef(mod1)
        coeffs2 = stats.coef(mod2)
        coeffs3 = stats.coef(mod3)
        tuple(coeffs1.names)
        
        
        # plot confidence range
        # alpha=0.2 代表設定陰影的透明度為 20%
        axr.fill_between(x_sites1, 
                         y_richness1 - y_sd1, 
                         y_richness1 + y_sd1, 
                         color='#1f77b4', alpha=0.2, label='± 1 Standard Deviation')
        
        
        axr.fill_between(x_sites3, 
                          y_richness3 - y_sd3, 
                          y_richness3 + y_sd3, 
                          color='red', alpha=0.2, label='± 1 Standard Deviation')
        
        # 設定圖表的標題與軸標籤
        axr.set_title(f'The Species Accumulation Curve of {content[file_id][2:-18]}', fontsize=14)
        axr.set_xlabel('Number of Sampling Years', fontsize=12)
        axr.set_ylabel('Cumulative Counts of Species', fontsize=12)
        
        # 強制 X 軸顯示整數 (因為年份不能是小數)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # 顯示網格線與圖例
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='lower right')
        
        # 將圖表顯示出來！
        plt.show()
                







        #1. Annual Species Counts
        data_taxon_yearly = data1.groupby(['year'])['name_species'].nunique(dropna=True).to_frame()
        #每一年當成是x軸
        #data_yearly_taxon_counts[f'{content[file_id][2:-18]}']=0   #index是年分，匯入總整理資料
        data_yearly_taxon_counts.loc[list(data_taxon_yearly.index), [f'{content[file_id][2:-18]}'] ] = data_taxon_yearly.loc[list(data_taxon_yearly.index)].values

        
        #2.Yearly Species Accumulation Curve (sac)        
        #species_cumulative = {y : 0 for y in range(1994,2026,1) }
        taxon_unique_years= np.sort(data1['year'].dropna().unique())
        species_cumulative0 = {y : 0 for y in taxon_unique_years }  #累積年份的物種數量
        taxon_cumulative = data1[['name_species','year']].dropna().drop_duplicates()        


        #2-1: 計算當年份之前(包含)的物種數量
        #beforeyear=2025
        taxon_sample_yearly_times = {} #單一年份的物種數量
    
        for beforeyear in taxon_unique_years:   #np.array(data1['year'].unique())
            # taxon_beforeyear=taxon_cumulative.loc[taxon_cumulative['year']<=beforeyear,'name_species'].value_counts()
            # len(taxon_beforeyear)      
            species_cumulative0[beforeyear] = taxon_cumulative.loc[taxon_cumulative['year'] <= beforeyear,'name_species'].nunique()         #累積年份的物種數量
            taxon_sample_yearly_times[beforeyear] = taxon_cumulative.loc[taxon_cumulative['year'] == beforeyear,'name_species'].nunique()    #單一年份的物種數量

        #計算累積曲線的遞增關係
        species_increment0={}
        for i, y in enumerate(taxon_unique_years) :
            if i==0:
                species_increment0[y] = species_cumulative0[y]
            elif i!=0 :
                year_previous = taxon_unique_years[i-1]
                species_increment0[y] = species_cumulative0[y] - species_cumulative0[year_previous]


        data_species_sample_year_cum = pd.DataFrame.from_dict(species_cumulative0 , orient='index',columns=[f'{content[file_id][2:-18]}'])
        data_species_sample_year_incr = pd.DataFrame.from_dict(species_increment0, orient='index', columns=[f'{content[file_id][2:-18]}'])  
        data_species_sample_year_cum.to_csv(output_path_sac + f'mhhp_yearly_species_accumulation_curve_{content[file_id][2:-18]}.csv', 
                                               sep=',', index=True, index_label='Year', encoding='utf_8')
        
        
        data_species_sample_year_cum.index=data_species_sample_year_cum.index.astype("str")
        # 從1994-2025所有年分
        data_species_cumulative0[f'{content[file_id][2:-18]}'] = pd.DataFrame.from_dict(species_cumulative0 , orient='index',columns=[f'{content[file_id][2:-18]}'])
        data_species_increment0[f'{content[file_id][2:-18]}'] = pd.DataFrame.from_dict(species_increment0, orient='index', columns=[f'{content[file_id][2:-18]}'])  
        # data_species_cumulative0.plot()
        
        
        # Plot: yearly_species_accumulation_curve
        size_point=20 #the size of the point
        fig2,ax2 = plt.subplots(1,1, figsize=(6,4), dpi=300)
        data_species_sample_year_cum.plot(ax=ax2)
        ax2.scatter(x = list(data_species_sample_year_cum.index) , y = data_species_sample_year_cum[f'{content[file_id][2:-18]}'],
                          s=size_point, marker='o')
        
        ax2.set_xticks(range(0,len(data_species_sample_year_cum)))
        ax2.set_xticklabels(list(data_species_sample_year_cum.index) , rotation=90, fontsize=15)
        ax2.set_xlabel('Year', fontsize=18)
        
        if file_id==4:
            ax2.set_yticks(range(0,data_species_sample_year_cum.max().values[0]+2, 1) )
            ax2.set_yticklabels(range(0, data_species_sample_year_cum.max().values[0]+2, 1), fontsize=15 )
            
        ax2.set_ylabel('Species Counts', fontsize=18)
        ax2.legend([f'{content[file_id][2:-18]}'], fontsize=20)
        plt.tight_layout()
        fig2.savefig(output_path_sac + f'mhhp_yearly_species_accumulation_curve_{content[file_id][2:-18]}.png')        



        
        #I.計算這個種類的生物在整年份的目擊分布>>使用所有的taxon occurrences(data0)
        data_year = data0.groupby('year')['occurrenceID'].size().to_frame(name=f'{content[file_id][2:-18]}')
        
        #單一物種整年份的目擊分布>>彙整至全部種類整年份的分布
        #data_yearly_occur_counts[f'{content[file_id][2:-18]}']=0  
        
        #index是年分，匯入總整理資料
        data_yearly_occur_counts.loc[data_year.index, f'{content[file_id][2:-18]}']=data_year.loc[data_year.index, f'{content[file_id][2:-18]}'].values
        
        #index不是年分，匯入總整理資料
        #data_yearly_occur_counts.loc[data_year['year'].values, f'{content[file_id][2:-18]}']=data_year.loc[data_year['year']==data_year['year'].values, f'{content[file_id][2:-18]}'].values
        

    else:
        print(f'Will not process this file: {content[file_id]}')
        
        
# Save the Table: yearly_species_counts_8_groups    
data_yearly_taxon_counts.to_csv(output_path_counts + 'mhhp_yearly_species_counts_8_groups.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')


# Save the Table: yearly_species_accumulation_curves_8_groups
data_species_cumulative0.to_csv(output_path_sac +'mhhp_yearly_species_accumulation_8_groups.csv',sep=',',
                                index=True, index_label='Year', encoding='utf_8')


# Save the Table: yearly_species_counts_increments_8_groups  
data_species_increment0.to_csv(output_path_sac +'mhhp_yearly_species_increments_8_groups.csv',sep=',',
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



#%% III. Visualizations  #3-1.Export 8 figures of mhhp_annual_species_counts

# Use the Variable to plot
data_yearly_counts_fig = data_yearly_taxon_counts.copy()


data_yearly_counts_fig = data_yearly_counts_fig.fillna(0).astype('int')
ylabel_name='Species Counts'


# data_yearly_counts_fig.columns
#['Algae', 'Avian', 'Benthic Invertebrate', 'Cetacean', 'Fish', 'Plant', 'Reptile', 'Insect']


color_category={
 'Algae':'#6ccb59',
 'Avian':'#ff9a03',
 'Benthic Invertebrate':'#46859c',
 'Cetacean':'#6ccbef',
 'Fish':'#4685ff',
 'Plant':'#077148',
 'Reptile':'#61396e',
 'Insect':'#613901'}


for category1 in [
  'Algae',
  'Avian',
  'Benthic Invertebrate',
  'Cetacean',
  'Fish',
  'Plant',
  'Reptile',
  'Insect']:

    fig0, axis0=plt.subplots(1,1, dpi=300)
    bar0=axis0.bar(data_yearly_counts_fig.index, data_yearly_counts_fig[category1], color= color_category[category1])
    
    #set the legend
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


fig1,axis1=plt.subplots(3,2, dpi=300, figsize=(16,16))
turn=0
for category1 in [
# 'Algae',
 'Avian',
 'Fish',
 'Insect',
 'Cetacean',
 'Benthic Invertebrate',
 'Plant',
# 'Reptile'
 ]:
    
    row1=np.mod( turn, fig_row_counts)
    column1=int( np.floor(turn/fig_row_counts) )
    data_yearly_counts_fig[category1]=data_yearly_counts_fig[category1].astype('Int64')
    
    #line1,=axis1[row1,column1].plot(data_yearly_counts_fig['year'], data_yearly_counts_fig[category1], color='black')
    bar1=axis1[row1,column1].bar(data_yearly_counts_fig.index, data_yearly_counts_fig[category1], color=color_category[category1])
   
    #set the legend
    bar1.set_label(category1)
    axis1[row1,column1].legend(prop={"size":25})
    
    #Set the Y interval to integer.
    axis1[row1,column1].yaxis.set_major_locator(MaxNLocator(integer=True))
    # Set the fontsize of Y label
    axis1[row1,column1].tick_params(axis='y',labelsize=20)
    axis1[row1,column1].set_xlabel('Year', fontsize=20)
    axis1[row1,column1].set_ylabel(ylabel_name, fontsize=20)
    
    axis1[row1,column1].set_xticks(range(1995,2026,5))
    axis1[row1,column1].set_xticklabels(range(1995,2026,5) ,fontsize=20)
    
    turn=turn+1

plt.tight_layout()
fig1.savefig(output_path_counts + 'mhhp_yearly_species_counts_6subplots.png')
plt.show()





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
 'Benthic Invertebrate',
 'Plant',
# 'Reptile'
 ]:

    
    line2,= axis2.plot(data_species_cumulative_fig.index, data_species_cumulative_fig[category2],
                      color=color_category[category2], linewidth=2)
    line2.set_label(category2)
    
    axis2.set_xlabel('Year', fontsize=15)
    axis2.set_ylabel(ylabel_name, fontsize=15)
    
    axis2.set_xticks(range(1995,2026,5))
    axis2.set_xticklabels(range(1995,2026,5) ,fontsize=15)
    
    axis2.tick_params(axis='y', labelsize=15)


#axis2.legend(title='8 Groups',title_fontsize=12 ,prop={'size':11})
axis2.legend(frameon=False, prop={'size':11})
plt.tight_layout()
fig2.savefig(output_path_sac + 'mhhp_yearly_species_accumulation_curves_6_groups.png')

plt.show()


 
#%%  
# #%% 4-1. Count the boolean of survey targets in each year (0 | 1).



# # Count the number of survey targets in each year.
# # Count the boolean of survey targets in each year (0 | 1).
# data_year_category_group = data_yearly_occur_counts>0
# data_year_category_group = data_year_category_group.astype('int64')

# # Delete it : If there isn't any survey targets in that year.
# data_year_category_group['sum'] = data_year_category_group.sum(axis=1).values
# drop_index1=list(data_year_category_group[data_year_category_group['sum']==0].index)
# data_year_category_group.drop(drop_index1, inplace=True)
# data_year_category_group.to_csv(output_path_csv +'mhhp_yearly_occur_counts_boolean_8_groups.csv',
#                                 sep=',',index=True, index_label='Year', encoding='utf_8')




#%%   

