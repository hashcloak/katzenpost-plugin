from os import path, curdir
from subprocess import run
from tempfile import gettempdir, NamedTemporaryFile
import urllib.request
from json import loads

from config import (
    CONFIG,
    checkoutRepo,
    warpedBuildFlags,
)

dockerApiUrl="https://hub.docker.com/v2/repositories"

def doesContainerExistsInCloud(name, tag):
    try:
        urllib.request.urlopen("{}/{}/tags/{}".format(dockerApiUrl, name, tag)).read()
    except urllib.error.HTTPError:
        return False

    return True

def getContainerInfo(name, tag):
    if not doesContainerExistsInCloud(name, tag):
        return None

    url = "{}/{}/tags/{}".format(dockerApiUrl, name, tag)
    return loads(urllib.request.urlopen(url).read().decode())

def compareRemoteContainers(ctrOne, ctrTwo):
    name1 = ctrOne.split(":")[0]
    tag1 = ctrOne.split(":")[1]
    name2 = ctrTwo.split(":")[0]
    tag2 = ctrTwo.split(":")[1]
    if not doesContainerExistsInCloud(name1, tag1) or \
            not doesContainerExistsInCloud(name2, tag2):
        return False

    return getContainerInfo(name1, tag1)['images'][0]['digest'] == \
            getContainerInfo(name2, tag2)['images'][0]['digest']

def buildContainer(container, tag, dockerFile, path):
    print("\nLOG: Building {}:{}\n".format(container, tag))
    run([
        "docker",
        "build",
        "-t",
        "{}:{}".format(container, tag),
        "-f",
        dockerFile,
        path
    ], check=True)

def reTag(container, tag1, tag2):
    print("\nLOG: Tagging {} {} -> {}\n".format(container, tag1, tag2))
    run([
        "docker",
        "tag",
        "{}:{}".format(container, tag1),
        "{}:{}".format(container, tag2)
    ], check=True)

def prepareDockerBuildContext(name, gitHash):
    repoPath = path.join(gettempdir(), name)
    if name == "authority":
        dockerFile = path.join(repoPath, "Dockerfile.nonvoting")
        checkoutRepo(repoPath, CONFIG["AUTH"]["REPOSITORY"], gitHash)
    elif name == "server":
        dockerFile = path.join(repoPath, "Dockerfile")
        checkoutRepo(repoPath, CONFIG["SERVER"]["REPOSITORY"], gitHash)
    elif name == "meson":
        repoPath = curdir
        dockerFile = "Dockerfile"

    tmpdf = NamedTemporaryFile().name
    with open(dockerFile, 'r') as infile, open(tmpdf, 'w+') as output:
        for line in infile:
            if "RUN cd cmd/" in line and "go build" in line and CONFIG["WARPED"]:
                line = line.strip() + " " + warpedBuildFlags + "\n"
            if CONFIG["SERVER"]["CONTAINER"] in line and CONFIG["WARPED"]:
                line = "FROM {}:{}\n".format(
                        CONFIG["SERVER"]["CONTAINER"],
                        CONFIG["SERVER"]["TAGS"]["NAMED"],
                    )

            output.write(line)

    return tmpdf, repoPath

for key in ["AUTH", "SERVER", "MESON"]:
    container = CONFIG[key]["CONTAINER"],
    namedTag = CONFIG[key]["TAGS"]["NAMED"],
    hashTag = CONFIG[key]["TAGS"]["HASH"],
    gitHash = CONFIG[key]["GITHASH"],
    if compareRemoteContainers(container+":"+namedTag, container+":"+hashTag):
        run([
            "docker",
            "pull",
            "{}:{}".format(container, namedTag)
        ], check=True)
    else:
        dockerFile, repoPath = prepareDockerBuildContext(container.split("/")[-1], gitHash)
        buildContainer(container, hashTag, dockerFile, repoPath)
        reTag(container, hashTag, namedTag)
