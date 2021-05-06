# -*- coding: utf-8 -*-
"""
Created on Wed May  5 15:19:34 2021

@author: john
"""

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
from covid19_plot_func import plot_fix_case_diff_days
from covid19_prob_parameter import P_matrix
from covid19_model import run_model

current_wd = Path(r'C:\John_folder\github_projects\covid19_model')
################################

from covid19_region_attr import bavaria, lombardy, wuhan, nsw
# Choose a region object to run the model with
r = nsw

# with open('./pickle_file/fix_infect_diff_days_df_infected_NSW.pkl', 'rb') as f:
#     list_fix_num_diff_days_df_infected = pickle.load(f)

# Assuming 500 infected per 100K people in total
n_infected_per_100k = 500


n_total_infect = int(n_infected_per_100k/100000*r.get_total_pop())

list_day_div = [200, 100, 50, 20, 10]

n_base_test_case = int(r.t_icu_est/10)

run_days = 90

t_hosp_bed = 2000
t_icu = [r.t_icu_est*20] # Maximise ICU beds to see the complete trends
t_vent = t_icu

# list_constant_flow = [n_base_test_case, n_base_test_case_2, n_base_test_case_5, n_base_test_case_10, n_base_test_case_20]

list_fix_total_diff_days_df_infected = []
fix_total_diff_days_text = []


for div in list_day_div:
    constant_daily_case = np.round(n_total_infect/div)
    daily_case = [constant_daily_case]*div # constant daily cases for 30 days
    
    fix_total_diff_days_text.append(f'{"%.0f" % constant_daily_case} ({"%.2f" % ((constant_daily_case/r.get_total_pop())*100000)} per 100K) per day for {div} days')
    
    
    list_df_infected, list_df_death_cause = run_model(daily_case, r.pop_ratio, run_days, P_matrix, t_hosp_bed, t_icu, t_vent)
    
    list_fix_total_diff_days_df_infected.append(list_df_infected[0])

# The last div run should be the most serious one, so can get the max ICU number reached
icu_case_max = (list_df_infected[0]['Total']['ICU'].max() + list_df_infected[0]['Total']['ICU + ventilator'].max())


plot_fix_case_diff_days(r, list_fix_total_diff_days_df_infected, fix_total_diff_days_text, icu_case_max, n_total_infect)