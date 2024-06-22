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
from src.covid19_plot_func import plot_state_num, plot_death_cause, plot_death_cumsum, plot_death_icu_rate
from src.covid19_prob_parameter import P_matrix
from src.covid19_model import run_model


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
from src.covid19_region_attr import bavaria, lombardy, wuhan, nsw
# Choose a region object to run the model with
region = lombardy

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
list_df_infected, list_df_death_cause = run_model(region.daily_case, region.pop_ratio, n_days, P_matrix, t_hosp_bed, t_icu, t_vent)



################
# Plotting part
################

df_infected = list_df_infected[0]
df_death_cause = list_df_death_cause[0]


##### Number of patients in different state plot (plot_state_num) #####
plot_state_num(df_infected, region.daily_case.sum(), region.get_plot_title('plot_state_num', t_icu[0]))

##### Number of deaths due to different causes over time #####
plot_death_cause(df_death_cause, region.daily_case.sum(), region.get_plot_title('plot_death_num', t_icu[0]))

##### Accumulated number of deaths due to different cuases over time #####
plot_death_cumsum(df_death_cause, region.daily_case.sum(), region.get_plot_title('plot_death_cumsum', t_icu[0]))



