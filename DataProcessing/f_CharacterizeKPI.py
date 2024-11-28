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
