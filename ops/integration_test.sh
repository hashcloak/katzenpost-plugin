#!/usr/bin/env bash
set -e
source ops/common.sh

# $1 Service to use
# $2 Provider name
# $3 private key
function runIntegrationTest() {
  if [ -z "$3" ]; then
    echo "Need to set the private key"
    exit -1
  fi
  go run $warpedBuildFlags \
  /tmp/Meson-client/integration/tests.go \
  -c /tmp/meson-current/client.toml \
  -t $1 -s $1 \
  -k /tmp/meson-current/$2/currency.toml \
  -pk $3
}

rm -rf /tmp/Meson-client
git clone https://github.com/hashcloak/Meson-client /tmp/Meson-client 
cd /tmp/Meson-client && git reset --hard $mesonClientTestCommit

runIntegrationTest gor provider-0 $ETHEREUM_PK
runIntegrationTest tbnb provider-1 $BINANCE_PK
