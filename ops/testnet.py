from os import path, mkdir
from typing import Tuple, List
from subprocess import run, check_output, PIPE, STDOUT
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

def generateTestnetConf(ip: str, confDir: str) -> List[str]:
    """
    Runs the genconfig tool at a specified directory
    and returns a list of paths of the generate configs
    """
    try: rmtree(confDir)
    except FileNotFoundError: pass
    mkdir(confDir)
    output = run([
        "genconfig",
        "-o",
        confDir,
        "-n",
        str(CONFIG["TEST"]["NODES"]),
        "-a",
        ip,
        "-p",
        str(CONFIG["TEST"]["PROVIDERS"]),
    ], stdout=PIPE, stderr=STDOUT)
    return [path.dirname(p.split(" ")[-1]) for p in output.stdout.decode().strip().split("\n")]

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
    confPaths = generateTestnetConf(ip, testnetConfDir)
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
        volumes=[p+":/conf" for p in confPaths if "nonvoting" in p],
    )
    idx=[i for i, p in enumerate(confPaths) if "nonvoting" in p][0]
    print(idx)
    confPaths.pop(idx)

    # TODO Change these ports numbers to be read from the config files!
    currentMixnetPortNumber = int(startingPortNumber)
    currentUserRegistrationPort = int(startingUserRegistrationPort)-1
    # We set this value with 35000 because there is no config file 
    # that we can scrape that has this value.
    currentPrometheusPort = 35000

    containerYaml = ""
    for confPath in confPaths:
        currentPrometheusPort += 1
        currentMixnetPortNumber += 1
        name=path.basename(confPath)
        ports = [
            "{0}:{0}".format(currentMixnetPortNumber),
            "{}:{}".format(currentPrometheusPort, "6543"),
        ]
        if "provider" in name:
            currentUserRegistrationPort += 1
            ports.append("{0}:{0}".format(currentUserRegistrationPort))

        containerYaml += genDockerService(
            name=name,
            image=REPOS["MESON"]["CONTAINER"]+":"+REPOS["MESON"]["NAMEDTAG"],
            ports=ports,
            volumes=[p+":/conf" for p in confPaths if name in p],
            dependsOn=["authority"]
        )

    # save compose file
    composePath = path.join(testnetConfDir, "testnet.yml")
    header = 'version: "3.7"\nservices:\n'
    with open(composePath, 'w+') as f:
        f.write("".join([header, authorityYAML, containerYaml ]))

    runDocker(ip, composePath)

main()
