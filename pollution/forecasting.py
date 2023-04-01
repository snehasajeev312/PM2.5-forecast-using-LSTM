from pandas import read_csv
from datetime import datetime
from math import sqrt
from numpy import concatenate
import matplotlib
matplotlib.use('Agg') #when error occurs
# matplotlib.use('TkAgg')
from matplotlib import pyplot

from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error,median_absolute_error,r2_score,mean_absolute_percentage_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def predict():
	# load and process data
	def parse(x):
		return datetime.strptime(x, '%Y %m %d %H')
	from pandas import read_csv
	dataset = read_csv('tvmdata.csv',  parse_dates = [['year', 'month', 'day', 'hour']], index_col=0, date_parser=parse)
	dataset.drop('No', axis=1, inplace=True)
	dataset.columns = ['pollution', 'RH', 'AT', 'BP', 'WD', 'WS', 'snow', 'rain','PM10','NO','NO2','NH3','CO']
	dataset.index.name = 'date'
	dataset['pollution'].fillna(0, inplace=True)
	dataset = dataset[24:]
	print("||"*40)
	print("** DATA PROCESSING COMPLETED **")
	print(dataset.head(5))
	print("||"*40)

	dataset.to_csv('pollution.csv')
	paths=os.path.join(BASE_DIR,"pollution\static\media")
	# generating dataset plot
	from pandas import read_csv
	from matplotlib import pyplot
	dataset = read_csv('pollution.csv', header=0, index_col=0)
	values = dataset.values
	groups = [0, 1, 2, 3, 5, 6, 7,8]
	i = 1
	pyplot.figure()
	for group in groups:
		pyplot.subplot(len(groups), 1, i)
		pyplot.plot(values[:, group],'k')
		pyplot.title(dataset.columns[group], y=0.5, loc='right')
		i += 1
	# pyplot.show()
	
	pyplot.savefig(paths+"/pollutions.png")
	pyplot.close()

	# Lets normalize all features, and remove the weather variables for the hour to be predicted.
	import pandas as pd 
	from sklearn import preprocessing
	from sklearn.preprocessing import MinMaxScaler

	def s_to_super(data, n_in=1, n_out=1, dropnan=True):
		n_vars = 1 if type(data) is list else data.shape[1]
		df = pd.DataFrame(data)
		cols, names = list(), list()
		for i in range(n_in, 0, -1):
			cols.append(df.shift(i))
			names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
		for i in range(0, n_out):
			cols.append(df.shift(-i))
			if i == 0:
				names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
			else:
				names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
		agg = pd.concat(cols, axis=1)
		agg.columns = names
		if dropnan:
			agg.dropna(inplace=True)
		return agg
	
	# load dataset
	dataset = read_csv('pollution.csv', header=0, index_col=0)
	values = dataset.values
	encoder = preprocessing.LabelEncoder()
	values[:,4] = encoder.fit_transform(values[:,4])
	values = values.astype('float32')
	scaler = MinMaxScaler(feature_range=(0, 1))
	scaled = scaler.fit_transform(values)
	reframed = s_to_super(scaled, 1, 1)
	# drop columns we don't want to predict
	reframed.drop(reframed.columns[[9,10,11,12,13,14,15]], axis=1, inplace=True)
	print("** NOT REQUIRED DATA COLUMNS DROPPED **")
	print("||"*40)
	# split data into training and testing, futher splitting the train and test sets into i/p and o/p variables
	# reshaped data further into 3D formate expected by LSTMs
	values = reframed.values
	# n_train_hours = 365 * 24
	n_train_hours = 900
	n_train_hours2=n_train_hours//2
	train = values[:n_train_hours, :]
	test = values[n_train_hours2:, :]
	# split into input and outputs
	train_X, train_y = train[:, :-1], train[:, -1]
	test_X, test_y = test[:, :-1], test[:, -1]
	train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
	test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
	print("** DATA SPLITTING COMPLETED **")
	print(" Training data shape X, y => ",train_X.shape, train_y.shape," Testing data shape X, y => ", test_X.shape, test_y.shape)
	print("||"*40)
	# defining LSTM with 50 neurons in first hidden layer and 1 neuron in the o/p layer
	# using the MAE loss function and Adma version of stochastic gradient descent
	from keras.models import Sequential
	from keras.layers import LSTM
	from keras.layers import Dense, Dropout
	model = Sequential()
	# 
	# 50 neurons in first hidden layer
	model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
	model.add(Dropout(0.3))
	model.add(Dense(1,kernel_initializer='normal', activation='sigmoid'))
	model.compile(loss='mae', optimizer='adam')
	history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
	# tracking history for plots
	pyplot.plot(history.history['loss'], 'b', label='training history')
	pyplot.plot(history.history['val_loss'],  'r',label='testing history')
	pyplot.title("Train and Test Loss for the LSTM")
	pyplot.legend()
	# pyplot.show()
	
	pyplot.savefig(paths+"/test vs train.png")
	pyplot.close()
	 #when error occurs
	
	# evaluating model
	# make a prediction
	from math import sqrt
	from numpy import concatenate
	yhat = model.predict(test_X)
	test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
	inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
	# check
	scaler = MinMaxScaler(feature_range=(0, 1)).fit(inv_yhat)
	#####
	inv_yhat = scaler.inverse_transform(inv_yhat)
	inv_yhat = inv_yhat[:,0]
	# check
	scaler = MinMaxScaler(feature_range=(0, 1)).fit(test_X)
	#####
	inv_y = scaler.inverse_transform(test_X)
	inv_y = inv_y[:,0]

	# print("*"*50)
	# print(inv_y)
	# print("*"*50)

	# calculate RMSE
	rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
	print('Test RMSE: %.3f' % rmse)

	mae = median_absolute_error(inv_y, inv_yhat)
	print('Test ME: %.3f' % mae)

	r2 = r2_score(inv_y, inv_yhat)
	print('Test R2: %.3f' % (r2))

	mape = mean_absolute_percentage_error(inv_y, inv_yhat)
	print('Test mape: %.3f' % mape)
	

	errors={"rmse":rmse*100,'mae':mae*100,"r2":r2*100,"mape":int(mape)}



	print('*'*50)
	print("next Data are")
	print('*'*50)
	# for i in inv_yhat[:20]:
	# 	print(i)
	return errors,inv_yhat



