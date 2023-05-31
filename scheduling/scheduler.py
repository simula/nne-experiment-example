import subprocess
import json
import datetime
import pytz
import time
import collections

new_5G_nodes = [
    #3781, # This node is broken and should be replaced
    4120,
    4121,
    4122,
    4123,
    4124,
    4125,
    4126,
    4127,
    4133,
    4134,
    4135,
    4137,
    4138,
    4141,
    4143,
    4144,
    4147,
    4151,
    4152]
old_4G_nodes = [875, 868]
CPE_5G_nodes = [870, 2561, 2564] # There are also ndoes 2562, 2563, which are inaccessible.
new_testing_nodes = [4125]


def humanDate(timeValue):
    return datetime.datetime.fromtimestamp(
        int(timeValue)
    ).strftime('%Y-%m-%d %H:%M:%S')

def getTimestamp(timeValue):
    return int(time.mktime(datetime.datetime.strptime(timeValue, '%Y-%m-%d %H:%M:%S').timetuple()))

def getLocalizedTimestampToUTC(timeValue):
    # !!!Warning!!!
    # The following is the proper way to handle timezones in python.
    # https://stackoverflow.com/a/18541344/3296739
    # create a datetime unaware object with the local time and then use the localize funtion to make it aware
    # then convert it to UTC and get the timestamp.

    t = pytz.timezone('Europe/Oslo').localize(
    datetime.datetime.strptime(timeValue, '%Y-%m-%d %H:%M:%S')
    )
    return int(t.astimezone(pytz.utc).timestamp())

def showBusyPeriods(schedules, endDate):
    endDateTimestamp = getTimestamp(endDate)
    for i in range(len(schedules)):
        if (schedules[i]["start"] > endDateTimestamp) or (schedules[i]["stop"] > endDateTimestamp):
            break
        print("start: " + humanDate(schedules[i]["start"]) + " end: " + humanDate(schedules[i]["stop"]) +\
        " duration: " + str(int(schedules[i]["stop"]) - int(schedules[i]["start"])) + " experiment: " +\
        schedules[i]["deployment_options"]["script"] + "\tstatus: " + schedules[i]["status"])

def findFreeSlots(schedules, endDate, minimumDuration, bufferTime):
    freeslots = []
    if len(schedules) == 0:
        return freeslots
    endDateTimestamp = getTimestamp(endDate)
    #first check if there is a free slot between now and the first scheduled experiment
    if (int(schedules[0]["start"]) - int(time.time())) > (minimumDuration + 2 * bufferTime):
        start = int(time.time()) + bufferTime
        stop = int(schedules[0]["start"]) - bufferTime
        duration = stop - start
        print("Free slot-> start: " + humanDate(start) + \
            " " + str(start) + " " + " stop: " + humanDate(stop) + \
            " " + str(start) + " " +  " duration: " + str(duration))
        freeslots.append([start, stop, duration])
    for i in range(len(schedules)):
        if (schedules[i]["start"] > endDateTimestamp) or (schedules[i]["stop"] > endDateTimestamp):
            break
        try: 
            start = int(schedules[i]["stop"]) + bufferTime
            stop = int(schedules[i+1]["start"]) - bufferTime
            duration = stop - start
            if duration > (minimumDuration):
                print("Free slot-> start: " + humanDate(start) + \
                    " " + str(start) + " " + " stop: " + humanDate(stop) + \
                    " " + str(start) + " " +  " duration: " + str(duration))
                freeslots.append([start, stop, duration])
        except IndexError:
            print("indexError")
            break
    return freeslots

def getExperimentIds(experimentDict):
    expIds = []
    for element in experimentDict:
        expIds.append(element["id"])
    return expIds

