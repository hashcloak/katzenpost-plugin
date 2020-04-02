#!/usr/bin/env bash
source ops/common.sh

function generateClientToml() {
# $1 DisableDecoyTraffic
# $2 Authority's public ipv4 address
# $3 Authority's Public key
  cat - > /tmp/meson-current/client.toml <<EOF
[Logging]
  Disable = false
  Level = "DEBUG"
  File = ""

[UpstreamProxy]
  Type = "none"

[Debug]
  DisableDecoyTraffic = $1
  CaseSensitiveUserIdentifiers = false
  PollingInterval = 1

[NonvotingAuthority]
    Address = "$2:30000"
    PublicKey = "$3"
EOF
}

numberMixNodes=${NUMBER_NODES:-2}
numberProviders=${NUMBER_PROVIDERS:-2}
startingPortNumber=30000
globalPortIndex=0

tempDir=$(mktemp -d /tmp/meson-conf.XXXX)
rm -f /tmp/meson-current
ln -s $tempDir /tmp/meson-current
publicIP=$(ip route get 1 | head -1 | sed 's/.*src//' | cut -f2 -d' ')
genconfig -o /tmp/meson-current -n $numberMixNodes -a $publicIP -p $numberProviders
authorityPublicKey=$(cat /tmp/meson-current/nonvoting/identity.public.pem | grep -v "PUBLIC")
generateClientToml true $publicIP $authorityPublicKey

composeFile=$tempDir/testnet-compose.yml 
# we will need to add a federated prometheus node here
cat - > $composeFile<<EOF
version: "3.7"
services:
  authority:
    image: hashcloak/authority:$katzenBaseAuthTag
    volumes:
      - /tmp/meson-current/nonvoting:/conf
    ports:
      - "$startingPortNumber:$startingPortNumber"

EOF

for i in $(seq 0 $(($numberProviders-1))); do
  globalPortIndex=$(($globalPortIndex+1))
  # the 30000 40000 port values are hardcodeed in genconfig
  # which is why static port numbers need to be used
  mixnetPort=$((30000+$globalPortIndex))
  httpRegistrationPort=$((40000+$globalPortIndex))
  prometheusPort=$((35000+$globalPortIndex))
  cat - >> $composeFile<<EOF
  provider$i:
    image: hashcloak/meson:$mesonCurrentBranchTag
    volumes:
      - /tmp/meson-current/provider-$i:/conf
    ports:
      - "$mixnetPort:$mixnetPort"
      - "$httpRegistrationPort:$httpRegistrationPort"
      - "$prometheusPort:6543"
    depends_on:
      - "authority"

EOF
done

for i in $(seq 0 $(($numberMixNodes-1))); do
  globalPortIndex=$(($globalPortIndex+1))
  # the 30000 40000 port values are hardcodeed in genconfig
  # which is why static port numbers need to be used
  mixnetPort=$((30000+$globalPortIndex))
  prometheusPort=$((35000+$globalPortIndex))
  cat - >> $composeFile<<EOF
  node$i:
    image: hashcloak/meson:$mesonCurrentBranchTag
    volumes:
      - /tmp/meson-current/node-$i:/conf
    ports:
      - "$mixnetPort:$mixnetPort"
      - "$prometheusPort:6543"
    depends_on:
      - "authority"

EOF
done

docker stack deploy -c $composeFile mixnet
