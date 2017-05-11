import collections
import seaborn as sns
import pandas as pd

import time
import base64
import pickle
import numpy as np
import random as rd
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
from pymongo import MongoClient
from bokeh.charts import HeatMap, output_file, show

def MongoAcces(clientId, clientIp):
	"""

	:param clientId: Client Id to access Mongo Database
	:param clientIp: Client Ip to find whos database to acces
	:return: database of the selected ip
	"""

	client = MongoClient(clientId)
	db = client[clientIp]

	return db

def AccessCollectionData(dir, collection, weeklySession=False):
	"""
	:param db: database
	:param weeklySession: Not operational Yet
	:return: All data available to be rendered
	"""
	with open(dir + "/" + collection, 'rb') as handle:
		collectionDB = pickle.load(handle)

	# Parameters Mouse
	x = []
	y = []
	rate_xy = []
	counterX = []
	counterY = []
	xScroll = []
	yScroll = []
	TimestampMouse = []

	#Parameters Keyboard
	keyNbr = []
	alt = []
	shift = []
	ctrl = []
	cpslk = []
	TimestampKeyBrd = []


	#Boolean Control
	Settings = False
	Screenshot = False
	Url = False
	Mouse = False
	Keyboard = False
	i = 0

	for EventSection in collectionDB:

		event = collectionDB[EventSection]
		print(event)

		if(event['Type'] == 'New Connection'):
			print("Access url")
			url = event['Data']
			URL = True

		elif(event['Type'] == 'Settings'):
			print("Access Screen Resolution")

			height = event['Data']['ScreenProperties']['availHeight']
			width = event['Data']['ScreenProperties']['availWidth']

			Settings  = True

		elif(event['Type'] == 'Screenshot'):
			print("Acces Screenshot")

			imData = base64.b64decode(event['Data'].split(';')[1].split(',')[1])

			with open("static/ScreenShots/Screen.png", "wb") as fh:
				fh.write(imData)

			im = Image.open("static/ScreenShots/Screen.png")
			width1, height1 = im.size

			Screenshot = True


		elif(event['Type'] == 'Mouse'):
			print("Access Mouse data")

			data = event["Data"].split(';')
			x.append(data[0])
			y.append(data[1])
			rate_xy.append(str(data[0])+"."+str(data[1]))
			xScroll.append(data[2])
			yScroll.append(data[3])
			TimestampMouse.append(data[4])
			i = i+ 1
			Mouse = True

		elif(event['Type'] == 'Keyboard'):
			print("Access Keyboard Data")

			data = event["Data"].split(';')
			keyNbr.append(data[0])
			alt.append(data[1])
			shift.append(data[2])
			ctrl.append(data[3])
			cpslk.append(data[4])
			TimestampKeyBrd.append(data[5])

			Keyboard = True

		else:
			print('you"re wrong man')

	if (Settings and Screenshot and Mouse and i > 10):
		return 0, width, height, width1, height1, xScroll, yScroll, TimestampMouse
	elif(Settings and Mouse and i > 10 and not Screenshot):
		return 1, width, height, xScroll, yScroll, TimestampMouse
	else:
		return False


	#
	# 	TimeofEvent = []
	# 	TotalEvents =  []
	# 	LastEventTime = []
	# 	ActivityRatio = []
	# 	for file in db:
	#
	# 		#open Collection/Session
	# 		with open(dir + "/" + file, 'rb') as handle:
	# 			collection = pickle.load(handle)
	#
	#
	#
	# 		#Scroll in collection to find all events
	# 		for i in collection:
	# 			event = collection[i]
	# 			# print(event)
	# 			if(event['Type'] == 'Settings'):
	# 				continue
	# 			else:
	# 				# print(event)
	# 				TotalEvents.append(event['Time'])
	# 				# ActivityRatio.append(event['Data']['NumberOfMessages']/event['Data']['Duration'])
	# 				# TimeofEvent.append((event['Time']))
	#
	# 	TimeEvents = dict()
	# 	Hours = np.linspace(0, 23, 24).astype('int')
	#
	#
	# 	for x in TotalEvents:
	# 		key = str(time.localtime(x)[2])
	# 		TimeEvents.setdefault(key, []).append(time.localtime(x)[3])
	#
	# 	Days = TimeEvents.keys()
	#
	#
	# 	# print(TimeEvents.items())
	# 	for a in TimeEvents.keys():
	# 		Cou  = Counter(TimeEvents[a])
	# 		TimeEvents[a] = Cou
	# 	Values = np.zeros((len(Hours), len(Days)))
	#
	# 	i = 0
	# 	for day in Days:
	# 		for hour in Hours:
	# 			print(TimeEvents[day][int(hour)])
	# 			Values[int(hour)][i] = TimeEvents[day][int(hour)]
	# 		i = i + 1
	#
	# 	print(Values)
	#
	# 	df = pd.DataFrame(Values, index=Hours, columns=Days)
	# 	# print(TimeEvents)
	#
	# 	# print(a)
	# 	# Days = []
	# 	# Hours = []
	# 	# for k in a.keys():
	# 	# 	Days.append(k[0])
	# 	# 	Hours.append(k[1])
	#
	# 	# print(Days)
	#
	#
	# 	# ActivityDic = {}
	# 	# i=0
	# 	# for (A, T) in sorted(zip(ActivityRatio, TimeofEvent), key=lambda pair: pair[1]):
	# 	# 	ActivityDic[i] = A
	# 	# 	i = i+1
	#
	# 	# print(ActivityDic)
	# 	df.index.names = ['Hours']
	# 	df.columns.names = ["Days"]
	#
	# 	hm =  HeatMap(df, width=3, height=24)
	#
	# 	output_file("HeatMapActivity.html")
	# 	show(hm)
	# 	# #
	# 	# print(df)
	# 	# sns.heatmap(df)
	# 	# plt.show()
	#
	# 	# WeekSession = {k: rd.random() for k in range(100)}
	# 	# print(WeekSession)
	#
	# 	# plot Heatmap of activity:
	#
	# 	# print(ActivityDic)
	# 	# # BeginSessionTime.sort()
	# 	# # plt.plot(BeginSessionTime)
	# 	# plt.plot(Act, 'b')
	# 	# plt.plot(Time,'r')
	# 	# plt.show()
	#
	#
	#
	#
	# 	# print("Sorry but this function is not ready yet...")
	#
	# return
	#
