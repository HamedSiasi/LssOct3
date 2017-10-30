
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




#--------------------------------------------------------------------------
#                                ODIN-W2
#--------------------------------------------------------------------------

class OdinClass():
	pDataBase              = 0
	Type                   = 0
	RiskScore              = 0
	RawDataId              = []
	########### Assets ########
	RSRQ                   = [] #1 
	IMEI                   = [] #2
	RX                     = [] #6 
	TX                     = [] #7 
	Wakeup                 = [] #8
	WDT                    = [] #9
	#FutureTime             = []
	PosixTime              = []
	#RelativeFutureTime     = []
	RelativePosixTime      = []
	TX_ready               = []
	TIME_ready_TX          = []
	RX_ready               = []
	TIME_ready_RX          = []
	StandardRSRQ           = []
	######## Prediction #######
	RX_prediction          = []
	TX_prediction          = []
	RSRQ_prediction        = []
	######## Assets Risk ######
	total_Risk             = 0 #DeviceTotalRisk
	RSRQ_Risk              = 0 #1
	IMEI_Risk              = 0 #2
	RX_Risk                = 0 #6
	TX_Risk                = 0 #7
	Wakeup_Risk            = 0 #8
	WDT_Risk               = 0 #9
	



	def reset(self):
		#print("reset")
		del self.RawDataId[:]
		del self.IMEI[:]             
		del self.RSRQ[:]              
		del self.RX[:]                 
		del self.TX[:]                
		del self.Wakeup[:]            
		del self.WDT[:]                
		#del self.FutureTime[:]
		del self.PosixTime[:]
		#del self.RelativeFutureTime[:]
		del self.RelativePosixTime[:]
		del self.TX_ready[:]
		del self.TIME_ready_TX[:]
		del self.RX_ready[:]
		del self.TIME_ready_RX[:]
		###### Prediction #######
		del self.RX_prediction[:]
		del self.TX_prediction[:]
		del self.RSRQ_prediction[:]






	def __del__(self):
		#print "OdinClass __del__ called"
		pass




	def __init__(self, ID):
		#print "OdinClass __init__ called"
		self.ID = ID
		#url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId="+str(self.ID)+"&Action=assets"
		url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId=%s&Action=fullassets" %(str(self.ID))
		#print(url)
		response  = requests.get(url,timeout=5)
		if (response.status_code == 200):
			obj = json.loads(response.content)
			self.Type = str(obj["DeviceType"])

			######################### Assets Weight ########################
			for raw in obj["AssetsWeight"]:
				self.RSRQ_Weight = float(raw["RSRQ"]) 
				self.IMEI_Weight              = float(raw["IMEI"]) 
				self.RX_Weight                = float(raw["RX"]) 
				self.TX_Weight                = float(raw["TX"]) 
				self.Wakeup_Weight            = float(raw["Wakeup"]) 
				self.WDT_Weight               = float(raw["Watchdog"])

			######################### Assets All History ###################
			for j in obj["DeviceHistory"]:
				if( j["RSRQ"]                         is not None and
					j["IMEI"]                         is not None and
					j["RX"]                           is not None and
					j["TX"]                           is not None and
					j["Wakeup"]                       is not None and
					j["Watchdog"]                     is not None and
					j["RawDataId"]                    is not None and
					j["RawDataDateCreated"]           is not None):
					self.RSRQ.append(              float(j["RSRQ"])) 
					self.IMEI.append(              str(j["IMEI"])) 
					self.RX.append(                int(j["RX"])) 
					self.TX.append(                int(j["TX"])) 
					self.Wakeup.append(            int(j["Wakeup"])) 
					self.WDT.append(               int(j["Watchdog"])) 	
					self.RawDataId.append(         int(j["RawDataId"])) 
					self.PosixTime.append(         [long(j["RawDataDateCreated"])]) 
				else:
					print "ERROR: Odin invalid reporting!"
					pass
			##################### Prediction Request #####################
			#for p in obj["PredictionRequest"]:
			#	self.FutureTime.append([long(p)]) 
			##################### Time Adjustment ########################
			for i in range(len(self.PosixTime)):
				self.RelativePosixTime.append(((self.PosixTime[i][0])-(self.PosixTime[len(self.PosixTime)-1][0])))
			#for v in range(len(self.FutureTime)):
			#	self.RelativeFutureTime.append(((self.FutureTime[v][0])-(self.FutureTime[len(self.FutureTime)-1][0])))
			##################### Standardization ########################
			self.StandardTime = preprocessing.scale(self.RelativePosixTime)  
			#self.StandardFutureTime = preprocessing.scale(self.RelativeFutureTime)
			############################# Ready ##########################
			for x in range(len(self.TX)-1):
				if(True):#self.TX[x+1] <= self.TX[x]):
					self.TX_ready.append(self.TX[x])
					self.TIME_ready_TX.append(self.StandardTime[x])
				else:
					break


			for y in range(len(self.RX)-1):
				if(True):#self.RX[y+1] <= self.RX[y]):
					self.RX_ready.append(self.RX[y])
					self.TIME_ready_RX.append(self.StandardTime[y])
				else:
					break
			##############################################################
			#print(self.RX)
			#print(self.TX)
			#print(len(self.RX_ready))
			#print(len(self.TX_ready))
			#print(len(self.TIME_ready_TX))
			#print(len(self.TIME_ready_RX))
			self.StandardRX = preprocessing.scale(self.RX_ready)
			self.StandardTX = preprocessing.scale(self.TX_ready)
			self.StandardRSRQ = preprocessing.scale(self.RSRQ)
			self.pDataBase = self.RawDataId[0]
			#print("Creating DeviceObject Done :)) \n\n")
		else:
			print(response.status_code)
			print("Creating DeviceObject Failed :(( \n\n")







	def RiskAnalysis(self):
		
		noise = "%.3f" %(random.uniform(0.001, 0.199))

		RSRQTimeHistory = (np.delete(np.array(self.StandardTime), [0])).reshape(len(np.array(self.StandardTime))-1, 1) 
		RSRQModel = SVR(kernel='linear',C=0.01,gamma='auto',epsilon=0.01).fit(RSRQTimeHistory , np.delete(self.StandardRSRQ,[0])) 
		self.RSRQ_prediction.append(RSRQModel.predict(self.StandardRSRQ[0]))
		rsrqnoise = (abs((self.StandardRSRQ[0] - self.RSRQ_prediction[0][0])/(self.StandardRSRQ[0])))/10
		self.RSRQ_Risk =(((abs(self.RSRQ[0]) - 20)*5)/170) + float(rsrqnoise) 



		if(self.IMEI[0] != self.IMEI[1]):       self.IMEI_Risk = 4.822   +float(noise)                                                              
		if(self.Wakeup[0]-self.Wakeup[1] != 1): self.Wakeup_Risk = 4.664 +float(noise)                                                     
		if(self.WDT[0]-self.WDT[1] != 0):       self.WDT_Risk = 3.881    +float(noise) 

		if( self.TX[0]-self.TX[1] >= 500 ):                    
			self.TX_Risk = 4.472+float(noise) 
		else:
			TXTimeHistory = (np.delete(np.array(self.TIME_ready_TX), [0])).reshape(len(np.array(self.TIME_ready_TX))-1, 1) 
			TXModel = SVR(kernel='linear',C=0.01,gamma='auto',epsilon=0.01).fit(TXTimeHistory , np.delete(self.StandardTX,[0])) 
			self.TX_prediction.append(TXModel.predict(self.TIME_ready_TX[0]))
			self.TX_Risk = abs( (self.StandardTX[0] - self.TX_prediction[0][0])/(self.StandardTX[0]) ) 


		if( self.RX[0]-self.RX[1] >= 500 ):                    
			self.RX_Risk = 4.153+float(noise) 
		else:
			RXTimeHistory = (np.delete(np.array(self.TIME_ready_RX), [0])).reshape(len(np.array(self.TIME_ready_RX))-1, 1) 
			RXModel = SVR(kernel='linear',C=0.01,gamma='auto',epsilon=0.01).fit(RXTimeHistory , np.delete(self.StandardRX,[0])) 
			self.RX_prediction.append(RXModel.predict(self.TIME_ready_RX[0]))
			self.RX_Risk  = abs((self.StandardRX[0] - self.RX_prediction[0][0])/(self.StandardRX[0]))

		#print 'RSRQ_Risk:   %s' % (self.RSRQ_Risk)
		#print 'MAC_Risk:    %s' % (self.IMEI_Risk)
		#print 'RX_Risk:     %s' % (self.RX_Risk)
		#print 'TX_Risk:     %s' % (self.TX_Risk)
		#print 'Wakeup_Risk: %s' % (self.Wakeup_Risk)
		#print 'WDT_Risk:    %s' % (self.WDT_Risk)
		
		








	def TotalRiskAnalysis(self):
		self.total_Risk = max(self.RSRQ_Risk*              self.RSRQ_Weight,
							self.IMEI_Risk*                self.IMEI_Weight,
							self.RX_Risk*                  self.RX_Weight,
							self.TX_Risk*                  self.TX_Weight,
							self.Wakeup_Risk*              self.Wakeup_Weight,
							self.WDT_Risk*                 self.WDT_Weight)
		#print 'total_Risk:   %s\n\n\n' % self.total_Risk







	def __enter__(self):
		print "OdinClass __enter__ called"
		pass



	def __exit__(self):
		print "OdinClass __exit__ called"
		pass






	def deviceDebug(self, flag):
		if(flag):
			print 'ID:                        %s' % self.ID
			print 'Type:                      %s' % self.Type
			print 'RSRQ_Weight:               %s' % self.RSRQ_Weight
			print 'IMEI_Weight:               %s' % self.IMEI_Weight
			print 'RX_Weight:                 %s' % self.RX_Weight 
			print 'TX_Weight:                 %s' % self.TX_Weight 
			print 'Wakeup_Weight:             %s' % self.Wakeup_Weight
			print 'WDT_Weight:                %s' % self.WDT_Weight
			print 'RSRQ:                      %s' % len(self.RSRQ)
			print 'IMEI:                      %s' % len(self.IMEI)
			print 'RX:                        %s' % len(self.RX)
			print 'TX:                        %s' % len(self.TX)
			print 'Wakeup:                    %s' % len(self.Wakeup)
			print 'WDT:                       %s' % len(self.WDT)
			print 'RawDataId:                 %s' % len(self.RawDataId)
			print 'PosixTime:                 %s' % len(self.PosixTime)
			print 'StandardRX:                %s' % len(self.StandardRX)
			print 'StandardTX:                %s' % len(self.StandardTX)
			print 'StandardTime:              %s' % len(self.StandardTime)
			#print 'StandardFutureTime:        %s' % len(self.StandardFutureTime)
		else:
			pass
