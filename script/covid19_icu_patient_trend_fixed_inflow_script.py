# -*- coding: utf-8 -*-
"""
Created on Wed May  5 00:29:57 2021

@author: john
"""

###############################
# Import packages
import git
repo = git.Repo('.', search_parent_directories=True)
repo_loc = repo.working_tree_dir

import os
import sys
from pathlib import Path

sys.path.append(repo_loc)

import numpy as np
import pandas as pd

# Import custom functions
# from covid19_prob_func import severe_prob_update, icu_or_vent_prob_update, update_prob, death_num_update
from src.covid19_plot_func import plot_death_icu_rate
from src.covid19_model import run_model, run_multiple
from src import conf_helper as cf
from src.covid19_region_attr import create_region
from src import covid19_plot_func
################################

model_config_file = 'model_param_v1.yaml'
model_config = cf.CovidConf(project_dir=repo_loc, config_file=model_config_file)

# Choose a region object to run the model with
region_config = 'bavaria_20200416.yaml' # 'lombardy_20200417.yaml', 'nsw_20200425.yaml', 'wuhan_20200412.yaml']

r = create_region(region_config)

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
    
    list_df_infected, list_df_death_cause = run_multiple(daily_case, r.pop_ratio, n_days, t_hosp_bed, t_icu, t_vent, model_config)
    
    list_constant_df_infected.append(list_df_infected[0])
    
icu_case_max = (list_df_infected[0]['Total']['ICU'].max() + list_df_infected[0]['Total']['ICU + ventilator'].max())

# Run the daily case from the region as well
list_df_infected, list_df_death_cause = run_multiple(r.daily_case, r.pop_ratio, n_days, t_hosp_bed, t_icu, t_vent, model_config)
    
list_constant_df_infected.append(list_df_infected[0])
constant_flow_text.append(f'Inflow with {r.region_name} cases')


covid19_plot_func.plot_constant_daily_case_curve(r, list_constant_df_infected, constant_flow_text, icu_case_max)


# constant_flow_text = [f'{n_base_test_case} per day ({"%.2f" % ((n_base_test_case/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_2} per day ({"%.2f" % ((n_base_test_case_2/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_5} per day ({"%.2f" % ((n_base_test_case_5/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_10} per day ({"%.2f" % ((n_base_test_case_10/r.get_total_pop())*100000)} per 100K pop per day)', \
#                       f'{n_base_test_case_20} per day ({"%.2f" % ((n_base_test_case_20/r.get_total_pop())*100000)} per 100K pop per day)',
#                       f'Inflow with {r.region_name} cases']
# list_constant_df_infected.append(df_infected)



