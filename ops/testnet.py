from os import path, mkdir
from typing import Tuple
from subprocess import run, check_output
from socket import socket
from tempfile import gettempdir
from shutil import rmtree

from config import CONFIG
REPOS = CONFIG["REPOS"]

def generateClientTOML(
    tmpDir: str,
    authIP: str,
    startingPortNumber: str,
    authorityPublicKey:str,
    decoyTraffic="true"
) -> None:
    """Generates the client toml file used by the clients to connect
    to the mixnet"""
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

def genAuthorityYaml(
    container: str,
    confDir: str,
    mixnetPort: str,
    number=""
) -> str:
    """Generates the compose file syntax for the authority container"""
    return """
  authority{number}:
    image: {container}
    volumes:
      - {confDir}/nonvoting:/conf
    ports:
      - "{mixnetPort}:{mixnetPort}"
""".format(
        number=number,
        container=container,
        confDir=confDir,
        mixnetPort=mixnetPort
    )

def genProviderYaml(
    number: str,
    container: str,
    confDir: str,
    mixnetPort: str,
    registrationPort: str,
    prometheusPort: str
) -> str:
    """Generates the compose file syntax provider container"""
    return """
  provider{number}:
    image: {container}
    volumes:
      - {confDir}/provider-{number}:/conf
    ports:
      - "{mixnetPort}:{mixnetPort}"
      - "{registrationPort}:{registrationPort}"
      - "{prometheusPort}:6543"
    depends_on:
      - "authority"
""".format(
        number=number,
        container=container,
        confDir=confDir,
        mixnetPort=mixnetPort,
        registrationPort=registrationPort,
        prometheusPort=prometheusPort,
    )

def genMixNodeYaml(
    number: str,
    container: str,
    confDir: str,
    mixnetPort: str,
    prometheusPort: str
) -> str:
    """Generates the compose file syntax mix node container"""
    return """
  node{number}:
    image: {container}
    volumes:
      - {confDir}/node-{number}:/conf
    ports:
      - "{mixnetPort}:{mixnetPort}"
      - "{prometheusPort}:6543"
    depends_on:
      - "authority"
""".format(
        number=number,
        container=container,
        confDir=confDir,
        mixnetPort=mixnetPort,
        prometheusPort=prometheusPort,
    )

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
    generateClientTOML(testnetConfDir, ip, startingPortNumber, authorityPublicKey)

    authorityYAML = genAuthorityYaml(
            REPOS["AUTH"]["CONTAINER"]+":"+REPOS["AUTH"]["NAMEDTAG"],
            testnetConfDir,
            startingPortNumber
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
        providersYAML += genProviderYaml(
                str(idx),
                REPOS["MESON"]["CONTAINER"]+":"+REPOS["MESON"]["NAMEDTAG"],
                testnetConfDir,
                str(currentMixnetPortNumber),
                str(currentUserRegistrationPort),
                str(currentPrometheusPort)
            )

    mixnodesYAML = ""
    for idx in range(0, CONFIG["TEST"]["NODES"]):
        currentPrometheusPort += 1
        currentMixnetPortNumber += 1
        mixnodesYAML += genMixNodeYaml(
                str(idx),
                REPOS["MESON"]["CONTAINER"]+":"+REPOS["MESON"]["NAMEDTAG"],
                testnetConfDir,
                str(currentMixnetPortNumber),
                str(currentPrometheusPort)
            )

    # save compose file
    composePath = path.join(testnetConfDir, "testnet.yml")
    with open(composePath, 'w+') as f:
        f.write('version: "3.7"\nservices:\n' + authorityYAML + providersYAML + mixnodesYAML)

    runDocker(ip, composePath)

main()
