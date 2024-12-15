
import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import adfuller
import itertools
from tqdm import notebook
from statsmodels.tsa.statespace.sarimax import SARIMAX
import xgboost as xgb
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from model import Severity, Alert

import json
import os
import base64

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

import requests
from datetime import datetime, timedelta

from XAI_forecasting import ForecastExplainer
from storage.storage_operations import insert_model_to_storage, retrieve_model_from_storage


####################################
#####==========================#####
### I. Data Exploration Pipeline ###
#####==========================#####
####################################

# This first section creates a starting point for our data to be modeled and
# analyzed in real-time. The same pipeline should be applied to any new batch
# of data that we wish to add in the future and for which we have enough
# historical data

observation_window = 15

def execute_druid_query(body):
    """
    Executes a SQL query on a Druid instance.
    
    :param url: The Druid SQL endpoint.
    :param body: A dictionary containing the query body.
    :return: The response from the Druid server.
    """
    headers = {
        "Content-Type": "application/json"
    }
    url = "http://router:8888/druid/v2/sql"
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def data_load(machine,kpi):
  # Controlla gli ultimi tre caratteri
  # Tipi di aggregazione validi
  kpi_types = {"sum", "min", "max", "avg"}

  kpi_name = ''
  data_type = ''
  if kpi[-3:] in kpi_types:
      # Trova l'ultimo underscore
      split_index = kpi.rfind("_")
      
      # Dividi il nome del KPI
      kpi_name = kpi[:split_index]  # Parte prima dell'underscore
      data_type = kpi[split_index + 1:]  # Parte dopo l'underscore
  query_body = {
        "query": f"SELECT * FROM \"timeseries\" where name = '{machine}' AND kpi = '{kpi_name}'"
  } # Execute the query
  response = execute_druid_query(query_body)
  avg_r = []
  avg_t = []
  for r in response:
    avg_r.append(r[data_type])
    avg_t.append(r['__time'])
  return avg_t,avg_r
# def data_load(machine,kpi):
#   # Controlla gli ultimi tre caratteri
#   # Tipi di aggregazione validi
#   query_body = {
#         "query": f"SELECT * FROM \"timeseries\" where name = '{machine}' AND kpi = '{kpi}'"
#   } # Execute the query
#   response = execute_druid_query(query_body)
#   avg_r = []
#   avg_t = []
#   for r in response:
#     avg_r.append(r['avg'])
#     avg_t.append(r['__time'])
#   return avg_t,avg_r

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

def create_model_data(): #TODO: instead of path we need to save the model on the DB
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
      'q': 0,
      'xgb_bytes': ''
  }
  return a_dict


def save_model_data(machine, kpi, n_dict):
  
  file_name = f'{machine}_{kpi}.json'

  insert_model_to_storage("models", file_name, n_dict, kpi, machine)

  # final_path = os.path.join(models_path, f'{machine}_{kpi}.json')
  # with open(final_path, 'w') as outfile:
  #   json.dump(n_dict, outfile)

def load_model(machine, kpi): #handle loading with a query

  dct = retrieve_model_from_storage(kpi,machine)  
  if dct != None:
     return dct
  else:
     return create_model_data()
  # final_path = os.path.join(models_path, f'{machine}_{kpi}.json')
  # if not os.path.isfile(final_path):
  #   return create_model_data(machine, kpi, final_path)
  # else:
  #   dct = {}
  #   with open(final_path, "r") as file:
  #     dct = json.load(file)
  #   return dct

def check_model_exists(machine, kpi):

  dct = retrieve_model_from_storage(kpi,machine)
  if dct == None:
     return False
  else:
     return True
  # final_path = os.path.join(models_path, f'{machine}_{kpi}.json')
  

  # if os.path.isfile(final_path):
  #    a_dict = load_model(machine,kpi)
  #    if a_dict["model"]["name"] != "":
  #       return True
  # return False

   

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

