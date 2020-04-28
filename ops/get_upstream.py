import fileinput

from os import path, chdir
from subprocess import run
from tempfile import gettempdir

from setup import CONFIG, compareRemoteContainers, warpedBuildFlags, checkoutRepo

def updateDockerFile(dockerFile):
    for line in fileinput.input(dockerFile, inplace=True):
        newLine = line
        if "RUN cd cmd/" in line and "go build":
            newLine = "{} {}\n".format(line.strip(), warpedBuildFlags)

        print(newLine, end='')

def buildUpstream(container, tag, gitHash):

    name = container.split("/")[1]
    repoPath = path.join(gettempdir(), name)

    if name == "authority":
        dockerFile = path.join(repoPath, "Dockerfile.nonvoting")
        repoUrl = CONFIG["AUTH"]["REPOSITORY"]
    elif name =="server":
        dockerFile = path.join(repoPath, "Dockerfile")
        repoUrl = CONFIG["SERVER"]["REPOSITORY"]

    checkoutRepo(repoPath, repoUrl, gitHash.split("_")[-1])

    if CONFIG["WARPED"]: updateDockerFile(dockerFile)
    #print(sp.run(["cat", dockerFile]))
    run([
        "docker",
        "build",
        "-t",
        "{}:{}".format(container, tag),
        "-f", dockerFile,
        repoPath
    ])

def pullOrBuild(container, namedTag, hashTag):

    if compareRemoteContainers(container+":"+namedTag, container+":"+hashTag):
        run([
            "docker",
            "pull",
            "{}:{}".format(container, namedTag)
        ], check=True)
    else:
        print("\nLOG: Building {}:{}\n".format(container, hashTag))
        buildUpstream(container, hashTag, hashTag)
        print("\nLOG: Retagging {} from: {} to: {} tag\n".format(
                container,
                hashTag,
                namedTag,
            )
        )
        run([
            "docker",
            "tag",
            "{}:{}".format(container, hashTag),
            "{}:{}".format(container, namedTag),
        ], check=True)

for key in ["AUTH", "SERVER"]:
    pullOrBuild(
        CONFIG[key]["CONTAINER"],
        CONFIG[key]["TAGS"]["NAMED"],
        CONFIG[key]["TAGS"]["HASH"]
    )
