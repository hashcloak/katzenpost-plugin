import subprocess as sp
from setup import CONFIG

def pushContainer(container):
    try:
        print(sp.check_output(["docker", "push", container]).decode())
    except:
        pass

for key in ["AUTH", "SERVER"]:
    pushContainer("{}:{}".format(
        CONFIG[key]["CONTAINER"],
        CONFIG[key]["TAGS"]["NAMED"],
    ))
    pushContainer("{}:{}".format(
        CONFIG[key]["CONTAINER"],
        CONFIG[key]["TAGS"]["HASH"],
    ))

pushContainer("{}:{}".format(
    CONFIG["MESON"]["CONTAINER"],
    CONFIG["MESON"]["BRANCH"],
))
pushContainer("{}:{}".format(
    CONFIG["MESON"]["CONTAINER"],
    CONFIG["MESON"]["GITHASH"],
))

