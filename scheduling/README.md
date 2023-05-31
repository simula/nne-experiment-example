# How to use the scheduler for academic experiments

## The scheduler server

The scheduler is hosted at the machine `haugerud.nntb.no` with fixed IP `128.39.37.151`. It is important to know both the IP and the domain name. When scheduling a campaign we might have to make hundrends or thousands of calls to the scheduler API. Each call is made with the `wget` command. If we just pass the domain name to `wget`, then `wget` will make a new DNS query per call. This is both slow and, if we use an external DNS server, might be interpretted as an attack. So, at each call we pass to `wget` the IP and include the domain name as a parameter, so that the responding server will know which API we want to use.

We need to have an account to the scheduler to make calls. Contact Celerway for that and they will create an account for you and provide you with the credentials in the form of a single `p12` file or alternativly a set of a certificate and a key. `p12` is an archive that bundles the certificate and the key together and you can import it directly to chrome and then access `haugerud.nntb.no`.

`wget` can not use `p12` files but only the certificate and key pair. We can extract these from the `p12` with the commands:

* key: `openssl pkcs12 -in <name>.p12 -out <name>.key.pem -nocerts -nodes`
* certificate: `openssl pkcs12 -in <name>.p12 -out <name>.crt.pem -clcerts -nokeys`

## The scheduler API

The sceduler at `haugerud.nntb.no` is accessible either throught the website or through making API requests directly.

For example, we can make a request for the available resources with `wget` by requesting the `v1/resources/` endpoint as follows:

```bash
wget --header=Host:haugerud.nntb.no --no-check-certificate --certificate=./file.crt.pem --private-key=./file.key.pem https://128.39.37.151/v1/resources/
```

### Scheduler API endpoints

#### resources

We get list of the active nodes and their context / metadata. The endpoint is `v1/resources/`. An example entry looks like:

```json
{
    "address": "29, Dronning Eufemias gate - Norway 0194",
    "country": "norway",
    "heartbeat": 1678979049,
    "hostname": "nne0cfe5d9016a3",
    "id": 4120,
    "interfaces": [
      {
        "heartbeat": 1654591762,
        "iccid": "8947080037110727046",
        "imei": "863305040235011",
        "interface": "op2",
        "mccmnc": "24202",
        "operator": "Telia Norge",
        "quota_current": 0,
        "quota_last_reset": 0,
        "quota_reset_date": 0,
        "quota_reset_value": 0,
        "status": "current"
      },
      {
        "heartbeat": 1652274396,
        "iccid": "89470000210701063863",
        "imei": "863305040251422",
        "interface": "op1",
        "mccmnc": "24201",
        "operator": "Telenor",
        "quota_current": 0,
        "quota_last_reset": 0,
        "quota_reset_date": 0,
        "quota_reset_value": 0,
        "status": "current"
      },
      {
        "heartbeat": 1648366521,
        "iccid": "89470060210610151376",
        "imei": "860517049473608",
        "interface": "op0",
        "mccmnc": "24201",
        "operator": "Telenor",
        "quota_current": 0,
        "quota_last_reset": 0,
        "quota_reset_date": 0,
        "quota_reset_value": 0,
        "status": "current"
      }
    ],
    "latitude": "59.827152",
    "longitude": "10.784092",
    "model": "arcus",
    "project": "nornet",
    "site": "nornet",
    "status": "active",
    "type": "deployed"
  }
 ```
#### Scheduling information of a specific node

Get the scheduling information of a specific node. We get a list of the future scheduled experiments for this node. The endpoint is `v1/resources/<nodeId>/schedules`. An example entry looks like:

```json
  {
    "deployment_options": {
      "nodes": "2562",
      "script": "docker.io/foivosm/basic_tests",
      "shared": 0,
      "storage": 1048576000,
      "traffic": 2097152000
    },
    "expid": 984,
    "id": "1995075",
    "nodeid": 2562,
    "shared": 0,
    "start": 1616510810,
    "status": "deployed",
    "stop": 1616511460
  }
```

#### Check availability of a slot for a specific node or group of nodes.

You may request a if a node or group of nodes are available at a specific time for a specific experiment duration. The scheduler respondes with the earliest time the node or group of nodes are avaialble after the requested time. If the returned time is equal to the requested time, then the resources are available at the requested time. If not you can choose the proposed time to schedule the experiment. All times are UTC timestamps. The relevant parameters are:

* `nodeId`: coma serated values of the desired nodeId(s).
* `start`: UTC timestamp of the desired start time. The response will provide the earliest time after the `start` time that the requested resources are available for the requested period of time.
* `duration`: The time in seconds to keep the container running. If the container exits before that nothings happens. If the container is not finished by this time, it is terminated.
* `nodecount`: The number of nodes to run the experiment in parallel.
* `nodetypes`: The type of nodes. Currently it can be either `Testing` or `Deployed`.