def xgboost_parameter_select(X_train,y_train):
  # Define the XGBoost regressor
  xgb_model = XGBRegressor(objective="reg:squarederror", random_state=42)

  # Define a small parameter grid
  param_grid = {
      "n_estimators": [50, 100, 200, 300, 400],
      "max_depth": [3, 5, 7],
      "learning_rate": [0.01, 0.1, 0.2],
  }
  param_combinations = list(ParameterGrid(param_grid))
  # ParameterGrid
  # Set up GridSearchCV
  # grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring="neg_mean_squared_error", verbose=1)

  # Perform the grid search
  # grid_search.fit(X_train, y_train)

  # Best parameters and model performance
  # print("Best Parameters:", grid_search.best_params_)

  # Data preparation (replace with your dataset)
  dtrain = xgb.DMatrix(X_train, label=y_train)

  # Perform cross-validation
  best_params = None
  best_score = float("inf")
  best_model = None

  for params in param_combinations:
      # Create XGBoost parameters
      xgb_params = {
          "max_depth": params["max_depth"],
          "eta": params["learning_rate"],
          "objective": "reg:squarederror",
      }

      # Perform cross-validation
      cv_results = xgb.cv(
          params=xgb_params,
          dtrain=dtrain,
          num_boost_round=params["n_estimators"],
          nfold=3,
          metrics="rmse",
          early_stopping_rounds=10,
          seed=42,
      )

      # Extract the best RMSE score
      mean_rmse = cv_results["test-rmse-mean"].min()
      best_iteration = cv_results["test-rmse-mean"].idxmin()

      # Update best parameters if score improves
      if mean_rmse < best_score:
          best_score = mean_rmse
          best_params = params
          best_model = xgb.train(
            params=xgb_params,
            dtrain=dtrain,
            num_boost_round=best_iteration + 1,  # Use the optimal number of iterations
        )

    # Print the best parameters and score
    # print("Best Parameters:", best_params)
    # print("Best RMSE:", best_score)



  return best_model


def custom_tts(data, labels, window_size = 20):

  X_train = []
  y_train = []
  total_points = len(data)
  for i in range(total_points - window_size - 1):
      X_train.append(data[i:i+window_size])
      y_train.append(data[i+window_size])

  X_train = np.array(X_train)
  y_train = np.array(y_train)

  # # Train XGBoost model
  # model.fit(X_train, y_train)

  # X = []
  # y = []
  # for i in range(len(data) - window_size):
  #   X.append(data[i:i + window_size])  # Input is the window of 10 elements
  #   y.append(data[i + window_size])    # Target is the next value

  # X = np.array(X)
  # y = np.array(y)
  # X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.15, random_state=42) #decide what to do
  return X_train, y_train

#########################
### 1. data profiling ###
#########################

def characterize_KPI(machine, kpi):
  # DATA LOADING
  a_dict = load_model(machine, kpi)
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

  # STATIONARITY CHECK
  orig_statistic, orig_p_value = perform_adfuller(data['Value'])

  stationarity_results = {
      'Differencing': 0,
      'Statistic': round(orig_statistic, 3),
      'P-value': f'{orig_p_value:.2E}',
      'Stationary': 1 if orig_p_value < 0.05 else 0
  }
  if orig_p_value >= 0.05: # if the data is not stationary we check the first difference
    diff1_series = pd.DataFrame({'Timestamp':data['Value'].index, 'Value': data['Value'].diff().bfill()})
    diff1_statistic, diff1_p_value = perform_adfuller(diff1_series['Value'].values)
    # data['Value'] = data_normalize_params(diff1_series['Value'])
    stationarity_results = {
      'Differencing': 1,
      'Statistic': round(diff1_statistic, 3),
      'P-value': f'{diff1_p_value:.2E}',
      'Stationary': 1 if diff1_p_value < 0.05 else 0
    }
    if diff1_p_value >= 0.05: # if the first difference is still non stationary we check the second
        diff2_series = pd.DataFrame({'Timestamp':diff1_series['Value'].index, 'Value': diff1_series['Value'].diff().bfill()})
        diff2_statistic, diff2_p_value = perform_adfuller(diff2_series['Value'].values)
        # data['Value'] = data_normalize_params(diff2_series['Value'])
        stationarity_results = {
          'Differencing': 2,
          'Statistic': round(diff2_statistic, 3),
          'P-value': f'{diff2_p_value:.2E}',
          'Stationary': 1 if diff2_p_value < 0.05 else 0
        }
  # else:
  #   data['Value'] = data_normalize_params(data['Value'])
  a_dict['stationarity'] = stationarity_results
  ###########################
  ### 3. Model definition ###
  ###########################
  model_selected = 'xgboost'
  if model_selected == 'ARIMA':
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
  elif model_selected == 'xgboost':
    # parameter selection for xgboost
    X_train, y_train = custom_tts(data['Value'].values,kpi_data_Time,observation_window)

    # model = xgboost_parameter_select(X_train,y_train)
    # # model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
    # model.fit(X_train, y_train)

    # booster = model.get_booster()
    booster = xgboost_parameter_select(X_train,y_train)
    model_bytes = booster.save_raw()
    encoded_model = base64.b64encode(model_bytes).decode('utf-8')
    a_dict['model'] = {
       'name': 'xgboost',
       'xgb_bytes': encoded_model,
       'metadata': {
          'trained_on': str(datetime.today().date())},
          # 'hyperparameters': model.get_params()},
    }
  ############################
  ### 4. Meta-Data storage ###
  ############################
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

