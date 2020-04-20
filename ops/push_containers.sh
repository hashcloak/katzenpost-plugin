#!/usr/bin/env bash
source ops/common.sh
docker push $katzenAuthContainer:$katzenAuthTag
docker push $katzenAuthContainer:$katzenAuthBranchHash
docker push $katzenServerContainer:$katzenServerTag
docker push $katzenServerContainer:$katzenServerBranchHash
docker push $mesonContainer:$mesonCurrentBranchHash
docker push $mesonContainer:$mesonCurrentBranchTag
