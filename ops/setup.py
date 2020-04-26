#!/usr/bin/env python3
import os
import subprocess as sp
import urllib.request
import json
import pprint

dockerApiUrl="https://hub.docker.com/v2/repositories"
gitHashLength=7
warpedBuildFlags='-ldflags "-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true"'

DEFAULT_VALUES = {
    "KATZEN": {
        "AUTH": {
            "CONTAINER": "hashcloak/authority",
            "REPOSITORY": "https://github.com/katzenpost/authority",
            "BRANCH": "master",
            "DOCKERTAG": "master",
            "GITHASH": "",
        },
        "SERVER" : {
            "CONTAINER": "hashcloak/server",
            "REPOSITORY": "https://github.com/katzenpost/server",
            "BRANCH": "master",
            "DOCKERTAG": "master",
            "GITHASH": "",
        },
    },
    "HASHCLOAK": {
        "MESON": {
            "CONTAINER": "hashcloak/meson",
            "DOCKERTAG": "master",
            "BRANCH": "",
            "GITHASH": "",
        },
        "CLIENT":{
            "TEST": {
                "COMMIT": "master"
            }
        }
    },
}

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
    return json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

def compareRemoteContainers(ctrOne, ctrTwo):
    nameOne = ctrOne.split(":")[0]
    tagOne = ctrOne.split(":")[1]
    nameTwo = ctrTwo.split(":")[0]
    tagTwo = ctrTwo.split(":")[1]

    if not doesContainerExistsInCloud(nameOne, tagTwo) or \
            not doesContainerExistsInCloud(nameTwo, tagTwo):
        return False

    return getContainerInfo(nameOne, tagOne)['images'][0]['digest'] == \
            getContainerInfo(nameTwo, tagTwo)['images'][0]['digest']


def getRemoteGitHash(repositoryURL, branch):
    arguments = ["git", "ls-remote", "--heads", repositoryURL, branch]
    return sp.check_output(arguments).decode("utf-8").split('\t')[0][:gitHashLength]

def getLocalGitBranch():
    try:
        if os.environ['TRAVIS_EVENT_TYPE'] == "pull_request":
            gitBranch = os.environ['TRAVIS_PULL_REQUEST_BRANCH']
        else:
            gitBranch = os.environ['TRAVIS_BRANCH']

    except KeyError:
        arguments = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        gitBranch = sp.check_output(arguments).decode("utf-8").strip()

    return gitBranch


def getLocalGitHash():
    try:
        if os.environ['TRAVIS_EVENT_TYPE'] == "pull_request":
            githash = os.environ['TRAVIS_PULL_REQUEST_SHA'][:gitHashLength]
        else:
            githash = os.environ['TRAVIS_COMMIT'][:gitHashLength]

    except KeyError:
        arguments = ["git", "rev-parse", "HEAD"]
        gitHash = sp.check_output(arguments).decode("utf-8")[:gitHashLength].strip()

    return gitHash

def expandDictionary(mainDictionary):
    tempList = []
    for key, value in mainDictionary.items():
        if type(value) == dict:
            newList = expandDictionary(value)
            for item in newList:
                tempList.append(key+"_"+item)
        else:
            tempList.append(key)

    return tempList

def getNestedValue(dictionary, *args):
    if args and dictionary:
        subkey = args[0]
        if subkey:
            value = dictionary.get(subkey)
            return value if len(args) == 1 else getNestedValue(value, *args[1:])

def setNestedValue(dictionary, value, keys):
    if keys and dictionary:
        if len(keys) == 1:
            dictionary[keys[0]] = value
        else:
            setNestedValue(dictionary.get(keys[0]), value, keys[1:])


def updateDefaults():
    for environmentVar in expandDictionary(DEFAULT_VALUES):
        try:
            setNestedValue(
                DEFAULT_VALUES,
                os.environ[environmentVar],
                environmentVar.split("_"),
            )
        except KeyError:
            pass

    repo = DEFAULT_VALUES["KATZEN"]["AUTH"]["REPOSITORY"]
    branch = DEFAULT_VALUES["KATZEN"]["AUTH"]["BRANCH"]
    value = DEFAULT_VALUES["KATZEN"]["AUTH"]["GITHASH"] 
    DEFAULT_VALUES["KATZEN"]["AUTH"]["GITHASH"] = value if value else getRemoteGitHash(repo, branch)

    repo = DEFAULT_VALUES["KATZEN"]["SERVER"]["REPOSITORY"]
    branch = DEFAULT_VALUES["KATZEN"]["SERVER"]["BRANCH"]
    value = DEFAULT_VALUES["KATZEN"]["SERVER"]["GITHASH"]
    DEFAULT_VALUES["KATZEN"]["SERVER"]["GITHASH"] = value if value else getRemoteGitHash(repo, branch)

    value = DEFAULT_VALUES["HASHCLOAK"]["MESON"]["GITHASH"]
    DEFAULT_VALUES["HASHCLOAK"]["MESON"]["GITHASH"] = value if value else getLocalGitHash()
    value = DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"]
    DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"] = value if value else getLocalGitBranch()

    if DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"] != "master":
        DEFAULT_VALUES["KATZEN"]["SERVER"]["DOCKERTAG"] = "warped"
        DEFAULT_VALUES["KATZEN"]["AUTH"]["DOCKERTAG"] = "warped"


print(compareRemoteContainers("hashcloak/meson:devops-restructure", "hashcloak/meson:devops-restructure"))
print(compareRemoteContainers("hashcloak/meson:devops-restructure", "hashcloak/meson:master"))
print(compareRemoteContainers("hashcloak/server:warped", "hashcloak/meson:master"))
