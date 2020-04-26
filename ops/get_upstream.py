import tempfile
import subprocess as sp

from setup import *

def buildUpstream(container, tag, gitHash):
    print("HI", tempfile.gettempdir())
    t = tempfile.mkdtemp()
    print('created temporary directory', t)

def pullOrBuild(container, tag, gitHash):

    hashTag = "warped_"+gitHash if tag == "warped" else tag

    if compareRemoteContainers(container+":"+tag, container+":"+hashTag):
        print("pulling")
        arguments = ["docker", "pull", "{}:{}".format(container, hashTag)]
        sp.run(arguments, check=True)
    else:
        print("Building")
        buildUpstream(container, hashTag, gitHash)
        arguments = [
                "docker",
                "tag",
                "{}:{}".format(container, hashTag),
                "{}:{}".format(container, tag),
            ]
        sp.run(arguments, check=True)



pullOrBuild(
    DEFAULT_VALUES["KATZEN"]["SERVER"]["CONTAINER"],
    DEFAULT_VALUES["KATZEN"]["SERVER"]["DOCKERTAG"],
    DEFAULT_VALUES["KATZEN"]["SERVER"]["GITHASH"],
)
pullOrBuild(
    DEFAULT_VALUES["KATZEN"]["AUTH"]["CONTAINER"],
    DEFAULT_VALUES["KATZEN"]["AUTH"]["DOCKERTAG"],
    DEFAULT_VALUES["KATZEN"]["AUTH"]["GITHASH"],
)