def XAI_PRED(data, model, total_points, seq_length = 10, n_predictions = 30):
  # Seed
  np.random.seed(42)

  # Prepare training data for XGBoost: predict next value from last seq_length values
  X_train = []
  y_train = []
  for i in range(total_points - seq_length - 1):
      X_train.append(data[i:i+seq_length])
      y_train.append(data[i+seq_length])

  X_train = np.array(X_train)
  y_train = np.array(y_train)

  # Perform predictions beyond the training range
  input_data = data[(total_points - seq_length - n_predictions): (total_points - n_predictions)]

  # Generate labels for the input_data
  start_date = datetime.today().date() - timedelta(observation_window - 1)
  input_labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(seq_length)]

  # Initialize the explainer
  explainer = ForecastExplainer(model, X_train)

  # Perform autoregressive predictions
  results = explainer.predict_and_explain(
      input_data=input_data,
      n_predictions=n_predictions,
      input_labels=input_labels,
      num_features=5,
      confidence=0.95,
      n_samples=100,
      use_mean_pred=True
  )
  return results

def make_prediction(machine, kpi, length):

  a_dict = load_model(machine, kpi)

  kpi_data_Time, kpi_data_Avg = data_load(machine, kpi) # load a single time series

  timestamps = pd.to_datetime(kpi_data_Time)
  timeseries = pd.DataFrame({'Timestamp':timestamps, 'Value': kpi_data_Avg})
  timeseries.set_index('Timestamp', inplace=True)
  data = data_clean_missing_values(timeseries)

  avg_values1 = data['Value'].values
  if a_dict['model']['name'] == 'ARIMA':

    # Split into train and test sets
    train_len = int(len(avg_values1) * 0.85)
    train, test = avg_values1[:train_len], avg_values1[train_len:]

    window = 1
    horizon = length

    # model = any
    # training_data: Union[np.ndarray, torch.Tensor]
    # explainer = ForecastExplainer(model, training_data)
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

  elif a_dict['model']['name'] == 'xgboost':
    # TODO: perform differentiation here
    # X_train, y_train = custom_tts(avg_values1,kpi_data_Time)
    # X_test = [avg_values1[-11:-1]]

    # print(f'testlen: {len(X_test)}')

    # Decode the Base64 string back to raw bytes
    encoded_model = a_dict['model']['xgb_bytes']
    raw_model_bytes = bytearray(base64.b64decode(encoded_model))

    # Load the model from raw bytes
    booster = xgb.Booster()
    booster.load_model(raw_model_bytes)

    # Optionally, wrap the Booster back into an XGBRegressor for convenience
    loaded_model = xgb.XGBRegressor()
    loaded_model._Booster = booster

    # Use the loaded model for predictions

    # explainer = ForecastExplainer(loaded_model, X_train)
    # formatted_dates = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") for date in kpi_data_Time[-11:-1]]

    results = XAI_PRED(avg_values1,loaded_model,len(avg_values1),seq_length = observation_window,n_predictions = length)
    
    x = [r.item() for r in results['Predicted_value']]
    y = [r.item() for r in results['Lower_bound']]
    z = [r.item() for r in results['Upper_bound']]
    k = [r.item() for r in results['Confidence_score']]
    results['Predicted_value'] = x
    results['Lower_bound'] = y
    results['Upper_bound'] = z
    results['Confidence_score'] = k
    
    return results

def kpi_exists(machine, KPI, api_key):
  machine = machine.replace(" ", "_")
  headers = {
      "x-api-key": api_key
  }
  
  # Send GET request with headers
  host_port = 8000
  url_KB = f"http://kb:{host_port}/kb/{machine}/{KPI}/check"
  # Kpi_info  = requests.post(url_KB)
  Kpi_info = requests.get(url_KB, headers=headers)

  return Kpi_info.json()

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



