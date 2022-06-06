import numpy as np
import pandas as pd

default_parameters = pd.DataFrame()
parameter_list = pd.DataFrame()

facility_name=''
discount_rate = 0
appraisal_period = 0
base_year = 0
start_year= 0
opening_year = 0
annualisation = 0
facility_length = 0
facility_type_existing = ""
facility_type_new = ""
year = list()
costs = pd.DataFrame()
base_year_demand = pd.DataFrame()
demand_growth = pd.DataFrame()
uploaded_demand = pd.DataFrame()
diversion_rate = pd.DataFrame()
diversion_congestion = pd.DataFrame()
speed_active = pd.DataFrame()
speed_from_mode = pd.DataFrame()
trip_distance_raw = pd.DataFrame()
trip_distance_change = pd.DataFrame()
surface_distance_prop_base = pd.DataFrame()
surface_distance_prop_project = pd.DataFrame()
time_saving = pd.DataFrame()
transport_share = pd.DataFrame()
relative_risk = pd.DataFrame()
vott = 0
health_system = pd.DataFrame()
health_private = pd.DataFrame()
voc_active = pd.DataFrame()
voc_car = pd.DataFrame()
congestion_cost = pd.DataFrame()
crash_cost_active = pd.DataFrame()
crash_cost_from_mode = pd.DataFrame()
injury_cost = pd.DataFrame()
car_externalities = pd.DataFrame()
road_provision = 0
parking_cost = 0
demand_ramp_up = 0
number_of_intersections = 0
intersection_inputs = pd.DataFrame()

custom_demand = False

travel_time_weighting = pd.DataFrame()

sensitivities = pd.DataFrame()

subtract_project_length = False

saved_vars = pd.DataFrame()

