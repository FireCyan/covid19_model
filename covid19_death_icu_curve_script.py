###############################
# Import packages
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import sklearn
# import requests
# from bs4 import BeautifulSoup
# import pickle

# Import custom functions
# from covid19_prob_func import severe_prob_update, icu_or_vent_prob_update, update_prob, death_num_update
from covid19_plot_func import plot_death_icu_rate
from covid19_prob_parameter import P_matrix
from covid19_model import run_model


current_wd = Path(r'C:\John_folder\github_projects\covid19_model')
################################
# Start coding

###########################################################################################################################
# Loading Covid-19 case data
# Choose a region to run the model
# (Thus far I have outputed only Bavaria (Germany), Lombardy (Italy) and Wuhan (China) Excel for running the model
# (With the addition of data warehouse in the vacquishcovid19 project, can run with different regions with updated numbers)
###########################################################################################################################
# Bavaria, Lombardy, Wuhan
from covid19_region_attr import bavaria, lombardy, wuhan, nsw
# Choose a region object to run the model with

list_region = [bavaria, lombardy, wuhan, nsw]
# 

# n_total_bavaria = bavaria.get_total_case()
# n_total_wuhan = wuhan.get_total_case()
# n_total_lombardy = lombardy.get_total_case()

# death_rate_bavaria = bavaria.get_death_rate()*100 # Number obtained from Wiki/Worldometer
# death_rate_wuhan = wuhan.get_death_rate()*100 # Number obtained from Wiki/Worldometer
# death_rate_lombardy = lombardy.get_death_rate()*100 # Number obtained from Wiki/Worldometer

# # Bavaria_rate_ade_icu = 4410/3130
# Bavaria_rate_ade_icu = bavaria.get_est_ade_icu_rate()*100
# Wuhan_rate_ade_icu = wuhan.get_est_ade_icu_rate()*100
# Lombardy_rate_ade_icu = lombardy.get_est_ade_icu_rate()*100

df_d_icu_rate = pd.DataFrame()
t_hosp_bed = 2000 # Assuming there is enough number of beds

for r in list_region:
    print('Running model with region: ', r.region_name)
    temp_icu_rate = []

    n_days = len(r.daily_case) + 50

    t_icu = r.t_icu_ade

    t_icu_portion = np.arange(0.0, 1.01, 0.01)
    # t_icu_portion = ""


    if t_icu_portion !="":
        t_icu = (np.array(t_icu_portion)*t_icu).round()
    else:
        t_icu = [t_icu]
    t_vent = (np.array(t_icu)*0.6).round() # Initial number of ventilators

    list_df_infected, list_df_death_cause = run_model(r.daily_case, r.pop_ratio, n_days, P_matrix, t_hosp_bed, t_icu, t_vent)

    for i in range(len(list_df_death_cause)):
        temp_icu_rate.append(list_df_death_cause[i]['Total'].sum().sum()/r.get_total_case()*100)

    df_d_icu_rate[r.region_name] = temp_icu_rate


# with open('./pickle_file/Wuhan_df_death_cause_100_t_ratios.pkl', 'rb') as f:
#     list_Wuhan_df_death_cause = pickle.load(f)
    
# with open('./pickle_file/Bavaria_df_death_cause_100_t_ratios.pkl', 'rb') as f:
#     list_Bavaria_df_death_cause = pickle.load(f)
    
# with open('./pickle_file/Lombardy_df_death_cause_100_t_ratios.pkl', 'rb') as f:
#     list_Lombardy_df_death_cause = pickle.load(f)

# Wuhan_d_icu_rate = []
# Bavaria_d_icu_rate = []
# Lombardy_d_icu_rate= []

# for i in range(len(list_Wuhan_df_death_cause)):
#     Wuhan_d_icu_rate.append(list_Wuhan_df_death_cause[i]['Total'].sum().sum()/n_total_wuhan*100)
#     Bavaria_d_icu_rate.append(list_Bavaria_df_death_cause[i]['Total'].sum().sum()/n_total_bavaria*100)
#     Lombardy_d_icu_rate.append(list_Lombardy_df_death_cause[i]['Total'].sum().sum()/n_total_lombardy*100)
    
# # death_against_icu_rate[100] = 
# # print(Wuhan_d_icu_rate)

# df_d_icu_rate = pd.DataFrame(np.array([Bavaria_d_icu_rate, Wuhan_d_icu_rate, Lombardy_d_icu_rate]).T, \
#                              columns=['Bavaria', 'Wuhan', 'Lombardy'])

ax = plot_death_icu_rate(df_d_icu_rate, list_region)

# Bavaria_60_proportion = (0.11751394 + 0.08948367 + 0.0600025)*100
# Wu_60_proportion = (0.073404958 + 0.039966121 + 0.013451689)*100
# Lombardy_60_proportion = (0.11750413 + 0.09882498 + 0.07070879)*100

# plt.text(6, 26, "60+ proportion: {0:.1f}%".format(Lombardy_60_proportion), \
#              color='green', fontsize=20, fontweight='bold', horizontalalignment='left')

# plt.text(6, 24, "60+ proportion: {0:.1f}%".format(Bavaria_60_proportion), \
#              color='orange', fontsize=20, fontweight='bold', horizontalalignment='left')

# plt.text(6, 8, "60+ proportion: {0:.1f}%".format(Wu_60_proportion), \
#              color='red', fontsize=20, fontweight='bold', horizontalalignment='left')