#!/usr/bin/env bash
source ops/common.sh

function pullOrBuild() {
  container=$(echo -n $1 | cut -f1 -d:)
  tag=$(echo -n $1 | cut -f2 -d:)
  if containerExistsInCloud $container:$tag; then
    docker pull $container:$tag
  else
    LOG "Upstream $container:$tag not found. Building..."
    buildUpstream $container $tag
  fi
}

function buildUpstream() {
  name=$(echo -n $1 | cut -f2 -d/)
  container=$1
  tag=$2
  repoPath=/tmp/$name

  if [[ "$name" == "" ]]; then
    LOG "Var \$name not set. Stopping"
    exit 1
  fi

  if [[ "$name" == "authority" ]]; then
    # using nonvoting authority
    repoUrl=$katzenAuthRepo
    dockerFile=$repoPath/Dockerfile.nonvoting
    old="RUN cd cmd/nonvoting \&\& go build"
    new="RUN cd cmd/nonvoting \&\& go build $warpedBuildFlags"
  fi

  if [[ "$name" == "server" ]]; then
    repoUrl=$katzenServerRepo
    dockerFile=$repoPath/Dockerfile
    old="RUN cd cmd/server \&\& go build"
    new="RUN cd cmd/server \&\& go build $warpedBuildFlags"
  fi

  LOG "Building upstream... $container:$tag"
  rm -rf $repoPath
  git clone $repoUrl $repoPath > /dev/null
  cd $repoPath
  git -c advice.detachedHead="false" checkout $tag > /dev/null
  sed -i "s|$old*|$new\n|" $dockerFile
  docker build -f $dockerFile -t $container:$tag $repoPath
  cd -
}
