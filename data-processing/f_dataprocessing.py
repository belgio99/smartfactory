import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import StandardScaler
import itertools
from tqdm import notebook
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error

import json
import os


import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

import requests
import datetime

####################################
#####==========================#####
### I. Data Exploration Pipeline ###
#####==========================#####
####################################

# This first section creates a starting point for our data to be modeled and
# analyzed in real-time. The same pipeline should be applied to any new batch
# of data that we wish to add in the future and for which we have enough
# historical data
models_path = 'models/'

def data_load(machine,kpi):
  # time series should be loaded from the dataset,
  # right now they can be read directly from the pickle file
  # kpi_data = df.loc[df['name'] == machine].loc[df['kpi'] == kpi]
  return 0# kpi_data['time'].values, kpi_data['avg'].values

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
      'error_threshold' : 0, # amount after which an error is counted for concept drift
      'date_prediction' : (1000,1,1)
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

##############################
#####====================#####
### II. Real-Time Analysis ###
#####====================#####
##############################

#########################
### Alerts generation ###
#########################


def rolling_forecast(data, train_len: int, horizon: int, window: int, p: int , q: int, d: int) -> list:
    total_len = train_len + horizon
    pred_ARIMA = []

    for i in range(train_len, total_len, window):
        # Convert data to Series if it's not already
        if not isinstance(data, pd.Series):
            data = pd.Series(data)

        model = SARIMAX(data[:i], order=(p, d, q)) 
        res = model.fit(disp=False)

        # Get predictions for the next window size
        predictions = res.get_prediction(start=i, end=min(i + window - 1, total_len - 1))
        oos_pred = predictions.predicted_mean
        pred_ARIMA.extend(oos_pred)

    return pred_ARIMA[:horizon]
    
def make_prediction(machine, kpi, length):

  final_path = f'{models_path}{machine}_{kpi}.json'

  a_dict = {}
  with open(final_path, "r") as file:
    a_dict = json.load(file)

  kpi_data_Time, kpi_data_Avg = data_load(machine, kpi) # load a single time series

  timestamps = pd.to_datetime(kpi_data_Time)
  timeseries = pd.DataFrame({'Timestamp':timestamps, 'Value': kpi_data_Avg})
  timeseries.set_index('Timestamp', inplace=True)
  data = data_clean_missing_values(timeseries)

  avg_values1 = data['Value'].values
  # Split into train and test sets
  train_len = int(len(avg_values1) * 0.85)
  train, test = avg_values1[:train_len], avg_values1[train_len:]

  window = 1
  horizon = length

  # model = any
  # training_data: Union[np.ndarray, torch.Tensor]
  # explainer = forecastExplainer(model, training_data)
  # input_data: Union[np.ndarray, torch.Tensor]
  # n_predictions: int
  # input_labels = ['YYYY-MM-DD', 'YYYY-MM-DD'] 
  # Predicted_value, Lower_bound, Upper_bound, Confidence_score, Lime_explaination = explainer.predict_and_explain(input_data, n_predictions, input_labels)
  # Model MUST be able to do prediction = model.predict(input_data) <- predict should return a single value




  pred_ARIMA = rolling_forecast(
      avg_values1,
      train_len=train_len,
      horizon=horizon,
      window=window,
      p=a_dict['model']['p'],
      q=a_dict['model']['q'],
      d=a_dict['stationarity']['Differencing']
  )

  # Evaluate predictions
  if len(test) > 0:
      test_length = min(len(test), horizon)
      rmse = np.sqrt(mean_squared_error(test[:test_length], pred_ARIMA[:test_length]))
      mae = mean_absolute_error(test[:test_length], pred_ARIMA[:test_length])
      print(f"Evaluation Metrics for {machine} - {kpi}:")
      print(f"  RMSE: {rmse:.3f}")
      print(f"  MAE: {mae:.3f}")
  else:
      print(f"No test data available for evaluation for {machine} - {kpi}")

  return 0,pred_ARIMA

