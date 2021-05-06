# -*- coding: utf-8 -*-
"""
Created on Wed May  5 00:29:57 2021

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
from covid19_plot_func import plot_constant_daily_case_curve
from covid19_prob_parameter import P_matrix
from covid19_model import run_model

current_wd = Path(r'C:\John_folder\github_projects\covid19_model')
################################

from covid19_region_attr import bavaria, lombardy, wuhan, nsw
# Choose a region object to run the model with
r = wuhan

# with open('./pickle_file/constant_infect_num_df_infected_NSW.pkl', 'rb') as f:
#     list_constant_df_infected = pickle.load(f)


list_base_factor = [1, 2, 5, 10, 20]

n_base_test_case = int(r.t_icu_est/10)
# n_base_test_case_2 = 2*n_base_test_case
# n_base_test_case_5 = 5*n_base_test_case
# n_base_test_case_10 = 10*n_base_test_case
# n_base_test_case_20 = 20*n_base_test_case

constant_flow_days = 30

n_days = constant_flow_days*3
t_hosp_bed = 2000
t_icu = [r.t_icu_est*20] # Maximise ICU beds to see the complete trends
t_vent = t_icu

# list_constant_flow = [n_base_test_case, n_base_test_case_2, n_base_test_case_5, n_base_test_case_10, n_base_test_case_20]

list_constant_df_infected = []
constant_flow_text = []

for factor in list_base_factor:
    constant_daily_case = n_base_test_case*factor
    daily_case = [constant_daily_case]*constant_flow_days # constant daily cases for 30 days
    
    constant_flow_text.append(f'{constant_daily_case} per day ({"%.2f" % ((constant_daily_case/r.get_total_pop())*100000)} per 100K pop per day)')
    
    
    list_df_infected, list_df_death_cause = run_model(daily_case, r.pop_ratio, n_days, P_matrix, t_hosp_bed, t_icu, t_vent)
    
    list_constant_df_infected.append(list_df_infected[0])
    
icu_case_max = (list_df_infected[0]['Total']['ICU'].max() + list_df_infected[0]['Total']['ICU + ventilator'].max())

# Run the daily case from the region as well
list_df_infected, list_df_death_cause = run_model(r.daily_case, r.pop_ratio, n_days, P_matrix, t_hosp_bed, t_icu, t_vent)
    
list_constant_df_infected.append(list_df_infected[0])
constant_flow_text.append(f'Inflow with {r.region_name} cases')


plot_constant_daily_case_curve(r, list_constant_df_infected, constant_flow_text, icu_case_max)


# constant_flow_text = [f'{n_base_test_case} per day ({"%.2f" % ((n_base_test_case/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_2} per day ({"%.2f" % ((n_base_test_case_2/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_5} per day ({"%.2f" % ((n_base_test_case_5/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_10} per day ({"%.2f" % ((n_base_test_case_10/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_20} per day ({"%.2f" % ((n_base_test_case_20/r.get_total_pop())*100000)} per 100K pop per day)',
#                       f'Inflow with {r.region_name} cases']
# list_constant_df_infected.append(df_infected)



