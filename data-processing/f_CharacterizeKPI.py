import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import StandardScaler
import itertools
from tqdm import tqdm_notebook


import json
import os
####################################
#####==========================#####
### I. Data Exploration Pipeline ###
#####==========================#####
####################################

# This first section creates a starting point for our data to be modeled and
# analyzed in real-time. The same pipeline should be applied to any new batch
# of data that we wish to add in the future and for which we have enough
# historical data

def data_load(machine,kpi):
  # time series should be loaded from the dataset,
  # right now they can be read directly from the pickle file
  kpi_data = df.loc[df['name'] == machine].loc[df['kpi'] == kpi]
  return kpi_data['time'].values, kpi_data['avg'].values

def data_extract_trends(ts):
  trends = {
      'max': np.max(ts),
      'min': np.min(ts),
      'mean': np.mean(ts),
      'std': np.std(ts)
  }
  return trends

def perform_adfuller(series):
    """
    Perform ADF test and return test statistic and p-value
    """
    result = adfuller(series, regression='ct')
    return result[0], result[1]  # Returns test statistic and p-value

def data_clean_missing_values(data):
  # remove null values, furhter studies are needed to evaluate the zeros
  cleaned_data = data
  if data['Value'].isna().sum()!=0:
    # data = data.fillna(data.mean())
    # data = data.bfill()
    cleaned_data['Value'] = data.interpolate(method='linear')
  return cleaned_data

# normalize the time series to a common scale
def data_normalize_params(data):
  scaler = StandardScaler()
  array_value = data.values.reshape(-1,1)
  array_scaled = scaler.fit_transform(array_value)
  normalized_data = pd.Series(array_scaled.flatten(),index=data.index,name='Timestamp')
  return normalized_data

# window_size = 30
# df_zscore = zscore(df, window_size)

# threshold = 3
# outliers_dates = df_zscore[abs(df_zscore.Value) > threshold].index
# outliers_dates
def create_model_data(machine, kpi, path):
  a_dict = {}
  a_dict['trends'] = {
      'max': 0,
      'min': 0,
      'mean': 0,
      'std': 0
  }
  a_dict['stationarity'] = {
    'Differencing': '', #which grade of differentiation is used?
    'Statistic': 0, # stationarity score
    'P-value': 0, # along with Statistic helps understanding how certain we are about the stationarity
    'Stationary': 0 #1: yes, 0: no
  }
  a_dict['outliers'] = {}
  a_dict['missingval'] = {
      'fill_method': 'N/A', # can't differentiate between correct MV or wrong MV
      'missing_streak': 0, # number of missing values in a row
      'alert_sent': False # avoid sending multiple alarms for the same missing streak
  }
  a_dict['predictions'] = {
      'first_prediction' : 0, # next prediction in line
      'error_threshold' : 0 # amount after which an error is counted for concept drift
  }
  a_dict['drift'] = {
      'num_instances': 0, # number of valid datapoints
      'p_min': 0, # historical minimum of p_mean + s_mean, helps in establishing a reference point for the lowest error rate observed in the past
      's_min': 0, # the corresponding standard deviation value associated with p_min.
      'p_mean': 0, # represents the mean error rate over time, It helps capture the current estimate of the error rate as more data comes in.
      's_mean': 0 # standard deviation of the error rate over time. It captures the variability of the error rate around p_mean.
  }
  a_dict['model'] = {
      'name': '', #name of the model used
      'p': 0, # p, q are the ARMA parameters
      'q': 0
  }
  with open(path, 'w', os.O_CREAT) as outfile:
    json.dump(a_dict, outfile)


def save_model_data(machine, kpi, n_dict):

  final_path = f'{models_path}{machine}_{kpi}.json'
  with open(final_path, 'w') as outfile:
    json.dump(n_dict, outfile)

def optimize_ARIMA(endog, order_list, d):

  results = []
  for order in tqdm_notebook(order_list):
      try:
          model = SARIMAX(endog, order=(order[0], d, order[1]), simple_differencing=False).fit(disp=False)
          aic = model.aic
          results.append([order, aic])
      except:
          continue

  optimize_ARIMA_results = pd.DataFrame(results, columns=['(p,q)', 'AIC'])
  optimize_ARIMA_results = optimize_ARIMA_results.sort_values(by='AIC', ascending=True).reset_index(drop=True)
  return optimize_ARIMA_results

