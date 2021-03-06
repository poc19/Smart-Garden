#!/usr/bin/env python
import Adafruit_GPIO.SPI #software SPI import
import Adafruit_MCP3008 #for the Digital to Analog converter
import Adafruit_DHT #for the temp sensor
import RPi.GPIO as GPIO #for the digital pins
import sys, ast, datetime, os ##basic imports, nothing cool here
import json # for sending data
import urllib2 #for php calls
import Config 
import simplejson
import time
myConf= Config.Config() # load configuration file

def configCheck():
	url = "http://jchavis.hopto.org:49180/ConfigCheck.php?user="+ myConf.getUser()
	url += "&password="+ myConf.getPassword() + "&localDate=" 
	url += myConf.getUpdateDate().replace(" ", "%20")
	#url += "2016-10-17 13:14:15".replace(" ", "%20")

	print('calling ' + url)
	resp = urllib2.urlopen(urllib2.Request(url))#make PHP call
	#print(resp.read())
	json_data = json.load(resp)
	print(json_data)

	if(json_data):
		print("New JSON found, saving...")
		with open("config.json", "w") as f:
			f.write(json_data)

		global myConf
		myConf = Config.Config()

	else:
		print("no new data")

configCheck()
#DHT declerations
sensor = Adafruit_DHT.DHT11 #set sensor type, use DHT22 or DHT11
#pins = [19, 17, 6, 22] - we will reads these in later from sensors.lst

#connection variables
timeStamp = str(datetime.datetime.now()).split('.')[0] #timestamp
urlBase = 'http://jchavis.hopto.org:49180/SendData.php?' #base url

# Software SPI configuration: various pins
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI) #combine MCP3008 pins
#channel = 0 #MCP3008 channel - this will be read from channels.lst

#ready digital pin
GPIO.setmode(GPIO.BCM)#set board type (BCM or BOARD)
#GPIO.setup(12,GPIO.IN)#mark pin as input

#read in log in info
userName = myConf.getUser() #read in user name
password = myConf.getPassword() #read in password
urlBase += ('user=' + userName + '&password=' + password)#append url info

#making arrays to hold the readings based on size of tempSensors and channels
tempReadings = []
humReadings = []
moistReadings = []
tempResponses = []
moistReponses = []
moistLimits = []


#flips the bit values of the read in rate
def invert(number):
    xorNum = 0b1111111111#8 bits, all high
    answer = number ^ xorNum # XOR opperation
    #print("converting " + bin(number)+" xor " + str(xorNum) + " to " + bin(answer))
    return answer #returns flipped bits

#converts celcius to farenheight
def convertTemp(temp):
        return ((temp*1.8)+32)

#will take temp readings and store them in tempReadings
def readTemps(index):
    #start read loop for sensors
    tempChans = myConf.getTempChan(index)   
    for i in tempChans:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, i) # get readings
        tempReadings.append(temperature) # append to temp list
        humReadings.append(humidity) # append to humid list
        
        #if this is true, hopefully None (null) is written to the list and the order is maintained
        if humidity is None and temperature is None:
            print('Failed to get reading.')

#will take the moisture readings
def getMoist(index):
    moistChans = myConf.getMoistChan(index)

    for x in moistChans:
    	print "trying to read " + x
    	#moistNum = moistLimits[int(x)]
    	#print("**********************************" + str(moistNum))
    	moisture = invert(mcp.read_adc(int(x)))#get readings
    	#moisture = mcp.read_adc(int(x))
	moistReadings.append(moisture)#store to end of list

#writes the given line to the log file
def writeToLog(writeData):
    fo = open("log.txt", "ab")
    for curr in writeData:
        fo.write(curr + ' ' + timeStamp + '\n')

    fo.close()

#push temp readings to php
def sendTempReadings(index):
    tempNames = myConf.getTempNames(index)
    for x, w in enumerate(tempReadings):
        if tempNames[x] is None:
            print("there are now more sensor names")
            break
        else:
            strData = '&name=' + tempNames[x] + '&temp=' + str(w) +'&hum=' + str(humReadings[x])
            url = urlBase + strData
            print('calling ' + url)
            resp = urllib2.urlopen(urllib2.Request(url))#make PHP call
            tempResponses.append(strData + ' ' + resp.read())#store reponse
    print(tempResponses)#print all responses
    writeToLog(tempResponses)

#push moisture readings to 
def sendMoistTemps(index):
    moistNames = myConf.getMoistNames(index)
    for x, w in enumerate(moistReadings):
        if moistNames[x] is None:
            print("there are now more sensor names")
            break
        else: 
            strData = '&name=' + moistNames[x] + '&moisture=' + str(w)
            url = urlBase + strData
            print('calling ' + url)
            resp = urllib2.urlopen(urllib2.Request(url))#make PHP call
            moistReponses.append(strData + ' ' + resp.read())#store reponse
    print(moistReponses)#print all responses
    writeToLog(moistReponses)
        
#pump pin
#just call Pump() whenever the moisture level gets below the set value
def Pump(seconds):

   # GPIO.cleanup()
   # GPIO.setmode(GPIO.BOARD)
    GPIO_PIN = 21
    GPIO.setup(GPIO_PIN, GPIO.OUT)

# Send a signal to the relay
    def SendSignal():
        try:
            GPIO.output(GPIO_PIN, GPIO.HIGH)
            print("After high call")
            time.sleep(seconds)
            GPIO.output(GPIO_PIN, GPIO.LOW)
	    print("After low call")
        except:
            print ("Something wrong")
            pass

    SendSignal()
    print("Signal was called")
    GPIO.cleanup()

#same variables current is currently measured moisture
#user defined moisture limit can place signal processing here to start pump
def checkWater(mLimit, seconds, current):
    
	if(current < mLimit):
        #possible way to keep track of watering cycles/ water usage
        #send the signal to the pump
        #and a bit to the database to show it was watered that day
        #watering time also goes here, a timer to be able to dispense 
        #a certain amount of water
	       	print("watering")
        	Pump(seconds)
    	else:
       		print("no water needed")
        

for i in range(len(myConf.getGardenNames())):
    readTemps(i)#get temperature and humidity readings
    getMoist(i)# get moisture readings
    sendTempReadings(i)#send the temp/humid readings
    sendMoistTemps(i)#send moisture readings
for m in range(len(myConf.getGardenNames())):
        tempList = myConf.getMoistLimit(m)
        for j in tempList:
                moistLimits.append(j)
        print(moistLimits)
for k in range(len(moistLimits)):
	checkWater(900, 2, moistReadings[k])

