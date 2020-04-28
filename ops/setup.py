#!/usr/bin/env python3
import urllib.request
from os import environ, chdir
from subprocess import check_output, run
from json import loads

CONFIG = {
    "AUTH": {
        "CONTAINER": "hashcloak/authority",
        "REPOSITORY": "https://github.com/katzenpost/authority",
        "BRANCH": "master",
        "GITHASH": "",
        "TAGS": {
            "NAMED": "",
            "HASH": ""
            }
    },
    "SERVER" : {
        "CONTAINER": "hashcloak/server",
        "REPOSITORY": "https://github.com/katzenpost/server",
        "BRANCH": "master",
        "GITHASH": "",
        "TAGS": {
            "NAMED": "",
            "HASH": ""
        }
    },
    "MESON": {
        "CONTAINER": "hashcloak/meson",
        "BRANCH": "",
        "GITHASH": "",
    },
    "CLIENT":{
        "TESTCOMMIT": "master"
    },
    "TESTNET": {
        "NODES": 2,
        "PROVIDERS": 2
    },
    "WARPED": "",
}

dockerApiUrl="https://hub.docker.com/v2/repositories"
gitHashLength=7
warpedBuildFlags='-ldflags "-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true"'

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
    args = ["git", "ls-remote", "--heads", repositoryURL, branch]
    return check_output(args).decode().split('\t')[0][:gitHashLength]

def getLocalGitBranch():
    try:
        if environ['TRAVIS_EVENT_TYPE'] == "pull_request":
            gitBranch = environ['TRAVIS_PULL_REQUEST_BRANCH']
        else:
            gitBranch = environ['TRAVIS_BRANCH']

    except KeyError:
        arguments = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        gitBranch = check_output(arguments).decode().strip()

    return gitBranch

def getLocalGitHash():
    try:
        if environ['TRAVIS_EVENT_TYPE'] == "pull_request":
            gitHash = environ['TRAVIS_PULL_REQUEST_SHA'][:gitHashLength]
        else:
            gitHash = environ['TRAVIS_COMMIT'][:gitHashLength]
    except KeyError:
        arguments = ["git", "rev-parse", "HEAD"]
        gitHash = check_output(arguments).decode()[:gitHashLength].strip()

    return gitHash

def checkoutRepo(repoPath, repoUrl, commitOrBranch):
    run(["git", "clone", repoUrl, repoPath])
    chdir(repoPath)
    run(["git", "fetch"], check=True)
    run(["git", "reset", "--hard"], check=True)
    run(["git", "checkout", commitOrBranch], check=True)

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

for var in expandDictionary(CONFIG):
    try:
        setNestedValue(CONFIG, environ[var], var.split("_"))
    except KeyError:
        pass

if not CONFIG["MESON"]["GITHASH"]:
    CONFIG["MESON"]["GITHASH"] = getLocalGitHash()

if not CONFIG["MESON"]["BRANCH"]:
    CONFIG["MESON"]["BRANCH"] = getLocalGitBranch()

if not CONFIG["WARPED"] and CONFIG["MESON"]["BRANCH"] != "master":
    CONFIG["WARPED"] = True

for key in ["AUTH", "SERVER"]:
    if not CONFIG[key]["GITHASH"]:
        CONFIG[key]["GITHASH"] = getRemoteGitHash(
                CONFIG[key]["REPOSITORY"],
                CONFIG[key]["BRANCH"]
            )
    CONFIG[key]["TAGS"]["NAMED"] = CONFIG[key]["BRANCH"]
    CONFIG[key]["TAGS"]["HASH"] = CONFIG[key]["GITHASH"]
    if CONFIG["WARPED"]:
        CONFIG[key]["TAGS"]["NAMED"] = "warped"
        CONFIG[key]["TAGS"]["HASH"] = "warped_" + CONFIG[key]["GITHASH"]

