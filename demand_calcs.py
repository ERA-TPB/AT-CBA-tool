import numpy as np
import pandas as pd
import inputs

def get_basic_demand_frame(demand_sensitivity=1):
    """Returns demand by mode based on inputs from inputs.py"""
    
    if inputs.custom_demand == False:
        growth_factors = pd.DataFrame(index =pd.MultiIndex.from_product([inputs.demand_growth.index.tolist(),inputs.year],names=['mode','year'])) 
        n=0
        for thisyear in inputs.year:
            if thisyear < inputs.opening_year:
                for thismode in inputs.demand_growth.index.tolist():
                    growth_factors.loc[(thismode,thisyear),'value'] = 0 #No demand in years before opening year
            else:
                for thismode in inputs.demand_growth.index.tolist():
                    growth_factors.loc[(thismode,thisyear),'value'] = (1 + inputs.demand_growth.loc[thismode,'value']/100)**n #Growth factor is base^years
                n=n+1

 
    if inputs.custom_demand == True:
        basic_demand = inputs.uploaded_demand*demand_sensitivity
    else:
        basic_demand = inputs.base_year_demand*growth_factors*demand_sensitivity

    return basic_demand

def get_demand_frame(basic_demand, new_trips_sensitivity=1):
    """Returns demand by diversion source and applies demand ramp up"""
    
    
    #alter diversion frame for reassign sensitivity
    reassign_sensitivity = 1-new_trips_sensitivity
    diversion = inputs.diversion_rate.copy()
    for mode in inputs.demand_growth.index.tolist():
        total_change = inputs.diversion_rate.loc[mode,'Reassign']*reassign_sensitivity
        diversion.loc[mode,'Reassign'] = inputs.diversion_rate.loc[mode,'Reassign'] + total_change
        #Check if sensitivity has resulted in diversion <0 or >100
        if diversion.loc[(mode,'Reassign'),'value'] > 100:
            diversion.loc[mode,'Reassign'] = 100
            total_change = 100 - inputs.diversion_rate.loc[mode,'Reassign']
        if diversion.loc[(mode,'Reassign'),'value'] < 0:
            diversion.loc[mode,'Reassign'] = 0
            total_change = 0 - inputs.diversion_rate.loc[mode,'Reassign']
        other_from_modes = inputs.diversion_rate.loc[mode].drop('Reassign')
        from_mode_proportion = other_from_modes/other_from_modes.sum()
        for other_from_mode in other_from_modes.index.tolist():
            diversion.loc[mode,other_from_mode] = inputs.diversion_rate.loc[mode,other_from_mode]-total_change*from_mode_proportion.loc[other_from_mode]
    
    demand = basic_demand*(diversion/100)*inputs.annualisation
    demand = demand.swaplevel('year','from_mode')

    #Set up years in which demand is not equal to inputs due to ramp up. Ramp up lasts ramp up years minus 1
    ramp_up_years = [num for num in inputs.year if num >= inputs.opening_year and num < inputs.opening_year + inputs.demand_ramp_up -1]

    for mode in list(set(demand.index.get_level_values('mode'))):
        for from_mode in list(set(demand.index.get_level_values('from_mode'))):
            if from_mode != 'Reassign':
                for yr in ramp_up_years:
                    #Multiply demand by how far throguh ramp up years this year is (1/5, 2/5, 3/5, 4/5)
                    demand.loc[(mode,from_mode,yr),'value'] = (demand.loc[(mode,from_mode,yr),'value']*
                    ((yr-inputs.opening_year+1)/inputs.demand_ramp_up))

    return demand

