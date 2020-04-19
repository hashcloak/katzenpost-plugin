#!/usr/bin/env bash
#set -eo pipefail
source ops/common.sh

function buildUpstream() {
  name=$(echo -n $1 | cut -f2 -d/) 
  container=$1
  gitHash=$2
  tag=$3
  repoPath=/tmp/$name

  if [[ "$name" == "authority" ]]; then
    # using nonvoting authority
    repoUrl=$katzenAuthRepo
    dockerFile=$repoPath/Dockerfile.nonvoting
    old="RUN cd cmd/nonvoting \&\& go build"
    new="RUN cd cmd/nonvoting \&\& go build$warpedBuildFlags"
  elif [[ "$name" == "server" ]]; then
    repoUrl=$katzenServerRepo
    dockerFile=$repoPath/Dockerfile
    old="RUN cd cmd/server \&\& go build"
    new="RUN cd cmd/server \&\& go build$warpedBuildFlags"
  else
    LOG "Variable \$name is not either authority or server. Stopping"
    exit 1
  fi

  LOG "Building upstream... $container:$tag"
  rm -rf $repoPath && git clone $repoUrl $repoPath > /dev/null
  cd $repoPath > /dev/null
  git reset --hard $gitHash > /dev/null
  sed -i "s|$old*|$new|" $dockerFile
  docker build -f $dockerFile -t $container:$tag $repoPath
  cd - > /dev/null
}

function pullOrBuild() {
  container=$1
  hashTag=$2
  namedTag=$3
  gitHash=$4

  compareRemoteContainers $container:$namedTag $container:$hashTag
  if [ $? -eq 0 ]; then
    docker pull $container:$namedTag
  else
    buildUpstream $container $gitHash $hashTag
    LOG "Tagging $container SOURCE: $hashTag target: $namedTag"
    docker tag $container:$hashTag $container:$namedTag
  fi
}


# Authority
hashTag=$katzenAuthBranchHash
if [[ -n $warpedBuildFlags ]]; then
  hashTag=$katzenAuthWarpedHash
fi
pullOrBuild $katzenAuthContainer $hashTag $katzenAuthTag $katzenAuthBranchHash

# Server
hashTag=$katzenServerBranchHash
if [[ -n $warpedBuildFlags ]]; then
  hashTag=$katzenServerWarpedHash
fi
pullOrBuild $katzenServerContainer $hashTag $katzenServerTag $katzenServerBranchHash