def kpi_exists(machine, KPI):

  url = "http://service2:5000/api/resource" #get_kpi
  Kpi_info = requests.post(url, json=data)

###########################################
#####=================================#####
### III. Drift Detection & Model Update ###
#####=================================#####
###########################################

###############################
### DDM For drift detection ###
###############################

class DDM: # Drift Detection Modelworks by keeping track of the error rate in a stream of predictions.
           # It raises a warning or signals a drift if it detects significant deviations based on
           # statistical analysis of the error rate.
  def __init__(self, warning_level=2.0, drift_level=3.0, state_file="ddm_state.json"):
    """
    - warning_level: float, threshold for raising a warning.
    - drift_level: float, threshold for detecting a drift.
    - state_file: str, file path for saving and loading the DDM state.
    """
    self.warning_level = warning_level
    self.drift_level = drift_level
    self.state_file = state_file

    # Initialize state variables
    self.num_instances = 0
    self.p_min = float('inf')
    self.s_min = float('inf')
    self.p_mean = 0.0
    self.s_mean = 0.0

    # Load state if the state file exists
    if os.path.exists(self.state_file):
      self.load_state()

  def update(self, error):
    """
    Update the DDM statistics with a new error value.

    Parameters:
    - error: int, 0 or 1 representing whether the prediction was correct (0) or incorrect (1).
    """
    self.num_instances += 1

    # Update p_mean and s_mean
    self.p_mean += (error - self.p_mean) / self.num_instances
    self.s_mean = np.sqrt(self.p_mean * (1 - self.p_mean) / self.num_instances)

    # Calculate thresholds
    warning_threshold = self.p_mean + self.warning_level * self.s_mean
    drift_threshold = self.p_mean + self.drift_level * self.s_mean

    # Update p_min and s_min (historical minimum values)
    if self.p_mean + self.s_mean < self.p_min + self.s_min:
      self.p_min = self.p_mean
      self.s_min = self.s_mean

    # Check for warning or drift
    self.drift_detected = 0
    if self.p_mean + self.s_mean > drift_threshold:
      print(f"Drift detected at instance {self.num_instances}: p_mean={self.p_mean:.4f}")
      self.drift_detected = 2
      # Reset the detector after drift detection
      self.reset()
    if self.p_mean + self.s_mean > warning_threshold:
      print(f"Warning at instance {self.num_instances}: p_mean={self.p_mean:.4f}")
      self.drift_detected = 1


    # Save the state after each update
    self.save_state()
    return self.drift_detected

  def reset(self):
    """Reset the DDM statistics after drift detection."""
    self.num_instances = 0
    self.p_min = float('inf')
    self.s_min = float('inf')
    self.p_mean = 0.0
    self.s_mean = 0.0

  def save_state(self):
    """Save the current state of DDM to a JSON file."""
    n_dict = {}

    with open(self.state_file, "r") as file:
      n_dict = json.load(file)

      n_dict['drift'] = {
        "num_instances": self.num_instances,
        "p_min": self.p_min,
        "s_min": self.s_min,
        "p_mean": self.p_mean,
        "s_mean": self.s_mean,
      }

    with open(self.state_file, "w") as file:
      json.dump(n_dict, file)

  def load_state(self):
    """Load the state of DDM from a JSON file."""
    with open(self.state_file, "r") as file:
      state = json.load(file)
      self.num_instances = state['drift']["num_instances"]
      self.p_min = state['drift']["p_min"]
      self.s_min = state['drift']["s_min"]
      self.p_mean = state['drift']["p_mean"]
      self.s_mean = state['drift']["s_mean"]

def read_value(machine, kpi):
  return 0 #read data from the DB

def missingdata_check(current_value):
  if current_value == float('nan'):
    return -1
  elif current_value == 0:
    return 0
  else:
    return 1

