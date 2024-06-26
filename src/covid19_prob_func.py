###############################
# Import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.covid19_prob_parameter import state_num
################################

###########################################################
# Update the state change probabilities from severe state #
###########################################################
def severe_prob_update(
        x: np.array,
        a_hosp_bed: int,
        n_age_group: int,
        young_age_first: bool
    ) -> np.array:
    '''
    Update the probability of severe state to hospitalised state given the number of hospital beds available

    Args:
        x (np.array): number of patients in each age group (1st dimension) and each state (2nd dimension)
        a_hosp_bed (int): number of hospital beds
        n_age_group (int): number of age groups
        young_age_first (bool): whether to assign beds to younger age groups (Yes if True, otherwise assign evenly)
    
    Return:
        Psh (np.array): Probability to transition from severe to hospitalised (for each age group)
    '''
    # Severe case update testing
    Psh = np.zeros((n_age_group))

    if a_hosp_bed > 0:
        n_severe = x[:, state_num["s_state"]]
        zero_mask = n_severe == 0
        
        if not young_age_first:
            n_severe = np.array(x.sum(axis=0)[state_num["s_state"]])

        severe_mat_acc = n_severe.cumsum(axis=0)
        hosp_bed_left = a_hosp_bed - np.insert(severe_mat_acc, 0, 0)[:-1]


        if len(severe_mat_acc) == 1:
            severe_mat_acc = np.ones(n_age_group)*severe_mat_acc[0]
            hosp_bed_left = np.ones(n_age_group)*hosp_bed_left[0]

        full_fill_mask = np.bitwise_and((severe_mat_acc <= a_hosp_bed), ~zero_mask)

        partial_fill_mask = np.bitwise_and(np.bitwise_and(~full_fill_mask, hosp_bed_left >= 0), ~zero_mask)

        if full_fill_mask.any():
            Psh[full_fill_mask] = 1
        if partial_fill_mask.any():
            Psh[partial_fill_mask] = \
            np.array(hosp_bed_left[partial_fill_mask]/n_severe[partial_fill_mask]).flatten()
    
    return Psh

