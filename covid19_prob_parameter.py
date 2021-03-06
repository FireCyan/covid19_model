#################################
# Import packages

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#################################

# Note that the rate for each age is store in the following list, with index 0 corresponding to 0-9 age group and 
# so on.

##########################################
# Assign parameters for different states
##########################################

death_rate_crude = np.array([0, 0.00182, 0.00193, 0.00237, 0.00443, 0.013, 0.036, 0.0796, 0.148])
death_rate_adj_censoring = np.array([0.000954, 0.00352, 0.00296, 0.00348, 0.00711, 0.0206, 0.0579, 0.127, 0.233])
death_rate_adj_censoring_under_asce = np.array([0.000026, 0.000148, 0.0006, 0.00146, 0.00295, 0.0125, 0.0399, \
                                                0.0861, 0.134])
# death_rate_hospitalised is used for hospitalised, ICU or ICU + vent to death
dr_h_0_59 = 1/30
death_rate_hospitalised = np.append(np.array(np.ones((6))*dr_h_0_59), np.array([1/11, 1/10, 1/5])).flatten()
# Based on Figure 3 from IMHE paper. Note that I took average of the hospitalizations per death value between groups
# because I used 10-19 rather than 15-24 age group.

death_rate_severe = 1 # Probability of death is set to 100% if a patient stays in severe state (without hospitalised)
death_rate_critical = 1 # Probability of death is set to 100% if a patient stays in critical state (without ICU or ICU + vent)

# severe_rate = np.array([0, 0.000408, 0.0104, 0.0343, 0.0425, 0.0816, 0.118, 0.166, 0.184]) # From Robert Verity et al. 2020

severe_rate = np.array([0.0006, 0.0006, 0.0078, 0.029, 0.0511, 0.099, 0.1549, 0.3576, 0.6594]).flatten() # from Moss et al. 2020

icu_rate = np.array([0.0002, 0.0002, 0.0023, 0.0085, 0.015, 0.0291, 0.0455, 0.105, 0.1936]).flatten() # from Moss et al. 2020

icu_with_vent_rate = 0.54 # from IMHE paper

n_age_group = severe_rate.shape[0]
n_state = 10

# Average days from one state to the other
# mild to others
avg_m_to_r = 10
avg_m_to_s = 2
avg_m_to_c = 3

# Severe to others
avg_s_to_c = 2
avg_s_to_d = 2
# Note that severe goes to hospitalisation straightaway provided bed is available

# Critical to others
avg_c_to_d = 1
# Note that critical goes to ICU straightaway provided ICU is available

# Hospitalised to others
avg_h_to_i = 2 # hospitalised to ICU
avg_h_to_v = 2 # hospitalised to ICU + ventilator
avg_h_to_r = 12 # Originally use 30
avg_h_to_d = 12 # Originally used 35

avg_i_to_d = 10
avg_i_to_r = 10

avg_v_to_d = 10
avg_v_to_r = 10

s_to_c_control = 1 # whether to have severe to critical (and hospitalised to ICU) pathways. 0 = no, 1 = yes
h_to_i_control = s_to_c_control

# m_c_rate = 0.5
s_c_rate = 0.3 # According to paper from Moss et al. 2020, the ratio between hospitalised and ICU is 3:1.
h_i_rate = s_c_rate



##################################
# Probabilities for state changes
##################################
# Mild to other states' probabilities
Pms = severe_rate/avg_m_to_s
Pmc = icu_rate/avg_m_to_c
# The percentage of mild to recover is the probability of not getting severe or critical (1 - Ps - Pc).
# The value is then divided by the average days from mild to recover.
Pmr = (1 - severe_rate - icu_rate)/avg_m_to_r
# The probability of staying at the same state is 1 minus the probability of going to other states.
Pmm = 1 - Pms - Pmc - Pmr

Pmh = np.zeros((n_age_group))
Pmhiw = np.zeros((n_age_group))
Pmhvw = np.zeros((n_age_group))
Pmi = np.zeros((n_age_group))
Pmv = np.zeros((n_age_group))
Pmd = np.zeros((n_age_group))


