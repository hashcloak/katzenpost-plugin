#!/usr/bin/env bash
source ops/common.sh

# Authority
namedtag=$katzenauthcontainer:$katzenbaseauthtag
hashtag=$katzenauthcontainer:$katzenauthmasterhash
if [[ -n  $warpedbuildflags ]]; then
  namedtag=$katzenauthcontainer:warped
  hashtag=$katzenauthcontainer:warped$katzenauthmasterhash
fi

compareRemoteContainers $namedtag $hashtag
if [ $? -eq 0 ]; then
  docker pull $namedtag
else
  bash ops/build_upstream.sh $katzenauthcontainer $katzenauthmasterhash
  log "tagging $katzenauthcontainer source: $hashtag target: $namedtag"
  docker tag  $hashtag $namedtag
fi

# Server
namedTag=$katzenServerContainer:$katzenBaseServerTag
hashTag=$katzenServerContainer:$katzenServerMasterHash
if [[ -n  $warpedBuildFlags ]]; then
  namedTag=$katzenServerContainer:warped
  hashTag=$katzenServerContainer:warped$katzenServerMasterHash
fi

compareRemoteContainers $namedTag $hashTag
if [ $? -eq 0 ]; then
  docker pull $namedTag
else
  bash ops/build_upstream.sh $katzenServerContainer $katzenServerMasterHash
  LOG "Tagging $katzenServerContainer SOURCE: $hashTag TARGET: $namedTag"
  docker tag  $hashTag $namedTag
fi
