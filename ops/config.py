from os import getenv
from typing import List, Tuple
from subprocess import check_output

CONFIG = {
    "REPOS": {
        "AUTH": {
            "CONTAINER": "hashcloak/authority",
            "REPOSITORY": "https://github.com/katzenpost/authority",
            "BRANCH": "master",
            "GITHASH": "",
            "NAMEDTAG": "",
            "HASHTAG": "",
        },
        "SERVER" : {
            "CONTAINER": "hashcloak/server",
            "REPOSITORY": "https://github.com/katzenpost/server",
            "BRANCH": "master",
            "GITHASH": "",
            "NAMEDTAG": "",
            "HASHTAG": "",
        },
        "MESON": {
            "CONTAINER": "hashcloak/meson",
            "BRANCH": "",
            "GITHASH": "",
            "NAMEDTAG": "",
            "HASHTAG": "",
        },
    },
    "TEST": {
        "PKS": {
            "ETHEREUM": "",
            "BINANCE": ""
        },
        "CLIENTCOMMIT": "master",
        "NODES": 2,
        "PROVIDERS": 2,
        "ATTEMPTS": 3,
    },
    "LOG": "",
    "WARPED": "true",
    "BUILD": "",
}

gitHashLength=7
def getRemoteGitHash(repositoryURL: str, branchOrTag: str) -> str:
    """Gets the first 7 characters of a git commit hash in a remote repository"""
    args = ["git", "ls-remote", repositoryURL, branchOrTag]
    return check_output(args).decode().split('\t')[0][:gitHashLength]

def getLocalRepoInfo() -> Tuple[str, str]:
    """
    Gets the local repository information.
    This is changes depending on whether it is is running in Travis.
    """
    arguments = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    gitBranch = check_output(arguments).decode().strip()
    arguments = ["git", "rev-parse", "HEAD"]
    gitHash = check_output(arguments).decode().strip()
    if getenv('TRAVIS_EVENT_TYPE') == "pull_request":
        gitBranch = getenv('TRAVIS_PULL_REQUEST_BRANCH', gitBranch)
        gitHash = getenv('TRAVIS_PULL_REQUEST_SHA', gitHash)
    else:
        gitBranch = getenv('TRAVIS_BRANCH', gitBranch)
        gitHash = getenv('TRAVIS_COMMIT', gitHash)

    return gitBranch, gitHash[:gitHashLength]

def expandDictionary(dictionary: dict, seperator="_") -> List[str]:
    """
    Joins all the keys of a dictionary with a seperator string
    seperator default is '_'
    """
    tempList = []
    for key, value in dictionary.items():
        if type(value) == dict:
            for item in expandDictionary(value):
                tempList.append(key+seperator+item)
        else:
            tempList.append(key)

    return tempList

def setNestedValue(dictionary: dict, value: str, keys: List[str]) -> None:
    """Sets a nested value inside a dictionary"""
    if keys and dictionary:
        if len(keys) == 1:
            dictionary[keys[0]] = value
        else:
            setNestedValue(dictionary.get(keys[0]), value, keys[1:])

def getNestedValue(dictionary: dict, *args: List[str]) -> str:
    """Gets a nested value from a dictionary"""
    if args and dictionary:
        subkey = args[0]
        if subkey:
            value = dictionary.get(subkey)
            return value if len(args) == 1 else getNestedValue(value, *args[1:])

def main():
    for envVar in expandDictionary(CONFIG):
        value = getenv(envVar, getNestedValue(CONFIG, *envVar.split("_")))
        setNestedValue(CONFIG, value, envVar.split("_"))

    if CONFIG["WARPED"] == "false" or CONFIG["REPOS"]["MESON"]["BRANCH"] == "master":
        CONFIG["WARPED"] = ""

    localBranch, localHash = getLocalRepoInfo()
    if CONFIG["REPOS"]["MESON"]["BRANCH"] == "":
        CONFIG["REPOS"]["MESON"]["BRANCH"] = localBranch

    for key, repo in CONFIG["REPOS"].items():
        hashValue = localHash
        if key != "MESON":
            hashValue = getRemoteGitHash(repo["REPOSITORY"], repo["BRANCH"])

        repo["GITHASH"] = repo["GITHASH"] if repo["GITHASH"] else hashValue
        repo["NAMEDTAG"] = "warped_"+repo["BRANCH"] if CONFIG["WARPED"] else repo["BRANCH"]
        repo["HASHTAG"] = "warped_"+repo["GITHASH"] if CONFIG["WARPED"] else repo["GITHASH"]

main()
