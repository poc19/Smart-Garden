#!/usr/bin/env python
import os.path  # file check
import setupfiles.fullSetup
import setupfiles.moistSetup
import setupfiles.gardenSetup
import setupfiles.tempSetup
import setupfiles.timer
import pprint, json

list1 = []
list2 = []
goodAnswers = ['y', 'Y', 'yes', 'Yes', 'YES']
boolStop = False

def printConfig():
    with open("config.json", "r") as f:
        data = json.load(f)
    f.close()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)        

# start registration process
if os.path.isfile("./config.json") == False:
    print("****************************************WARNING****************************************")
    print("No existing setup detected")
    
print("1 - Complete install, registration, and setup with the latest packages and drivers")
print("2 - Complete install, registration, and setup with current files")
print("3 - Complete registration and setup, without install")
print("4 - Add a Garden")
print("5 - Delete a Garden")
print("6 - Add a moisture sensor")
print("7 - Delete a moisture sensor")
print("8 - Add a temperature  sensor")
print("9 - Delete a temperature  sensor")
print("10 - view configuration file")
print("11 - view/change scheduled readings")
print("12 - Exit the Setup Menu")
answer = raw_input("Choose one of the following options\n")

if(answer == "1"):
    setupfiles.fullSetup.installOnlineFiles("True")
elif(answer == "2"):
    setupfiles.fullSetup.installLocalFiles("True")
elif(answer == "3"):
    setupfiles.fullSetup.fullSetup()
elif(answer == "4"):
    setupfiles.gardenSetup.addGarden()
elif(answer == "5"):
    setupfiles.gardenSetup.removeGarden()
elif(answer == "6"):
    setupfiles.gardenSetup.addNewSensor('moist')
elif(answer == "7"):
    setupfiles.moistSetup.removeSensor()
elif(answer == "8"):
    setupfiles.gardenSetup.addNewSensor('temp')
elif(answer == "9"):
    setupfiles.tempSetup.removeSensor()
elif(answer =="10"):
    printConfig()
elif(answer =="11"):
    setupfiles.timer.scheduleJob()
else:
    print("invalid input")
    
print 'Goodbye'
exit()


