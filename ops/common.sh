#!/usr/bin/env bash

katzenRepo=https://github.com/katzenpost
katzenServerRepo="${KATZEN_SERVER_REPO:-${katzenRepo}/server}"
katzenAuthRepo="${KATZEN_AUTH_REPO:-${katzenRepo}/authority}"

katzenServerMasterHash="${katzenServerMasterHash:-$(git ls-remote --heads $katzenServerRepo | grep master | cut -c1-7)}"
katzenAuthMasterHash="${katzenAuthMasterHash:-$(git ls-remote --heads $katzenAuthRepo | grep master | cut -c1-7)}"
katzenServerTag=${KATZEN_SERVER_TAG:-master}
katzenAuthTag=${KATZEN_AUTH_TAG:-master}

dockerApiURL=https://hub.docker.com/v2/repositories

function LOG(){
  echo "LOG: $1"
}

pushContainers() {
  tags=$(docker images $1 --format "{{.Tag}}")
  for x in $tags; do
    docker push $1:$x
  done
}

function containerExistsInCloud() {
  # We pipe the standard output to null when it finds the container
  # because this means the function returns a 0 but it doesn't
  # clog the output
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  curl -sflSL $dockerApiURL/$container/tags/$tag > /dev/null
}

function getContainerInfo() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  echo "HI"
  result=$(curl -sflSL $dockerApiURL/$container/tags/$tag)
  LOG "result $result"
  printf $result
}

function compareRemoteContainers() {
  containerOne=$(getContainerInfo $1 | jq '.images[0].digest')
  containerTwo=$(getContainerInfo $2 | jq '.images[0].digest')
  if [[ $containerOne == $containerTwo ]]; then
    return 0
  fi
  return 1
}

function compareLocalContainers() {
  containerOne=$(docker image inspect $1 --format "{{.Id}}")
  containerTwo=$(docker image inspect $2 --format "{{.Id}}")
  if [[ "${containerOne}" == "${containerTwo}" ]]; then
    return 0
  fi
  return 1
}