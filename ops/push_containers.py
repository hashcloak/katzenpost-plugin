from subprocess import run
from config import setup_config

CONFIG = setup_config()

def push_containers():
    for repo in CONFIG["REPOS"].values():
        run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["NAMEDTAG"])])
        run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["HASHTAG"])])