#######################################################################
# Update the state change probabilities from ICU or ventilation states 
#######################################################################
def icu_or_vent_prob_update(
        a_resource: int,
        r_mat_acc: np.array,
        n_hosp: np.array,
        n_critical: np.array,
        n_age_group: int,
        young_age_first: bool
    ):
    '''
    Update the probability of other states entering ICU or ventilator states based on the ICU beds or ventilators available and the number of hospitalised and critial patients.
    The general idea is to fill in all the available ICU beds or ventilators to those who are waiting, and if there is a shortage, then update the state probability accordingly. 

    Args:
        a_resource (int): number of ICU beds or ventilators available
        r_mat_acc (np.array): accumulated number of patients waiting for ICU beds or ventilators
        n_hosp (np.array): number of hospitalised patients for each age group
        n_critical (np.array): number of critical patients for each age group
        n_age_group (int): number of age groups
        young_age_first (bool): whether to assign beds to younger age groups (Yes if True, otherwise assign evenly)
    
    Return:
        Phxwx (np.array): Probability to transition from waiting for ICU beds or ventilators to getting ICU beds or ventilators
        Phx (np.array): Probability to transition from hospitalised to having ICU beds or ventilators
        Pcx (np.array): Probability to transition from critical to having ICU beds or ventilators
        used_resource (int): how many ICU beds or ventilators have been used
        r_full_fill_mask(np.array): groups that have all ICU beds or ventilators fulfilled
        r_partial_fill_mask (np.array): groups that have ICU beds or ventilators partially fulfilled
        resource_left (np.array): number of ICU beds or ventlators left after assigning to those in needs
    '''
    
    Phxwx = np.zeros((n_age_group))
    Phx = np.zeros((n_age_group))
    Pcx = np.zeros((n_age_group))
    used_resource = 0
    r_full_fill_mask = ""
    r_partial_fill_mask = ""
    resource_left = ""
    
    if a_resource > 0:
        n_awaiting = r_mat_acc[0]
        n_h_to_needing = r_mat_acc[1]
        n_critical_to_resource = r_mat_acc[2]
        
        zero_mask_awaiting = n_awaiting == 0
        zero_mask_h_to_needing = n_h_to_needing == 0
        zero_mask_critical_to_resource = n_critical_to_resource == 0
        
        if not young_age_first:
            # If young_age_first is not applied, then let the sum of each state for all age groups to be the same
            # To do so, accumulate the sum over columns
            r_mat_acc = r_mat_acc.sum(axis=1)
            # Repeat the same number of patient over all age group for consistent probability computation
            n_awaiting = np.repeat(n_awaiting.sum(), n_age_group)
            n_hosp = np.repeat(n_hosp.sum(), n_age_group)
            n_h_to_needing = np.repeat(n_h_to_needing.sum(), n_age_group)
            n_critical = np.repeat(n_critical.sum(), n_age_group)
            n_critical_to_resource = np.repeat(n_critical_to_resource.sum(), n_age_group)

        r_mat_acc = r_mat_acc.flatten(order='F')
        r_mat_acc = r_mat_acc.cumsum(axis=0)
        resource_left = a_resource - np.insert(r_mat_acc, 0, 0)[:-1]
        
        if young_age_first:
            r_mat_acc = np.reshape(r_mat_acc, (3, n_age_group), order='F')
            resource_left = np.reshape(resource_left, (3, n_age_group), order='F')
        else:
            r_mat_acc = np.repeat(r_mat_acc, n_age_group, axis=0).reshape(3, n_age_group)
            resource_left = np.repeat(resource_left, n_age_group, axis=0).reshape(3, n_age_group)

        r_full_fill_mask = r_mat_acc <= a_resource
        r_full_fill_mask[0, :] = np.bitwise_and(r_full_fill_mask[0, :], ~zero_mask_awaiting)
        r_full_fill_mask[1, :] = np.bitwise_and(r_full_fill_mask[1, :], ~zero_mask_h_to_needing)
        r_full_fill_mask[2, :] = np.bitwise_and(r_full_fill_mask[2, :], ~zero_mask_critical_to_resource)

        r_partial_fill_mask = np.bitwise_and(~r_full_fill_mask, resource_left >= 0)
        r_partial_fill_mask[0, :] = np.bitwise_and(r_partial_fill_mask[0, :], ~zero_mask_awaiting)
        r_partial_fill_mask[1, :] = np.bitwise_and(r_partial_fill_mask[1, :], ~zero_mask_h_to_needing)
        r_partial_fill_mask[2, :] = np.bitwise_and(r_partial_fill_mask[2, :], ~zero_mask_critical_to_resource)
        
        if r_full_fill_mask[0, :].any():
            Phxwx[r_full_fill_mask[0, :]] = 1
        if r_partial_fill_mask[0, :].any():
            Phxwx[r_partial_fill_mask[0, :]] = \
            np.array(resource_left[0, r_partial_fill_mask[0, :]]/n_awaiting[r_partial_fill_mask[0, :]]).flatten()

        if r_full_fill_mask[1, :].any():            
            Phx[r_full_fill_mask[1, :]] = \
            (n_h_to_needing[r_full_fill_mask[1, :]]/n_hosp[r_full_fill_mask[1, :]]).flatten()

        if r_partial_fill_mask[1, :].any():
            Phx[r_partial_fill_mask[1, :]] = \
            np.array(resource_left[1, r_partial_fill_mask[1, :]]/n_hosp[r_partial_fill_mask[1, :]]).flatten()

        if r_full_fill_mask[2, :].any():
            Pcx[r_full_fill_mask[2, :]] = \
            (n_critical_to_resource[r_full_fill_mask[2, :]]/n_critical[r_full_fill_mask[2, :]]).flatten()
        if r_partial_fill_mask[2, :].any():
            Pcx[r_partial_fill_mask[2, :]] = \
            np.array(resource_left[2, r_partial_fill_mask[2, :]]/n_critical[r_partial_fill_mask[2, :]]).flatten()
        
        if young_age_first:
            used_resource = np.multiply(Phxwx, n_awaiting) + \
            np.multiply(Phx, n_hosp) + np.multiply(Pcx, n_critical)
        else:
            used_resource = Phxwx[0]*n_awaiting[0] + Phx[0]*n_hosp[0] + \
            Pcx[0]*n_critical[0]
        
        used_resource = used_resource.sum()
    
    return Phxwx, Phx, Pcx, used_resource, r_full_fill_mask, r_partial_fill_mask, resource_left

