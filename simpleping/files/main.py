#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author: Foivos Michelinakis
# Date: January 2021
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project


import subprocess
import time
import json
import shutil
from helper import *

RESULTS_DIR = "/monroe/results/"
OUTPUTFILEDIR = "/opt/simpleping/"
DEFAULTCONFIGURATIONPARAMETERS = {"target": "www.google.com", "numberOfPings": 10, "Operator": ["Telenor", "Telia"]}
REVERTTODEFAULT = True # True: if the configuration file is unreadable run the experiment with the default parameters. False: there is not point to run the experiment if we can not test our specified parameters, so we abort.


# ====== Read the configuration file ==================================
try:
    with open("/monroe/config", "r") as fd:
        configurationParameters = json.load(fd)
        print(configurationParameters)
        usingDefaults = False
        saveResultFromString("False", "usingDefaults.txt")
    saveResultFromFileGenericPath("/monroe/config") # just to have the exact experiment configuration of this isntance alongside its results
    saveResultFromFileGenericPath("/nodeid")
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


# we use the `get` method, to assign values, so that in case a value is missing
# from the configurtion file, we can use its default value.
operatorList = configurationParameters.get("Operator", DEFAULTCONFIGURATIONPARAMETERS["Operator"])
target = configurationParameters.get("target", DEFAULTCONFIGURATIONPARAMETERS["target"])
numberOfPings = configurationParameters.get("numberOfPings", DEFAULTCONFIGURATIONPARAMETERS["numberOfPings"])

operatorContextDict = mapMobileOperatorsToInterfacesAndSourceIPs(operatorList)

for operatorName, operatorContext in operatorContextDict.items():
    print(operatorName)
    print(operatorContext)
    targetInterface = operatorContext['interface']
    if targetInterface != None:
        cmd = ["ping", "-I", targetInterface, "-c", str(numberOfPings), target]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd).decode('ascii')
        OUTPUTFILE = OUTPUTFILEDIR + "_" + operatorName + ".txt"
        with open(OUTPUTFILE, 'w') as resultsTxt:
            resultsTxt.write(output)
        shutil.copy2(OUTPUTFILE, RESULTS_DIR + "simplepingResults"+ "_" + operatorName + ".txt" + ".tmp")
        shutil.move(RESULTS_DIR + "simplepingResults"+ "_" + operatorName + ".txt" + ".tmp", RESULTS_DIR + "simplepingResults"+ "_" + operatorName + ".txt")
        # os.remove("/opt/simpleping/simplepingResults.txt")

# we add a bit of time at the end to make sure the results are copied before
# the container instance exits.
time.sleep(10)