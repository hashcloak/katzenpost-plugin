from os import path, mkdir
from typing import Tuple
from subprocess import run, check_output
from socket import socket
from tempfile import gettempdir
from shutil import rmtree

from config import CONFIG
from utils import genDockerService
REPOS = CONFIG["REPOS"]

clientTomlTemplate = """
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
"""

def generateTestnetConf(ip: str, confDir: str) -> None:
    """Runs the genconfig tool at a specified directory"""
    try: rmtree(confDir)
    except FileNotFoundError: pass
    mkdir(confDir)
    run([
        "genconfig",
        "-o",
        confDir,
        "-n",
        str(CONFIG["TEST"]["NODES"]),
        "-a",
        ip,
        "-p",
        str(CONFIG["TEST"]["PROVIDERS"]),
    ], check=True)


def getConfigValues(confDir: str) -> Tuple[str, str, str]:
    """Gets the public key, port number and registration port values from files"""
    with open(path.join(confDir, "nonvoting", "identity.public.pem"), 'r') as f:
        authorityPublicKey = f.read().split("\n")[1] # line index 1

    with open(path.join(confDir, "nonvoting", "authority.toml"), 'r') as f:
        for line in f:
            if "Addresses = [" in line:
                startingPortNumber = line.split('"')[1].split(":")[1]
                break

    with open(path.join(confDir, "provider-0", "katzenpost.toml"), 'r') as f:
        for line in f:
            if "UserRegistrationHTTPAddresses" in line:
                startingUserRegistrationPort = line.split('"')[1].split(":")[1]
                break

    return authorityPublicKey, startingPortNumber, startingUserRegistrationPort

def getIpAddress() -> str:
    """Gets the IP address that is accesible by all containers"""
    s = socket()
    s.connect(("1.1.1.1", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def runDocker(ip: str, composePath: str) -> None:
    """Starts Docker stack deploy. Starts a docker swarm if there isn't one"""
    output = check_output(["docker", "info"])
    if "Swarm: inactive" in output.decode():
        run(["docker", "swarm", "init", "--advertise-addr={}".format(ip)], check=True)

    run(["docker",
        "stack",
        "deploy",
        "-c",
        composePath,
        "mixnet",
        ], check=True)

    run(["docker", "service",  "ls", "--format", '"{{.Name}} with tag {{.Image}}"'])

def main():
    testnetConfDir = path.join(gettempdir(), "meson-testnet")
    ip = getIpAddress()
    generateTestnetConf(ip, testnetConfDir)
    authorityPublicKey, startingPortNumber, startingUserRegistrationPort = getConfigValues(testnetConfDir)

    # Save client.toml
    with open(path.join(testnetConfDir, "client.toml"), 'w+') as f:
        f.write(clientTomlTemplate.format(
            "true",
            ip,
            startingPortNumber,
            authorityPublicKey
        ))

    authorityYAML = genDockerService(
        name="authority",
        image=REPOS["AUTH"]["CONTAINER"]+":"+REPOS["AUTH"]["NAMEDTAG"],
        ports=["30000:30000"],
        volumes=["/tmp/meson-testnet/nonvoting:/conf"],
    )

    currentMixnetPortNumber = int(startingPortNumber)
    currentUserRegistrationPort = int(startingUserRegistrationPort)-1
    # We set this value with 35000 because there is no config file 
    # that we can scrape that has this value.
    currentPrometheusPort = 35000

    providersYAML = ""
    for idx in range(0, CONFIG["TEST"]["PROVIDERS"]):
        currentPrometheusPort += 1
        currentMixnetPortNumber += 1
        currentUserRegistrationPort += 1
        providersYAML += genDockerService(
            name="provider{}".format(idx),
            image=REPOS["MESON"]["CONTAINER"]+":"+REPOS["MESON"]["NAMEDTAG"],
            ports = [
                "{0}:{0}".format(currentMixnetPortNumber),
                "{0}:{0}".format(currentUserRegistrationPort),
                "{}:{}".format(currentPrometheusPort, "6543")
            ],
            volumes=[
                path.join(testnetConfDir, "provider-"+str(idx))+":"+"/conf"
            ],
            dependsOn=["authority"]
        )

    mixnodesYAML = ""
    for idx in range(0, CONFIG["TEST"]["NODES"]):
        currentPrometheusPort += 1
        currentMixnetPortNumber += 1
        mixnodesYAML += genDockerService(
            image=REPOS["MESON"]["CONTAINER"]+":"+REPOS["MESON"]["NAMEDTAG"],
            ports=[
                "{0}:{0}".format(currentMixnetPortNumber),
                "{}:{}".format(currentPrometheusPort, "6543")
            ],
            volumes=[
                path.join(testnetConfDir, "node-"+str(idx))+":"+"/conf"
            ],
            dependsOn=["authority"],
            name="node{}".format(idx),
        )

    # save compose file
    composePath = path.join(testnetConfDir, "testnet.yml")
    header = 'version: "3.7"\nservices:\n'
    with open(composePath, 'w+') as f:
        f.write("".join([header, authorityYAML, providersYAML, mixnodesYAML]))

    runDocker(ip, composePath)

main()
