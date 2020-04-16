#!/usr/bin/env bash
source ops/common.sh
source ops/build_upstream.sh

branchTag=$katzenAuthContainer:$katzenBaseAuthTag
hashTag=$katzenAuthContainer:$katzenAuthMasterHash
compareRemoteContainers $branchTag $hashTag
if [ $? -eq 0 ]; then
  docker pull $branchTag
else
  pullOrBuild $hashTag
  LOG "Tagging $katzenAuthContainer: SOURCE: $branchTag TARGET: $hashTag "
  docker tag $hashTag $branchTag
fi

branchTag=$katzenServerContainer:$katzenBaseServerTag
hashTag=$katzenServerContainer:$katzenServerMasterHash
compareRemoteContainers $branchTag $hashTag
if [ $? -eq 0 ]; then
  docker pull $branchTag
else
  pullOrBuild $hashTag
  LOG "Taggin $katzenServerMasterHash: SOURCE: $hashTag TARGET: $branchTag"
  docker tag $hashTag $branchTag
fi
