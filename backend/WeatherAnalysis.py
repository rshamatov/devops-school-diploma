
import logging
import pandas as pd


def get_mean_weather(keys, weathers):
    logging.debug(f"Trying to get mean weather for keys {keys}")

    d = {}
    for i, key in enumerate(keys, start=0): 
        d[key] = [w[i] for w in weathers]

    series = pd.DataFrame(d)
    logging.debug(f"Pandas DataFrame: \n{series}")

    TEXT_KEYS = [
        "weather_state_name",
        "weather_state_abbr",
        "wind_direction_compass"
    ]

    NUM_KEYS = [
		"min_temp",
		"max_temp",
		"the_temp",
		"wind_speed",
		"wind_direction",
		"air_pressure",
		"humidity",
		"visibility",
		"predictability"
    ]
    
    mean = {}
    for key in TEXT_KEYS:
        if key in keys:
            mean[key] = series[key].value_counts().index[0]

    for key in NUM_KEYS:
        if key in keys:
            mean[key] = series[key].mean()
   
    logging.info(f"Mean weather: {mean}")
    
    '''
    template_dict["wind_direction_compass"] = statistics.mean()

    for i,key in enumerate(template_dict.keys(), start=1):
        logging.debug(f"Iterating, i = '{i}', key = '{key}', {[w[i] for w in values_dict]}")
        template_dict[key] = statistics.mean(
            [w[i] for w in values_dict])
    '''
    return mean