# Severe to other states' probabilities
Psc = np.ones((n_age_group))*s_c_rate/avg_s_to_c * s_to_c_control
Psh = np.zeros((n_age_group)) # This value is dynamic. It depends on the number of normal beds available
Psd = np.ones((n_age_group))*death_rate_severe/avg_s_to_d # Assumption: 100% death rate if not hospitalised
Pss = 1 - Psc - Psh - Psd

Psr = np.zeros((n_age_group)) # Assumption: there is no patient who can recover from severe state without hospitalisation
Psm = np.zeros((n_age_group))
Pshiw = np.zeros((n_age_group))
Pshvw = np.zeros((n_age_group))
Psi = np.zeros((n_age_group)) # severe case does not go to ICU straight away
Psv = np.zeros((n_age_group)) # severe case does not go to ICU + ventilator straight away


# Critical to other states' probabilities
Pci = np.zeros((n_age_group)) # This value is dynamic. It depends on the number of ICU available
Pcv = np.zeros((n_age_group)) # This value is dynamic. It depends on the number of ICU + ventilator available
Pcd = np.ones((n_age_group))*death_rate_critical/avg_c_to_d # Assumption: 100% death rate if not hospitalised
Pcc = 1 - Pci - Pcv - Pcd

Pcm = np.zeros((n_age_group))
Pcs = np.zeros((n_age_group))
Pch = np.zeros((n_age_group)) # critical condition goes to ICU, not normal bed
Pchiw = np.zeros((n_age_group))
Pchvw = np.zeros((n_age_group))
Pcr = np.zeros((n_age_group)) # Assumption: there is no patient who can recover from critical state without hospitalisation


# Hospitalised to other states' probabilities
Phi = np.zeros((n_age_group)) # This parameter depends on the number of ICU available
Phv = np.zeros((n_age_group)) # This parameter depends on the number of ICU + ventilator available
Phhiw = np.zeros((n_age_group)) # This parameter depends on the shortage of ICU
Phhvw = np.zeros((n_age_group)) # This parameter depends on the shortage of ICU + ventilator
Phd = death_rate_hospitalised/avg_h_to_d
Phr = (1 - death_rate_hospitalised)/avg_h_to_r
Phh = 1 - Phi - Phv - Phhiw - Phhvw - Phd - Phr 

Phm = np.zeros((n_age_group))
Phs = np.zeros((n_age_group))
Phc = np.zeros((n_age_group))


# Hospitalised awaiting ICU to other states' probabilities
Phiwi = np.zeros((n_age_group)) # This parameter depends on the number of ICU available
Phiwd = np.ones((n_age_group))*death_rate_critical/avg_c_to_d # Assumption: 100% death rate if not transferred to ICU
Phiwhiw = 1 - Phiwi - Phiwd # This should be 0 if avg_c_to_d is 1, which means that a patient would either go to ICU or pass away the next day

Phiwm = np.zeros((n_age_group))
Phiws = np.zeros((n_age_group))
Phiwc = np.zeros((n_age_group))
Phiwr = np.zeros((n_age_group))
Phiwh = np.zeros((n_age_group))
Phiwv = np.zeros((n_age_group)) # Patients waiting for ICU do not go to ICU + ventialtor
Phiwhvw = np.zeros((n_age_group))


# Hospitalised awaiting ICU + ventilator to other states' probabilities
Phvwv = np.zeros((n_age_group)) # This parameter depends on the number of ICU + ventilators available
Phvwd = np.ones((n_age_group))*death_rate_critical/avg_c_to_d # Assumption: 100% death rate if not transferred to ICU + ventilator
Phvwhvw = 1 - Phvwv - Phvwd # This should be 0 if avg_c_to_d is 1, which means that a patient would either go to ICU + ventilator or pass away the next day