#############################################
# Update the number of deaths and the cause
#############################################

def death_num_update(
        x: np.array,
        P_matrix: np.array,
        icu_with_vent_rate: float,
        n_age_group: int,
        d_cause_num: dict,
    ) -> np.array:
    '''
    Update the number of deaths for each age group and cause

    Args:
        x (np.array): number of patients in each age group (1st dimension) and each state (2nd dimension)
        P_matrix (np.array): state transition probability matrix (Markov matrix)
        icu_with_vent_rate (float): the ratio of ventilator:ICU beds
        n_age_group (int): number of age groups
        d_cause_num (dict): dictionary that has death causes as keys and ordered numbers as values
    
    Return:
        death_cause_mat (np.array): number of deaths for each age group and cause
    '''
    
    # Death due to lack of hospital beds
    n_death_cause = len(d_cause_num)
    death_cause_mat = np.zeros((n_age_group, n_death_cause))
    
    death_cause_mat[:, d_cause_num['s']] = \
    np.floor(np.multiply(x[:, state_num['s_state']], P_matrix[state_num['s_state'],state_num['d_state'], :]))
        
    death_cause_mat[:, d_cause_num['c_hiw']] = \
    np.floor(np.multiply(x[:, state_num['c_state']], \
                    P_matrix[state_num['c_state'],state_num['d_state'], :])*(1 - icu_with_vent_rate)) + \
    np.floor(np.multiply(x[:, state_num['hiw_state']], P_matrix[state_num['hiw_state'],state_num['d_state'], :]))
        
    death_cause_mat[:, d_cause_num['c_hvw']] = \
    np.floor(np.multiply(x[:, state_num['c_state']], \
                    P_matrix[state_num['c_state'],state_num['d_state'],:])*icu_with_vent_rate) + \
    np.floor(np.multiply(x[:, state_num['hvw_state']], P_matrix[state_num['hvw_state'],state_num['d_state'],:]))
    
    death_cause_mat[:, d_cause_num['h']] = \
    np.floor(np.multiply(x[:, state_num['h_state']], P_matrix[state_num['h_state'],state_num['d_state'], :]))
    
    death_cause_mat[:, d_cause_num['i']] = \
    np.floor(np.multiply(x[:, state_num['i_state']], P_matrix[state_num['i_state'],state_num['d_state'], :]))
    
    death_cause_mat[:, d_cause_num['v']] = \
    np.floor(np.multiply(x[:, state_num['v_state']], P_matrix[state_num['v_state'],state_num['d_state'], :]))
    
    return death_cause_mat

############################################################################################################################################
# Update the state change probabilities based on the numbers of paitients in each state, the number of available beds, ICUs and ventilators
# Would call severe_prob_update() and icu_or_vent_prob_update() for the state change probability update
############################################################################################################################################

