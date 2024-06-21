###############################
# Import packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pickle
import random

# Import custom functions
from src.covid19_prob_func import severe_prob_update, icu_or_vent_prob_update, update_prob, death_num_update
from src.covid19_prob_parameter import d_cause_num
from src.covid19_prob_parameter import get_prob_matrix

################################


########################################
# Initialise variables and column names
########################################

col_state = ['Mild', 'Severe', 'Critical', 'Hospitalised', 'Awaiting_ICU-hospitalised_to_critical', \
             'Awaiting_ICU_and_vent-hospitalised_to_critical', 'ICU', 'ICU + ventilator', 'Recovered', 'Death']

col_death_cause = ['Death - lack of hospital bed', 'Death - lack of ICU', 'Death - lack of ICU + ventilator', \
              'Death - hospitalised', 'Death - ICU', 'Death - ICU + ventilator']
col_age = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+', 'Total']
col_iterables = [col_age, col_state]

col_death_iterables = [col_age, col_death_cause]
# test = pd.MultiIndex.from_product(col_iterables)

def initialise_model(model_config):

    dict_initial_rate = {}

    init_P_matrix = get_prob_matrix(model_config)
    
    dict_initial_rate['Psc'] = init_P_matrix[1,2,:].flatten() # Need to flatten for the multiplication to work
    dict_initial_rate['Psd'] = init_P_matrix[1,9,:].flatten()
    dict_initial_rate['Pcd'] = init_P_matrix[2,9,:].flatten()
    dict_initial_rate['Phr'] = init_P_matrix[3,8,:].flatten()
    dict_initial_rate['Phd'] = init_P_matrix[3,9,:].flatten()
    dict_initial_rate['Pir'] = init_P_matrix[6,8,:].flatten()
    dict_initial_rate['Pid'] = init_P_matrix[6,9,:].flatten()
    dict_initial_rate['Pvr'] = init_P_matrix[7,8,:].flatten()
    dict_initial_rate['Pvd'] = init_P_matrix[7,9,:].flatten()
    dict_initial_rate['Phiwd'] = init_P_matrix[4,9,:].flatten()
    dict_initial_rate['Phvwd'] = init_P_matrix[5,9,:].flatten()
    dict_initial_rate['h_i_rate'] = model_config['rate']['hospitalised_to_icu_rate']
    dict_initial_rate['icu_with_vent_rate'] = model_config['rate']['icu_with_vent_rate']

    return init_P_matrix, dict_initial_rate

def run_multiple(daily_case, pop_ratio, n_days, t_hosp_bed, t_icu, t_vent, model_config):
    '''
    Use this function to run for loops to get the modelled number of patients in different states with different number of ICU beds
    '''

    ##### Initialise variables #####
    list_df_infected = []
    list_df_death_cause = []

    a_hosp_bed = t_hosp_bed

    for t in range(len(t_icu)):
        print("t_icu: ", t_icu[t])
        a_icu = int(t_icu[t])
        a_vent = int(t_vent[t])

        ##### Run the main model step #####
        df_infected, df_death_cause = run_model(daily_case, pop_ratio, n_days, a_hosp_bed, a_icu, a_vent, model_config)

        print("Finished running model for t_icu value of {}".format(a_icu))
        print("================================================================\n")

        ##### Append the results into list for further analyses/plotting #####
        list_df_infected.append(df_infected)
        list_df_death_cause.append(df_death_cause)

    return list_df_infected, list_df_death_cause


def run_model(daily_case, pop_ratio, n_days, a_hosp_bed, a_icu, a_vent, model_config):
    
    df_infected = pd.DataFrame(columns=pd.MultiIndex.from_product(col_iterables))
    df_death_cause = pd.DataFrame(columns=pd.MultiIndex.from_product(col_death_iterables))

    init_P_matrix, dict_initial_rate = initialise_model(model_config)

    P_mat = init_P_matrix

    n_age_group = init_P_matrix.shape[2]
    n_state = init_P_matrix.shape[0]
    icu_with_vent_rate = dict_initial_rate['icu_with_vent_rate']

    df_current = np.zeros((n_age_group, n_state))
    df_next = np.zeros((n_age_group, n_state))

    ##### Loop over number of days to get modelled number of patients in different states #####
    for d in range(n_days):
        if d % 10 == 0:
            print("Running model for Day {}...".format(d))        
        
        if d < len(daily_case):
            additional_cases = np.round(pop_ratio*daily_case[d])
            df_current[:,0] = df_current[:,0] + additional_cases

        ##### Update probability matrix #####
        P_mat, _, _, _ = update_prob(P_mat, dict_initial_rate, df_current, a_hosp_bed, a_icu, a_vent, young_age_first=True)

        ##### Update the number of cases for the next step/day #####
        for i in range(n_age_group):
            df_next[i, :] = np.dot(df_current[i, :], P_mat[:,:,i])
            df_next[i, :]= np.floor(df_next[i, :])

        ##### Update the number of deaths and the cause #####
        death_cause_mat = death_num_update(df_current, P_mat, icu_with_vent_rate, n_age_group, d_cause_num)
        df_death_cause.loc[len(df_infected)] = death_cause_mat.flatten(order='C').tolist() + \
        death_cause_mat.sum(axis=0).tolist()

        ##### Update the number of patients in each state #####
        df_infected.loc[len(df_infected)] = df_next.flatten(order='C').tolist() + df_next.sum(axis=0).tolist()

        df_current = df_next

    return df_infected, df_death_cause