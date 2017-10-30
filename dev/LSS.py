
from C027 import *
from C030 import *
from Odin import *
import json

#--------------------------------------------------------------------------
#                          LSS Configuration
#--------------------------------------------------------------------------
#DeviceSafeMovement = 500
debuging = False
gDevice  = None
gDeviceID = ['8']
gDeviceType = ['c030']
#dict = {}
dict = {'8':0} #demo


#--------------------------------------------------------------------------
#                    Lifetime Security Service
#--------------------------------------------------------------------------
def isNewReport(deviceID):
	if (dict[deviceID] != gDevice.RawDataId[0]):
		dict[deviceID] = gDevice.RawDataId[0]
		return True
	return False


def elapsedTime():
	global gDevice
	now = datetime.datetime.fromtimestamp(time.time())
	last = datetime.datetime.fromtimestamp(gDevice.PosixTime[0][0])
	#print ("current time:   %s" %now)
	#print ("last report:    %s" %last)
	elapsed = time.time() - gDevice.PosixTime[0][0]
	return "%.2f" %(abs(elapsed))




def postDB(rawDataId,riskScore,
	RSRQ = "Null", 
	IMEI = "Null",
	IMSI = "Null", 
	Lat = "Null",
	Lon = "Null",
	RX = "Null",
	TX = "Null",
	Wakeup = "Null",
	WDT = "Null",
	BatVol= "Null", 
	BatChipTemp = "Null",
	BatAmp = "Null", 
	BatRemCap = "Null",
	BatRemPer = "Null",
	CellIdChangeCount = "Null",
	Jam = "Null",
	SleepCont = "Null",
	CoreTemp = "Null",
	EnvTemp = "Null",
	HeapStatus = "Null"):

	print("rawDataId:               %s" %rawDataId)
	print("riskScore:               %s" %riskScore)
	print("(1)  RSRQ:               %s" %RSRQ)
	print("(2)  IMEI:               %s" %IMEI)
	print("(3)  IMSI:               %s" %IMSI)
	print("(4)  Lat:                %s" %Lat)
	print("(5)  Lon:                %s" %Lon)
	print("(6)  RX:                 %s" %RX)
	print("(7)  TX:                 %s" %TX)
	print("(8)  Wakeup:             %s" %Wakeup)
	print("(9)  WDT:                %s" %WDT)
	print("(10) BatVol:             %s" %BatVol)
	print("(11) BatChipTemp:        %s" %BatChipTemp)
	print("(12) BatAmp:             %s" %BatAmp)
	print("(13) BatRemCap:          %s" %BatRemCap)
	print("(14) BatRemPer:          %s" %BatRemPer)
	print("(15) CellIdChangeCount:  %s" %CellIdChangeCount)
	print("(16) Jam:                %s" %Jam)
	print("(17) SleepCont:          %s" %SleepCont)
	print("(18) CoreTemp:           %s" %CoreTemp)
	print("(19) EnvTemp:            %s" %EnvTemp)
	print("(20) HeapStatus:         %s" %HeapStatus)
	data = {'a1' :str(RSRQ),
			'a2' :str(IMEI),
			'a3' :str(IMSI),
			'a4' :str(Lat),
			'a5' :str(Lon),
			'a6' :str(RX),
			'a7' :str(TX),
			'a8' :str(Wakeup),
			'a9' :str(WDT),
			'a10':str(BatVol),
			'a11':str(BatChipTemp),
			'a12':str(BatAmp),
			'a13':str(BatRemCap),
			'a14':str(BatRemPer),
			'a15':str(CellIdChangeCount),
			'a16':str(Jam),
			'a17':str(SleepCont),
			'a18':str(CoreTemp),
			'a19':str(EnvTemp),
			'a20':str(HeapStatus)}
	try:
		response  = requests.post("http://151.9.34.99/webservice/svmhandler.php?Action=fullrisk", 
			data={'RawDataId': rawDataId,
			      'RiskScore': riskScore,
			      'FullRiskScore':json.dumps(data) },timeout=5)
		if (response.text == "RC 000"):
			#print "postDB OK"
			pass
		else:
			print (response.text)
			print "postDB ERROR"
	except Exception, ee:
		print(str(ee))
	finally:
		time.sleep(0.1)




def postStatus(deviceID , status):
	try:
		response  = requests.post("http://151.9.34.99/webservice/svmhandler.php?Action=status", data={'DeviceId': deviceID, 'DeviceStatus': status}, timeout=5)
		if (response.text == "RC 000"):
			#print "postStatus OK"
			pass
		else:
			print (response.text)
			print "postStatus ERROR"
	except Exception, ee:
		print(str(ee))
	finally:
		time.sleep(0.1)





