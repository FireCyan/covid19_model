import matplotlib.pyplot as plt
###########################################################
# Specify the color to be used for each state on the plot
###########################################################
state_color_dict = {'Severe': 'grey', 'Critical': 'orange', 'Severe-Hospitalised': 'magenta', \
              'Critical-ICU': 'black', 'Critical-ICU + ventilator': 'red', \
              'Awaiting ICU - hosp to ICU': 'blue', 'Awaiting ICU+vent - hosp to ICU+vent': 'green'}

death_color_dict = {'Death - lack of hospital bed': 'grey', 'Death - lack of ICU': 'blue', \
                    'Death - lack of ICU + ventilator': 'green', \
                    'Death - hospitalised': 'magenta', 'Death - ICU': 'black', 'Death - ICU + ventilator': 'red'}

####################################################
# Plot the number of people in each state over time 
####################################################

def plot_state_num(df, n_total, title):

    fig, ax = plt.subplots(figsize=(20,10))
    
    df_infected = df.copy()

    plot_col = ['Severe', 'Critical', 'Severe-Hospitalised', 'Critical-ICU', 'Critical-ICU + ventilator',\
                'Awaiting ICU - hosp to ICU', 'Awaiting ICU+vent - hosp to ICU+vent']
    
    color_list = []
    
    for c in plot_col:
        color_list.append(state_color_dict[c])
    
    df_infected = df_infected.rename(columns={'Hospitalised': 'Severe-Hospitalised', 'ICU': 'Critical-ICU', \
                                             'ICU + ventilator': 'Critical-ICU + ventilator', \
                                             'Awaiting_ICU-hospitalised_to_critical': 'Awaiting ICU - hosp to ICU', \
                                             'Awaiting_ICU_and_vent-hospitalised_to_critical': \
                                             'Awaiting ICU+vent - hosp to ICU+vent'})
    df_infected['Total'][plot_col].plot(kind='line', ax=ax, linewidth=4, color=color_list)
    ax.set_xlabel('Day number', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Number of people', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')
    fig.suptitle(title, fontsize=24, fontname="Arial",fontweight="bold")
    ax.legend(fontsize=18)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Ratio over total infected (%)', fontsize=24, fontname="Arial",fontweight="bold")
    (df_infected['Total'][plot_col]/n_total*100).plot(kind='line', ax=ax2, legend=False, color=color_list)
    ax2.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    # ax2.tick_params(axis='y', labelcolor=color)
    
    for tick in ax2.get_yticklabels():
        tick.set_fontsize(20) 
        tick.set_fontweight("bold")

##############################################################
# Plot the number of death due to different causes against time
##############################################################

