from subprocess import run
from config import CONFIG

for repo in CONFIG["REPOS"].values():
    run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["NAMEDTAG"])])
    run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["HASHTAG"])])
