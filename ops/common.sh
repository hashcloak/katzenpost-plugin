#!/usr/bin/env bash
dockerApiURL=https://hub.docker.com/v2/repositories

katzenAuthContainer=hashcloak/authority
katzenAuthRepo="${KATZEN_AUTH_REPO:-https://github.com/katzenpost/authority}"
katzenAuthBranch="${KATZEN_AUTH_BRANCH:-master}"
katzenAuthTag="${KATZEN_AUTH_TAG:-$katzenAuthBranch}"
katzenAuthBranchHash="${katzenAuthBranchHash:-$(git ls-remote --heads $katzenAuthRepo | grep $katzenAuthBranch | cut -c1-7)}"

katzenServerContainer=hashcloak/server
katzenServerRepo="${KATZEN_SERVER_REPO:-https://github.com/katzenpost/server}"
katzenServerBranch="${KATZEN_SERVER_BRANCH:-master}"
katzenServerTag="${KATZEN_SERVER_TAG:-$katzenServerBranch}"
katzenServerBranchHash="${katzenServerBranchHash:-$(git ls-remote --heads $katzenServerRepo | grep $katzenServerBranch | cut -c1-7)}"

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
mesonBranch="${BRANCH:-$(git branch | grep \* | cut -d' ' -f2 )}"
# This removes any underscore and dash from the meson container tag 
mesonBranch=$(echo -n $mesonBranch | sed 's/[_\-]//g')
mesonBranchHash="${HASH:-$(git rev-parse HEAD | cut -c1-7)}"
mesonClientTestCommit=${CLIENT_TEST_COMMIT:-master}

if [[ $mesonBranch != "master" ]]; then
  warpedBuildFlags=' -ldflags "-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true"'
  katzenAuthTag=warped
  katzenServerTag=warped
fi

function LOG(){
  GREEN='\033[0;32m'
  NO_COLOR='\033[0m'
  printf "${GREEN}LOG: $1${NO_COLOR}\n"
}

function containerExistsInCloud() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  curl -sflSL $dockerApiURL/$container/tags/$tag &> /dev/null
  return $?
}

function getContainerInfo() {
  # be careful when adding logs here since it
  # prints to stdout and the other functions that
  # call this one might not be able to handle the logs
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  result=$(curl -sflSL $dockerApiURL/$container/tags/$tag)
  printf $result
}

function compareRemoteContainers() {
  if ! containerExistsInCloud $1; then
    LOG "Compare remote #1: $1 not found in cloud"
    return 1
  fi

  if ! containerExistsInCloud $2; then
    LOG "Compare remote #2: $2 not found in cloud"
    return 1
  fi

  [[ $(getContainerInfo $1 | jq '.images[0].digest') == $(getContainerInfo $2 | jq '.images[0].digest') ]]
}
