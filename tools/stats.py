# External imports
import pandas as pd

# Internal imports
from models import mydb

# 2.2
def get_all_states_empty():
    # Returns a pd.DataFrame of (
    #   usa_state_code, 
    #   usa_state_latitude, 
    #   usa_state_longitude,
    #   accidents_num
    # ) of all 50 states, accidents_num all 0
    cursor = mydb.cursor()
    script = "SELECT * FROM state_coors"
    cursor.execute(script)
    df_states = pd.DataFrame(cursor.fetchall())
    df_states = df_states.assign(accidents_num=0)
    return df_states

# 2.3
def get_all_counties_empty():
    # Returns a pd.DataFrame of (
    #   NAME, 
    #   STUSAB, 
    #   INTPTLAT,
    #   INTPTLON,
    #   accidents_num
    # ) of all 3000+ counties, accidents_num all 0
    cursor = mydb.cursor()
    script = "SELECT NAME, STUSAB, INTPTLAT, INTPTLON FROM us_counties"
    cursor.execute(script)
    df_counties = pd.DataFrame(cursor.fetchall())
    df_counties = df_counties.assign(accidents_num=0)
    return df_counties