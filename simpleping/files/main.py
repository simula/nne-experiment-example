#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author: Foivos Michelinakis
# Date: January 2021
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

from helper import *
import subprocess
import time


OUTPUTFILEDIR = "./"
DEFAULTCONFIGURATIONPARAMETERS = {"targets": ["www.google.com"], "numberOfPings": 10, "Operator": ["Telenor", "Telia"]}
REVERTTODEFAULT = True # True: if the configuration file is unreadable run the experiment with the default parameters. False: there is not point to run the experiment if we can not test our specified parameters, so we abort.


# ====== Read the configuration file - START ==================================
try:
    with open(CONFIG_FILE, "r") as fd:
        configurationParameters = json.load(fd)
        print(configurationParameters)
        usingDefaults = False
        saveResultFromString("False", "usingDefaults.txt")
    saveResultFromFileGenericPath(CONFIG_FILE) # just to have the exact experiment configuration of this isntance alongside its results
    if os.path.isdir("/nodeid"):
        saveResultFromFileGenericPath("/nodeid")
    else:
        saveResultFromString("00000", "nodeid")
except Exception as e:
    print("Cannot retrive /monroe/config {}".format(e))
    if REVERTTODEFAULT:
        print("Using default parameters.......")
        configurationParameters = DEFAULTCONFIGURATIONPARAMETERS
        usingDefaults = True
        saveResultFromString("True", "usingDefaults.txt")
    else:
        print("we abort this experimnt.......")
        sys.exit(1)
# ====== Read the configuration file - STOP ==================================

# we use the `get` method, to assign values, so that in case a value is missing
# from the configurtion file, we can use its default value.
operatorList = configurationParameters.get("Operator", DEFAULTCONFIGURATIONPARAMETERS["Operator"])
targets = configurationParameters.get("targets", DEFAULTCONFIGURATIONPARAMETERS["targets"])
numberOfPings = configurationParameters.get("numberOfPings", DEFAULTCONFIGURATIONPARAMETERS["numberOfPings"])

if typeOfNode == "Monroe":
    operatorContextDict = mapMobileOperatorsToInterfacesAndSourceIPs(operatorList)
elif typeOfNode == "testing":
    operatorContextDict = getWiredInterfaceSourceIP("eno1")
else:
    print("Unknown type of node. Exiting....")
    sys.exit(1)

for operatorName, operatorContext in operatorContextDict.items():
    print(operatorName)
    print(operatorContext)
    targetInterface = operatorContext['interface']
    if targetInterface != None:
        for target in targets:
            cmd = ["ping", "-I", targetInterface, "-c", str(numberOfPings), target]
            print(" ".join(cmd))
            output = subprocess.check_output(cmd).decode('ascii')
            OUTPUTFILE = f"{OUTPUTFILEDIR}_{operatorName}_{target}.txt"
            with open(OUTPUTFILE, 'w') as resultsTxt:
                resultsTxt.write(output)
            saveResultFromFile(OUTPUTFILE)

# we add a bit of time at the end to make sure the results are copied before
# the container instance exits.
time.sleep(3)