from config import CONFIG
from subprocess import run
from typing import List

def log(message: str, err=False) -> None:
    """Logs a message to the console with purple.
    If err is True then it will log with red"""
    color = '\033[0;31m' if err else '\033[0;35m'
    noColor='\033[0m' # No Color
    if CONFIG["LOG"]:
        print("{}LOG: {}{}".format(color, message, noColor))

def checkoutRepo(repoPath: str, repoUrl: str, commitOrBranch: str) -> None:
    """Clones, and git checkouts a repository given a path, repo url and a commit or branch"""
    run(["git", "clone", repoUrl, repoPath])
    run(["git", "fetch"], check=True, cwd=repoPath)
    run(["git", "reset", "--hard"], check=True, cwd=repoPath)
    run(["git", "-c", "advice.detachedHead=false", "checkout", commitOrBranch], check=True, cwd=repoPath)

def genDockerService(
    name: str,
    image: str,
    ports: List[str] = [],
    volumes: List[str] = [],
    dependsOn: List[str] = [],
) -> str:

    s = '  '
    baseString = "{s}{name}:\n{s}{s}image: {image}\n".format(
        s=s,
        name=name,
        image=image,
    )

    if ports:
        baseString += "{s}ports:\n".format(s=s*2)
        for i in ports:
            baseString += '{s}- "{port}"\n'.format(s=s*3, port=i)

    if volumes:
        baseString += "{s}volumes:\n".format(s=s*2)
        for i in volumes:
            baseString += '{s}- {vol}\n'.format(s=s*3, vol=i)

    if dependsOn:
        baseString += "{s}depends_on:\n".format(s=s*2)
        for i in dependsOn:
            baseString += '{s}- "{dep}"\n'.format(s=s*3, dep=i)

    return baseString
