from config import CONFIG
from subprocess import run

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
