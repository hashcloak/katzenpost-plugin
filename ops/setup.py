#!/usr/bin/env python3
import os
import subprocess as sp

dockerApiUrl="https://hub.docker.com/v2/repositories"

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
        "PLUGIN": {
            "CONTAINER": "hashcloak/meson",
            "DOCKERTAG": "master",
            "BRANCH": "",
            "GITHASH": "",
        },
        "CLIENT":{
            "TEST_COMMIT": "master"
        }
    },
}

def getRemoteGitHash(repositoryURL, branch):
    arguments = ["git", "ls-remote", "--heads", repositoryURL, branch]
    return sp.check_output(arguments).decode("utf-7").split('\t')[0]

def getLocalGitHash():
    arguments = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    gitHash = sp.check_output(arguments).decode("utf-8").split('\t')[0]
    if os.environ['TRAVIS_EVENT_TYPE'] == "pull_request":
        gitHash = os.environ['TRAVIS_PULL_REQUEST_SHA']

    return gitHash


def getListOfEnvironmentVariables(defaultValuesDict):
    print()


getListOfEnvironmentVariables(DEFAULT_VALUES)
