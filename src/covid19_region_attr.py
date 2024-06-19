import numpy as np
import pandas as pd

# TODO: fix the numbers by using variables rather than hard-coded numbers




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



############
# Bavaria
############

# Population at different age groups for Bavaria
pop_bavaria = np.array([1200904, 1217533, 1638957, 1717926, 1701205, 2108710, 1536697, 1170153, 784636])
pop_ratio_bavaria = pop_bavaria/pop_bavaria.sum()

# According to Wikipedia, there are 28000 ICU beds in Germany as of 16-Apr-2020
# Using 83020000 as the total population of Germany and the ratio between 
# German total population:Bavaria total population, can get ICU = 13076721/83020000*28000 = 4410
t_icu_est_bavaria = int(pop_bavaria.sum()/83020000*28000) # Initial estimated number of ICU beds in Bavaria

# Bavaria adequate ICU requirement: 3130 (total accumulated number of infected: 35142 16-Apr-2020)
t_icu_ade_bavaria = 3130
df_bavaria = pd.read_csv("./csv_input/df_Bavaria_cleaned_20200415.csv")

acc_case_bavaria = df_bavaria['Bavaria'].to_numpy() # accumulated number
daily_case_bavaria = np.append(acc_case_bavaria[0], np.diff(acc_case_bavaria)) # daily number
n_death_bavaria = 1049

bavaria = region(
    'Bavaria', # region_name
    'Germany', # country
    daily_case_bavaria, # daily_case
    acc_case_bavaria, # acc_case
    pop_bavaria, # population age group
    pop_ratio_bavaria, # population age group ratio
    t_icu_est_bavaria, # estimated available number of ICUs
    t_icu_ade_bavaria, # adequate number of ICU required
    n_death_bavaria, # number of deaths
)

############
# Lombardy
############

# Population at different age groups for Lombardy
pop_lombardy = np.array([884414, 961237, 982354, 1187594, 1591034, 1566175, 1182159, 994236, 711371])
pop_ratio_lombardy = pop_lombardy/pop_lombardy.sum()

t_icu_est_lombardy = 1174 # Initial estimated number of ICU beds in lombardy


df_lombardy = pd.read_csv("./csv_input/df_lombardia_cleaned_20200417.csv")

daily_case_lombardy = df_lombardy['LOM'].to_numpy() # daily number
acc_case_lombardy = np.cumsum(daily_case_lombardy) # accumulated number
n_death_lombardy = 9808

# Lombardy adequate ICU requirement: 4500 (total accumulated number of infected: 64135, 17-Apr-2020)
t_icu_ade_lombardy = 4500


lombardy = region(
    'Lombardy', # region_name
    'Italy', # country
    daily_case_lombardy, # daily_case
    acc_case_lombardy, # acc_case
    pop_lombardy, # population age group
    pop_ratio_lombardy, # population age group ratio
    t_icu_est_lombardy, # estimated available number of ICUs
    t_icu_ade_lombardy, # adequate number of ICU required
    n_death_lombardy, # number of deaths
)


#########
# Wuhan
#########

# https://www.citypopulation.de/php/china-hubei-admin_c.php?adm1id=4201
pop_wuhan = np.array([655178, 1193294, 2279487, 1486647, 1668609, 1261163, 718296, 391084, 131630])
# Based on 2010 data

pop_ratio_wuhan = pop_wuhan/pop_wuhan.sum()


acc_case_wuhan = np.array([495, 572, 618, 698, 1590, 1905, 2261, 2639, 3215, 4109, 5142, 6384, 8351, 10117, 11618, 13603, \
        14982, 16902, 18454, 19558, 32994, 35991, 37914, 39462, 41152, 42752, 44412, 45027, 45346, 45660, \
        46259, 46607, 47071, 47441, 47824, 48137, 48557, 49122, 49315, 49426, 49540, 49671, 49797, 49871, \
        49912, 49948, 49965, 49978, 49986, 49991, 49995, 49999, 50003, 50004, 50005, 50005, 50005, 50005, \
        50005, 50005, 50006, 50006, 50006, 50006, 50006, 50006, 50006, 50006, 50007, 50007, 50007, 50008, \
                     50008, 50008, 50008, 50008, 50008, 50008, 50008, 50008, 50008])

daily_case_wuhan = np.append(acc_case_wuhan[0], np.diff(acc_case_wuhan))

# https://www.chainnews.com/articles/852047607288.htm
# Assume there are 5 ICU beds per 100000 in China
# Wuhan should have 5*wuhan_pop.sum()/100000 = 489
# Also assume that the number of ICU is increased 3 times (2 new hospitals + additional resources from other provinces)
t_icu_est_wuhan = np.round(5*pop_wuhan.sum()/100000*3)

# Wuhan adequate ICU requirement: 3200 (total accumulated number of infected: 50008, 12-Apr-2020)
t_icu_ade_wuhan = 3200

n_death_wuhan = 3869

wuhan = region(
    'Wuhan', # region_name
    'China', # country
    daily_case_wuhan, # daily_case
    acc_case_wuhan, # acc_case
    pop_wuhan, # population age group
    pop_ratio_wuhan, # population age group ratio
    t_icu_est_wuhan, # estimated available number of ICUs
    t_icu_ade_wuhan, # adequate number of ICU required
    n_death_wuhan, # number of deaths
)

#######
# NSW
#######

# 2016 demographics "https://quickstats.censusdata.abs.gov.au/census_services/getproduct/census/2016/quickstat/1"
pop_nsw = np.array([465135 + 478184, 443009 + 448425, 489673 + 527161, 540360 + 499724, 503169 + 492440, 485546 + 469726, \
          420044 + 384470, 292556 + 217308, 155806 + 167506])

pop_ratio_nsw = pop_nsw/pop_nsw.sum()

df_nsw = pd.read_csv("./csv_input/df_NSW_cleaned_20200425.csv")

acc_case_nsw = df_nsw['acc_cases'].to_numpy() # accumulated number
daily_case_nsw = np.append(acc_case_nsw[0], np.diff(acc_case_nsw)) # daily number

# From ANZIC report
# https://www.anzics.com.au/wp-content/uploads/2019/10/2018-ANZICS-CORE-Report.pdf
# There are 874 ICU beds in 2018 report
t_icu_est_nsw = 874

n_death_nsw = 33

# NSW adequate ICU requirement: 230 (total accumulated number of infected: 2994, 25-Apr-2020)
t_icu_ade_nsw = 230

nsw = region(
    'NSW', # region_name
    'Australia', # country
    daily_case_nsw, # daily_case
    acc_case_nsw, # acc_case
    pop_nsw, # population age group
    pop_ratio_nsw, # population age group ratio
    t_icu_est_nsw, # estimated available number of ICUs
    t_icu_ade_nsw, # adequate number of ICU required
    n_death_nsw, # number of deaths
)