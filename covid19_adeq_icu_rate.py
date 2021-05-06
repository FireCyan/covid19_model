




# Specify number of icu and ventilator available
# Bavaria adequate ICU requirement: 3130 (total accumulated number of infected: 35142)
# Lombardy adequate ICU requirement: 4500 (total accumulated number of infected: 64135)
# Wuhan adequate ICU requirement: 3200 (total accumulated number of infected: 50008)

n_total_Bavaria = 35142
n_total_Wuhan = 50008
n_total_Lombardy = 64135

Bavaria_death_rate = 1049/n_total_Bavaria*100
Wuhan_death_rate = 3869/n_total_Wuhan*100
Lombardy_death_rate = 9808/n_total_Lombardy*100

# Bavaria_rate_ade_icu = 4410/3130
Bavaria_rate_ade_icu = 100
Wuhan_rate_ade_icu = 1468/3200*100
Lombardy_rate_ade_icu = 1174/4500*100


with open('./pickle_file/Wuhan_df_death_cause_100_t_ratios.pkl', 'rb') as f:
    list_Wuhan_df_death_cause = pickle.load(f)
    
with open('./pickle_file/Bavaria_df_death_cause_100_t_ratios.pkl', 'rb') as f:
    list_Bavaria_df_death_cause = pickle.load(f)
    
with open('./pickle_file/Lombardy_df_death_cause_100_t_ratios.pkl', 'rb') as f:
    list_Lombardy_df_death_cause = pickle.load(f)

Wuhan_d_icu_rate = []
Bavaria_d_icu_rate = []
Lombardy_d_icu_rate= []

for i in range(len(list_Wuhan_df_death_cause)):
    Wuhan_d_icu_rate.append(list_Wuhan_df_death_cause[i]['Total'].sum().sum()/n_total_Wuhan*100)
    Bavaria_d_icu_rate.append(list_Bavaria_df_death_cause[i]['Total'].sum().sum()/n_total_Bavaria*100)
    Lombardy_d_icu_rate.append(list_Lombardy_df_death_cause[i]['Total'].sum().sum()/n_total_Lombardy*100)
    
# death_against_icu_rate[100] = 
# print(Wuhan_d_icu_rate)

df_d_icu_rate = pd.DataFrame(np.array([Bavaria_d_icu_rate, Wuhan_d_icu_rate, Lombardy_d_icu_rate]).T, \
                             columns=['Bavaria', 'Wuhan', 'Lombardy'])

title = "Death rates over different rates of adequate ICU\nModelled with Bavaria, Wuhan and Lombardy cases"

ax = plot_death_icu_rate(df_d_icu_rate, title)

Bavaria_60_proportion = (0.11751394 + 0.08948367 + 0.0600025)*100
Wu_60_proportion = (0.073404958 + 0.039966121 + 0.013451689)*100
Lombardy_60_proportion = (0.11750413 + 0.09882498 + 0.07070879)*100

plt.text(6, 26, "60+ proportion: {0:.1f}%".format(Lombardy_60_proportion), \
             color='green', fontsize=20, fontweight='bold', horizontalalignment='left')

plt.text(6, 24, "60+ proportion: {0:.1f}%".format(Bavaria_60_proportion), \
             color='orange', fontsize=20, fontweight='bold', horizontalalignment='left')

plt.text(6, 8, "60+ proportion: {0:.1f}%".format(Wu_60_proportion), \
             color='red', fontsize=20, fontweight='bold', horizontalalignment='left')