import git
repo = git.Repo('.', search_parent_directories=True)
repo_loc = repo.working_tree_dir

import os
import sys
from pathlib import Path

sys.path.append(repo_loc)

import numpy as np
import pandas as pd
from src.conf_helper import CovidConf

class region():
    
    def __init__(self, region_name, country, daily_case, acc_case, pop, pop_ratio, t_icu_est, t_icu_ade, n_death):
        self.region_name = region_name # name of the region
        self.country = country
        self.daily_case = daily_case # number of daily Covid-19 cases
        self.acc_case = acc_case # number of cumulative daily Covid-19 cases
        self.pop = pop # population at different age groups of the region
        self.pop_ratio = pop_ratio # age group ratio of the region
        self.t_icu_est = t_icu_est # estimated number of ICU available in the region
        self.t_icu_ade = t_icu_ade # adequate number of ICU required to have all critically illed patients covered
        self.n_death = n_death
        self.title = ""

    def get_plot_title(self, plot_type, n_icu):
        if plot_type == 'plot_state_num':
            self.title = f"Number of people in each state of severity and care - assumed {int(n_icu)} ICU beds available ({int((n_icu/self.t_icu_ade)*100)}% of {int(self.t_icu_ade)} adequate ICU beds)\nModel with cases in {self.region_name}, {self.country}"
        elif plot_type == 'plot_death_cumsum':
            self.title = f"Cumulative number of deaths by cause - assumed {int(n_icu)} ICU beds available ({int((n_icu/self.t_icu_ade)*100)}% of {int(self.t_icu_ade)} adequate ICU beds)\nModel with cases in {self.region_name}, {self.country}"
        elif plot_type == 'plot_death_num':
            self.title = f"Number of deaths by cause - assumed {int(n_icu)} ICU beds available ({int((n_icu/self.t_icu_ade)*100)}% of {int(self.t_icu_ade)} adequate ICU beds)\nModel with cases in {self.region_name}, {self.country}"

        return self.title

    def get_total_case(self):
        return self.daily_case.sum()

    def get_death_rate(self):
        return self.n_death/self.get_total_case()

    def get_est_ade_icu_rate(self):
        return self.t_icu_est/self.t_icu_ade if self.t_icu_est/self.t_icu_ade <= 1 else 1

    def get_total_pop(self):
        return self.pop.sum()

def create_region(
        config_file: str,
        config_dir='config/region_model'
    ) -> region:
    config = CovidConf(project_dir=repo_loc, config_file=config_file, config_dir=config_dir)
    
    ##### Extract region information #####
    region_name = config['region']['name']
    country = config['country']['name']
    age_group_pop_region = []
    for i in config['region']['population_group']:
        age_group_pop_region.append(config['region']['population_group'].get(i))
    age_group_pop_region = np.array(age_group_pop_region)
    age_group_pop_ratio_region = age_group_pop_region/age_group_pop_region.sum()

    # Daily cases
    df_region_case = pd.read_csv(repo_loc + config['raw_data'])
    acc_case = df_region_case[config['col_daily_case']].to_numpy() # accumulated Covid cases
    daily_case = np.append(acc_case[0], np.diff(acc_case))
    # if 'raw_data' in config.__dict__.keys():
        
    # elif config['region']['name'].upper() == 'WUHAN':
    #     acc_case = np.array(config['daily_accumulated_case_data']) # accumulated Covid cases

    # ICU beds
    if config['region']['name'].upper() == 'BAVARIA':
        # According to Wikipedia, there are 28000 ICU beds in Germany as of 16-Apr-2020
        # Using 83020000 as the total population of Germany and the ratio between 
        # German total population:Bavaria total population, can get ICU = 13076721/83020000*28000 = 4410
        pop_country = config['country']['population']
        icu_country = config['country']['icu_bed']
        t_icu_est = int(age_group_pop_region.sum()/pop_country*icu_country)
    elif config['region']['name'].upper() == 'WUHAN':
        # https://www.chainnews.com/articles/852047607288.htm
        # Assume there are 5 ICU beds per 100000 in China
        # Wuhan should have 5*wuhan_pop.sum()/100000 = 489
        # Also assume that the number of ICU is increased 3 times (2 new hospitals + additional resources from other provinces)
        t_icu_est = np.round(5*age_group_pop_region.sum()/100000*3)
    else:
        t_icu_est = config['region']['icu_bed_estimated']

    t_icu_ade = config['region']['icu_bed_required']

    # Number of deaths
    n_death = config['region']['death']

    ##### Build region attribute object #####
    region_obj = region(
        region_name, # region_name
        country, # country
        daily_case, # daily_case
        acc_case, # acc_case
        age_group_pop_region, # population age group
        age_group_pop_ratio_region, # population age group ratio
        t_icu_est, # estimated available number of ICUs
        t_icu_ade, # adequate number of ICU required
        n_death, # number of deaths
    )

    return region_obj