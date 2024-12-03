import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import itertools

from matplotlib.ticker import MaxNLocator
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.stattools import adfuller
from tqdm import notebook
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error


import json
import os

##############################
#####====================#####
### II. Real-Time Analysis ###
#####====================#####
##############################
models_path = 'models/'
def rolling_forecast(data, train_len: int, horizon: int, window: int, p: int , q: int, d) -> list:
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

  # Plot results -< instead of plotting, send the series as the output
  plt.figure(figsize=(12, 6))
  plt.plot(range(len(train)), train, label='Train Data', color='blue')
  if len(test) > 0:
      plt.plot(range(len(train), len(train) + len(test)), test, label='Test Data', color='orange')
      plt.plot(range(len(train), len(train) + horizon), pred_ARIMA, label='Forecast', color='green')
      plt.title(f'Forecast for {machine} - {kpi}')
      plt.xlabel('Time Steps')
      plt.ylabel('Value')
      plt.legend()
      plt.show()
