###############################
# Import packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
import requests
from bs4 import BeautifulSoup
import pickle
import random

# Import custom functions
from covid19_prob_func import severe_prob_update, icu_or_vent_prob_update, update_prob, death_num_update
# from covid19_plot_func import plot_state_num, plot_death_cause, plot_death_acc, plot_death_icu_rate
from covid19_prob_parameter import *

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




def run_model(daily_case, pop_ratio, n_days, init_P_matrix, t_hosp_bed, t_icu, t_vent):
    list_df_infected = []
    list_df_death_cause = []

    a_hosp_bed = t_hosp_bed
    a_icu = t_icu
    a_vent = t_vent
    
    for t in range(len(t_icu)):
        print("t_icu: ", t_icu[t])
        a_icu = int(t_icu[t])
        a_vent = int(t_vent[t])

        df_infected = ""
        df_infected = pd.DataFrame(columns=pd.MultiIndex.from_product(col_iterables))
        df_death_cause = ""
        df_death_cause = pd.DataFrame(columns=pd.MultiIndex.from_product(col_death_iterables))

        x = np.zeros((n_age_group, n_state))
        y = np.zeros((n_age_group, n_state))

        P_mat = init_P_matrix

        for d in range(n_days):
            if d % 10 == 0:
                print("Running model for Day {}...".format(d))
                # print(P_mat)
            
            
            if d < len(daily_case):
                additional_cases = np.round(pop_ratio*daily_case[d])
                x[:,0] = x[:,0] + additional_cases
                # print("additional_cases: ", additional_cases)


            # print("x: ", x)
            # print("a_hosp_bed: ", a_hosp_bed)
            # print("a_icu: ", a_icu)
            # print("a_vent: ", a_vent)
            # print(additional_cases)

            # Update probability matrix
            P_mat, _, _, _ = update_prob(P_mat, x, a_hosp_bed, a_icu, a_vent,\
                                                            state_num, young_age_first=True)


            for i in range(n_age_group):
                y[i, :] = np.dot(x[i, :], P_mat[:,:,i])
                # y[i, :]= np.round(y[i, :])
                y[i, :]= np.floor(y[i, :])
                # mat_one = y[i, :] == 1
                # if random.random() > 0.5:
                #     y[i, :][mat_one] = 0

            death_cause_mat = death_num_update(x, P_mat, n_age_group, d_cause_num)
            df_death_cause.loc[len(df_infected)] = death_cause_mat.flatten(order='C').tolist() + \
            death_cause_mat.sum(axis=0).tolist()

        #     print(y.flatten(order='C').tolist() + y.sum(axis=0).tolist())

            df_infected.loc[len(df_infected)] = y.flatten(order='C').tolist() + y.sum(axis=0).tolist()
        #     df_infected.append(pd.Series(y.flatten(order='C').tolist()), ignore_index=True)
            x = y

            
            # print("------------------------------------------------------\n")
        print("Finished running model for t_icu value of {}".format(t_icu[t]))
        print("================================================================\n")
        list_df_infected.append(df_infected)
        list_df_death_cause.append(df_death_cause)

    return list_df_infected, list_df_death_cause