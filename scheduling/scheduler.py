import subprocess
import json
import datetime
import pytz
import time
import collections

resultsServerKey = '/home/foivos/.ssh/monroeResults' # <-- change this to point to your own pioneer key
userId = 106 # <-- change this to your own user ID

PENDINGFILESCLIENTDIR = "../pendingFilesClient/" # directory where we save the results of the experiments
PROCESSEDFILESCLIENTDIR = "../processedFilesClient/"
supportDir = './' # directory with the pem key and certificate and where we store the intermediate scheduling files.
MonroeSystemsIp = "128.39.37.151"


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




# wget --header=Host:haugerud.nntb.no --no-check-certificate --certificate=./file.crt.pem --private-key=./file.key.pem https://128.39.37.151/v1/resources/

def getSchedulingNode(nodeId):
    #url = 'https://haugerud.nntb.no/v1/resources/' + str(nodeId) + "/schedules"
    #url = 'https://haugerud.nntb.no/v1/resources/870/schedules"
    url = 'https://' + MonroeSystemsIp +'/v1/resources/' + str(nodeId) + "/schedules"
    outfile = supportDir + "schedule" + str(nodeId)


    cmd = [
        "wget",
        "--certificate=" + supportDir + "file.crt.pem",
        "--private-key=" + supportDir + "file.key.pem",
        "--no-check-certificate",
        "--header=Host:haugerud.nntb.no",
        url,
        "-O",
        outfile
    ]
    print(" ".join(cmd))

    output = subprocess.check_output(cmd)

    with open(outfile, "r") as schedfile:
        scheduling = "".join(schedfile.readlines())

    schedules = json.loads(scheduling)
    return schedules

def getResources():
    #url = 'https://haugerud.nntb.no/v1/resources/'
    url = 'https://' + MonroeSystemsIp +'/v1/resources/'
    outfile = supportDir + "resources"


    cmd = [
        "wget",
        "--certificate=" + supportDir + "file.crt.pem",
        "--private-key=" + supportDir + "file.key.pem",
        "--no-check-certificate",
        "--header=Host:haugerud.nntb.no",
        url,
        "-O",
        outfile
    ]
    print(" ".join(cmd))
    
    output = subprocess.check_output(cmd)
    
    with open(outfile, "r") as schedfile:
        scheduling = "".join(schedfile.readlines())

    resources = json.loads(scheduling)
    return resources

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

def checkAvailability(nodeId, start, duration, nodecount):
    #urlBase = 'https://scheduler.monroe-system.eu/v1/schedules/find?'
    urlBase = 'https://' + MonroeSystemsIp + '/v1/schedules/find?'
    url = urlBase + "duration=" + str(duration) + "&nodecount=" + str(nodecount) + "&nodes=" + str(nodeId) + "&nodetypes=type:testing&start=" + str(start)
    outfile = supportDir + "schedulingVerification"
    cmd = [
        "wget",
        "--certificate=" + supportDir + "file.crt.pem",
        "--private-key=" + supportDir + "file.key.pem",
        "--no-check-certificate",
        "--header=Host:haugerud.nntb.no",
        url,
        "-O",
        outfile
    ]
    print(" ".join(cmd))
    output = subprocess.check_output(cmd)
    
    with open(outfile, "r") as schedfile:
        scheduling = "".join(schedfile.readlines())
    response = json.loads(scheduling)
    if str(start) == str(response[0]['start']):
        print("good to go")
    return response

def submitExperiment(nodeId, start, duration, nodecount, experimentName, script, options):
    #urlBase = 'https://haugerud.nntb.no/v1/experiments'
    urlBase = 'https://' + MonroeSystemsIp + '/v1/experiments'
    outfile = supportDir + "submitExperimentVerification"
    postfile = supportDir + "jsonForm"
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
        "--certificate=" + supportDir + "file.crt.pem",
        "--private-key=" + supportDir + "file.key.pem",
        "--no-check-certificate",
        "--header=Host:haugerud.nntb.no",
        urlBase,
        "-O",
        outfile
    ]
    print(" ".join(cmd))
    output = subprocess.check_output(cmd)
    
    with open(outfile, "r") as schedfile:
        scheduling = "".join(schedfile.readlines())
    response = json.loads(scheduling)
    return response


