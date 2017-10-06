

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
#                                C030
#--------------------------------------------------------------------------

class C030Class():
	pDataBase              = 0
	Type                   = 0
	RiskScore              = 0
	########### Assets ########
	RSRQ                   = [] #1 
	IMEI                   = [] #2
	IMSI                   = [] #3
	Lat                    = [] #4
	Lon                    = [] #5
	RX                     = [] #6 
	TX                     = [] #7 
	Wakeup                 = [] #8
	WDT                    = [] #9
	BatVol                 = [] #10 
	BatChipTemp            = [] #11 
	BatAmp                 = [] #12
	BatRemCap              = [] #13 
	BatRemPer              = [] #14 
	CellIdChangeCount      = [] #15 
	Jam                    = [] #16
	SleepCont              = [] #17
	CoreTemp               = [] #18 
	EnvTemp                = [] #19 
	HeapStatus             = [] #20
	RawDataId              = []
	FutureTime             = []
	PosixTime              = []
	RelativeFutureTime     = []
	RelativePosixTime      = []
	TX_ready               = []
	TIME_ready_TX          = []
	RX_ready               = []
	TIME_ready_RX          = []
	### Prediction ############
	RX_prediction          = []
	TX_prediction          = []
	### Assets Risk ############
	total_Risk             = 0 #DeviceTotalRisk
	RSRQ_Risk              = 0 #1
	IMEI_Risk              = 0 #2
	IMSI_Risk              = 0 #3
	lat_Risk               = 0 #4
	lon_Risk               = 0 #5
	RX_Risk                = 0 #6
	TX_Risk                = 0 #7
	Wakeup_Risk            = 0 #8
	WDT_Risk               = 0 #9
	BatVol_Risk            = 0 #10
	BatChipTemp_Risk       = 0 #11
	BatAmp_Risk            = 0 #12
	BatRemCap_Risk         = 0 #13
	BatRemPer_Risk         = 0 #14
	CellIdChangeCount_Risk = 0 #15
	Jam_Risk               = 0 #16
	SleepCont_Risk         = 0 #17
	CoreTemp_Risk          = 0 #18
	EnvTemp_Risk           = 0 #19
	HeapStatus_Risk        = 0 #20




	def reset(self):
		del self.RawDataId[:]
		del self.RSRQ[:]               #1 
		del self.IMEI[:]               #2
		del self.IMSI[:]               #3
		del self.Lat[:]                #4
		del self.Lon[:]                #5
		del self.RX[:]                 #6 
		del self.TX[:]                 #7 
		del self.Wakeup[:]             #8
		del self.WDT[:]                #9
		del self.BatVol[:]             #10 
		del self.BatChipTemp[:]        #11 
		del self.BatAmp[:]             #12
		del self.BatRemCap[:]          #13 
		del self.BatRemPer[:]          #14 
		del self.CellIdChangeCount[:]  #15 
		del self.Jam[:]                #16
		del self.SleepCont[:]          #17
		del self.CoreTemp[:]           #18 
		del self.EnvTemp[:]            #19 
		del self.HeapStatus[:]         #20
		del self.RawDataId[:]
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
		#print "C030Class __del__ called"
		pass






	def __init__(self, ID):
		#print "C030Class __init__ called"
		self.ID = ID
		#url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId="+str(self.ID)+"&Action=assets"
		url = "http://151.9.34.99/webservice/assetviewer.php?DeviceId="+str(self.ID)+"&Action=fullassets"
		response  = requests.get(url)
		if (response.status_code == 200):
			obj = json.loads(response.content)
			self.Type = str(obj["DeviceType"])
			######################### Assets Weight #########################
			for raw in obj["AssetsWeight"]:
				self.RSRQ_Weight              = float(raw["RSRQ"])                         #1
				self.IMEI_Weight              = float(raw["IMEI"])                         #2
				self.IMSI_Weight              = float(raw["IMSI"])                         #3
				self.Lat_Weight               = float(raw["Latitude"])                     #4
				self.Lon_Weight               = float(raw["Longitude"])                    #5
				self.RX_Weight                = float(raw["RX"])                           #6
				self.TX_Weight                = float(raw["TX"])                           #7
				self.Wakeup_Weight            = float(raw["Wakeup"])                       #8
				self.WDT_Weight               = float(raw["Watchdog"])                     #9
				self.BatVol_Weight            = float(raw["Battery Voltage"])              #10
				self.BatChipTemp_Weight       = float(raw["Battery Chip Temperature"])     #11
				self.BatAmp_Weight            = float(raw["Current Drawn From Battery"])   #12
				self.BatRemCap_Weight         = float(raw["Remaining Battery Capacity"])   #13
				self.BatRemPer_Weight         = float(raw["Remaining Battery Percentage"]) #14
				self.CellIdChangeCount_Weight = float(raw["Cell Id Change Counter"])       #15
				self.Jam_Weight               = float(raw["Jamming Detection"])            #16
				self.SleepCont_Weight         = float(raw["Sleep Counter"])                #17
				self.CoreTemp_Weight          = float(raw["Core Temperature"])             #18
				self.EnvTemp_Weight           = float(raw["Environment Temperature"])      #19
				self.HeapStatus_Weight        = float(raw["Heap Status"])                  #20


			######################### Assets All History #####################
			for j in obj["DeviceHistory"]:
				if( j["RSRQ"]                         is not None and 
					j["IMEI"]                         is not None and
					j["IMSI"]                         is not None and
					j["Latitude"]                     is not None and
					j["Longitude"]                    is not None and
					j["RX"]                           is not None and
					j["TX"]                           is not None and
					j["Wakeup"]                       is not None and
					j["Watchdog"]                     is not None and
					j["Battery Voltage"]              is not None and
					j["Battery Chip Temperature"]     is not None and
					j["Current Drawn From Battery"]   is not None and
					j["Remaining Battery Capacity"]   is not None and
					j["Remaining Battery Percentage"] is not None and
					j["Cell Id Change Counter"]       is not None and
					j["Jamming Detection"]            is not None and
					j["Sleep Counter"]                is not None and
					j["Core Temperature"]             is not None and
					j["Environment Temperature"]      is not None and
					j["Heap Status"]                  is not None and
					j["RawDataId"]                    is not None and
					j["RawDataDateCreated"]           is not None):

					self.RSRQ.append(              float(j["RSRQ"]))                         #1
					self.IMEI.append(              int(j["IMEI"]))                           #2
					self.IMSI.append(              int(j["IMSI"]))                           #3
					self.Lat.append(               float(j["Latitude"]))                     #4 
					self.Lon.append(               float(j["Longitude"]))                    #5
					self.RX.append(                int(j["RX"]))                             #6
					self.TX.append(                int(j["TX"]))                             #7 
					self.Wakeup.append(            int(j["Wakeup"]))                         #8
					self.WDT.append(               int(j["Watchdog"]))                       #9
					self.BatVol.append(            float(j["Battery Voltage"]))              #10
					self.BatChipTemp.append(       float(j["Battery Chip Temperature"]))     #11 
					self.BatAmp.append(            float(j["Current Drawn From Battery"]))   #12
					self.BatRemCap.append(         float(j["Remaining Battery Capacity"]))   #13
					self.BatRemPer.append(         float(j["Remaining Battery Percentage"])) #14
					self.CellIdChangeCount.append( int(j["Cell Id Change Counter"]))         #15
					self.Jam.append(               int(j["Jamming Detection"]))              #16
					self.SleepCont.append(         int(j["Sleep Counter"]))                  #17
					self.CoreTemp.append(          float(j["Core Temperature"]))             #18
					self.EnvTemp.append(           float(j["Environment Temperature"]))      #19 
					self.HeapStatus.append(        int(j["Heap Status"]))                    #20
					self.RawDataId.append(         int(j["RawDataId"]))
					self.PosixTime.append(         [long(j["RawDataDateCreated"])])
				else:
					#print "ERROR: C030 invalid reporting!"
					pass
			#for

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
		if(self.RSRQ[0]-self.RSRQ[1]):
			self.RSRQ_Risk = (abs(self.RSRQ[0]-self.RSRQ[1])*5.4 ) / max(abs(self.RSRQ[0]), abs(self.RSRQ[1]))  
		#if(self.BatVol[0]-self.BatVol[1]):
		#	self.BatVol_Risk = (abs(self.BatVol[0]-self.BatVol[1])*5 ) / max(abs(self.BatVol[0]), abs(self.BatVol[1]))  
		#if(self.BatChipTemp[0]-self.BatChipTemp[1]):
		#	self.BatChipTemp_Risk = (abs(self.BatChipTemp[0]-self.BatChipTemp[1])*5 )/ max(abs(self.BatChipTemp[0]),abs(self.BatChipTemp[1])) 
		#if(self.BatAmp[0]-self.BatAmp[1]):
		#	self.BatAmp_Risk = (abs(self.BatAmp[0]-self.BatAmp[1])*5 ) / max(abs(self.BatAmp[0]), abs(self.BatAmp[1])) 
		#if(self.BatRemCap[0]-self.BatRemCap[1]):
		#	self.BatRemCap_Risk = (abs(self.BatRemCap[0]-self.BatRemCap[1])*5 ) / max(abs(self.BatRemCap[0]),  abs(self.BatRemCap[1]))   
		#if(self.BatRemPer[0]-self.BatRemPer[1]):
		#	self.BatRemPer_Risk = (abs(self.BatRemPer[0]-self.BatRemPer[1])*5 ) / max(abs(self.BatRemPer[0]),  abs(self.BatRemPer[1]))   
		#if(self.CoreTemp[0]-self.CoreTemp[1]):
		#	self.CoreTemp_Risk = (abs(self.CoreTemp[0]-self.CoreTemp[1])*5 ) / max(abs(self.CoreTemp[0]),   abs(self.CoreTemp[1])) 
		#if(self.EnvTemp[0]-self.EnvTemp[1]):
		#	self.EnvTemp_Risk = (abs(self.EnvTemp[0]-self.EnvTemp[1])*5 ) / max(abs(self.EnvTemp[0]),    abs(self.EnvTemp[1]))   
		#if(self.HeapStatus[0]-self.HeapStatus[1]):
		#	self.HeapStatus_Risk = (abs(self.HeapStatus[0]-self.HeapStatus[1])*5 ) / max(abs(self.HeapStatus[0]), abs(self.HeapStatus[1]))   

		#if(abs(self.IMEI[0]-self.IMEI[1])):                              self.IMEI_Risk = 4.511                                                                  
		#if(abs(self.IMSI[0]-self.IMSI[1])):                              self.IMSI_Risk = 4.122                                                                 
		#if(abs(self.Wakeup[0]-self.Wakeup[1]) != 1):                     self.Wakeup_Risk = 4.664                                                       
		#if(abs(self.WDT[0]-self.WDT[1])):                                self.WDT_Risk = 3.881                                                                     	
		#if(abs(self.CellIdChangeCount[0]-self.CellIdChangeCount[1])>=1): self.CellIdChangeCount_Risk = 0                        
		#if(abs(self.Jam[0]-self.Jam[1])):                                self.Jam_Risk = 5                                                                     
		#if(abs(self.SleepCont[0]-self.SleepCont[1])):                    self.SleepCont_Risk = 5                                                   

		#movement = gpxpy.geo.haversine_distance(self.Lat[1], self.Lon[1], self.Lat[0], self.Lon[0])                           
		#if(movement):
		#	self.lat_Risk =  ( abs(movement-DeviceSafeMovement)*5 )/max(DeviceSafeMovement,movement)
		#	self.lon_Risk =  self.lat_Risk

		#print self.TX[0]
		#print self.TX[1]
		if( abs(self.TX[0]-self.TX[1])> 900 ):                    self.SleepCont_Risk = 4.153
		if( abs(self.RX[0]-self.RX[1])> 900 ):                    self.SleepCont_Risk = 4.042

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

		#print 'RSRQ_Risk:              %s' % (self.RSRQ_Risk)
		#print 'IMEI_Risk:              %s' % (self.IMEI_Risk)
		#print 'IMSI_Risk:              %s' % (self.IMSI_Risk)
		#print 'lat_Risk:               %s' % (self.lat_Risk)
		#print 'lon_Risk:               %s' % (self.lon_Risk)
		#print 'RX_Risk:                %s' % (self.RX_Risk)
		#print 'TX_Risk:                %s' % (self.TX_Risk)
		#print 'Wakeup_Risk:            %s' % (self.Wakeup_Risk)
		#print 'WDT_Risk:               %s' % (self.WDT_Risk)
		#print 'BatVol_Risk:            %s' % (self.BatVol_Risk)
		#print 'BatChipTemp_Risk:       %s' % (self.BatChipTemp_Risk)
		#print 'BatAmp_Risk:            %s' % (self.BatAmp_Risk)
		#print 'BatRemCap_Risk:         %s' % (self.BatRemCap_Risk)
		#print 'BatRemPer_Risk:         %s' % (self.BatRemPer_Risk)
		#print 'CellIdChangeCount_Risk: %s' % (self.CellIdChangeCount_Risk)
		#print 'Jam_Risk:               %s' % (self.Jam_Risk)
		#print 'SleepCont_Risk:         %s' % (self.SleepCont_Risk)
		#print 'CoreTemp_Risk:          %s' % (self.CoreTemp_Risk)
		#print 'EnvTemp_Risk:           %s' % (self.EnvTemp_Risk)
		#print 'HeapStatus_Risk:        %s' % (self.HeapStatus_Risk)








	def TotalRiskAnalysis(self):
		noise = "%.3f" %(random.uniform(0.100, 0.199))
		self.total_Risk = max(self.RSRQ_Risk*            self.RSRQ_Weight,
							self.IMEI_Risk*              self.IMEI_Weight,
							self.IMSI_Risk*              self.IMSI_Weight,
							self.lat_Risk*               self.Lat_Weight,
							self.lon_Risk*               self.Lon_Weight,
							self.RX_Risk*                self.RX_Weight,
							self.TX_Risk*                self.TX_Weight,
							self.Wakeup_Risk*            self.Wakeup_Weight,
							self.WDT_Risk*               self.WDT_Weight,
							self.BatVol_Risk*            self.BatVol_Weight,
							self.BatChipTemp_Risk*       self.BatChipTemp_Weight ,
							self.BatAmp_Risk*            self.BatAmp_Weight,
							self.BatRemCap_Risk*         self.BatRemCap_Weight,
							self.BatRemPer_Risk*         self.BatRemPer_Weight,
							self.CellIdChangeCount_Risk* self.CellIdChangeCount_Weight,
							self.Jam_Risk*               self.Jam_Weight,
							self.SleepCont_Risk*         self.SleepCont_Weight,
							self.CoreTemp_Risk*          self.CoreTemp_Weight,
							self.EnvTemp_Risk*           self.EnvTemp_Weight,
							self.HeapStatus_Risk*        self.HeapStatus_Weight)+float(noise)
		#print 'total_Risk:             %s\n\n\n'   % self.total_Risk










	def __enter__(self):
		print "C030Class __enter__ called"
		pass





	def __exit__(self):
		print "C030Class __exit__ called"
		pass









	def deviceDebug(self, flag):
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
			print 'RSRQ_Weight:               %s' % self.RSRQ_Weight
			print 'BatVol_Weigh:              %s' % self.BatVol_Weight
			print 'BatChipTemp_Weight:        %s' % self.BatChipTemp_Weight
			print 'BatAmp_Weight:             %s' % self.BatAmp_Weight
			print 'BatRemCap_Weight:          %s' % self.BatRemCap_Weight
			print 'BatRemPer_Weight:          %s' % self.BatRemPer_Weight
			print 'CellIdChangeCount_Weight:  %s' % self.CellIdChangeCount_Weight
			print 'Jam_Weight:                %s' % self.Jam_Weight
			print 'SleepCont_Weight:          %s' % self.SleepCont_Weight
			print 'CoreTemp_Weight:           %s' % self.CoreTemp_Weight
			print 'EnvTemp_Weight:            %s' % self.EnvTemp_Weight
			print 'HeapStatus_Weight:         %s' % self.HeapStatus_Weight
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
			print 'RSRQ:                      %s' % len(self.RSRQ)
			print 'BatVol:                    %s' % len(self.BatVol)
			print 'BatChipTemp:               %s' % len(self.BatChipTemp)
			print 'BatAmp:                    %s' % len(self.BatAmp)
			print 'BatRemCap:                 %s' % len(self.BatRemCap)
			print 'BatRemPer:                 %s' % len(self.BatRemPer)
			print 'CellIdChangeCount:         %s' % len(self.CellIdChangeCount)
			print 'Jam:                       %s' % len(self.Jam)
			print 'SleepCont:                 %s' % len(self.SleepCont)
			print 'CoreTemp:                  %s' % len(self.CoreTemp)
			print 'EnvTemp:                   %s' % len(self.EnvTemp)
			print 'HeapStatus:                %s' % len(self.HeapStatus)
			print 'FutureTime:                %s' % len(self.FutureTime)
			print 'StandardFutureTime:        %s' % len(self.StandardFutureTime)
			print 'RelativeFutureTime:        %s' % len(self.RelativeFutureTime)
			print 'RelativePosixTime:         %s' % len(self.RelativePosixTime)
			print 'TX_ready:                  %s' % len(self.TX_ready)
			print 'TIME_ready_TX:             %s' % len(self.TIME_ready_TX)
			print 'RX_ready:                  %s' % len(self.RX_ready)
			print 'TIME_ready_RX:             %s' % len(self.TIME_ready_RX)
			print 'RX_prediction:             %s' % len(self.RX_prediction)
			print 'TX_prediction:             %s' % len(self.TX_prediction)
		else:
			pass
