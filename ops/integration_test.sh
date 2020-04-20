#!/usr/bin/env bash
source ops/common.sh
set -ex

# $1 Service to use
# $2 Provider name
# $3 private key
function runIntegrationTest() {
  if [ -z "$3" ]; then
    echo "Need to set the private key"
    exit -1
  fi

  # This way of running the command is needed
  # to properly expand the warpedBuildFlags variable
  commandToRun="go run $warpedBuildFlags \
  /tmp/Meson-client/integration/tests.go \
  -c /tmp/meson-current/client.toml \
  -t $1 -s $1 \
  -k /tmp/meson-current/$2/currency.toml \
  -pk $3"

  /bin/bash -c "$commandToRun"
}

rm -rf /tmp/Meson-client
 git clone https://github.com/hashcloak/Meson-client /tmp/Meson-client
 cd /tmp/Meson-client && git fetch && git checkout $mesonClientTestCommit

runIntegrationTest gor provider-0 $ETHEREUM_PK
#runIntegrationTest tbnb provider-1 $BINANCE_PK
