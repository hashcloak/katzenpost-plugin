from os import environ, getenv
from subprocess import run, check_output

CONFIG = {
    "REPOS": {
        "AUTH": {
            "CONTAINER": "hashcloak/authority",
            "REPOSITORY": "https://github.com/katzenpost/authority",
            "BRANCH": "master",
            "GITHASH": "",
        },
        "SERVER" : {
            "CONTAINER": "hashcloak/server",
            "REPOSITORY": "https://github.com/katzenpost/server",
            "BRANCH": "master",
            "GITHASH": "",
        },
        "MESON": {
            "CONTAINER": "hashcloak/meson",
            "BRANCH": "",
            "GITHASH": "",
        },
    },
    "TEST": {
        "PKS": {
            "ETHEREUM": "",
            "BINANCE": ""
        },
        "CLIENTCOMMIT": "master",
        "NODES": 2,
        "PROVIDERS": 2
    },
    "WARPED": "true"
}

gitHashLength=7
warpedBuildFlags='-ldflags "-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true"'

def getRemoteGitHash(repositoryURL, branch):
    args = ["git", "ls-remote", "--heads", repositoryURL, branch]
    return check_output(args).decode().split('\t')[0][:gitHashLength]

def getLocalRepoInfo():
    try:
        if environ['TRAVIS_EVENT_TYPE'] == "pull_request":
            gitBranch = environ['TRAVIS_PULL_REQUEST_BRANCH']
            gitHash = environ['TRAVIS_PULL_REQUEST_SHA'][:gitHashLength]
        else:
            gitBranch = environ['TRAVIS_BRANCH']
            gitHash = environ['TRAVIS_COMMIT'][:gitHashLength]
    except KeyError:
        arguments = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        gitBranch = check_output(arguments).decode().strip()
        arguments = ["git", "rev-parse", "HEAD"]
        gitHash = check_output(arguments).decode()[:gitHashLength].strip()

    return gitBranch, gitHash

def checkoutRepo(repoPath, repoUrl, commitOrBranch):
    run(["git", "clone", repoUrl, repoPath])
    run(["git", "fetch"], check=True, cwd=repoPath)
    run(["git", "reset", "--hard"], check=True, cwd=repoPath)
    run(["git", "checkout", commitOrBranch], check=True, cwd=repoPath)

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

def setNestedValue(dictionary, value, keys):
    if keys and dictionary:
        if len(keys) == 1:
            dictionary[keys[0]] = value
        else:
            setNestedValue(dictionary.get(keys[0]), value, keys[1:])

def getNestedValue(dictionary, *args):
    if args and dictionary:
        subkey = args[0]
        if subkey:
            value = dictionary.get(subkey)
            return value if len(args) == 1 else getNestedValue(value, *args[1:])

for var in expandDictionary(CONFIG):
    value = getenv(var, getNestedValue(CONFIG, *var.split("_")))
    setNestedValue(CONFIG, value, var.split("_"))

if CONFIG["WARPED"] == "false" or CONFIG["MESON"]["BRANCH"] == "master":
    CONFIG["WARPED"] = ""

localBranch, localHash = getLocalRepoInfo()
if CONFIG["REPOS"]["MESON"]["BRANCH"] == "":
    CONFIG["REPOS"]["MESON"]["BRANCH"] = localBranch

for key, innerDict in CONFIG["REPOS"].items():
    if innerDict["GITHASH"] == "":
        if key == "MESON":
            innerDict["GITHASH"] = localHash
        else:
            innerDict["GITHASH"] = getRemoteGitHash(innerDict["REPOSITORY"], innerDict["BRANCH"])