def outlier_check(new_value, data):
    multiplier = 3
    mean = sum(data)/len(data)
    variance = sum((x - mean) ** 2 for x in data)/len(data)
    std_dev = variance ** 0.5
    return abs(new_value - mean) > std_dev * multiplier
    # return [f"An anomaly has been detected: {new_value} deviates significantly from the {mean}"]



def send_Alert(url, data):
  try:
      response = requests.post(url, json=data)
      print(f"Response status code: {response.status_code}")
      print(f"Response body: {response.json()}")
  except requests.exceptions.RequestException as e:
      print(f"Error sending POST request: {e}")

def incaseofalert():
    # URL of the other microservice (container name is the hostname)
    url = "http://service2:5000/api/resource"

    # Data to send in the POST request
    data = {
        "key1": "value1",
        "key2": "value2",
    }
    send_Alert(url,data)
    #title description

# outlier detection
def detect_outlier(x, window):
  r = x.rolling(window=window)
  m = r.mean().shift(1)
  s = r.std(ddof=0).shift(1)
  z = (x[-1]-m)/s
  return z > 3 # if the last object is outside the 97% of the range in the
                # window, the data point is evaluated as an outlier

       
def elaborate_new_datapoint(machine, kpi):

  ##################################
  ### 1. Initial data processing ###
  ##################################

  # LOADING NEW DATA and KPI metadata
  final_path = f'{models_path}{machine}_{kpi}.json'
  # d = read_value(machine, kpi)
  kpi_data_Date, kpi_data_Avg = data_load(machine, kpi) # load a single time series

  d_date = kpi_data_Date[-1]
  d = kpi_data_Avg[-1]

  a_dict = {}
  with open(final_path, "r") as file:
    a_dict = json.load(file)
  

  last_pred =  datetime.date(a_dict['predictions']['date_prediction'][0],
                             a_dict['predictions']['date_prediction'][1],
                             a_dict['predictions']['date_prediction'][2])


  # if missing_count >= threshold_count:
  #     return [f"No valid data received for {missing_count} consecutive days."]
  # elif zeros_count >= threshold_count:
  #     return [f"Zeros data received for {zeros_count} consecutive days."]
  url_alert = ''
  if last_pred < d_date: # if the prediction is relative to a new date
    
    is_missing = missingdata_check(d)
    if is_missing == -1: # the data is 'nan', fill it and send an alert
      d = a_dict['predictions']['first_prediction']
      a_dict['missingval']['alert_sent'] = True
      alert_data ={'error': 'did not receive any value. filling with last prediction'}
      send_Alert(url_alert, alert_data)
    elif is_missing == 0:
      a_dict['missingval']['missing_streak'] += 1
      if a_dict['missingval']['missing_streak'] > 2 and not a_dict['missingval']['alert_sent']:
        a_dict['missingval']['alert_sent'] = True
        alert_data ={'error': 'Too many zeros received'}
        send_Alert(url_alert, alert_data)        
    else:
      a_dict['missingval']['alert_sent'] = False
      a_dict['missingval']['missing_streak'] = 0
    #if the value is not missing we test if it is within range
    if is_missing != -1:
      
      is_outlier = outlier_check(d, kpi_data_Avg[-31:-1])
      if is_outlier:
        prediction_error = d - a_dict['predictions']['first_prediction']
      error = 0
      if prediction_error > a_dict['predictions']['error_threshold']:
        error = 1
      # Initialize DDM with warning level and drift level thresholds
      ddm = DDM(warning_level=2.0, drift_level=3.0, state_file=final_path)
      is_drifting = ddm.update(error)
      if is_drifting == 2:
        characterize_KPI(machine, kpi)
      #if is_drifting == 1: warning
      #predict only the first data point after the series and save it here
    d,v = make_prediction(machine,kpi,1)
    a_dict['predictions']['first_prediction'] = v #put here first predicted value
    a_dict['predictions']['date_prediction'] = f"{d.Year}/{d.Month}/{d.Day}" 

    save_model_data(machine, kpi, a_dict)