#########################
### 1. data profiling ###
#########################

def characterize_KPI(machine, kpi):
  # DATA LOADING
  final_path = f'{models_path}{machine}_{kpi}.json'
  if not os.path.isfile(final_path):
    create_model_data(machine, kpi, final_path)

  a_dict = {}
  with open(final_path, "r") as file:
    a_dict = json.load(file)

  kpi_data_Time, kpi_data_Avg = data_load(machine, kpi) # load a single time series

  # EXTRACT DATA TRENDS
  # conversion of the two arrays in a dataframe
  timestamps = pd.to_datetime(kpi_data_Time)
  timeseries = pd.DataFrame({'Timestamp':timestamps, 'Value': kpi_data_Avg})
  timeseries.set_index('Timestamp', inplace=True)
  trends = data_extract_trends(timeseries['Value']) # find range, distribution, or any pattern that may be used
                                                    # to treat missing values or outliers.
                                                    # maybe also find correlations and mutual information
  a_dict['trends'] = trends

  # MISSING VALUE HANDLING
  data = data_clean_missing_values(timeseries)  # mean/median OR Interpolation OR Forward/backward fill
                                                          #1- if we have no other data, just decide how to fill the hole
                                                          #2- [NOT IMPLEMENTED YET] if we have other ts look for
                                                          #   correlation of holes with other trends and report them

  # OUTLIER DETECTION
  # Outliers are not detected here, as we only focus on finding them on upcoming new data points


  # STATIONARITY CHECK
  orig_statistic, orig_p_value = perform_adfuller(data['Value'])

  stationarity_results = {
      'Differencing': 0,
      'Statistic': round(orig_statistic, 3),
      'P-value': f'{orig_p_value:.2E}',
      'Stationary': 1 if orig_p_value < 0.05 else 0
  }
  print()
  if orig_p_value >= 0.05: # if the data is not stationary we check the first difference
    diff1_series = pd.DataFrame({'Timestamp':data['Value'].index, 'Value': data['Value']})
    diff1_statistic, diff1_p_value = perform_adfuller(diff1_series['Value'].values)
    print(diff1_series)
    data['Value'] = data_normalize_params(diff1_series['Value'])

    stationarity_results = {
      'Differencing': 1,
      'Statistic': round(diff1_statistic, 3),
      'P-value': f'{diff1_p_value:.2E}',
      'Stationary': 1 if diff1_p_value < 0.05 else 0
    }
    if diff1_p_value >= 0.05: # if the first difference is still non stationary we check the second
        diff2_series = pd.DataFrame({'Timestamp':diff1_series['Value'].index, 'Value': diff1_series['Value']})
        diff2_statistic, diff2_p_value = perform_adfuller(diff2_series['Value'].values)
        data['Value'] = data_normalize_params(diff2_series['Value'])

        stationarity_results = {
          'Differencing': 2,
          'Statistic': round(diff2_statistic, 3),
          'P-value': f'{diff2_p_value:.2E}',
          'Stationary': 1 if diff2_p_value < 0.05 else 0
        }
  else:
    data['Value'] = data_normalize_params(data['Value'])

  a_dict['stationarity'] = stationarity_results
  # ###########################
  # ### 3. Model definition ###
  # ###########################

  # Set up the p and q ranges
  # p = range(0, 10,1)  # You can adjust the range as needed
  # q = range(0, 20,1)  # You can adjust the range as needed
  p = range(2, 4,1)  # You can adjust the range as needed
  q = range(2, 4,1)  # You can adjust the range as needed
  order_list = list(itertools.product(p, q))

  # Differencing parameter
  d = 1  # Assumed based on standard practice. Adjust if necessary.

  # Create an empty list to store optimization results
  best_arima = optimize_ARIMA(data['Value'].values, order_list, d)
  pq_tuple = best_arima.iloc[0].iloc[0]
  p = pq_tuple[0]
  q = pq_tuple[1]
  print(p,q)
  a_dict['model'] = {
      'name': 'ARIMA',
      'p': p,
      'q': q
  }

  # ############################
  # ### 4. Meta-Data storage ###
  # ############################
  save_model_data(machine, kpi, a_dict)
