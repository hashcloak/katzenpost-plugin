#!/usr/bin/env bash
set -eo pipefail
source ops/common.sh

function main() {
  # grabs the container name after the organization name
  name=$(echo -n $1 | cut -f2 -d/) 
  container=$1
  gitHash=$2
  tag=$gitHash
  repoPath=/tmp/$name
  if [[ -n  $warpedBuildFlags ]]; then
    tag=warped$gitHash
  fi

  if [[ "$name" == "" ]]; then
    LOG "Var \$name not set. Stopping"
    exit 1
  fi

  if [[ "$name" == "authority" ]]; then
    # using nonvoting authority
    repoUrl=$katzenAuthRepo
    dockerFile=$repoPath/Dockerfile.nonvoting
    old="RUN cd cmd/nonvoting \&\& go build"
    new="RUN cd cmd/nonvoting \&\& go build$warpedBuildFlags"
  fi

  if [[ "$name" == "server" ]]; then
    repoUrl=$katzenServerRepo
    dockerFile=$repoPath/Dockerfile
    old="RUN cd cmd/server \&\& go build"
    new="RUN cd cmd/server \&\& go build$warpedBuildFlags"
  fi

  LOG "Building upstream... $container:$tag"
  rm -rf $repoPath && git clone $repoUrl $repoPath > /dev/null
  cd $repoPath > /dev/null
  git -c advice.detachedHead="false" checkout $gitHash > /dev/null
  sed -i "s|$old*|$new|" $dockerFile
  docker build -f $dockerFile -t $container:$tag $repoPath
  cd - > /dev/null
}

main $1 $2
