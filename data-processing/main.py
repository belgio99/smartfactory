import f_CharacterizeKPI
import f_forecasting

m = 'Medium Capacity Cutting Machine 1'
k = 'consumption'
x,y = data_load(m,k)
plt.plot(x,y)
characterize_KPI('Medium Capacity Cutting Machine 1', 'consumption')