def getUserExperimentsDate(userId, starDate):
    #url = 'https://haugerud.nntb.no/v1/users/' + str(userId) + "/experiments/"
    url = 'https://' + MonroeSystemsIp + '/v1/users/' + str(userId) + "/experiments/"
    print(url)
    outfile = supportDir + "UserExperiments_" + str(userId)
    starDateTimestamp = getTimestamp(starDate)

    cmd = [
        "wget",
        "--certificate=" + supportDir + "file.crt.pem",
        "--private-key=" + supportDir + "file.key.pem",
        "--no-check-certificate",
        "--header=Host:haugerud.nntb.no",
        url,
        "-O",
        outfile
    ]
    print(" ".join(cmd))
    
    output = subprocess.check_output(cmd)
    
    with open(outfile, "r") as schedfile:
        scheduling = "".join(schedfile.readlines())

    resources = json.loads(scheduling)
    filtered = []
    for element in resources:
        if starDateTimestamp < element['start']:
            filtered.append(element)
    return filtered

def getExperimentIds(experimentDict):
    expIds = []
    for element in experimentDict:
        expIds.append(element["id"])
    return expIds

def getSpecificExperimentElements(expIds):
    epxerimentElements = collections.defaultdict(list)
    for expId in expIds:
        #url = 'https://haugerud.nntb.no/v1/experiments/' + str(expId) + "/schedules"
        url = 'https://' + MonroeSystemsIp + '/v1/experiments/' + str(expId) + "/schedules"
        outfile = supportDir + "ExperimentElements_" + str(expId)
        
        cmd = [
            "wget",
            "--certificate=" + supportDir + "file.crt.pem",
            "--private-key=" + supportDir + "file.key.pem",
            "--no-check-certificate",
            "--header=Host:haugerud.nntb.no",
            url,
            "-O",
            outfile]
        print(" ".join(cmd))
        output = subprocess.check_output(cmd)
        with open(outfile, "r") as schedfile:
            scheduling = "".join(schedfile.readlines())

        resources = json.loads(scheduling)
        for elementId, value in resources['schedules'].items():
            if True: # if value['status'] in ['finished']
                epxerimentElements[expId].append(elementId)
    return epxerimentElements

def downloadExperimentalElementResults(epxerimentElement):
    cmd = [
        "scp",
        "-r",
        "monroeresults:/nne/user/" + str(epxerimentElement) + "/",
        PENDINGFILESCLIENTDIR
    ]
    print(" ".join(cmd))
    output = subprocess.check_output(cmd)

    
"""
example usage

# get all the experimetnts of a user scheduled after a date.
userId = 106
starDate = "2021-03-24 00:00:00"

test = getUserExperimentsDate(userId, starDate)
expIds = getExperimentIds(test)
epxerimentElements = getSpecificExperimentElements(expIds)
for experiment, elementList in epxerimentElements.items():
    for element in elementList:
        print(element)

#download experiments
downloadExperimentalElementResults(1995072)

# submit an experiment
nodeId = 2561
start = 1616582750
duration = 650
nodecount = 1
experimentName = "test cli scheduling"
script = "docker.io/foivosm/basic_tests"
options = {
    "iperf3_udp": {
        "performTest": "yes",
        "iperfBinary": "37",
        "serverIP": "128.39.37.74",
        "serverPort": "60000",
        "useTcpdump": "no",
        "targetBitrate": "600M",
        "transmissionTime": "3"
    },
    "cubic": {
        "performTest": "no",
        "serverIP": "128.39.37.74",
        "serverPort": "54541",
        "useTcpdump": "yes",
        "targetFile": "1M",
        "captureLength": "74"
    },
    "bbr": {
        "performTest": "no",
        "serverIP": "128.39.37.74",
        "serverPort": "54541",
        "useTcpdump": "yes",
        "targetFile": "1M",
        "captureLength": "74"
    },
    "interfaces_placeholder": ["eth0"],
    "configurationSource": "configFile",
    "trace_ping_target": "128.39.37.74",
    "traceroute": "no",
    "ping": "no"
}

submitExperiment(nodeId, start, duration, nodecount, experimentName, script, options)








"""