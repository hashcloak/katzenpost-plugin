#!/usr/bin/env bash
source ops/common.sh

function isContainerSameAsMasterTag() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  if compareLocalContainers $container:master $container:$tag; then
    return 0
  else
    return 1
  fi
}

function provideMasterTag() {
  docker inspect $1:master > /dev/null
  if [ $? -eq 0 ]; then
    return 0
  fi
  LOG "Master tag for $1 container doesn't exist locally."
  if containerExistsInCloud $1:master; then
    docker pull $1:master
    return 0
  fi
  LOG "Master tag for $1 container doesn't in cloud."
  return 1
}

function pullOrBuild() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  if containerExistsInCloud $container:$tag; then
    docker pull $container:$tag
  else
    LOG "Upstream $container:$tag not found. Building..."
    buildUpstream $(echo -n $container | cut -f2 -d/) $tag
  fi
}

function buildUpstream() {
  name=$1
  tag=$2
  LOG "Building upstream... $name $tag"
  if [[ "$name" == "authority" ]]; then
    # using nonvoting authority
    dockerFile=/tmp/$name/Dockerfile.nonvoting
  fi

  if [[ "$name" == "server" ]]; then
    dockerFile=/tmp/$name/Dockerfile
  fi

  rm -rf /tmp/$name
  git clone $katzenRepo/$name /tmp/$name > /dev/null
  cd /tmp/$name
  git -c advice.detachedHead="false" checkout $tag > /dev/null
  LOG "Docker file $dockerFile"
  docker build -f $dockerFile -t hashcloak/$name:$tag /tmp/$name > /dev/null
  cd -
}

function pushMaster() {
  name=$1
  if containerExistsInCloud $name:master; then
    LOG "Docker hub is up to date"
  else
    LOG "Docker hub needs update for $name:master tag. Pushing..."
    docker push $name:master
  fi
}

function retagAsMaster() {
  isContainerSameAsMasterTag $1
  if [ $? -eq 0 ]; then
   LOG "Container $container is the same as master tag."
  else
    container=$(echo -n $1 | cut -f1 -d:)
    tag=$(echo -n $1 | cut -f2 -d:)
    LOG "Container $container is NOT the same as master tag"
    LOG "Retagging master with $tag"
    docker tag hashcloak/authority:master hashcloak/authority:$tag
  fi
}

master=hashcloak/authority:master
newTag=hashcloak/authority:$katzenAuthMasterHash
compareRemoteContainers $master $newTag
if [ $? -eq 1 ]; then
  docker pull $master
else
  pullOrBuild $newTag
  retagAsMaster $newTag
fi

master=hashcloak/server:master
newTag=hashcloak/server:$katzenServerMasterHash
compareRemoteContainers $master $newTag
if [ $? -eq 1 ]; then
  docker pull $master
else
  pullOrBuild $newTag
  retagAsMaster $newTag
fi