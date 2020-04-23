#!/usr/bin/env python3
import os
import subprocess as sp

dockerApiUrl="https://hub.docker.com/v2/repositories"

CONFIG = {
        }
defaultValues = {
    "KATZEN_AUTH_CONTAINER": "hashcloak/authority",
    "KATZEN_AUTH_REPOSITORY": "https://github.com/katzenpost/authority",
    "KATZEN_AUTH_BRANCH": "master",
    "KATZEN_AUTH_DOCKERTAG": "master",
    "KATZEN_AUTH_GITHASH": "",
    "KATZEN_SERVER_CONTAINER": "hashcloak/server",
    "KATZEN_SERVER_REPOSITORY": "https://github.com/katzenpost/server",
    "KATZEN_SERVER_BRANCH": "master",
    "KATZEN_SERVER_DOCKERTAG": "master",
    "KATZEN_SERVER_GITHASH": "",
    "HASHCLOAK_PLUGIN_CONTAINER": "hashcloak/meson",
    "HASHCLOAK_PLUGIN_DOCKERTAG": "master",
    "HASHCLOAK_PLUGIN_BRANCH": "",
    "HASHCLOAK_PLUGIN_GITHASH": "",
    "HASHCLOAK_CLIENT_TEST_COMMIT": "master"
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

def getEnvironmentVariables(defaultValuesDict):
    newConfig = {}
    for key, value in defaultValuesDict.items():

        splitKeyPath = key.split("_")
        try:
            value = os.environ[key]
        except:
            pass

        if value == "":

            if "GITHASH" in splitKeyPath[-1]:
                getRemoteGitHash
            elif


        newConfig[

        print(key, value)


getEnvironmentVariables(defaultValues)
