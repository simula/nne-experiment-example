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


try:
    with open("/monroe/config", "r") as fd:
        configurationParameters = json.load(fd)
        print(configurationParameters)
except Exception as e:
    print("Cannot retrive /monroe/config {}".format(e))
    print("Using default parameters.......")
    configurationParameters = {"target": "www.google.com", "numberOfPings": 10, "Operator": ["Telenor", "Telia"]}
    usingDefaults = True


operatorList = configurationParameters["Operator"]
target = configurationParameters["target"]
numberOfPings = configurationParameters["numberOfPings"]

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


time.sleep(10)