Phvwm = np.zeros((n_age_group))
Phvws = np.zeros((n_age_group))
Phvwc = np.zeros((n_age_group))
Phvwr = np.zeros((n_age_group)) # Patients waiting for ICU + ventilator do not recover by themselves
Phvwh = np.zeros((n_age_group))
Phvwi = np.zeros((n_age_group)) # Patients waiting for ICU + ventilator do not go to ICU
Phvwhiw = np.zeros((n_age_group))


# ICU state to other states' probabilities
Pid = death_rate_hospitalised/avg_i_to_d
Pir = (1 - death_rate_hospitalised)/avg_i_to_r
Pii = 1 - Pid - Pir

Pim = np.zeros((n_age_group))
Pis = np.zeros((n_age_group))
Pic = np.zeros((n_age_group))
Pih = np.zeros((n_age_group))
Piv = np.zeros((n_age_group)) # Assumption and simplification: ICU state does not go to ICU + ventilator state
Pihiw = np.zeros((n_age_group)) # Patient in ICU don't go back on waiting for ICU
Pihvw = np.zeros((n_age_group)) # Patient in ICU don't go back on waiting for ICU + ventilator


# ICU + ventilator state to other states' probabilities
Pvd = death_rate_hospitalised/avg_v_to_d
Pvr = (1 - death_rate_hospitalised)/avg_v_to_r
Pvv = 1 - Pvd - Pvr

Pvm = np.zeros((n_age_group))
Pvs = np.zeros((n_age_group))
Pvc = np.zeros((n_age_group))
Pvh = np.zeros((n_age_group))
Pvi = np.zeros((n_age_group)) # Assumption and simplification: ICU + ventilaotr state does not go to ICU
Pvhiw = np.zeros((n_age_group)) # Patient in ICU + ventilator don't go back on waiting for ICU
Pvhvw = np.zeros((n_age_group)) # Patient in ICU + ventilator don't go back on waiting for ICU + ventilator


# Recovered to other states
Prm = np.zeros((n_age_group))
Prs = np.zeros((n_age_group))
Prc = np.zeros((n_age_group))
Prh = np.zeros((n_age_group))
Prhiw = np.zeros((n_age_group))
Prhvw = np.zeros((n_age_group))
Pri = np.zeros((n_age_group))
Prv = np.zeros((n_age_group))
Prr = np.ones((n_age_group))
Prd = np.zeros((n_age_group))

# Death to other states
Pdm = np.zeros((n_age_group))
Pds = np.zeros((n_age_group))
Pdc = np.zeros((n_age_group))
Pdh = np.zeros((n_age_group))
Pdhiw = np.zeros((n_age_group))
Pdhvw = np.zeros((n_age_group))
Pdi = np.zeros((n_age_group))
Pdv = np.zeros((n_age_group))
Pdr = np.zeros((n_age_group))
Pdd = np.ones((n_age_group))


############################################
# Initialise and set up state numbers/names
############################################
P_matrix = np.zeros((n_state, n_state, n_age_group))

state_num = {}

state_num["m_state"]= 0
state_num["s_state"] = 1
state_num["c_state"] = 2
state_num["h_state"] = 3
state_num["hiw_state"] = 4
state_num["hvw_state"] = 5
state_num["i_state"] = 6
state_num["v_state"] = 7
state_num["r_state"] = 8
state_num["d_state"] = 9


P_matrix[state_num["m_state"], state_num["m_state"], :] = Pmm
P_matrix[state_num["m_state"], state_num["s_state"], :] = Pms
P_matrix[state_num["m_state"], state_num["c_state"], :] = Pmc
P_matrix[state_num["m_state"], state_num["h_state"], :] = Pmh
P_matrix[state_num["m_state"], state_num["i_state"], :] = Pmi
P_matrix[state_num["m_state"], state_num["v_state"], :] = Pmv
P_matrix[state_num["m_state"], state_num["hiw_state"], :] = Pmhiw
P_matrix[state_num["m_state"], state_num["hvw_state"], :] = Pmhvw
P_matrix[state_num["m_state"], state_num["r_state"], :] = Pmr
P_matrix[state_num["m_state"], state_num["d_state"], :] = Pmd


