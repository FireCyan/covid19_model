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
from src.covid19_model import run_model, run_multiple
from src import conf_helper as cf
from src.covid19_region_attr import create_region
from src import covid19_plot_func
################################
# Start coding

model_config_file = 'model_param_v1.yaml'
model_config = cf.CovidConf(project_dir=repo_loc, config_file=model_config_file)

# Choose a region object to run the model with
region_config = 'bavaria_20200416.yaml' # 'lombardy_20200417.yaml', 'nsw_20200425.yaml', 'wuhan_20200412.yaml']

region = create_region(region_config)

n_days = len(region.daily_case) + 50

##### Setting hopsital beds, ICU and ventilator numbers #####

t_hosp_bed = 2000 # Assuming there is enough number of beds

# Set the t_icu number
# Can set it to region.t_icu_est (estimated available ICU avaiable for the region), region.t_icu_ade (adequate ICU number for the region) or any numbers one wants
t_icu = region.t_icu_est

# Initial number of ICU beds. If t_icu_portion is a list, then will run with multiple tests with different t_icu_portion
# t_icu_portion = [1/10, 1/5, 1/2, 1]
# t_icu_portion = np.arange(0.0, 1.01, 0.01)
t_icu_portion = ""


if t_icu_portion !="":
    t_icu = (np.array(t_icu_portion)*t_icu).round()
else:
    t_icu = [t_icu]
t_vent = (np.array(t_icu)*0.6).round() # Initial number of ventilators

############
# Run model
############
print("Run model for region: ", region.region_name)
list_df_infected, list_df_death_cause = run_multiple(region.daily_case, region.pop_ratio, n_days, t_hosp_bed, t_icu, t_vent, model_config)

################
# Plotting part
################
df_infected = list_df_infected[0]
df_death_cause = list_df_death_cause[0]

##### Number of patients in different state plot (plot_state_num) #####
covid19_plot_func.plot_state_num(df_infected, region.daily_case.sum(), region.get_plot_title('plot_state_num', t_icu[0]))

##### Number of deaths due to different causes over time #####
covid19_plot_func.plot_death_cause(df_death_cause, region.daily_case.sum(), region.get_plot_title('plot_death_num', t_icu[0]))

##### Accumulated number of deaths due to different cuases over time #####
covid19_plot_func.plot_death_cumsum(df_death_cause, region.daily_case.sum(), region.get_plot_title('plot_death_cumsum', t_icu[0]))



