from os import path, mkdir
from subprocess import check_output
from socket import socket
from tempfile import gettempdir
from shutil import rmtree

from setup import DEFAULT_VALUES

def generateClientTOML(tmpDir, authIP, startingPortNumber, authorityPublicKey, decoyTraffic="true"):
    with open(path.join(tmpDir, "client.toml"), 'w+') as f:
        f.write(
            """
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
            """.format(decoyTraffic, authIP, startingPortNumber, authorityPublicKey)
        )

# get ip address
s = socket()
s.connect(("hashcloak.com", 80))
ip = s.getsockname()[0]
print("Accesible IP address: ", ip)
s.close()

testnetConfDir = path.join(gettempdir(), "meson-testnet")
try: rmtree(testnetConfDir)
finally: mkdir(testnetConfDir)

check_output([
    "genconfig",
    "-o",
    testnetConfDir,
    "-n",
    str(DEFAULT_VALUES["TESTNET"]["NODES"]),
    "-a",
    ip,
    "-p",
    str(DEFAULT_VALUES["TESTNET"]["PROVIDERS"]),
])

# open some files to read their contents
with open(path.join(testnetConfDir, "nonvoting", "identity.public.pem"), 'r') as f:
    authorityPublicKey = f.read().split("\n")[1] # line index 1

with open(path.join(testnetConfDir, "nonvoting", "authority.toml"), 'r') as f:
    for line in f:
        if "Addresses = [" in line:
            startingPortNumber = line.split('"')[1].split(":")[1]
            break

with open(path.join(testnetConfDir, "provider-0", "katzenpost.toml"), 'r') as f:
    for line in f:
        if "UserRegistrationHTTPAddresses" in line:
            startingUserRegistrationPort = line.split('"')[1].split(":")[1]
            break

generateClientTOML(testnetConfDir, ip, startingPortNumber, authorityPublicKey)

composeYMLFile = """
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
    testnetConfDir,
    startingPortNumber
)

currentMixnetPortNumber = int(startingPortNumber)
currentPrometheusPort = 35000
# This one is -1 because it isn't used by the authority but
# it is used by the providers
currentUserRegistrationPort = int(startingUserRegistrationPort)-1

# append provider configuration
for idx in range(0, DEFAULT_VALUES["TESTNET"]["PROVIDERS"]):
    currentPrometheusPort += 1
    currentMixnetPortNumber += 1
    currentUserRegistrationPort += 1
    composeYMLFile += """
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
    testnetConfDir,
    str(currentMixnetPortNumber),
    str(currentUserRegistrationPort),
    str(currentPrometheusPort),
)

# append mixnode configuration
for idx in range(0, DEFAULT_VALUES["TESTNET"]["NODES"]):
    currentPrometheusPort += 1
    currentMixnetPortNumber += 1
    composeYMLFile += """
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
    testnetConfDir,
    str(currentMixnetPortNumber),
    str(currentPrometheusPort),
)

# save compose file
with open(path.join(testnetConfDir, "testnet.yml"), 'w+') as f:
    f.write(composeYMLFile)

print("\n", check_output(
    ["docker",
    "stack",
    "deploy",
    "-c",
    path.join(testnetConfDir, "testnet.yml"),
    "mixnet",],
    encoding="utf-8")
)
