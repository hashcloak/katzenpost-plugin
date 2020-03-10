#!/usr/bin/env bash
source ops/common.sh

function isContainerSameAsMasterTag() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  compareLocalContainers $container:master $container:$tag
  if [ 0 -eq $? ]; then
    return 0
  else
    return 1
  fi
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
  LOG "Building upstream... $name @ $tag"
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
  docker build -f $dockerFile -t hashcloak/$name:$tag /tmp/$name > /dev/null
  cd -
}

function retagAsMaster() {
  isContainerSameAsMasterTag $1
  if [ 0 -eq $? ]; then
    LOG "Container $container is the same as master tag. Doing nothing."
  else
    container=$(echo -n $1 | cut -f1 -d:)
    tag=$(echo -n $1 | cut -f2 -d:)
    LOG "Retagging master with $tag"
    docker tag $container:$tag $container:master
  fi
}

master=hashcloak/authority:$katzenBaseAuthTag
newTag=hashcloak/authority:$katzenAuthMasterHash
compareRemoteContainers $master $newTag
if [ $? -eq 0 ]; then
  docker pull $master
else
  pullOrBuild $newTag
  retagAsMaster $newTag
fi
