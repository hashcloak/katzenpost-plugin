#!/usr/bin/env bash
source ops/common.sh

function pushContainer() {
  if ! containerExistsInCloud $1; then
    docker push $container
  fi
}

pushContainer $katzenAuthContainer:$katzenBaseAuthTag
pushContainer $katzenAuthContainer:$katzenAuthMasterHash

pushContainer $katzenServerContainer:$katzenBaseServerTag
pushContainer $katzenServerContainer:$katzenServerMasterHash

pushContainer $mesonContainer:$mesonCurrentBranchHash
pushContainer $mesonContainer:$mesonCurrentBranchTag