def securityAgent():
	global gDeviceID, gDeviceType, gDevice
	for i in range(len(gDeviceID)):
		try:
			if  (gDeviceType[i] == "c027"):gDevice = C027Class(gDeviceID[i])
			elif(gDeviceType[i] == "c030"):gDevice = C030Class(gDeviceID[i])
			elif(gDeviceType[i] == "odin"):gDevice = OdinClass(gDeviceID[i])
			else:
				print "ERROR! Unknown DeviceType !!!"
				break
			#----------------------------------------------------------------------------------------------------------
			#                    Checking Device Object Status
			#----------------------------------------------------------------------------------------------------------
			if(gDevice == None):
				print "ERROR! gDevice"
				break
			if(gDevice.pDataBase == 0):
				print "ERROR! pDataBase"
				break
			#gDevice.deviceDebug(True)

			elapsed = elapsedTime()
			if(elapsed is None):print("Elapsed time ERROR !!!")
			if(float(elapsed)>150):
			##---------------------------------------------------------------------------------------------------------
			##                            DEVICE_OFFLINE
			##---------------------------------------------------------------------------------------------------------
				postStatus(gDeviceID[i], "0")   # DB OFFline
				postDB(gDevice.pDataBase, 4.99) # DB DeviceTotalRisk
				print "R:(%s) ID:(%s %s) T:(%s) (OFFLINE)" %(gDevice.pDataBase, gDeviceID[i], gDeviceType[i], elapsed)
			else:
			##----------------------------------------------------------------------------------------------------------
			##                            DEVICE_ONLINE
			##----------------------------------------------------------------------------------------------------------
				postStatus(gDeviceID[i], "1") # DB ONline
				if(isNewReport(gDeviceID[i])):
					gDevice.RiskAnalysis()
					gDevice.TotalRiskAnalysis()
					if  (gDeviceType[i] == "c027"):postDB(gDevice.pDataBase,gDevice.total_Risk,    "Null",             gDevice.IMEI_Risk,  gDevice.IMSI_Risk,  gDevice.lat_Risk,  gDevice.lon_Risk,  gDevice.RX_Risk,  gDevice.TX_Risk,  gDevice.Wakeup_Risk,  gDevice.WDT_Risk,  "Null",                "Null",                    "Null",               "Null",                  "Null",                  "Null",                          "Null",             "Null",                  "Null",                 "Null",                "Null") #C027#
					elif(gDeviceType[i] == "c030"):postDB(gDevice.pDataBase,gDevice.total_Risk,    gDevice.RSRQ_Risk,  gDevice.IMEI_Risk,  gDevice.IMSI_Risk,  gDevice.lat_Risk,  gDevice.lon_Risk,  gDevice.RX_Risk,  gDevice.TX_Risk,  gDevice.Wakeup_Risk,  gDevice.WDT_Risk,  gDevice.BatVol_Risk,  gDevice.BatChipTemp_Risk,  gDevice.BatAmp_Risk,  gDevice.BatRemCap_Risk,  gDevice.BatRemPer_Risk,  gDevice.CellIdChangeCount_Risk,  gDevice.Jam_Risk,   gDevice.SleepCont_Risk,  gDevice.CoreTemp_Risk,  gDevice.EnvTemp_Risk,  gDevice.HeapStatus_Risk)
					elif(gDeviceType[i] == "odin"):postDB(gDevice.pDataBase,gDevice.total_Risk,    gDevice.RSRQ_Risk,  gDevice.IMEI_Risk,  "Null",             "Null",            "Null",            gDevice.RX_Risk,  gDevice.TX_Risk,  gDevice.Wakeup_Risk,  gDevice.WDT_Risk,  "Null",                "Null",                    "Null",               "Null",                  "Null",                  "Null",                          "Null",             "Null",                  "Null",                 "Null",                "Null") #Odin#
					else:log.error('Unknown DeviceType !!!')
					print "R:(%s) ID:(%s %s) T:(%s) (ONLINE) NewTotalRiskScore:(%s)" %(gDevice.pDataBase, gDeviceID[i], gDeviceType[i], elapsed, gDevice.total_Risk)
				else:
					print "R:(%s) ID:(%s %s) T:(%s) (ONLINE)"  %(gDevice.pDataBase, gDeviceID[i], gDeviceType[i], elapsed)
					pass

		except Exception, syserr:
			print(str(syserr))
		finally:
			if(gDevice != None):
				gDevice.reset()
			time.sleep(0.5)





def deviceListAgent():
	global gDeviceID, gDeviceType
	try:
		del gDeviceID[:]
		del gDeviceType[:]
		url = "http://151.9.34.99/webservice/assetviewer.php?Action=deviceList"
		#print(url)
		response  = requests.get(url)
		if (response.status_code == 200):
			obj = json.loads(response.content)
			for raw in obj["Devices"]:
				gDeviceID.append(str(raw["DeviceId"]))
				gDeviceType.append(str(raw["DeviceType"]))
				dict [str(raw["DeviceId"])] = 0
			if(len(gDeviceID) != len(gDeviceType)): print "ERROR !!! DeviceList API"
			if(len(gDeviceID) == 0):                print "ERROR !!! DeviceList API gDeviceID"
			if(len(gDeviceType) == 0):              print "ERROR !!! DeviceList API gDeviceType"
			#print(gDeviceID)
			#print(gDeviceType)
		else:
			print(response.status_code)
			print("deviceList API Failed :((\n\n")
	except Exception, syserr:
		print(str(syserr))
	finally:
		time.sleep(0.5)






def main():
	#warnings.filterwarnings("ignore", category=DeprecationWarning)
	while True:
		try:
			#deviceListAgent() #productionCode
			securityAgent()
		except Exception as e:
			print str(e)
		finally:
			time.sleep(0.1)



if __name__ == "__main__":
    main()
