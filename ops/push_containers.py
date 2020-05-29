from subprocess import run
from config import setup_config

CONFIG = setup_config()

def main():
    for repo in CONFIG["REPOS"].values():
        run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["NAMEDTAG"])])
        run(["docker", "push", "{}:{}".format(repo["CONTAINER"], repo["HASHTAG"])])

if __name__ == "__main__":
    main()
