# How to run an experiment manually (i.e. without the scheduler) on a node

## Manual

The MONROE manual is at the following [github repository](https://github.com/MONROE-PROJECT/UserManual)

## Develop directly on the node

1. copy the `runOnNode.sh` script in the node.
2. change the following in the `runOnNode.sh` script:
    1. `CONTAINERTAG` to the tag of the container on docker hub.
    2. Pass the parameters of the configuration files in `prepare` section of the script in the line that reads something like `echo '{"measurement_id": 99999}' > $WORKDIR/config`. Make sure the `measurement_id` is not conflicting with an existing `measurement_id`. So, put a very high number there.
    3. (optional) `CONTAINER`: just put the name of the container.
    4. (optional) `TESTNAME`: add here a name that is not conflicting with an existing `TESTNAME` at the node.
3. run the `runOnNode.sh`. You will end up inside the container.

### Example configuration files

You can find the configuration files of the experiments running currently at the node at the directory: `/experiments/monroe/`.

## Log in to a running container instance

1. Log in to the node and become root: `sudo -s`.
2. List all the running containers: `docker ps`. In case you do not see any
container instance in the process list try running `docker ps -a`, which also
shows exited instances. That way you can verify if the container at least tried
to run.
3. From the above command copy the `CONTAINER ID` of the container instance we want to investigate.
4. Attach to the running container and get an interactive shell: `docker exec -i -t CONTAINER ID bash`.