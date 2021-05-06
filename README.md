# Covid-19 model for ICU number required and death rate 

## Table of contents

 * [Introduction](#Introduction)
 * [Quick start](#Quick-start)
 * [Plot examples](#Plot-examples)
 * [Method](#Method)


## Introduction
(The model was built around 2020 April/May, so the parameters may be a bit outdated. But I think the model concept is still relevant)

One of my friends asked me if there are any factors that drive the number of people infected with Covid-19.

I thought of doing anaylsis with some factors such as the number masks. However, it is difficult to get a good estimate of the number of masks. Therefore, I dropped the idea of getting the relationship between infected people and masks.

However, another factor got my attention. There was news about the number of critical beds per capital for each country, and I plotted a simple graph to show the relationship between that and the death rate due to Covid-19 for some countries. With the size showing the number for people infected, I saw some patterns and wanted to investigate further.

![death_rate_vs_ICU_per_capita](/fig_example/death_rate_per_1m_vs_icu.png)

Therefore, I built a Markov's chain model to answer some of my questions. What I wanted to find out is, assuming that the death rate is relatively stable provided that there are sufficient medical resources, what is the portion of people who could have been saved but passed away due to lack of medical resources? Also, given a certain number of critical beds available, is it possible to predict the number of deaths due to different causes? And what is the number of critical beds each country needs to minimise casualty? I used this model to try solve these questions.

---

## Quick start
There are 4 types of graph that can be plotted with scripts provided
1. covid19_status_plot_script.py
    - The number of patients in each state
    - The number of deaths and the cause 
    - The cumulative number of deaths and the cause 
2. covid19_death_icu_curve_script.py
    - Model and plot curves showing the death rate against different ICU rates (can plot for multiple regions)
3. covid19_icu_patient_trend_fixed_inflow_script.py
    - Model and plot curves showing ICU numbers used with constant inflow of infected patients for a fixed number of days (can plot for different numbers of constant inflow)
4. covid19_icu_patient_trend_fixed_total_script.py
    - Model and plot curves showing ICU numbers used with fixed number of total infected patients distributed to different numbers of days (can plot for different numbers of total infected patients)

---

## Plot examples
### covid19_status_plot_script.py
![status_plot_example](/fig_example/status_plot_lombardy.png)
### covid19_death_icu_curve_script.py
![death_vs_different_ICU_rates_example](/fig_example/death_rate_vs_icu_rate.png)
### covid19_icu_patient_trend_fixed_inflow_script.py
![constant_inflow_example](/fig_example/constant_inflow_case_wuhan.png)
### covid19_icu_patient_trend_fixed_total_script.py
![fixed_case_diff_days_example](/fig_example/fix_case_diff_days_nsw.png)

---

## Method
Using a P matrix that stores the probability of one state going to the others, I can get the number of people in each state for the next time step.

I set the states as:
- Mild (m)
- Severe (s)
- Critical (c)
- Hospitalised (h) (Note this is normal bed, not ICU)
- Hospitalised but progressed to critical and required ICU - awaiting ICU (hiw)
- Hospitalised but progressed to critical and required ICU + ventilator - awaiting ICU + ventilator (hvw)
- ICU (i)
- ICU + ventialtor (v)
- Recovered (r)
- Death (d)

How the state changes:
![model_state_change_diagram](/fig_example/state_diagram.PNG)

The time step unit is 1 day

Since the probability of people getting to different states is highly dependent on age, I made several different P matrices for each age group for the investigation. The age groups are:
- 0-9
- 10-19
- 20-29
- 30-39
- 40-49
- 50-59
- 60-69
- 70-79
- 80+

Limitation
- Death rates for hospitalised, ICU or ICU + vent are the same
- That severe and critical cases would not recover by themselves without hospitalisation (100% death rate if not hospitalised/ICU in time)
- ICU pateints do not go back to hospitalised (less critical case), but straight to recovered

The parameters come from the following papers 
- Robert Verity et al. 2020. Estimates of the severity of coronavirus disease 2019: a model-based analysis
- Moss et al. 2020. Modelling the impact of COVID-19 in Australia to inform transmission reducing measures and health system preparedness
- IHME COVID-19 health service utilization forecasting team. Forecasting COVID-19 impact on hospital bed-days, ICU-days, ventilator-days and deaths by US state in the next 4 months

