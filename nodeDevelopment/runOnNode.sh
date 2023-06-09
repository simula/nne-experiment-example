#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONTAINER="simpleping"
CONTAINERTAG="crnaeng/simpleping"

TESTNAME="simpleping"
WORKDIR="/run/shm/${TESTNAME}"


echo "Prepare:"
rm -rf $WORKDIR
mkdir -p $WORKDIR
echo ' {"targets": ["www.vg.no"],"numberOfPings": 5,"Operator": ["Telenor", "Telia"], "measurement_id": 99999}' > $WORKDIR/config
mkdir -p $WORKDIR/results


echo "Update:"
docker rm -f ${TESTNAME} >/dev/null 2>&1 || true
sudo docker pull ${CONTAINERTAG}


echo "Run:"
MONROE_NAMESPACE=$(docker ps --no-trunc -aqf name=monroe-namespace)
docker run -d \
   --name ${TESTNAME} \
   --net=container:$MONROE_NAMESPACE \
   --cap-add NET_ADMIN \
   --cap-add NET_RAW \
   --shm-size=1G \
   -v $WORKDIR/results:/monroe/results \
   -v $WORKDIR/config:/monroe/config:ro \
   -v /etc/nodeid:/nodeid:ro \
   ${CONTAINERTAG}

sleep 1

echo "Shell:"
docker exec --interactive=true --tty=true ${TESTNAME} /bin/bash