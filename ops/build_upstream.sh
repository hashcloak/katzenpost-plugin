#!/usr/bin/env bash
set -eo pipefail
source ops/common.sh

# it takes in a repository and a githash and builds the containers
name=$(echo -n $1 | cut -f2 -d/) 
container=$1
gitHash=$2
tag=$gitHash
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

LOG "Building upstream... $container:$gitHash"
rm -rf $repoPath && git clone $repoUrl $repoPath > /dev/null
cd $repoPath > /dev/null
git -c advice.detachedHead="false" checkout $gitHash > /dev/null
sed -i "s|$old*|$new|" $dockerFile
docker build -f $dockerFile -t $container:$gitHash $repoPath
cd - > /dev/null
