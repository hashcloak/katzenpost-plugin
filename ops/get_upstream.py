import tempfile
import fileinput
import os
import subprocess as sp

from setup import *

def updateDockerFile(dockerFile):
    for line in fileinput.input(dockerFile, inplace=True):
        newLine = line
        if "RUN cd cmd/" in line and "go build":
            newLine = "{} {}\n".format(line.strip(), warpedBuildFlags)

        print(newLine, end='')

def buildUpstream(container, tag, gitHash):

    name = container.split("/")[1]
    repoPath = os.path.join(tempfile.TemporaryDirectory().name, name)

    if name == "authority":
        dockerFile = os.path.join(repoPath, "Dockerfile.nonvoting")
        repoUrl = DEFAULT_VALUES["KATZEN"]["AUTH"]["REPOSITORY"]
    elif name =="server":
        dockerFile = os.path.join(repoPath, "Dockerfile")
        repoUrl = DEFAULT_VALUES["KATZEN"]["SERVER"]["REPOSITORY"]

    
    sp.run(["git", "clone", repoUrl, repoPath], check=True)
    os.chdir(repoPath)
    sp.run(["git", "checkout", gitHash], check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if "warped" in tag: updateDockerFile(dockerFile)
    #print(sp.check_output(["cat", dockerFile]).decode("utf-8"))
    args = ["docker", "build", "-t", "{}:{}".format(container, tag), "-f", dockerFile, repoPath]
    sp.run(args, check=True)

def pullOrBuild(container, tag, gitHash):

    hashTag = "warped_"+gitHash if tag == "warped" else tag

    if compareRemoteContainers(container+":"+tag, container+":"+hashTag):
        sp.run(["docker", "pull", "{}:{}".format(container, hashTag)], check=True)
    else:
        print("\nLOG: Building {}:{}\n".format(container, hashTag))
        buildUpstream(container, hashTag, gitHash)
        print("\nLOG: Tagging {}:{}\n".format(container, hashTag))
        arguments = [
                "docker",
                "tag",
                "{}:{}".format(container, hashTag),
                "{}:{}".format(container, tag),
            ]
        sp.run(arguments, check=True)



pullOrBuild(
    DEFAULT_VALUES["KATZEN"]["SERVER"]["CONTAINER"],
    DEFAULT_VALUES["KATZEN"]["SERVER"]["DOCKERTAG"],
    DEFAULT_VALUES["KATZEN"]["SERVER"]["GITHASH"],
)
pullOrBuild(
    DEFAULT_VALUES["KATZEN"]["AUTH"]["CONTAINER"],
    DEFAULT_VALUES["KATZEN"]["AUTH"]["DOCKERTAG"],
    DEFAULT_VALUES["KATZEN"]["AUTH"]["GITHASH"],
)