def update_prob(
        P_matrix: np.array,
        dict_initial_rate: dict,
        x: np.array,
        t_hosp_bed,
        t_icu,
        t_vent,
        n_age_group=9,
        young_age_first=True
    ):
    # If young_age first, then tyounger people have higher priority to get medical resouces 
    # (unfortunate in this situation)
    '''
    Update the state transition probability matrix 

    Args:
        P_matrix (np.array): state transition probability matrix (Markov matrix)
        dict_initial_rate (dict): dictionary containing the initial probability matrix values
        x (np.array): number of patients in each age group (1st dimension) and each state (2nd dimension)
        t_hosp_bed (int): Number of hospital beds available
        t_icu (int): Number of ICU beds available
        t_vent (int): Number of ventilators available
        n_age_group (int): number of age groups
        young_age_first (bool): whether to assign beds to younger age groups (Yes if True, otherwise assign evenly)
    
    Return:
        P_matrix (np.array): state transition probability matrix (Markov matrix)
        a_hosp_bed (int): number of hospital beds available after updating probability matrix
        a_icu (int): number of ICU beds available after updating probability matrix
        a_vent (int): number of ventilators available after updating probability matrix
    '''

    h_i_rate = dict_initial_rate['h_i_rate']
    icu_with_vent_rate = dict_initial_rate['icu_with_vent_rate']

    Psc = dict_initial_rate['Psc']
    Psd = dict_initial_rate['Psd']
    Pcd = dict_initial_rate['Pcd']
    
    Phr = dict_initial_rate['Phr']
    Phd = dict_initial_rate['Phd']
    Pir = dict_initial_rate['Pir']
    Pid = dict_initial_rate['Pid']
    Pvr = dict_initial_rate['Pvr']
    Pvd = dict_initial_rate['Pvd']
    Phiwd = dict_initial_rate['Phiwd']
    Phvwd = dict_initial_rate['Phvwd']
    
    # Update the number of empty hospital beds and the probability of Psh
    # Patients who will recover or pass away will vacate the hospital bed
    vacated_bed = np.floor(np.multiply(x[:, state_num['h_state']], Phr)) + \
    np.floor(np.multiply(x[:, state_num['h_state']], Phd))
    
    a_hosp_bed = t_hosp_bed - x.sum(axis=0)[state_num["h_state"]] + vacated_bed.sum()
    
    Psh = severe_prob_update(x, a_hosp_bed, n_age_group, young_age_first)
        
    # There are 3 pathways of getting into ICU or ICU + ventilator
    # 1. Patients whose conditions have already worsened (in hiw and hvw state) and are waiting for ICU or ICU + ventilator
    # 2. Hospitalised patients whose conditions would (in h state) worsen and need ICU or ICU + ventilator
    # 3. Patients who have not been hospitalised but present critical conditions
    # To simplify the model, the order in which these patients would been filled would follow 1, 2 and 3.
    # Note that for patients in 2, if they don't get ICU or ICU + ventilator, they would all go to 1 (hiw and hvw)
    # Update critical case probability
    # Fill in ventilators first
    n_severe = x[:, state_num["s_state"]]
    n_critical = x[:, state_num["c_state"]]
    n_hosp = x[:, state_num["h_state"]]
    n_icu = x[:, state_num["i_state"]]
    n_icu_vent = x[:, state_num["v_state"]]
    n_icu_awaiting = x[:, state_num["hiw_state"]]
    n_icu_vent_awaiting = x[:, state_num["hvw_state"]]    
    
    # Hospitalised to (ICU or ICU + vent) OR (awaiting ICU or ICU + vent) would depend on ICU and vent availability
    n_h_to_needing_icu = np.floor(np.round(n_hosp*h_i_rate)*(1 - icu_with_vent_rate))
    # print('n_h_to_needing_icu: ', n_h_to_needing_icu)
    n_h_to_needing_icu_vent = np.round(n_hosp*h_i_rate) - n_h_to_needing_icu
    # print('n_h_to_needing_icu_vent: ', n_h_to_needing_icu_vent)

    n_critical_to_icu = np.floor(n_critical*(1 - icu_with_vent_rate))
    n_critical_to_icu_vent = n_critical - n_critical_to_icu
    
    vacated_icu = np.floor(np.multiply(x[:, state_num['i_state']], Pir)) + \
    np.floor(np.multiply(x[:, state_num['i_state']], Pid)) + \
    np.floor(np.multiply(x[:, state_num['v_state']], Pvr)) + \
    np.floor(np.multiply(x[:, state_num['v_state']], Pvd))
    
    vacated_vent = np.floor(np.multiply(x[:, state_num['v_state']], Pvr)) + \
    np.floor(np.multiply(x[:, state_num['v_state']], Pvd))

    # available ICU = total - number of patients in ICU and ICU + vent
    a_icu = t_icu - n_icu.sum() - n_icu_vent.sum() + vacated_icu.sum()
    a_vent = t_vent - n_icu_vent.sum() + vacated_vent.sum()
    a_resource = np.amin([a_icu, a_vent])

    # Fill in ICU + vent first
    v_mat_acc = np.concatenate(([n_icu_vent_awaiting], [n_h_to_needing_icu_vent], \
                                [n_critical_to_icu_vent]), axis=0)


    Phvwv, Phv, Pcv, used_icu_vent, _, _, _ = \
    icu_or_vent_prob_update(a_resource, v_mat_acc, n_hosp, n_critical, n_age_group, young_age_first)

    # Update available resources 
    # (by taking away resources that will be used by the number of patients who will get ICU + vent)
    a_icu = a_icu - used_icu_vent
    a_vent = a_vent - used_icu_vent    
    
    # Fill in the rest of ICU beds
    i_mat_acc = np.concatenate(([n_icu_awaiting], [n_h_to_needing_icu], \
                                [n_critical_to_icu]), axis=0)

    Phiwi, Phi, Pci, used_icu, _, _, _ = \
    icu_or_vent_prob_update(a_icu, i_mat_acc, n_hosp, n_critical, n_age_group, young_age_first)

    # Update available resources 
    a_icu = a_icu - used_icu
    
    
    # Update probabilities and the P_matrix
    
    # Severe cases
    # The porbability of severe cases that will develop into critical state if not hospitalised is adjusted based on 
    # hospitalised (left severe cases untreated = (1 - Psh))
    severe_zero_mask = n_severe == 0
    # print("severe_zero_mask: ", severe_zero_mask)
    nPsc = np.zeros((n_age_group))
    nPsd = np.zeros((n_age_group))
    
    if not severe_zero_mask.all():
        nPsc[~severe_zero_mask] = (1 - Psh[~severe_zero_mask])*Psc[~severe_zero_mask]
    # The probability of severe cases that will pass away if not hospitalised is adjusted based on 
    # hospitalised (left severe cases untreated = (1 - Psh))
        nPsd[~severe_zero_mask] = (1 - Psh[~severe_zero_mask])*Psd[~severe_zero_mask]
    
    Pss = 1 - nPsc - Psh - nPsd
    
    # Critical cases
    # The probability of critical cases that will pass away if not sent into ICU is adjusted based on 
    # ICU and ICU + vent (left critical cases untreated = (1 - Pci - Pcv))
    critical_zero_mask = n_critical == 0
    nPcd = np.zeros((n_age_group))
    
    if not critical_zero_mask.all():
        nPcd[~critical_zero_mask] = (1 - Pci[~critical_zero_mask] - Pcv[~critical_zero_mask])*Pcd[~critical_zero_mask]
    nPcd[np.absolute(nPcd) < 1e-6] = 0
    Pcc = 1 - Pci - Pcv - nPcd
    # print("nPcd: ", nPcd)
    # print("Pcc: ", Pcc)
    
    
    # Hospitalised cases
    # The probability of hospitalised cases that will recover or pass away is adjusted based on 
    # hospitalised to other states (left hospitalised cases = (1 - Phi - Phv - Phhiw - Phhvw))
    h_zero_mask = n_hosp == 0
    Phhiw = np.zeros((n_age_group))
    Phhvw = np.zeros((n_age_group))
    if not h_zero_mask.all():
        if a_icu == 0:
            Phhiw[~h_zero_mask] = h_i_rate*(1 - icu_with_vent_rate) - Phi[~h_zero_mask]
        if a_vent == 0:
            Phhvw[~h_zero_mask] = h_i_rate*icu_with_vent_rate - Phv[~h_zero_mask]
