import tempfile
import os
import subprocess as sp
import socket

from setup import *

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("1.1.1.1", 80))
ip = s.getsockname()[0]
print("IP address: ", ip)
s.close()

tmpDir = tempfile.mkdtemp(prefix='meson-', suffix='')
mixnodeQuantity = 2 #DEFAULT_VALUES["TESTNET"]["NODES"]
providerQuantity = 2 #DEFAULT_VALUES["TESTNET"]["PROVIDERS"]

print(tmpDir)

args = [
    "genconfig",
    "-o",
    tmpDir,
    "-n",
    str(mixnodeQuantity),
    "-a",
    ip,
    "-p",
    str(providerQuantity),
]

# We could try to capture the paths that this command
# outputs to use in the concatenation of the compose file
# This makes it that there is a single source of truth of where the config
# files should be sourced from instead of manually counting in the loops
#
# Example of the output is:
# 2020/04/27 22:56:43 saveCfg of /tmp/meson-2iybfqej/nonvoting/authority.toml
# 2020/04/27 22:56:43 saveCfg of /tmp/meson-2iybfqej/provider-0/katzenpost.toml
# 2020/04/27 22:56:43 saveCfg of /tmp/meson-2iybfqej/provider-1/katzenpost.toml
# 2020/04/27 22:56:43 saveCfg of /tmp/meson-2iybfqej/node-0/katzenpost.toml
# 2020/04/27 22:56:43 saveCfg of /tmp/meson-2iybfqej/node-1/katzenpost.toml
sp.run(args, check=True)

with open(os.path.join(tmpDir, "nonvoting", "identity.public.pem"), 'r') as f:
    authorityPublicKey = f.read().split("\n")[1] # line index 1

with open(os.path.join(tmpDir, "nonvoting", "authority.toml"), 'r') as f:
    for line in f:
        if "Addresses = [" in line:
            startingPortNumber = line.split('"')[1].split(":")[1]
            break

clientToml = """
[Logging]
  Disable = false
  Level = "DEBUG"
  File = ""

[UpstreamProxy]
  Type = "none"

[Debug]
  DisableDecoyTraffic = {}
  CaseSensitiveUserIdentifiers = false
  PollingInterval = 1

[NonvotingAuthority]
    Address = "{}:{}"
    PublicKey = "{}"
""".format("true", ip, startingPortNumber, authorityPublicKey)

with open(os.path.join(tmpDir, "client.toml"), 'w+') as f:
    f.write(clientToml)

composeFile = """
version: "3.7"
services:
  authority:
    image: {0}:{1}
    volumes:
      - {2}/nonvoting:/conf
    ports:
      - "{3}:{3}"
""".format(
        DEFAULT_VALUES["KATZEN"]["AUTH"]["CONTAINER"],
        DEFAULT_VALUES["KATZEN"]["AUTH"]["DOCKERTAG"],
        tmpDir,
        startingPortNumber
    )

with open(os.path.join(tmpDir, "provider-0", "katzenpost.toml"), 'r') as f:
    for line in f:
        if "UserRegistrationHTTPAddresses" in line:
            startingUserRegistrationPort = line.split('"')[1].split(":")[1]
            break


currentMixnetPortNumber = int(startingPortNumber)
currenPrometheusPort = 35000
currentUserRegistrationPort = int(startingUserRegistrationPort)
for idx in range(0, providerQuantity):
    currenPrometheusPort += 1
    currentMixnetPortNumber += 1
    currentUserRegistrationPort += 1
    composeFile += """
  provider{0}:
    image: {1}:{2}
    volumes:
      - {3}/provider-{0}:/conf
    ports:
      - "{4}:{4}"
      - "{5}:{5}"
      - "{6}:6543"
    depends_on:
      - "authority"
""".format(
        str(idx),
        DEFAULT_VALUES["HASHCLOAK"]["MESON"]["CONTAINER"],
        DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"],
        tmpDir,
        str(currentMixnetPortNumber),
        str(currentUserRegistrationPort),
        str(currenPrometheusPort),
    )

for idx in range(0, mixnodeQuantity):
    currenPrometheusPort += 1
    currentMixnetPortNumber += 1
    composeFile += """
  node{0}:
    image: {1}:{2}
    volumes:
      - {3}/node-{0}:/conf
    ports:
      - "{4}:{4}"
      - "{5}:6543"
    depends_on:
      - "authority"
""".format(
        str(idx),
        DEFAULT_VALUES["HASHCLOAK"]["MESON"]["CONTAINER"],
        DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"],
        tmpDir,
        str(currentMixnetPortNumber),
        str(currenPrometheusPort),
    )


with open(os.path.join(tmpDir, "testnet.yml"), 'w+') as f:
    f.write(composeFile)

args = [
    "docker",
    "stack",
    "deploy",
    "-c",
    os.path.join(tmpDir, "testnet.yml"),
    "mixnet",
]
sp.run(args, check=True)