P_matrix[state_num["s_state"], state_num["m_state"], :] = Psm
P_matrix[state_num["s_state"], state_num["s_state"], :] = Pss
P_matrix[state_num["s_state"], state_num["c_state"], :] = Psc
P_matrix[state_num["s_state"], state_num["h_state"], :] = Psh
P_matrix[state_num["s_state"], state_num["hiw_state"], :] = Pshiw
P_matrix[state_num["s_state"], state_num["hvw_state"], :] = Pshvw
P_matrix[state_num["s_state"], state_num["i_state"], :] = Psi
P_matrix[state_num["s_state"], state_num["v_state"], :] = Psv
P_matrix[state_num["s_state"], state_num["r_state"], :] = Psr
P_matrix[state_num["s_state"], state_num["d_state"], :] = Psd


P_matrix[state_num["c_state"], state_num["m_state"], :] = Pcm
P_matrix[state_num["c_state"], state_num["s_state"], :] = Pcs
P_matrix[state_num["c_state"], state_num["c_state"], :] = Pcc
P_matrix[state_num["c_state"], state_num["h_state"], :] = Pch
P_matrix[state_num["c_state"], state_num["hiw_state"], :] = Pchiw
P_matrix[state_num["c_state"], state_num["hvw_state"], :] = Pchvw
P_matrix[state_num["c_state"], state_num["i_state"], :] = Pci
P_matrix[state_num["c_state"], state_num["v_state"], :] = Pcv
P_matrix[state_num["c_state"], state_num["r_state"], :] = Pcr
P_matrix[state_num["c_state"], state_num["d_state"], :] = Pcd


P_matrix[state_num["h_state"], state_num["m_state"], :] = Phm
P_matrix[state_num["h_state"], state_num["s_state"], :] = Phs
P_matrix[state_num["h_state"], state_num["c_state"], :] = Phc
P_matrix[state_num["h_state"], state_num["h_state"], :] = Phh
P_matrix[state_num["h_state"], state_num["hiw_state"], :] = Phhiw
P_matrix[state_num["h_state"], state_num["hvw_state"], :] = Phhvw
P_matrix[state_num["h_state"], state_num["i_state"], :] = Phi
P_matrix[state_num["h_state"], state_num["v_state"], :] = Phv
P_matrix[state_num["h_state"], state_num["r_state"], :] = Phr
P_matrix[state_num["h_state"], state_num["d_state"], :] = Phd


P_matrix[state_num["hiw_state"], state_num["m_state"], :] = Phiwm
P_matrix[state_num["hiw_state"], state_num["s_state"], :] = Phiws
P_matrix[state_num["hiw_state"], state_num["c_state"], :] = Phiwc
P_matrix[state_num["hiw_state"], state_num["h_state"], :] = Phiwh
P_matrix[state_num["hiw_state"], state_num["hiw_state"], :] = Phiwhiw
P_matrix[state_num["hiw_state"], state_num["hvw_state"], :] = Phiwhvw
P_matrix[state_num["hiw_state"], state_num["i_state"], :] = Phiwi
P_matrix[state_num["hiw_state"], state_num["v_state"], :] = Phiwv
P_matrix[state_num["hiw_state"], state_num["r_state"], :] = Phiwr
P_matrix[state_num["hiw_state"], state_num["d_state"], :] = Phiwd


P_matrix[state_num["hvw_state"], state_num["m_state"], :] = Phvwm
P_matrix[state_num["hvw_state"], state_num["s_state"], :] = Phvws
P_matrix[state_num["hvw_state"], state_num["c_state"], :] = Phvwc
P_matrix[state_num["hvw_state"], state_num["h_state"], :] = Phvwh
P_matrix[state_num["hvw_state"], state_num["hiw_state"], :] = Phvwhiw
P_matrix[state_num["hvw_state"], state_num["hvw_state"], :] = Phvwhvw
P_matrix[state_num["hvw_state"], state_num["i_state"], :] = Phvwi
P_matrix[state_num["hvw_state"], state_num["v_state"], :] = Phvwv
P_matrix[state_num["hvw_state"], state_num["r_state"], :] = Phvwr
P_matrix[state_num["hvw_state"], state_num["d_state"], :] = Phvwd


