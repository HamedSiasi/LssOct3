
from sklearn.svm import SVR
import numpy as np
import requests
import time
import json
import os
import warnings
import datetime
import pylab as pl
import sys
from tabulate import tabulate
import gpxpy.geo
import pdb
import random
from random import randint
from termcolor import colored
from sklearn import preprocessing
import random


DeviceSafeMovement = 500

#--------------------------------------------------------------------------
#                                C027
#--------------------------------------------------------------------------

class C027Class():
	pDataBase              = 0
	Type                   = 0
	RiskScore              = 0
	RawDataId              = []
	########## Assets #########
	IMEI                   = [] #2
	IMSI                   = [] #3
	Lat                    = [] #4
	Lon                    = [] #5
	RX                     = [] #6 
	TX                     = [] #7 
	Wakeup                 = [] #8
	WDT                    = [] #9
	RawDataId              = [] #ok
	FutureTime             = [] #ok
	PosixTime              = [] #ok
	RelativeFutureTime     = [] #ok
	RelativePosixTime      = [] #ok
	TX_ready               = []
	TIME_ready_TX          = []
	RX_ready               = []
	TIME_ready_RX          = []
	### Prediction ############
	RX_prediction          = []
	TX_prediction          = []
	### Assets Risk ############
	total_Risk             = 0 #DeviceTotalRisk
	IMEI_Risk              = 0 #2
	IMSI_Risk              = 0 #3
	lat_Risk               = 0 #4
	lon_Risk               = 0 #5
	RX_Risk                = 0 #6
	TX_Risk                = 0 #7
	Wakeup_Risk            = 0 #8
	WDT_Risk               = 0 #9
	



	def reset(self):
		del self.RawDataId[:]
		del self.IMEI[:]               #2
		del self.IMSI[:]               #3
		del self.Lat[:]                #4
		del self.Lon[:]                #5
		del self.RX[:]                 #6 
		del self.TX[:]                 #7 
		del self.Wakeup[:]             #8
		del self.WDT[:]                #9
		del self.FutureTime[:]
		del self.PosixTime[:]
		del self.RelativeFutureTime[:]
		del self.RelativePosixTime[:]
		del self.TX_ready[:]
		del self.TIME_ready_TX[:]
		del self.RX_ready[:]
		del self.TIME_ready_RX[:]
		####### Prediction ######
		del self.RX_prediction[:]
		del self.TX_prediction[:]





	def __del__(self):
		#print "C027Class __del__ called"
		pass





	def __init__(self, ID):
		#print "C027Class __init__ called"
		self.ID = ID
		#url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId="+str(self.ID)+"&Action=assets"
		url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId=%s&Action=fullassets" %(str(self.ID))
		#print(url)
		response  = requests.get(url)
		if (response.status_code == 200):
			obj = json.loads(response.content)
			self.Type = str(obj["DeviceType"])
			######################### Assets Weight ######################
			for raw in obj["AssetsWeight"]:
				self.IMEI_Weight              = float(raw["IMEI"])      #1
				self.IMSI_Weight              = float(raw["IMSI"])      #2
				self.Lat_Weight               = float(raw["Latitude"])  #3
				self.Lon_Weight               = float(raw["Longitude"]) #4
				self.RX_Weight                = float(raw["RX"])        #5
				self.TX_Weight                = float(raw["TX"])        #6
				self.Wakeup_Weight            = float(raw["Wakeup"])    #7
				self.WDT_Weight               = float(raw["Watchdog"])  #8

			######################### Assets All History #################
			for j in obj["DeviceHistory"]:
				if( j["IMEI"]                     is not None and
					j["IMSI"]                     is not None and
					j["Latitude"]                 is not None and
					j["Longitude"]                is not None and
					j["RX"]                       is not None and
					j["TX"]                       is not None and
					j["Wakeup"]                   is not None and
					j["Watchdog"]                 is not None and
					j["RawDataId"]                is not None and
					j["RawDataDateCreated"]       is not None):
					self.IMEI.append(             int(j["IMEI"]))      
					self.IMSI.append(             int(j["IMSI"]))        
					self.Lat.append(              float(j["Latitude"]))    
					self.Lon.append(              float(j["Longitude"]))    
					self.RX.append(               int(j["RX"]))           
					self.TX.append(               int(j["TX"]))           
					self.Wakeup.append(           int(j["Wakeup"]))       
					self.WDT.append(              int(j["Watchdog"]))     
					self.RawDataId.append(        int(j["RawDataId"]))
					self.PosixTime.append(        [long(j["RawDataDateCreated"])] )
				else:
					#print "ERROR: C027 invalid reporting!"
					pass
			##################### Prediction Request #####################
			for p in obj["PredictionRequest"]:
				self.FutureTime.append([long(p)]) 
			##################### Time Adjustment ########################
			for i in range(len(self.PosixTime)):
				self.RelativePosixTime.append(((self.PosixTime[i][0])-(self.PosixTime[len(self.PosixTime)-1][0])))
			for v in range(len(self.FutureTime)):
				self.RelativeFutureTime.append(((self.FutureTime[v][0])-(self.FutureTime[len(self.FutureTime)-1][0])))
			##################### Standardization ########################
			self.StandardRX = preprocessing.scale(self.RX)
			self.StandardTX = preprocessing.scale(self.TX)
			self.StandardTime = preprocessing.scale(self.RelativePosixTime)  
			self.StandardFutureTime = preprocessing.scale(self.RelativeFutureTime)
			############################# Ready ##########################
			for x in range(len(self.StandardTX)-1):
				if(self.StandardTX[x+1] <= self.StandardTX[x]):
					self.TX_ready.append(self.StandardTX[x])
					self.TIME_ready_TX.append(self.StandardTime[x])
				else:
					break

			for y in range(len(self.StandardRX)-1):
				if(self.StandardRX[y+1] <= self.StandardRX[y]):
					self.RX_ready.append(self.StandardRX[y])
					self.TIME_ready_RX.append(self.StandardTime[y])
				else:
					break
			##############################################################
			self.pDataBase = self.RawDataId[0]
			#print("Creating DeviceObject done :))\n\n")
		else:
			print(response.status_code)
			print("Creating DeviceObject Failed :((\n\n")









	def RiskAnalysis(self):
		#if(abs(self.IMEI[0]-self.IMEI[1])):          self.IMEI_Risk = 4.511                                                                  
		#if(abs(self.IMSI[0]-self.IMSI[1])):          self.IMSI_Risk = 4.122                                                                 
		#if(abs(self.Wakeup[0]-self.Wakeup[1]) != 1): self.Wakeup_Risk = 4.664                                                       
		#if(abs(self.WDT[0]-self.WDT[1])):            self.WDT_Risk = 3.681                                                                      	 

		#movement = gpxpy.geo.haversine_distance(self.Lat[1], self.Lon[1], self.Lat[0], self.Lon[0])                           
		#if(movement):
		#	self.lat_Risk =  ( abs(movement-DeviceSafeMovement)*5 )/max(DeviceSafeMovement,movement)
		#	self.lon_Risk =  self.lat_Risk

		#print (abs(self.TX[0]-self.TX[1]))
		if( abs(self.TX[0]-self.TX[1]) > 900 ):                    self.TX_Risk = 4.142
		if( abs(self.RX[0]-self.RX[1]) > 900 ):                    self.RX_Risk = 4.153

		#RXTimeHistory = (np.delete(np.array(self.TIME_ready_RX), [0])).reshape(len(np.array(self.TIME_ready_RX))-1, 1) 
		#RXModel = SVR(kernel='linear',C=0.001,gamma='auto',epsilon=0.001,tol=0.01).fit(RXTimeHistory , np.delete(self.RX_ready,[0])) 
		#self.RX_prediction.append(RXModel.predict(self.TIME_ready_RX[0]))
		#RX_Delta = (abs((self.RX_ready[0] - self.RX_prediction[0][0])/(self.RX_ready[0])))*100
		#self.RX_Risk = RX_Delta/25

		#TXTimeHistory = (np.delete(np.array(self.TIME_ready_TX), [0])).reshape(len(np.array(self.TIME_ready_TX))-1, 1) 
		#TXModel = SVR(kernel='linear',C=0.001,gamma='auto',epsilon=0.001,tol=0.01).fit(TXTimeHistory , np.delete(self.TX_ready,[0])) 
		#self.TX_prediction.append(TXModel.predict(self.TIME_ready_TX[0]))
		#TX_Delta = (abs((self.TX_ready[0] - self.TX_prediction[0][0])/(self.TX_ready[0])))*100
		#self.TX_Risk = TX_Delta/25

		#print 'IMEI_Risk:       %s' % (self.IMEI_Risk)
		#print 'IMSI_Risk:       %s' % (self.IMSI_Risk)
		#print 'lat_Risk:        %s' % (self.lat_Risk)
		#print 'lon_Risk:        %s' % (self.lon_Risk)
		#print 'RX_Risk:         %s' % (self.RX_Risk)
		#print 'TX_Risk:         %s' % (self.TX_Risk)
		#print 'Wakeup_Risk:     %s' % (self.Wakeup_Risk)
		#print 'WDT_Risk:        %s' % (self.WDT_Risk)
		
		






	def TotalRiskAnalysis(self):
		noise = "%.3f" %(random.uniform(0.100, 0.199))
		self.total_Risk = max(self.IMEI_Risk*     self.IMEI_Weight,
							self.IMSI_Risk*       self.IMSI_Weight,
							self.lat_Risk*        self.Lat_Weight,
							self.lon_Risk*        self.Lon_Weight,
							self.RX_Risk*         self.RX_Weight,
							self.TX_Risk*         self.TX_Weight,
							self.Wakeup_Risk*     self.Wakeup_Weight,
							self.WDT_Risk*        self.WDT_Weight)+float(noise)
		#print 'total_Risk:      %s\n\n\n' % self.total_Risk






	def __enter__(self):
		print "C027Class __enter__ called"
		pass

	def __exit__():
		print "C027Class __exit__ called"
		pass





	def deviceDebug(self, flag):
		print("---deviceDebug---")
		if(flag):
			print 'ID:                        %s' % self.ID
			print 'Type:                      %s' % self.Type
			print 'IMEI_Weight:               %s' % self.IMEI_Weight
			print 'IMSI_Weight:               %s' % self.IMSI_Weight
			print 'Lat_Weight:                %s' % self.Lat_Weight
			print 'Lon_Weight:                %s' % self.Lon_Weight
			print 'RX_Weight:                 %s' % self.RX_Weight 
			print 'TX_Weight:                 %s' % self.TX_Weight 
			print 'Wakeup_Weight:             %s' % self.Wakeup_Weight
			print 'WDT_Weight:                %s' % self.WDT_Weight
			print 'IMEI:                      %s' % len(self.IMEI)
			print 'IMSI:                      %s' % len(self.IMSI)
			print 'Lat:                       %s' % len(self.Lat)
			print 'Lon:                       %s' % len(self.Lon)
			print 'RX:                        %s' % len(self.RX)
			print 'TX:                        %s' % len(self.TX)
			print 'Wakeup:                    %s' % len(self.Wakeup)
			print 'WDT:                       %s' % len(self.WDT)
			print 'RawDataId:                 %s' % len(self.RawDataId)
			print 'PosixTime:                 %s' % len(self.PosixTime)
			print 'StandardRX:                %s' % len(self.StandardRX)
			print 'StandardTX:                %s' % len(self.StandardTX)
			print 'StandardTime:              %s' % len(self.StandardTime)
			print 'StandardFutureTime:        %s' % len(self.StandardFutureTime)
		else:
			pass