class scheduler:
    MonroeSystemsIp = "128.39.37.151"
    pioneerUrl = "pioneer.nntb.no"
    
    def __init__(
            self,
            pioneerKeyPath = '/home/foivos/.ssh/monroeResults', # <-- change this to point to your own pioneer key
            pioneerUser = 'foivos',  # <-- change this to point to your own pioneer user
            userId = 245, # <-- change this to your own user ID
            pendingFilesClientDir = '../pendingFilesClient/', # directory where we save the results of the experiments
            processedFilesClientDir = '../processedFilesClient/',
            supportDir = './', # directory where we store the intermediate scheduling files.
            PemKeyDir = './', # pem key directory
            PemCerDir = './' # pem certificate directory
            ):
        self.pioneerKeyPath = pioneerKeyPath
        self.pioneerUser = pioneerUser 
        self.userId = userId
        self.pendingFilesClientDir = pendingFilesClientDir
        self.processedFilesClientDir = processedFilesClientDir
        self.supportDir = supportDir
        self.PemKeyDir = PemKeyDir
        self.PemCerDir = PemCerDir

    def getSchedulingNode(self, nodeId):
        #url = 'https://haugerud.nntb.no/v1/resources/' + str(nodeId) + "/schedules"
        #url = 'https://haugerud.nntb.no/v1/resources/870/schedules"
        url = 'https://' + self.MonroeSystemsIp +'/v1/resources/' + str(nodeId) + "/schedules"
        outfile = self.supportDir + "schedule" + str(nodeId)
        cmd = [
            "wget",
            "--certificate=" + self.PemCerDir,
            "--private-key=" + self.PemKeyDir,
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            url,
            "-O",
            outfile
        ]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd)
        print(output)

        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())

        schedules = json.loads(scheduling)
        return schedules

    def getResources(self):
        # wget --header=Host:haugerud.nntb.no --no-check-certificate --certificate=./file.crt.pem --private-key=./file.key.pem https://128.39.37.151/v1/resources/
        #url = 'https://haugerud.nntb.no/v1/resources/'
        url = 'https://' + self.MonroeSystemsIp +'/v1/resources/'
        outfile = self.supportDir + "resources"
        cmd = [
            "wget",
            "--certificate=" + self.PemCerDir,
            "--private-key=" + self.PemKeyDir,
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            url,
            "-O",
            outfile
        ]
        print(" ".join(cmd))
        
        output = subprocess.check_output(cmd)
        print(output)
        
        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())

        resources = json.loads(scheduling)
        return resources
    
    def checkAvailability(self, nodeId, start, duration, nodecount):
        #urlBase = 'https://scheduler.monroe-system.eu/v1/schedules/find?'
        urlBase = 'https://' + self.MonroeSystemsIp + '/v1/schedules/find?'
        url = urlBase + "duration=" + str(duration) + "&nodecount=" + str(nodecount) + "&nodes=" + str(nodeId) + "&nodetypes=type:testing&start=" + str(start)
        outfile = self.supportDir + "schedulingVerification"
        cmd = [
            "wget",
            "--certificate=" + self.PemCerDir,
            "--private-key=" + self.PemKeyDir,
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            url,
            "-O",
            outfile
        ]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd)
        print(output)
        
        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())
        response = json.loads(scheduling)
        if str(start) == str(response[0]['start']):
            print("good to go")
        return response

    def submitExperiment(self, nodeId, start, duration, nodecount, experimentName, script, options):
        #urlBase = 'https://haugerud.nntb.no/v1/experiments'
        urlBase = 'https://' + self.MonroeSystemsIp + '/v1/experiments'
        outfile = self.supportDir + "submitExperimentVerification"
        postfile = self.supportDir + "jsonForm"
        with open(postfile, "w") as schedfile:
            schedfile.write("{\"nodetypes\":\"type:testing\",")
            schedfile.write("\"name\":\"" +  str(experimentName) + "\",")
            #schedfile.write("\"standaloneNode\":\"" +  str(standaloneNode) + "\",")
            schedfile.write("\"nodecount\":" +  str(nodecount) + ",")
            schedfile.write("\"script\":\"" +  str(script) + "\",")
            schedfile.write("\"start\":" +  str(start) + ",")
            
            schedfile.write("\"options\":\"{\\\"traffic\\\":1048576,")
            schedfile.write("\\\"resultsQuota\\\":1048576,")
            schedfile.write("\\\"storage\\\":134217728,")
            schedfile.write("\\\"nodes\\\":\\\"" + str(nodeId) + "\\\",")
            
            
            
            if len(options) > 0:
                for key, value in options.items():
                    if isinstance(value, list):
                        schedfile.write("\\\"" + key + "\\\": [")
                        for i in range(len(value)):
                            schedfile.write("\\\"" + value[i] + "\\\"")
                            if i != (len(value) - 1):
                                schedfile.write(", ")
                            else:
                                schedfile.write("], ")
                    elif isinstance(value, dict):
                        schedfile.write("\\\"" + key + "\\\": {")
                        for i, (key1, value1) in enumerate(value.items()):
                            if i != len(value)-1:
                                schedfile.write("\\\"" + key1 + "\\\": \\\"" + str(value1) + "\\\", ")
                            else:
                                schedfile.write("\\\"" + key1 + "\\\": \\\"" + str(value1) + "\\\"}, ")
                    elif isinstance(value, int):
                        schedfile.write("\\\"" + key + "\\\": " + str(value) + ", ")
                    elif isinstance(value, str):
                        schedfile.write("\\\"" + key + "\\\": \\\"" + str(value) + "\\\", ")
                    else:
                        print("Error: Key: " + str(key) + " could not be converted to the option string")
            schedfile.write("\\\"shared\\\":0")
            
            schedfile.write("}\",")
            
            
            schedfile.write("\"stop\":" +  str(int(start) + int(duration)) + "")
            schedfile.write("}")
            #schedfile.write()
        
        cmd = [
            "wget",
            "--header=Content-Type:application/json",
            "--post-file=" + postfile,
            "--certificate=" + self.PemCerDir,
            "--private-key=" + self.PemKeyDir,
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            urlBase,
            "-O",
            outfile
        ]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd)
        print(output)
        
        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())
        response = json.loads(scheduling)
        return response

    def getUserExperimentsDate(self, startDate):
        #url = 'https://haugerud.nntb.no/v1/users/' + str(self.userId) + "/experiments/"
        url = 'https://' + self.MonroeSystemsIp + '/v1/users/' + str(self.userId) + "/experiments/"
        print(url)
        outfile = self.supportDir + "UserExperiments_" + str(self.userId)
        startDateTimestamp = getTimestamp(startDate)

        cmd = [
            "wget",
            "--certificate=" + self.PemCerDir,
            "--private-key=" + self.PemKeyDir,
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            url,
            "-O",
            outfile
        ]
        print(" ".join(cmd))
        
        output = subprocess.check_output(cmd)
        print(output)
        
        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())

        resources = json.loads(scheduling)
        filtered = []
        for element in resources:
            if startDateTimestamp < element['start']:
                filtered.append(element)
        return filtered

    def getSpecificExperimentElements(self, expIds):
        epxerimentElements = collections.defaultdict(list)
        for expId in expIds:
            #url = 'https://haugerud.nntb.no/v1/experiments/' + str(expId) + "/schedules"
            url = 'https://' + self.MonroeSystemsIp + '/v1/experiments/' + str(expId) + "/schedules"
            outfile = self.supportDir + "ExperimentElements_" + str(expId)
            
            cmd = [
                "wget",
                "--certificate=" + self.PemCerDir,
                "--private-key=" + self.PemKeyDir,
                "--no-check-certificate",
                "--header=Host:haugerud.nntb.no",
                url,
                "-O",
                outfile]
            print(" ".join(cmd))
            output = subprocess.check_output(cmd)
            print(output)
            with open(outfile, "r") as schedfile:
                scheduling = "".join(schedfile.readlines())

            resources = json.loads(scheduling)
            for elementId, value in resources['schedules'].items():
                if True: # if value['status'] in ['finished']
                    epxerimentElements[expId].append(elementId)
        return epxerimentElements
    
    def downloadExperimentalElementResults(self, epxerimentElement):
        cmd = [
            "scp",
            "-i",
            self.pioneerKeyPath,
            "-r",
            f"{self.pioneerUser}@{self.pioneerUrl}:/nne/user/{epxerimentElement}/",
            self.pendingFilesClientDir
        ]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd)
        print(output)