def send_Alert(url, data, api_key):

  headers = {
      "x-api-key": api_key
  }
  # new_al = Alert(
  #   title = data["title"],
  #   type = data["type"],
  #   description = data["description"],
  #   triggeredAt = str(datetime.now()),
  #   machineName = data["machine"],
  #   isPush = True,
  #   isEmail = True,
  #   recipients = data["recipients"],
  #   severity = data["severity"])
  # print("Sending_Alert")

  try:
      new_al = {
        "title": data["title"],
        "type": data["type"],
        "description": data["description"],
        "triggeredAt": str(datetime.now()),
        "machineName": data["machine"],
        "isPush": True,
        "isEmail": True,
        "recipients": data["recipients"],
        "severity": data["severity"].value
      }  
      response = requests.post(url, json=new_al, headers=headers)
      print(f"Response status code: {response.status_code}")
      print(f"Response body: {response.json()}")
  except requests.RequestException as e:
      print(f"Request failed: {e}")
  except Exception as e:
      print(f"Unexpected error: {e}")

# outlier detection
def detect_outlier(x, window):
  r = x.rolling(window=window)
  m = r.mean().shift(1)
  s = r.std(ddof=0).shift(1)
  z = (x[-1]-m)/s
  return z > 3 # if the last object is outside the 97% of the range in the
                # window, the data point is evaluated as an outlier

       
def elaborate_new_datapoint(machine, kpi):
  """
      daily check of new data point to update the models. 

      Args:
      machine: machine ID of the requested machine
      kpi: KPI ID of the requested machine

      Returns:      
  """
  ##################################
  ### 1. Initial data processing ###
  ##################################

  # LOADING NEW DATA and KPI metadata
  # d = read_value(machine, kpi)
  kpi_data_Date, kpi_data_Avg = data_load(machine, kpi) # load a single time series

  d_date = datetime.date(kpi_data_Date[-1])
  d = kpi_data_Avg[-1]

  a_dict = load_model(machine,kpi)
  
  last_pred =  datetime.date(a_dict['predictions']['date_prediction'][0],
                             a_dict['predictions']['date_prediction'][1],
                             a_dict['predictions']['date_prediction'][2])


  # if missing_count >= threshold_count:
  #     return [f"No valid data received for {missing_count} consecutive days."]
  # elif zeros_count >= threshold_count:
  #     return [f"Zeros data received for {zeros_count} consecutive days."]  
  alert_data = {
     'title': "",
     'type': "",
     'description': "",
     'machine': "",
     'isPush': True,
     'isEmail': True,
     'recipients': [],
     'severity': Severity.MEDIUM
  }

  url_alert = f"http://api:8000/smartfactory/postAlert"
  if last_pred < d_date: # if the prediction is relative to a new date
    is_missing = missingdata_check(d)
    if is_missing == -1: # the data is 'nan', fill it and send an alert
      d = a_dict['predictions']['first_prediction']
      alert_data['title'] = 'missing value'
      alert_data['description'] = f'{machine} did not yield a new value for:{kpi}'
      alert_data['machine'] = machine
      alert_data['recipients'] = ["FactoryFloorManager"]
      alert_data['type'] = 'machine_unreachable'
      send_Alert(url_alert, alert_data)
    elif is_missing == 0:
      a_dict['missingval']['missing_streak'] += 1
      if a_dict['missingval']['missing_streak'] > 2 and not a_dict['missingval']['alert_sent']:
        alert_data['title'] = 'Zero streak'
        alert_data['description'] = f"{kpi} for {machine} returned zeros for {a_dict['missingval']['missing_streak']} days in a row"
        alert_data['machine'] = machine
        alert_data['recipients'] = ["FactoryFloorManager"]
        alert_data['type'] = 'machine_unreachable'
        if a_dict['missingval']['missing_streak'] > 5:
           alert_data['severity'] = Severity.HIGH 
           a_dict['missingval']['alert_sent'] = False       
        send_Alert(url_alert, alert_data)        
    else:
      a_dict['missingval']['alert_sent'] = False
      a_dict['missingval']['missing_streak'] = 0
    #if the value is not missing we test if it is within range
    if is_missing != -1:
      
      is_outlier = outlier_check(d, kpi_data_Avg[-31:-1])
      if is_outlier:
        alert_data['title'] = 'Outlier detected'
        alert_data['description'] = f'{kpi} for {machine} returned a value higher than expected'
        alert_data['machine'] = machine
        alert_data['recipients'] = ["FactoryFloorManager","SpecialityManufacturingOwner"]
        alert_data['type'] = 'unexpected output'        
        send_Alert(url_alert, alert_data) 
      prediction_error = d - a_dict['predictions']['first_prediction']
      error = 0
      if prediction_error > 2*a_dict['trends']['std']: # a_dict['predictions']['error_threshold']:
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