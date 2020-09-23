import pandas as pd
import numpy as np
import glob

states = ['QLD1', 'NSW1', 'SA1', 'VIC1']
for state in states:

    city_to_region = {'Adelaide': 'SA1', 'Melbourne': 'VIC1', 'Sydney': 'NSW1', 'Brisbane': 'QLD1'}

    df = pd.read_csv("files/historical_weather.csv", parse_dates=['dt_iso'], )
    df = df[['dt', 'city_name', 'temp', 'humidity', 'wind_speed', 'wind_deg', 'clouds_all']]
    df['city_name'] = df['city_name'].apply(lambda x: city_to_region[x])
    df = df.loc[df['city_name'] == state]
    df['humidity'] = df['humidity'].apply(lambda x: x/100) # Normalise humdity to between 0 (0% humdity) and 1 (100% humdity)
    df['clouds_all'] = df['clouds_all'].apply(lambda x: x/100)# Normalise cloud cover to between 0 (0% cloud) and 1 (100% cloud)
    df.columns = ['UNIXTIME', 'REGIONID', 'TEMP', 'HUMIDITY', 'SPEED', 'DIRECTION', 'CLOUD']

    df['DATETIME'] = pd.to_datetime(df['UNIXTIME'], unit='s')
    df['DATETIME'] = df['DATETIME'].dt.tz_localize('UTC').dt.tz_convert('Australia/Brisbane') # In the NEM we hate daylight savings
    df = df.drop_duplicates(subset=['DATETIME'])
    df.index = df['DATETIME']
    df = df.resample('30min').pad() # Magically make 60 minute weather data into 30 minutes weather data

    # Ignore this, it's probably fine
    df['DATETIME'] = df.index
    df['UNIXTIME'] = df.index.astype(np.int64) // 10 ** 9
    df = df.reset_index(level=0, drop=True).reset_index()
    del df['index']




    data_frames = []
    files = glob.glob('files/{}*.csv'.format(state[:-1]))
    for f in files:
        p_df = pd.read_csv(f, parse_dates=['DATETIME'])
        data_frames.append(p_df)
    all_energy_data = pd.concat(data_frames)
    all_energy_data['DATETIME'] = all_energy_data['DATETIME'].dt.tz_localize('Australia/Brisbane') # More daylight savings hate

    def datetime_to_workday(d):

        # I made the 23/12 - 1/1 not work days
        if (d.day > 23 and d.month == 12) or (d.day == 1 and d.month==1):
            return 0
        # This makes Monday - Friday workdays
        if d.dayofweek < 5:
            return 1
        return 0
    all_energy_data['WORKDAY'] = all_energy_data['DATETIME'].apply(datetime_to_workday)
    all_energy_data['MONTH'] = all_energy_data['DATETIME'].apply(lambda x: x.month)

    def capacity_reserve(row):
        # Please god I hope this calculation is correct. Double check this before using it.
        calculation = (row['AVAILABLEGENERATIONPREDICTED'] - row['TOTALDEMANDPREDICTED'] - row['NETINTERCHANGEPREDICTED'])/row['AVAILABLEGENERATIONPREDICTED']
        if calculation < 0: # This is not a good situation for a grid to be in
            return 0
        return calculation

    testing = pd.merge(df, all_energy_data, on='DATETIME')
    testing['CAPACITYRESERVE'] = testing.apply(capacity_reserve, axis=1)

    testing = testing.drop(['DATETIME', 'REGIONID'], axis=1)
    testing.to_csv('{}-2015-2020.csv'.format(state), index=False, header=True)