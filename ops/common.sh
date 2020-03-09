#!/usr/bin/env bash

katzenRepo=https://github.com/katzenpost
katzenServerRepo="${KATZEN_SERVER_REPO:-${katzenRepo}/server}"
katzenAuthRepo="${KATZEN_AUTH_REPO:-${katzenRepo}/authority}"

katzenServerMasterHash="${katzenServerMasterHash:-$(git ls-remote --heads $katzenServerRepo | grep master | cut -c1-7)}"
katzenAuthMasterHash="${katzenAuthMasterHash:-$(git ls-remote --heads $katzenAuthRepo | grep master | cut -c1-7)}"
katzenServerTag=${KATZEN_SERVER_TAG:-master}
katzenAuthTag=${KATZEN_AUTH_TAG:-master}

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
  curl --silent -f -lSL https://hub.docker.com/v2/repositories/$1/tags/$2 > /dev/null
}

#if areContainersEqual hashcloak/meson:prometheus hashcloak/meson:prometheus; then echo "yes"; else echo "no"; fi

function containersAreEqual() {
  containerOne=$(docker image inspect $1 --format "{{.Id}}")
  containerTwo=$(docker image inspect $2 --format "{{.Id}}")
  if [[ "${containerOne}" == "${containerTwo}" ]]; then
    return 0
  fi
  return 1
}