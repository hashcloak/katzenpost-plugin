#!/usr/bin/env python3
import os
import subprocess as sp

dockerApiUrl="https://hub.docker.com/v2/repositories"
gitHashLength=7

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
        element  = args[0]
        if element:
            value = dictionary.get(element)
            return value if len(args) == 1 else getNestedValue(value, *args[1:])

def setNestedValue(dictionary, keys, value):
    for key in keys[-1]:
        pass

    print("set nested value: ", keys, value)

def getEnvironmentVariables():
    for environmentVar in expandDictionary(DEFAULT_VALUES):
        try:
            setNestedValue(
                DEFAULT_VALUES,
                environmentVar.split("_"),
                os.environ[environmentVar],
            )
        except KeyError:
            pass

    repo = DEFAULT_VALUES["KATZEN"]["AUTH"]["REPOSITORY"]
    branch = DEFAULT_VALUES["KATZEN"]["AUTH"]["BRANCH"]
    DEFAULT_VALUES["KATZEN"]["AUTH"]["GITHASH"] = getRemoteGitHash(repo, branch)

    repo = DEFAULT_VALUES["KATZEN"]["SERVER"]["REPOSITORY"]
    branch = DEFAULT_VALUES["KATZEN"]["SERVER"]["BRANCH"]
    DEFAULT_VALUES["KATZEN"]["SERVER"]["GITHASH"] = getRemoteGitHash(repo, branch)

    DEFAULT_VALUES["HASHCLOAK"]["MESON"]["GITHASH"] = getLocalGitHash()
    DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"] = getLocalGitBranch()

getEnvironmentVariables()
print(DEFAULT_VALUES)