#   # sometimes due to rounding, Phi can go over the limit (h_i_rate*(1 - icu_with_vent_rate)) a little
    Phhiw[Phhiw < 0] = 0
    
#   # sometimes due to rounding, Phv can go over the limit (h_i_rate*(1 - icu_with_vent_rate)) a little
    Phhvw[Phhvw < 0] = 0
    
    nPhr = (1 - Phi - Phv - Phhiw - Phhvw)*Phr
    nPhd = (1 - Phi - Phv - Phhiw - Phhvw)*Phd
    Phh = 1 - Phi - Phv - Phhiw - Phhvw - nPhd - nPhr
    
    # The probability of hospitalised cases awaiting ICU will pass away is adjusted based on 
    # hospitalised cases awaiting ICU to other states 
    # (left hospitalised cases awaiting ICU = (1 - Phiwi))
    hiw_zero_mask = n_icu_awaiting == 0
    nPhiwd = np.zeros((n_age_group))
    
    if not hiw_zero_mask.all():
        nPhiwd[~hiw_zero_mask] = (1 - Phiwi[~hiw_zero_mask])*Phiwd[~hiw_zero_mask]
    Phiwhiw = 1 - Phiwi - nPhiwd
    
    # The probability of hospitalised cases awaiting ICU + vent will pass away is adjusted based on 
    # hospitalised cases awaiting ICU + vent to other states 
    # (left hospitalised cases awaiting ICU + vent = (1 - Phvwv))
    hvw_zero_mask = n_icu_vent_awaiting == 0
    nPhvwd = np.zeros((n_age_group))
    
    if not hvw_zero_mask.all():
        nPhvwd[~hvw_zero_mask] = (1 - Phvwv[~hvw_zero_mask])*Phvwd[~hvw_zero_mask]
    Phvwhvw = 1 - Phvwv - nPhvwd
    
    P_matrix[state_num["s_state"], state_num["h_state"], :] = Psh
    P_matrix[state_num["s_state"], state_num["c_state"], :] = nPsc
    P_matrix[state_num["s_state"], state_num["d_state"], :] = nPsd
    P_matrix[state_num["s_state"], state_num["s_state"], :] = Pss
    
    P_matrix[state_num["c_state"], state_num["i_state"], :] = Pci
    P_matrix[state_num["c_state"], state_num["v_state"], :] = Pcv
    P_matrix[state_num["c_state"], state_num["d_state"], :] = nPcd
    P_matrix[state_num["c_state"], state_num["c_state"], :] = Pcc
    
    # Update Ph
    # Update Phi (hospitalised to critical)
    P_matrix[state_num["h_state"], state_num["i_state"], :] = Phi
    # Update Phv (hospitalised to critical + ventilator)
    P_matrix[state_num["h_state"], state_num["v_state"], :] = Phv
    # Update Phhiw (hospitalised to critical but awaiting)
    P_matrix[state_num["h_state"], state_num["hiw_state"], :] = Phhiw    
    # Update Phhvw (hospitalised to critical + ventilator but awaiting)
    P_matrix[state_num["h_state"], state_num["hvw_state"], :] = Phhvw
    P_matrix[state_num["h_state"], state_num["r_state"], :] = nPhr
    P_matrix[state_num["h_state"], state_num["d_state"], :] = nPhd
    # Update Phh
    P_matrix[state_num["h_state"], state_num["h_state"], :] = Phh
    
    # Update Phiwi (awaiting ICU to ICU)
    P_matrix[state_num["hiw_state"], state_num["i_state"], :] = Phiwi
    P_matrix[state_num["hiw_state"], state_num["d_state"], :] = nPhiwd
    P_matrix[state_num["hiw_state"], state_num["hiw_state"], :] = Phiwhiw
    
    # Update Phvwv (awaiting ICU + ventilator to ICU + ventilator)
    P_matrix[state_num["hvw_state"], state_num["v_state"], :] = Phvwv
    P_matrix[state_num["hvw_state"], state_num["d_state"], :] = nPhvwd
    P_matrix[state_num["hvw_state"], state_num["hvw_state"], :] = Phvwhvw
    
    return P_matrix, a_hosp_bed, a_icu, a_vent