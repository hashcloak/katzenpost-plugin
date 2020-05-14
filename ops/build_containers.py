from os import path, curdir
from subprocess import run
from tempfile import gettempdir
import urllib.request
from json import loads

from config import CONFIG, checkoutRepo

dockerApiUrl="https://hub.docker.com/v2/repositories"

def doesContainerExistsInCloud(name, tag):
    try:
        urllib.request.urlopen("{}/{}/tags/{}".format(dockerApiUrl, name, tag)).read()
    except urllib.error.HTTPError:
        return False

    return True

def getContainerInfo(name, tag):
    if not doesContainerExistsInCloud(name, tag):
        return {}

    url = "{}/{}/tags/{}".format(dockerApiUrl, name, tag)
    return loads(urllib.request.urlopen(url).read().decode())

def compareRemoteContainers(containerOne, containerTwo):
    info1 = getContainerInfo(containerOne.split(":")[0], containerOne.split(":")[1])
    info2 = getContainerInfo(containerTwo.split(":")[0], containerTwo.split(":")[1])
    if not info1 or not info2:
        return False

    return info1['images'][0]['digest'] == info2['images'][0]['digest']

def buildContainer(container, tag, dockerFile, path):
    print("\nLOG: Building {}:{}\n".format(container, tag))
    args = [
        "docker",
        "build",
        "-t",
        "{}:{}".format(container, tag),
        "-f",
        dockerFile,
        path,
    ]

    if CONFIG["WARPED"]:
        args.extend(["--build-arg", "warped=true", "--build-arg", "server=warped"])

    for a in args: print(a, end=' ')
    print(end='\n\n')

    run(args, check=True)

def reTag(container, tag1, tag2):
    print("\nLOG: Tagging {} {} -> {}\n".format(container, tag1, tag2))
    run([
        "docker",
        "tag",
        "{}:{}".format(container, tag1),
        "{}:{}".format(container, tag2)
    ], check=True)

for repo in CONFIG["REPOS"].values():
    container = repo["CONTAINER"]
    namedTag = "warped_"+repo["BRANCH"] if CONFIG["WARPED"] else repo["BRANCH"]
    hashTag = "warped_"+repo["GITHASH"] if CONFIG["WARPED"] else repo["GITHASH"]

    if compareRemoteContainers(container+":"+namedTag, container+":"+hashTag):
        run([
            "docker",
            "pull",
            "{}:{}".format(container, namedTag)
        ], check=True)
    else:
        name = repo["CONTAINER"].split("/")[-1]
        repoPath = path.join(gettempdir(), name)
        if name == "meson":
            repoPath = curdir
        else:
            checkoutRepo(repoPath, repo["REPOSITORY"], repo["GITHASH"])

        dockerFile = "Dockerfile" if name != "authority" else "Dockerfile.nonvoting"

        buildContainer(container, hashTag, path.join(repoPath, dockerFile), repoPath)
        reTag(container, hashTag, namedTag)