"""
example usage

from scheduler import *

s = scheduler(
            pioneerKeyPath = '/home/foivos/.ssh/monroeResults', # <-- change this to point to your own pioneer key
            pioneerUser = 'foivos',  # <-- change this to point to your own pioneer user
            userId = 245, # <-- change this to your own user ID
            pendingFilesClientDir = "../pendingFilesClient/", # directory where we save the results of the experiments
            processedFilesClientDir = "../processedFilesClient/",
            supportDir = './', # directory where we store the intermediate scheduling files.
            PemKeyDir = '/home/foivos/foivos.key.pem', # pem key directory
            PemCerDir = '/home/foivos/foivos.crt.pem' # pem certificate directory
            )

# Retrieve a list of the scheduled experiments (past and future) and download related results of a user scheduled after a date.
startDate = "2021-03-24 00:00:00"

scheduledExepriments = s.getUserExperimentsDate(startDate)
expIds = getExperimentIds(scheduledExepriments)
epxerimentElements = s.getSpecificExperimentElements(expIds)
for experiment, elementList in epxerimentElements.items():
    for element in elementList:
        print(element)
        try:
            s.downloadExperimentalElementResults(element)
        except:
            print("Not able to download")
            continue

#download experiments
s.downloadExperimentalElementResults(2985817)

# submit experiment to a list of nodes
# check in scheduler.py for predifined node lists.
nodeList = [4125]
# nodeList = new_5G_nodes

# start at a specific UTC time
# start = getTimestamp('2021-04-08 23:00:00')
# alternatively start 10 minutes from now
# you need to schedule experiments at least 5 minutes from now to allow the scheduler to
# communicate them to the nodes in time.
start = int(time.time() + 600)

duration = 600
nodecount = 1
experimentName = "jitter programmatically on operator"
containerURL = "docker.io/crnaeng/simpleping"
optionsList = [    
    {
        "targets": ["www.vg.no"],
         "numberOfPings": 5,
         "Operator": ["Telenor", "Telia"]
    }
]

# j: how many times to run an experiment per nonde
# i: some time spacing between nodes to make sure that they do not send requests to the same servers at the same time
# x: The different configurations, such as operators / interfaces
for j in range(1):
    for i in range(len(nodeList)):
        for x in range(len(optionsList)):
            initiallyRequestedStartTime = start + (3600 * j) + (i * 300) + (600 * x)
            nodeAvailability = s.checkAvailability(nodeList[i], initiallyRequestedStartTime, duration, nodecount)
            nonConflictingStartTime = nodeAvailability[0]["start"]
            print(f"Initially requested start time: UTC timestamp {initiallyRequestedStartTime}, UTC human readable: {humanDate(initiallyRequestedStartTime)}")
            print(f"nonConflictingStartTime: {nonConflictingStartTime}, UTC human readable: {humanDate(nonConflictingStartTime)}")
            s.submitExperiment(nodeList[i], nonConflictingStartTime, duration, nodecount, f"{experimentName} {optionsList[x]['operator']} and node {str(nodeList[i])}", containerURL, optionsList[x])
"""