The endpoint is `/v1/schedules/find?`. You pass the parameters after the `find?`. An example request is:

```bash
https://haugerud.nntb.no/v1/schedules/find?duration=300&nodecount=1&nodes=4125,4141,4140&nodetypes=&start=1679061278
```
An example response looks like:

```json
{
    "max_nodecount": 2,
    "max_stop": 1679088600,
    "nodecount": 1,
    "nodetypes": "",
    "start": 1679061278,
    "stop": 1679061578
  }
```

#### Submit an experiment

Make a `POST` request to the endpoint `/v1/experiments`. The post request should contain the following parameters:

* `nodetypes`: The type of nodes. Currently it can be either `Testing` or `Deployed`.
* `name`: The name of this experiment
* `nodecount`: The number of nodes to run the experiment in parallel.
* `script`: The full URL of the docker hub link of the container. For example: `docker.io/foivosm/basic_tests`
* `start`: The start time of the experiment as a UTC timestamp.
* `options`: A `JSON` string with the configuration parameters for this experiment.
* `stop`: The ending time of the experiment as a UTC timestamp.

Upon success, you get a response like the following:

```json
{
  "experiment": 3270,
  "intervals": 1,
  "message": "Allocated task 3270.",
  "nodecount": 1
}
```

#### Get a list of all the experiements submitted by a user

Get the scheduled (past and future) experiments of a user with user ID `userId`. The endpoint is `/v1/users/<userId>/experiments/`. The response is a list of experiments. An example entry is:

```json
{
    "id": 936,
    "name": "udp_speedtest",
    "options": {
      "shared": 0,
      "storage": 134217728,
      "traffic": 1048576
    },
    "ownerid": 106,
    "script": "foivosm/basic_tests",
    "start": 1615545480,
    "status": "active",
    "stop": 1615545780,
    "summary": {
      "stopped": 1
    },
    "type": ""
  }
```

We can use the `id` parameter to download the experiment files if the experiment is successful.


#### Get all the information of a specific experiment

We can use the `id` parameter of the above element to request more information for a specific experiment. The endpoint is `/v1/experiments/<id>/schedules`.

An example response is:

```json
{
  "id": 985,
  "name": "test cli scheduling",
  "options": {
    "shared": 0,
    "storage": 134217728,
    "traffic": 1048576
  },
  "ownerid": 106,
  "schedules": {
    "1995076": {
      "nodeid": 870,
      "start": 1616597210,
      "status": "aborted",
      "stop": 1616597860
    }
  },
  "script": "docker.io/foivosm/basic_tests",
  "start": 1616597210,
  "status": "active",
  "stop": 1616597860,
  "type": ""
}
```

The `schedules` parameter containes a list of the experiment isntances launched. The key of each isntance (for example in the above example `1995076`) can be used to fetch the files geneerated by the experiment.

## Storage of results: The Pioneer server

The nodes transmit their experimental files to the server `Pioneer` with URL `pioneer.nntb.no`.

The result of each experiment instance are stored at their own folder at the directory `/nne/user/<bigNumber>`, where `bigNumber` is an auto-incremented big number set by the scheduler. For example the `bigNumber` for the response of the above section is `1995076`. So the files for this experiment would be stored in the directory `/nne/user/1995076/`.

Due to the number of experiments, the parent directory `/nne/user/` contains a huge number of subdirectories (> 500000). So even attempting to do an `ls` might take several minutes. But if you already have the full path of the directory with the experiment results you can access it very fast.

The experiment results are deleted after a few months. For some of the results, the files are automatically added at the apollo database.

## Moving the results to the apollo database

TBA

## scheduler wrapper python script `scheduler.py`

This is a python script that automates everything discussed above.

Create your own instance of the `scheduler` object with the following parameters:

* `pioneerKeyPath`: Path of the private key to log in to `pioneer` for retrieving the results.
* `pioneerUser`: The user name of the linux account in `pioneer`.
* `userId`: Your user ID. You can see it at the top of the `haugerud.nntb.no` website if you visit it with a browser.
* `pendingFilesClientDir`: Directory where we save the results of the experiments.
* `processedFilesClientDir`: After we process the raw files in `pendingFilesClientDir`, we move them here.
* `supportDir`: Directory where we store the intermediate scheduling files.
* `PemKeyDir`: Path to the key file of the scheduler.
* `PemCerDir`: Path to the certificate file of the scheduler.

### Example usage of `scheduler.py` inside a jupyter notebook cell

```python
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



```