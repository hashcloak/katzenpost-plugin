import tempfile
import os
import subprocess as sp

from setup import *

currentPath = os.path.abspath(os.curdir)
dockerFile = os.path.join(currentPath, "Dockerfile")
tmpDockerFile = tempfile.NamedTemporaryFile().name

with open(dockerFile, 'r') as df, open(tmpDockerFile, 'w+') as tmpdf:
    for line in df:
        if DEFAULT_VALUES["KATZEN"]["SERVER"]["CONTAINER"] in line:
            line = "FROM {}:{}\n".format(
                    DEFAULT_VALUES["KATZEN"]["SERVER"]["CONTAINER"],
                    DEFAULT_VALUES["KATZEN"]["SERVER"]["DOCKERTAG"],
                )

        tmpdf.write(line)

container = DEFAULT_VALUES["HASHCLOAK"]["MESON"]["CONTAINER"]
tag = DEFAULT_VALUES["HASHCLOAK"]["MESON"]["GITHASH"]

print("\nLOG: Building Meson with {} tag\n".format(tag))
args = [
    "docker",
    "build",
    "-t",
    "{}:{}".format(container, tag),
    "-f",
    tmpDockerFile,
    currentPath
]
sp.run(args, check=True)

args = [
    "docker",
    "tag",
    "{}:{}".format(container, tag),
    "{}:{}".format(container, DEFAULT_VALUES["HASHCLOAK"]["MESON"]["BRANCH"]),
]
sp.run(args, check=True)