def plot_death_cause(df, n_total, title):

    fig, ax = plt.subplots(figsize=(20,10))
    
    df_death_cause = df.copy()
    
    plot_col = ['Death - lack of hospital bed', 'Death - lack of ICU', 'Death - lack of ICU + ventilator', \
                  'Death - hospitalised', 'Death - ICU', 'Death - ICU + ventilator']
    
    color_list = []
    
    for c in plot_col:
        color_list.append(death_color_dict[c])
    
    df_death_cause['Total'][plot_col].plot(kind='line', ax=ax, linewidth=4, color=color_list)
    ax.set_xlabel('Day number', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Number of deaths', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    fig.suptitle(title, \
                 fontsize=24, fontname="Arial",fontweight="bold")
    ax.legend(fontsize=20)

    for tick in ax.get_xticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")

    for tick in ax.get_yticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")

    ax2 = ax.twinx()

    ax2.set_ylabel('Ratio over total infected (%)', fontsize=24, fontname="Arial",fontweight="bold")
    (df_death_cause['Total'][plot_col]/n_total*100).plot(kind='line', ax=ax2, legend=False, color=color_list)
    ax2.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')

    for tick in ax2.get_yticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")

############################################################################
# Plot the accumulated number of death due to different causes against time
############################################################################

def plot_death_cumsum(df, n_total, title):
#     print(legend_app)
    fig, ax = plt.subplots(figsize=(20,10))
    
    df_death_cause = df.copy()
    
    plot_col = ['Death - lack of ICU', 'Death - lack of ICU + ventilator', \
                  'Death - hospitalised', 'Death - ICU', 'Death - ICU + ventilator']
    
    color_list = []
    
    for c in plot_col:
        color_list.append(death_color_dict[c])
    
    df_death_cause['Total'].cumsum(axis=0)[plot_col].plot(kind='line', ax=ax, linewidth=4, color=color_list)
    ax.set_xlabel('Day number', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Number of deaths', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    fig.suptitle(title, \
                 fontsize=24, fontname="Arial",fontweight="bold")
#     ax.legend(loc='upper left')
    ax.legend(loc='upper left', fontsize=20)

    for tick in ax.get_xticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")

    for tick in ax.get_yticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")

    ax2 = ax.twinx()

    ax2.set_ylabel('Ratio over total infected (%)', fontsize=24, fontname="Arial",fontweight="bold")
    (df_death_cause['Total'].cumsum(axis=0)[plot_col]/n_total*100).plot(kind='line', \
                                                                        ax=ax2, legend=False, color=color_list)
    ax2.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')

    for tick in ax2.get_yticklabels():
            tick.set_fontsize(20) 
            tick.set_fontweight("bold")
            
    return fig, ax, ax2

###################################################################
# Plot the death rate at different different rates of adequate ICU
###################################################################

def plot_death_icu_rate(df, list_region):
    df_d_icu_rate = df.copy()
    
    fig, ax = plt.subplots(figsize=(20,10))

    colors = [ "red", "blue", "green", "orange", "magenta", "black", "cyan", "purple" ]
    
    color_list = colors[0:len(list_region)]

    df_d_icu_rate.plot(kind='line', ax=ax, linewidth=4, color=color_list)

    title = "Death rates over different rates of adequate ICU\nModelled with "
    #  Bavaria, Wuhan and Lombardy cases

    i = 0
    for r in list_region:
        plt.plot(r.get_est_ade_icu_rate()*100, r.get_death_rate()*100, marker='o', markersize=20, color=color_list[i])
        plt.text(r.get_est_ade_icu_rate()*100, r.get_death_rate()*100 + 1, r.region_name + " cases", \
        color=color_list[i], fontsize=20, fontweight='bold', horizontalalignment='center')

        over_60_proportion = r.pop_ratio[-3:].sum()*100

        plt.text(70, 12+2*i, "60+ proportion: {0:.1f}%".format(over_60_proportion), \
        color=color_list[i], fontsize=20, fontweight='bold', horizontalalignment='left')

            

        i = i + 1
        if (i + 1) < len(list_region):
            title = title + r.region_name + ', '
        elif i < len(list_region):
            title = title + r.region_name + ' and '
        else:
            title = title + r.region_name + ' cases'


    # plt.plot(Bavaria_rate_ade_icu, Bavaria_death_rate, marker='o', markersize=20, color=color_list[0])
    # plt.plot(Wuhan_rate_ade_icu, Wuhan_death_rate, marker='o', markersize=20, color=color_list[1])
    # plt.plot(Lombardy_rate_ade_icu, Lombardy_death_rate, marker='o', markersize=20, color=color_list[2])

    # plt.text(Bavaria_rate_ade_icu, Bavaria_death_rate + 1, "Bavaria cases", \
    #          color=color_list[0], fontsize=20, fontweight='bold', horizontalalignment='center')

    # plt.text(Wuhan_rate_ade_icu + 9, Wuhan_death_rate - 1.4, "Wuhan cases", \
    #          color=color_list[1], fontsize=20, fontweight='bold', horizontalalignment='center')

    # plt.text(Lombardy_rate_ade_icu - 2, Lombardy_death_rate - 2, "Lombardy cases", \
    #          color=color_list[2], fontsize=20, fontweight='bold', horizontalalignment='center')

    fig.suptitle(title, \
                     fontsize=24, fontname="Arial",fontweight="bold")

    ax.set_xlabel('Rate of adequate ICU (%)', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Death rate (%)', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_ylim([0, 30])
    ax.set_xlim([0, 110])

    ax.legend(fontsize=18)

    for tick in ax.get_xticklabels():
        tick.set_fontsize(20) 
        tick.set_fontweight("bold")

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')
        
    return ax

def plot_constant_daily_case_curve(region, list_constant_df_infected, constant_flow_text, icu_case_max):
    r = region

    fig, ax = plt.subplots(figsize=(20,10))

    color_list = ['blue', 'orange', 'magenta', 'red', 'purple', 'green']

    for i in range(len(list_constant_df_infected)):
        df = list_constant_df_infected[i]['Total']
        
        plot_col = ['Critical-ICU', 'Critical-ICU + ventilator']
        df = df.rename(columns={'ICU': 'Critical-ICU', 'ICU + ventilator': 'Critical-ICU + ventilator'})
        df[plot_col].sum(axis=1).plot(kind='line', ax=ax, linewidth=4, color=color_list[i])
        
        peak = df[plot_col].sum(axis=1).max()
        if i < (len(list_constant_df_infected) - 1):
            plt.text(35, peak + 40, constant_flow_text[i], color=color_list[i], fontsize=16,\
                fontweight='bold', horizontalalignment='center', verticalalignment='bottom')
        else:
            plt.text(80, peak + 40, constant_flow_text[i], color=color_list[i], fontsize=16,\
                fontweight='bold', horizontalalignment='center', verticalalignment='bottom')

    # df.head()

    title = f"Number of people in ICU or ICU + vent with constant inflow of patients for 30 days (and {r.region_name} inflow)\nModelled with {r.region_name} age demographic"
    ax.set_xlabel('Day number', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Number of people (dashed line: ICU number)', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')
    fig.suptitle(title, fontsize=24, fontname="Arial",fontweight="bold")

    factor = 1

    while (factor*r.t_icu_est) < icu_case_max*1.2:
        print(factor)
        plt.hlines(factor*int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
        icu_rate = "%.2f" % ((factor*r.t_icu_est/r.get_total_pop())*100000)
        plt.text(60, factor*int(r.t_icu_est)+6, f"ICU number: {factor*int(r.t_icu_est)} ({icu_rate} per 100K pop)", color='black', fontsize=16,\
                fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

        factor = factor + 1
        

    # plt.hlines(int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
    # icu_rate = "%.2f" % ((r.t_icu_est/r.get_total_pop())*100000)
    # plt.text(60, int(r.t_icu_est) + 6, f"ICU number: {int(r.t_icu_est)} ({icu_rate} per 100K pop)", color='black', fontsize=16,\
    #         fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

    # icu_rate_double = "%.2f" % ((2*r.t_icu_est/r.get_total_pop())*100000)
    # if ((2*r.t_icu_est/r.get_total_pop())*100000) < n_max*1.2:
    #     plt.hlines(2*int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
    #     plt.text(60, 2*int(r.t_icu_est)+6, f"ICU number: {2*int(r.t_icu_est)} ({icu_rate_double} per 100K pop)", color='black', fontsize=16,\
    #             fontweight='bold', horizontalalignment='left', verticalalignment='bottom')
        
    # icu_rate_triple = "%.2f" % ((3*r.t_icu_est/r.get_total_pop())*100000)
    # if ((3*r.t_icu_est/r.get_total_pop())*100000) < n_max*1.2:
    #     plt.hlines(3*int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
    #     plt.text(60, 3*int(r.t_icu_est)+6, f"ICU number: {3*int(r.t_icu_est)} ({icu_rate_triple} per 100K pop)", color='black', fontsize=16,\
    #             fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

    # icu_rate_quadruple = "%.2f" % ((4*r.t_icu_est/r.get_total_pop())*100000)
    # if ((4*r.t_icu_est/r.get_total_pop())*100000) < n_max*1.2:
    #     plt.hlines(4*int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
    #     plt.text(60, 4*int(r.t_icu_est)+6, f"ICU number: {4*int(r.t_icu_est)} ({icu_rate_quadruple} per 100K pop)", color='black', fontsize=16,\
    #             fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

    total_pop = r.get_total_pop()

    ax2 = ax.twinx()

    (df[plot_col].sum(axis=1)/total_pop*100000).plot(kind='line', ax=ax2, linewidth=4, color=color_list[i])

    ax2.set_ylabel('Number of people per 100K population', fontsize=24, fontname="Arial",fontweight="bold")

    ax2.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    # ax2.tick_params(axis='y', labelcolor=color)
    ax.set_ylim([-1/100000*total_pop, icu_case_max*1.2])
    ax2.set_ylim([-1, icu_case_max*1.2/total_pop*100000])
    # ax.set_ylim([-1/100000*total_pop, 58/100000*total_pop])
    # ax2.set_ylim([-1, 58])


    for tick in ax2.get_yticklabels():
        tick.set_fontsize(20) 
        tick.set_fontweight("bold")

    # Australian and New Zealand Intensive Care Society. Centre for Outcome and Resource Evaluation 2018 report. 2018.
    # Number of ICU beds available in NSW: 874
    # Number of ICU beds in NSW doubled: 1748
    # Number of ICU beds in NSW tripled: 2622
    # Number of ICU beds in NSW quadrupled: 3496


def plot_fix_case_diff_days(region, list_fix_total_diff_days_df_infected, fix_total_diff_days_text, icu_case_max, n_total_infect):
    r = region
    fig, ax = plt.subplots(figsize=(20,10))

    # constant_flow_text = ["150 per day for 200 days", \
    #                       "300 per day for 100 days", \
    #                       "600 per day for 50 days", \
    #                       "1500 per day for 20 days", \
    #                       "3000 per day for 10 days"]

    color_list = ['blue', 'orange', 'magenta', 'red', 'purple']

    text_x_loc = [30, 53, 50, 35, 18]

    for i in range(len(list_fix_total_diff_days_df_infected)):
        df = list_fix_total_diff_days_df_infected[i]['Total']
        
        plot_col = ['Critical-ICU', 'Critical-ICU + ventilator']
        df = df.rename(columns={'ICU': 'Critical-ICU', 'ICU + ventilator': 'Critical-ICU + ventilator'})
        df[plot_col].sum(axis=1).plot(kind='line', ax=ax, linewidth=4, color=color_list[i])
        
        peak = df[plot_col].sum(axis=1).max()
    #     peak_loc = df[plot_col].sum(axis=1).idxmax()
        plt.text(text_x_loc[i], peak + 50, fix_total_diff_days_text[i], color=color_list[i], fontsize=16,\
            fontweight='bold', horizontalalignment='center', verticalalignment='bottom')

    # df.head()

    title = f"Number of people in ICU or ICU + vent with {n_total_infect} patients evenly distributed over different number of days\nModelled with {r.region_name} age demographic"
    ax.set_xlabel('Day number', fontsize=24, fontname="Arial",fontweight="bold")
    ax.set_ylabel('Number of people (dashed line: ICU number)', fontsize=24, rotation=90, fontname="Arial",fontweight="bold")
    ax.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20) 
        tick.label.set_fontweight('bold')
    fig.suptitle(title, fontsize=24, fontname="Arial",fontweight="bold")


    factor = 1

    while (factor*r.t_icu_est) < (icu_case_max*1.1):
        print(factor)
        plt.hlines(factor*int(r.t_icu_est), xmin=0, xmax=90, linestyles='dashed')
        icu_rate = "%.2f" % ((factor*r.t_icu_est/r.get_total_pop())*100000)
        plt.text(60, factor*int(r.t_icu_est)+6, f"ICU number: {factor*int(r.t_icu_est)} ({icu_rate} per 100K pop)", color='black', fontsize=16,\
                fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

        factor = factor + 1

    # plt.hlines(874, xmin=0, xmax=90, linestyles='dashed')
    # plt.text(60, 880, "ICU number: 874 (11.68 per 100K pop)", color='black', fontsize=16,\
    #          fontweight='bold', horizontalalignment='left', verticalalignment='bottom')
    # plt.hlines(1748, xmin=0, xmax=90, linestyles='dashed')
    # plt.text(60, 1754, "ICU number: 1748 (23.27 per 100K pop)", color='black', fontsize=16,\
    #          fontweight='bold', horizontalalignment='left', verticalalignment='bottom')
    # plt.hlines(2622, xmin=0, xmax=90, linestyles='dashed')
    # plt.text(60, 2628, "ICU number: 2622 (35.05 per 100K pop)", color='black', fontsize=16,\
    #          fontweight='bold', horizontalalignment='left', verticalalignment='bottom')
    # plt.hlines(3496, xmin=0, xmax=90, linestyles='dashed')
    # plt.text(60, 3502, "ICU number: 3496 (46.74 per 100K pop)", color='black', fontsize=16,\
    #          fontweight='bold', horizontalalignment='left', verticalalignment='bottom')

    ax.set_ylim([-100, icu_case_max*1.2])
    # ax.set_xlim([-5, run_days + 5])


    total_pop = r.get_total_pop()
    # n_NSW_pop = 7480242

    ax2 = ax.twinx()

    (df[plot_col].sum(axis=1)/total_pop*100000).plot(kind='line', ax=ax2, linewidth=4, color='purple')

    ax2.set_ylabel('Number of people per 100K population', fontsize=24, fontname="Arial",fontweight="bold")

    ax2.tick_params(labelsize=20, width=3, length=10, which='major', direction='in')
    # ax2.set_ylim([-100/total_pop*100000, 4200/total_pop*100000])
    # ax2.tick_params(axis='y', labelcolor=color)

    ax2.set_ylim([-1, icu_case_max*1.2/total_pop*100000])
    ax.set_ylim([-1/100000*total_pop, icu_case_max*1.2])

    for tick in ax2.get_yticklabels():
        tick.set_fontsize(20) 
        tick.set_fontweight("bold")