#!/usr/bin/env bash
source ops/common.sh

function pushContainer() {
  if ! containerExistsInCloud $1; then
    docker push $container
  fi
}

pushContainer $katzenAuthContainer:$katzenAuthTag
pushContainer $katzenAuthContainer:$katzenAuthBranchHash

pushContainer $katzenServerContainer:$katzenServerTag
pushContainer $katzenServerContainer:$katzenServerBranchHash

pushContainer $mesonContainer:$mesonCurrentBranchHash
pushContainer $mesonContainer:$mesonCurrentBranchTag
