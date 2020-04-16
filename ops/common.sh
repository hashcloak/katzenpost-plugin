#!/usr/bin/env bash
dockerApiURL=https://hub.docker.com/v2/repositories

katzenAuthRepo="${KATZEN_AUTH_REPO:-https://github.com/katzenpost/authority}"
katzenBaseAuthBranch="${KATZEN_AUTH_BRANCH:-master}"
katzenBaseAuthTag="${KATZEN_AUTH_TAG:-$katzenBaseAuthBranch}"
katzenAuthMasterHash="${katzenAuthMasterHash:-$(git ls-remote --heads $katzenAuthRepo | grep master | cut -c1-7)}"
katzenAuthContainer=hashcloak/authority

katzenServerRepo="${KATZEN_SERVER_REPO:-https://github.com/katzenpost/server}"
katzenBaseServerBranch="${KATZEN_SERVER_BRANCH:-master}"
katzenBaseServerTag="${KATZEN_SERVER_TAG:-$katzenBaseServerBranch}"
katzenServerMasterHash="${katzenServerMasterHash:-$(git ls-remote --heads $katzenServerRepo | grep master | cut -c1-7)}"
katzenServerContainer=hashcloak/server

warpedBuildFlags="-ldflags \"-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true\""


#TRAVIS_BRANCH
# - for push builds, or builds not triggered by a pull request, this is the name of the branch.
# - for builds triggered by a pull request this is the name of the branch targeted by the pull request.
# - for builds triggered by a tag, this is the same as the name of the tag (TRAVIS_TAG).
if [[ $TRAVIS_EVENT_TYPE == "pull_request" ]]; then
  HASH=${TRAVIS_PULL_REQUEST_SHA:0:7}
  BRANCH=$TRAVIS_PULL_REQUEST_BRANCH
else
  HASH=${TRAVIS_COMMIT:0:7}
  BRANCH=$TRAVIS_BRANCH
fi

mesonContainer=hashcloak/meson
mesonBranchHash="${HASH:-$(git rev-parse HEAD | cut -c1-7)}"
mesonBranchTag="${BRANCH:-$(git branch | grep \* | cut -d' ' -f2 )}"
# This removes any underscore and dash from the meson container tag 
mesonBranchTag=$(echo -n $mesonBranchTag | sed 's/[_\-]//g')
mesonClientTestCommit=${CLIENT_TEST_COMMIT:-master}

function LOG(){
  GREEN='\033[0;32m'
  NO_COLOR='\033[0m'
  printf "${GREEN}LOG: $1${NO_COLOR}\n"
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
  # be careful when adding logs here since
  # it prints to stdout and the other functions
  # that call this one might not be able to handle
  # the logs
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  result=$(curl -sflSL $dockerApiURL/$container/tags/$tag)
  printf $result
}

function compareRemoteContainers() {
  if containerExistsInCloud $1; then
    containerOne=$(getContainerInfo $1 | jq '.images[0].digest')
  else
    LOG "Compare remote #1: $1 not found in cloud"
    return 1
  fi

  if containerExistsInCloud $2; then
    containerTwo=$(getContainerInfo $2 | jq '.images[0].digest')
  else
    LOG "Compare remote #2: $2 not found in cloud"
    return 1
  fi

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
