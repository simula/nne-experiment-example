#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author: Foivos Michelinakis
# Date: January 2021
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

from helper import *
import subprocess
import time

logstring = ""

logstring += "start of experiment\n"
logstring += f"Starting at {time.time()}\n"

OUTPUTFILEDIR = "./"
DEFAULTCONFIGURATIONPARAMETERS = {"targets": ["www.google.com"], "numberOfPings": 3, "Operator": ["Telenor", "Telia"]}
REVERTTODEFAULT = True # True: if the configuration file is unreadable run the experiment with the default parameters. False: there is not point to run the experiment if we can not test our specified parameters, so we abort.


logstring += "reading the configuration file\n"
# ====== Read the configuration file - START ==================================
try:
    with open(CONFIG_FILE, "r") as fd:
        configurationParameters = json.load(fd)
        logstring += str(configurationParameters) + "\n"
        usingDefaults = False
        saveResultFromString("False", "usingDefaults.txt")
    saveResultFromFileGenericPath(CONFIG_FILE) # just to have the exact experiment configuration of this isntance alongside its results
    if os.path.isfile("/nodeid"):
        logstring += "The nodeID file exists.\n"
        saveResultFromFileGenericPath("/nodeid")
    else:
        logstring += "The nodeID file is missing."
        saveResultFromString("00000", "nodeid")
    logstring += "The configuration file was successully parsed."
except Exception as e:
    logstring += f"Cannot retrive /monroe/config {e}"
    if REVERTTODEFAULT:
        logstring += "Using default parameters......."
        configurationParameters = DEFAULTCONFIGURATIONPARAMETERS
        usingDefaults = True
        saveResultFromString("True", "usingDefaults.txt")
        # also copy the default parameters to the results.
        saveResultFromString(str(DEFAULTCONFIGURATIONPARAMETERS), "config")
    else:
        logstring += "we abort this experimnt......."
        time.sleep(5)
        sys.exit(1)
# ====== Read the configuration file - STOP ==================================

# we use the `get` method, to assign values, so that in case a value is missing
# from the configurtion file, we can use its default value.
logstring += "The initial configurationParameters are:\n"
logstring += str(configurationParameters) + "\n"
operatorList = configurationParameters.get("Operator", DEFAULTCONFIGURATIONPARAMETERS["Operator"])
targets = configurationParameters.get("targets", DEFAULTCONFIGURATIONPARAMETERS["targets"])
numberOfPings = configurationParameters.get("numberOfPings", DEFAULTCONFIGURATIONPARAMETERS["numberOfPings"])

logstring += f"the operatorList is {operatorList}\n"
logstring += f"the targets is {targets}\n"
logstring += f"the numberOfPings is {numberOfPings}\n"


if typeOfNode == "Monroe":
    operatorContextDict = mapMobileOperatorsToInterfacesAndSourceIPs(operatorList)
elif typeOfNode == "testing":
    operatorContextDict = getWiredInterfaceSourceIP("eno1")
else:
    logstring += "Unknown type of node. Exiting....\n"
    saveResultFromString(logstring, "logstring.txt")
    sys.exit(1)

for operatorName, operatorContext in operatorContextDict.items():
    logstring += str(operatorName) + "\n"
    logstring += str(operatorContext) + "\n"
    targetInterface = operatorContext['interface']
    if targetInterface != None:
        for target in targets:
            cmd = ["ping", "-I", targetInterface, "-c", str(numberOfPings), target]
            logstring += " ".join(cmd) + "\n"
            output = subprocess.check_output(cmd).decode('ascii')
            OUTPUTFILE = f"{OUTPUTFILEDIR}_{operatorName}_{target}.txt"
            with open(OUTPUTFILE, 'w') as resultsTxt:
                resultsTxt.write(output)
            saveResultFromFile(OUTPUTFILE)

logstring += f"Finished at {time.time()}\n"

saveResultFromString(logstring, "logstring.txt")

# we add a bit of time at the end to make sure the results are copied before
# the container instance exits.
# typically 10 seconds are enough.
time.sleep(3000)