P_matrix[state_num["i_state"], state_num["m_state"], :] = Pim
P_matrix[state_num["i_state"], state_num["s_state"], :] = Pis
P_matrix[state_num["i_state"], state_num["c_state"], :] = Pic
P_matrix[state_num["i_state"], state_num["h_state"], :] = Pih
P_matrix[state_num["i_state"], state_num["hiw_state"], :] = Pihiw
P_matrix[state_num["i_state"], state_num["hvw_state"], :] = Pihvw
P_matrix[state_num["i_state"], state_num["i_state"], :] = Pii
P_matrix[state_num["i_state"], state_num["v_state"], :] = Piv
P_matrix[state_num["i_state"], state_num["r_state"], :] = Pir
P_matrix[state_num["i_state"], state_num["d_state"], :] = Pid


P_matrix[state_num["v_state"], state_num["m_state"], :] = Pvm
P_matrix[state_num["v_state"], state_num["s_state"], :] = Pvs
P_matrix[state_num["v_state"], state_num["c_state"], :] = Pvc
P_matrix[state_num["v_state"], state_num["h_state"], :] = Pvh
P_matrix[state_num["v_state"], state_num["hiw_state"], :] = Pvhiw
P_matrix[state_num["v_state"], state_num["hvw_state"], :] = Pvhvw
P_matrix[state_num["v_state"], state_num["i_state"], :] = Pvi
P_matrix[state_num["v_state"], state_num["v_state"], :] = Pvv
P_matrix[state_num["v_state"], state_num["r_state"], :] = Pvr
P_matrix[state_num["v_state"], state_num["d_state"], :] = Pvd


P_matrix[state_num["r_state"], state_num["m_state"], :] = Prm
P_matrix[state_num["r_state"], state_num["s_state"], :] = Prs
P_matrix[state_num["r_state"], state_num["c_state"], :] = Prc
P_matrix[state_num["r_state"], state_num["h_state"], :] = Prh
P_matrix[state_num["r_state"], state_num["hiw_state"], :] = Prhiw
P_matrix[state_num["r_state"], state_num["hvw_state"], :] = Prhvw
P_matrix[state_num["r_state"], state_num["i_state"], :] = Pri
P_matrix[state_num["r_state"], state_num["v_state"], :] = Prv
P_matrix[state_num["r_state"], state_num["r_state"], :] = Prr
P_matrix[state_num["r_state"], state_num["d_state"], :] = Prd


P_matrix[state_num["d_state"], state_num["m_state"], :] = Pdm
P_matrix[state_num["d_state"], state_num["s_state"], :] = Pds
P_matrix[state_num["d_state"], state_num["c_state"], :] = Pdc
P_matrix[state_num["d_state"], state_num["h_state"], :] = Pdh
P_matrix[state_num["d_state"], state_num["hiw_state"], :] = Pdhiw
P_matrix[state_num["d_state"], state_num["hvw_state"], :] = Pdhvw
P_matrix[state_num["d_state"], state_num["i_state"], :] = Pdi
P_matrix[state_num["d_state"], state_num["v_state"], :] = Pdv
P_matrix[state_num["d_state"], state_num["r_state"], :] = Pdr
P_matrix[state_num["d_state"], state_num["d_state"], :] = Pdd


####################################
# Initialise and set up death cause
####################################
d_cause_num = {}

d_cause_num["s"]= 0
d_cause_num["c_hiw"] = 1
d_cause_num["c_hvw"] = 2
d_cause_num["h"] = 3
d_cause_num["i"] = 4
d_cause_num["v"] = 5

n_death_cause = len(d_cause_num)