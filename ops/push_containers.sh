#!/usr/bin/env bash
source ops/common.sh

function pushContainer() {
  containerExistsInCloud $$
  if [ $? -eq 1 ]; then
    docker push $container
  fi
}

pushContainer hashcloak/server:$katzenBaseServerTag
pushContainer hashcloak/server:$katzenServerMasterHash

pushContainer hashcloak/authority:$katzenBaseAuthTag
pushContainer hashcloak/authority:$katzenAuthMasterHash

pushContainer hashcloak/meson:$mesonCurrentBranchHash
pushContainer hashcloak/meson:$mesonCurrentBranchTag